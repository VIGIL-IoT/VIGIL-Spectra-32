#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "driver/gpio.h"
#include "esp_event.h"
#include "esp_http_server.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_netif_ip_addr.h"
#include "esp_wifi.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "mqtt_client.h"
#include "nvs_flash.h"

#include "web_ui.h"

#define MQTT_COMMAND_TOPIC "spectra/device01/cmd"
#define MQTT_STATUS_TOPIC  "spectra/device01/status"

static const char *TAG = "spectra32";

static SemaphoreHandle_t s_state_mutex;
static gpio_num_t s_led_gpio = (gpio_num_t)CONFIG_SPECTRA32_LED_GPIO;
static bool s_led_on;
static bool s_mqtt_connected;
static esp_mqtt_client_handle_t s_mqtt_client;
static httpd_handle_t s_http_server;

static void state_snapshot(bool *led_on, bool *mqtt_connected)
{
    xSemaphoreTake(s_state_mutex, portMAX_DELAY);
    *led_on = s_led_on;
    *mqtt_connected = s_mqtt_connected;
    xSemaphoreGive(s_state_mutex);
}

static esp_err_t set_led_state(bool led_on)
{
    xSemaphoreTake(s_state_mutex, portMAX_DELAY);
    const esp_err_t err = gpio_set_level(s_led_gpio, led_on ? 1 : 0);
    if (err == ESP_OK) {
        s_led_on = led_on;
    }
    xSemaphoreGive(s_state_mutex);
    return err;
}

static void set_mqtt_connected(bool connected)
{
    xSemaphoreTake(s_state_mutex, portMAX_DELAY);
    s_mqtt_connected = connected;
    xSemaphoreGive(s_state_mutex);
}

static void publish_led_state(void)
{
    bool led_on;
    bool mqtt_connected;
    state_snapshot(&led_on, &mqtt_connected);
    if (!mqtt_connected || s_mqtt_client == NULL) {
        return;
    }

    const char *payload = led_on ? "ON" : "OFF";
    const int message_id = esp_mqtt_client_publish(
        s_mqtt_client, MQTT_STATUS_TOPIC, payload, 0, 0, 0);
    if (message_id < 0) {
        ESP_LOGW(TAG, "Could not publish LED status");
    }
}

static esp_err_t send_json(httpd_req_t *req, const char *status, const char *body)
{
    if (status != NULL) {
        httpd_resp_set_status(req, status);
    }
    httpd_resp_set_type(req, "application/json");
    httpd_resp_set_hdr(req, "Cache-Control", "no-store");
    return httpd_resp_send(req, body, HTTPD_RESP_USE_STRLEN);
}

static esp_err_t send_state(httpd_req_t *req)
{
    bool led_on;
    bool mqtt_connected;
    state_snapshot(&led_on, &mqtt_connected);

    char body[96];
    const int length = snprintf(
        body,
        sizeof(body),
        "{\"led\":\"%s\",\"mqtt_connected\":%s}",
        led_on ? "ON" : "OFF",
        mqtt_connected ? "true" : "false");
    if (length < 0 || (size_t)length >= sizeof(body)) {
        return ESP_FAIL;
    }
    return send_json(req, NULL, body);
}

static esp_err_t root_get_handler(httpd_req_t *req)
{
    httpd_resp_set_type(req, "text/html; charset=utf-8");
    httpd_resp_set_hdr(req, "Cache-Control", "no-store");
    return httpd_resp_send(req, SPECTRA32_INDEX_HTML, HTTPD_RESP_USE_STRLEN);
}

static esp_err_t state_get_handler(httpd_req_t *req)
{
    return send_state(req);
}

static esp_err_t led_post_handler(httpd_req_t *req)
{
    char body[32];
    if (req->content_len == 0 || req->content_len >= sizeof(body)) {
        return send_json(req, "400 Bad Request", "{\"error\":\"invalid request body\"}");
    }

    size_t received_total = 0;
    while (received_total < req->content_len) {
        const int received = httpd_req_recv(
            req,
            body + received_total,
            req->content_len - received_total);
        if (received <= 0) {
            return ESP_FAIL;
        }
        received_total += (size_t)received;
    }
    body[received_total] = '\0';

    bool next_state;
    if (strcmp(body, "state=on") == 0) {
        next_state = true;
    } else if (strcmp(body, "state=off") == 0) {
        next_state = false;
    } else {
        return send_json(req, "400 Bad Request", "{\"error\":\"state must be on or off\"}");
    }

    const esp_err_t err = set_led_state(next_state);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "GPIO update failed: %s", esp_err_to_name(err));
        return send_json(req, "500 Internal Server Error", "{\"error\":\"output update failed\"}");
    }

    ESP_LOGI(TAG, "Web command applied: %s", next_state ? "ON" : "OFF");
    publish_led_state();
    return send_state(req);
}

static void start_http_server(void)
{
    if (s_http_server != NULL) {
        return;
    }

    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.max_uri_handlers = 4;

    esp_err_t err = httpd_start(&s_http_server, &config);
    if (err != ESP_OK) {
        s_http_server = NULL;
        ESP_LOGE(TAG, "Could not start HTTP server: %s", esp_err_to_name(err));
        return;
    }

    const httpd_uri_t root_uri = {
        .uri = "/",
        .method = HTTP_GET,
        .handler = root_get_handler,
    };
    const httpd_uri_t state_uri = {
        .uri = "/api/state",
        .method = HTTP_GET,
        .handler = state_get_handler,
    };
    const httpd_uri_t led_uri = {
        .uri = "/api/led",
        .method = HTTP_POST,
        .handler = led_post_handler,
    };

    err = httpd_register_uri_handler(s_http_server, &root_uri);
    if (err == ESP_OK) {
        err = httpd_register_uri_handler(s_http_server, &state_uri);
    }
    if (err == ESP_OK) {
        err = httpd_register_uri_handler(s_http_server, &led_uri);
    }
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Could not register HTTP routes: %s", esp_err_to_name(err));
        httpd_stop(s_http_server);
        s_http_server = NULL;
        return;
    }

    ESP_LOGI(TAG, "Web control ready at http://<device-ip>/");
}

static void mqtt_event_handler(
    void *handler_args,
    esp_event_base_t event_base,
    int32_t event_id,
    void *event_data)
{
    (void)handler_args;
    (void)event_base;
    esp_mqtt_event_handle_t event = event_data;

    switch ((esp_mqtt_event_id_t)event_id) {
    case MQTT_EVENT_CONNECTED: {
        ESP_LOGI(TAG, "Connected to local MQTT broker");
        set_mqtt_connected(true);
        const int message_id = esp_mqtt_client_subscribe(
            s_mqtt_client, MQTT_COMMAND_TOPIC, 0);
        if (message_id < 0) {
            ESP_LOGW(TAG, "Could not subscribe to command topic");
        }
        publish_led_state();
        break;
    }
    case MQTT_EVENT_DISCONNECTED:
        ESP_LOGW(TAG, "Disconnected from MQTT broker");
        set_mqtt_connected(false);
        break;
    case MQTT_EVENT_DATA: {
        const size_t expected_topic_length = strlen(MQTT_COMMAND_TOPIC);
        if (event->topic_len != (int)expected_topic_length ||
            memcmp(event->topic, MQTT_COMMAND_TOPIC, expected_topic_length) != 0) {
            break;
        }

        // Commands are deliberately small. Ignore fragmented payloads rather than
        // accidentally treating a partial message as a complete LED command.
        if (event->current_data_offset != 0 || event->data_len != event->total_data_len) {
            ESP_LOGW(TAG, "Ignoring fragmented MQTT command");
            break;
        }

        bool next_state;
        if (event->data_len == 2 && memcmp(event->data, "ON", 2) == 0) {
            next_state = true;
        } else if (event->data_len == 3 && memcmp(event->data, "OFF", 3) == 0) {
            next_state = false;
        } else {
            ESP_LOGW(TAG, "Ignoring invalid MQTT LED command");
            break;
        }

        if (set_led_state(next_state) == ESP_OK) {
            ESP_LOGI(TAG, "MQTT command applied: %s", next_state ? "ON" : "OFF");
            publish_led_state();
        }
        break;
    }
    case MQTT_EVENT_ERROR:
        ESP_LOGW(TAG, "MQTT client reported an error");
        break;
    default:
        break;
    }
}

static void start_mqtt_client(void)
{
    if (s_mqtt_client != NULL) {
        return;
    }
    if (CONFIG_SPECTRA32_MQTT_BROKER_URI[0] == '\0') {
        ESP_LOGW(TAG, "MQTT broker URI is empty; web control remains available");
        return;
    }

    const esp_mqtt_client_config_t config = {
        .broker.address.uri = CONFIG_SPECTRA32_MQTT_BROKER_URI,
    };
    s_mqtt_client = esp_mqtt_client_init(&config);
    if (s_mqtt_client == NULL) {
        ESP_LOGE(TAG, "Could not initialize MQTT client");
        return;
    }

    esp_err_t err = esp_mqtt_client_register_event(
        s_mqtt_client, ESP_EVENT_ANY_ID, mqtt_event_handler, NULL);
    if (err == ESP_OK) {
        err = esp_mqtt_client_start(s_mqtt_client);
    }
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Could not start MQTT client: %s", esp_err_to_name(err));
        esp_mqtt_client_destroy(s_mqtt_client);
        s_mqtt_client = NULL;
        return;
    }

    ESP_LOGI(TAG, "MQTT client started for %s", CONFIG_SPECTRA32_MQTT_BROKER_URI);
}

static void wifi_event_handler(
    void *handler_args,
    esp_event_base_t event_base,
    int32_t event_id,
    void *event_data)
{
    (void)handler_args;
    (void)event_data;

    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
        ESP_ERROR_CHECK(esp_wifi_connect());
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        set_mqtt_connected(false);
        ESP_LOGW(TAG, "Wi-Fi disconnected; reconnecting");
        ESP_ERROR_CHECK(esp_wifi_connect());
    }
}

static void ip_event_handler(
    void *handler_args,
    esp_event_base_t event_base,
    int32_t event_id,
    void *event_data)
{
    (void)handler_args;
    if (event_base != IP_EVENT || event_id != IP_EVENT_STA_GOT_IP) {
        return;
    }

    const ip_event_got_ip_t *event = event_data;
    ESP_LOGI(TAG, "Connected; device IP: " IPSTR, IP2STR(&event->ip_info.ip));
    start_http_server();
    start_mqtt_client();
}

static void configure_led(void)
{
    if (!GPIO_IS_VALID_OUTPUT_GPIO(s_led_gpio)) {
        ESP_LOGE(TAG, "GPIO %d is not a valid output on this target", (int)s_led_gpio);
        abort();
    }

    const gpio_config_t config = {
        .pin_bit_mask = 1ULL << s_led_gpio,
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&config));
    ESP_ERROR_CHECK(gpio_set_level(s_led_gpio, 0));
}

static void start_wifi_station(void)
{
    wifi_config_t wifi_config = {0};
    const size_t ssid_length = strlen(CONFIG_SPECTRA32_WIFI_SSID);
    const size_t password_length = strlen(CONFIG_SPECTRA32_WIFI_PASSWORD);

    if (ssid_length == 0 || ssid_length >= sizeof(wifi_config.sta.ssid)) {
        ESP_LOGE(TAG, "Set a lab Wi-Fi SSID shorter than 32 characters in menuconfig");
        abort();
    }
    if (password_length < 8 || password_length >= sizeof(wifi_config.sta.password)) {
        ESP_LOGE(TAG, "Set a WPA2 lab Wi-Fi password between 8 and 63 characters in menuconfig");
        abort();
    }

    strlcpy((char *)wifi_config.sta.ssid, CONFIG_SPECTRA32_WIFI_SSID,
            sizeof(wifi_config.sta.ssid));
    strlcpy((char *)wifi_config.sta.password, CONFIG_SPECTRA32_WIFI_PASSWORD,
            sizeof(wifi_config.sta.password));
    wifi_config.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;

    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    if (esp_netif_create_default_wifi_sta() == NULL) {
        ESP_LOGE(TAG, "Could not create the station network interface");
        abort();
    }

    const wifi_init_config_t init_config = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&init_config));
    ESP_ERROR_CHECK(esp_event_handler_register(
        WIFI_EVENT, ESP_EVENT_ANY_ID, wifi_event_handler, NULL));
    ESP_ERROR_CHECK(esp_event_handler_register(
        IP_EVENT, IP_EVENT_STA_GOT_IP, ip_event_handler, NULL));
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());

    ESP_LOGI(TAG, "Joining the configured isolated lab Wi-Fi network");
}

void app_main(void)
{
    s_state_mutex = xSemaphoreCreateMutex();
    if (s_state_mutex == NULL) {
        ESP_LOGE(TAG, "Could not create state mutex");
        abort();
    }

    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    ESP_ERROR_CHECK(err);

    configure_led();
    start_wifi_station();
}
