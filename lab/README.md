# MQTT lab configurations

## v0.1 desktop simulation

The Python behavior model and its Mosquitto broker bind to loopback only. Start the broker with:

    mosquitto -c lab/simulation/mosquitto.conf

It listens on 127.0.0.1:1883. The model retries its local MQTT connection if Mosquitto is not ready. Keep this listener loopback-only.

## Later ESP32 hardware setup

The ESP-IDF port uses the separate hardware configuration at mosquitto.conf.example. That example binds an unauthenticated listener to 192.168.10.2.

1. Use a dedicated access point with no internet or other network uplink.
2. Reserve 192.168.10.2 for the host running Mosquitto.
3. Start Mosquitto with mosquitto.conf.example only after confirming that the address belongs to the lab-only interface.
4. Configure the firmware's lab SSID, Wi-Fi password, and broker URI in menuconfig.
5. Use the device IP printed by the firmware's serial monitor to open the web page.

The hardware listener also has anonymous access and no TLS by design. Do not expose it on a home, office, campus, public, or internet-facing network.
