idf_component_register(
    SRCS "app_main.c"
    INCLUDE_DIRS "."
    PRIV_REQUIRES
        esp_driver_gpio
        esp_event
        esp_http_server
        esp_netif
        esp_wifi
        mqtt
        nvs_flash
)
