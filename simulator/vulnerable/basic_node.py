#!/usr/bin/env python3
"""Loopback-only software model for the SPECTRA-32 v0.1 node behavior."""

from __future__ import annotations

import argparse
import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion


COMMAND_TOPIC = "spectra/device01/cmd"
STATUS_TOPIC = "spectra/device01/status"
WEB_ROOT = Path(__file__).resolve().parents[1] / "web"


class VirtualNode:
    """State-only behavioral model; this class does not emulate ESP32 hardware."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._led_on = False
        self._mqtt_connected = False
        self._commands_applied = 0

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            return {
                "led": "ON" if self._led_on else "OFF",
                "mqtt_connected": self._mqtt_connected,
                "commands_applied": self._commands_applied,
                "runtime": "software-simulation",
            }

    def set_mqtt_connected(self, connected: bool) -> None:
        with self._lock:
            self._mqtt_connected = connected

    def apply_command(self, led_on: bool, source: str) -> dict[str, object]:
        with self._lock:
            self._led_on = led_on
            self._commands_applied += 1
            snapshot = {
                "led": "ON" if self._led_on else "OFF",
                "mqtt_connected": self._mqtt_connected,
                "commands_applied": self._commands_applied,
                "runtime": "software-simulation",
            }
        logging.info(
            "command applied source=%s state=%s commands_applied=%d",
            source,
            snapshot["led"],
            snapshot["commands_applied"],
        )
        return snapshot


class MqttLink:
    """Connects the virtual node to a local Mosquitto broker."""

    def __init__(self, node: VirtualNode, host: str, port: int) -> None:
        self._node = node
        self._host = host
        self._port = port
        self._stop = threading.Event()
        self._connect_thread: threading.Thread | None = None
        self._loop_started = False

        self._client = mqtt.Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id="spectra32-software-sim",
            protocol=mqtt.MQTTv311,
        )
        self._client.reconnect_delay_set(min_delay=1, max_delay=5)
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message

    def start(self) -> None:
        self._connect_thread = threading.Thread(
            target=self._connect_until_ready,
            name="spectra32-mqtt-connect",
            daemon=True,
        )
        self._connect_thread.start()

    def _connect_until_ready(self) -> None:
        while not self._stop.is_set():
            try:
                result = self._client.connect(self._host, self._port, keepalive=30)
                if result == mqtt.MQTT_ERR_SUCCESS:
                    self._client.loop_start()
                    self._loop_started = True
                    return
                logging.warning("MQTT connect returned error code %s", result)
            except OSError as exc:
                logging.warning(
                    "MQTT broker unavailable at %s:%d (%s); retrying",
                    self._host,
                    self._port,
                    exc,
                )
            self._stop.wait(3)

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: Any,
        reason_code: Any,
        properties: Any,
    ) -> None:
        del userdata, flags, properties
        if reason_code != 0:
            logging.warning("MQTT connection rejected: %s", reason_code)
            self._node.set_mqtt_connected(False)
            return

        self._node.set_mqtt_connected(True)
        logging.info("connected to local MQTT broker %s:%d", self._host, self._port)
        result, _message_id = client.subscribe(COMMAND_TOPIC, qos=0)
        if result != mqtt.MQTT_ERR_SUCCESS:
            logging.warning("could not subscribe to %s: code=%s", COMMAND_TOPIC, result)
        self.publish_status()

    def _on_disconnect(
        self,
        client: mqtt.Client,
        userdata: Any,
        disconnect_flags: Any,
        reason_code: Any,
        properties: Any,
    ) -> None:
        del client, userdata, disconnect_flags, properties
        self._node.set_mqtt_connected(False)
        if not self._stop.is_set():
            logging.warning("MQTT disconnected: %s", reason_code)

    def _on_message(
        self,
        client: mqtt.Client,
        userdata: Any,
        message: Any,
    ) -> None:
        del client, userdata
        if message.topic != COMMAND_TOPIC:
            return

        if message.payload == b"ON":
            self._node.apply_command(True, source="MQTT")
        elif message.payload == b"OFF":
            self._node.apply_command(False, source="MQTT")
        else:
            logging.warning("ignored invalid MQTT command payload")
            return
        self.publish_status()

    def publish_status(self) -> None:
        snapshot = self._node.snapshot()
        if not snapshot["mqtt_connected"]:
            return
        payload = str(snapshot["led"])
        result = self._client.publish(STATUS_TOPIC, payload, qos=0, retain=False)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            logging.warning("could not publish MQTT state: code=%s", result.rc)

    def close(self) -> None:
        self._stop.set()
        if self._connect_thread is not None:
            self._connect_thread.join(timeout=1)
        if self._loop_started:
            self._client.disconnect()
            self._client.loop_stop()


def make_http_handler(node: VirtualNode, mqtt_link: MqttLink) -> type[BaseHTTPRequestHandler]:
    index_html = (WEB_ROOT / "index.html").read_bytes()

    class Handler(BaseHTTPRequestHandler):
        server_version = "SPECTRA32-SoftwareSim/0.1"

        def log_message(self, format_string: str, *args: object) -> None:
            logging.debug("HTTP " + format_string, *args)

        def _send_json(self, status: int, value: dict[str, object]) -> None:
            body = json.dumps(value, separators=(",", ":")).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            path = urlsplit(self.path).path
            if path == "/":
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(index_html)))
                self.end_headers()
                self.wfile.write(index_html)
                return
            if path == "/api/state":
                self._send_json(200, node.snapshot())
                return
            self._send_json(404, {"error": "not found"})

        def do_POST(self) -> None:
            if urlsplit(self.path).path != "/api/led":
                self._send_json(404, {"error": "not found"})
                return

            try:
                content_length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._send_json(400, {"error": "invalid content length"})
                return
            if content_length < 1 or content_length > 64:
                self._send_json(400, {"error": "invalid request body"})
                return

            try:
                form = parse_qs(
                    self.rfile.read(content_length).decode("ascii"),
                    keep_blank_values=True,
                    strict_parsing=True,
                )
            except (UnicodeDecodeError, ValueError):
                self._send_json(400, {"error": "invalid form body"})
                return

            values = form.get("state", [])
            if set(form) != {"state"} or len(values) != 1 or values[0] not in {"on", "off"}:
                self._send_json(400, {"error": "state must be on or off"})
                return

            snapshot = node.apply_command(values[0] == "on", source="HTTP")
            mqtt_link.publish_status()
            self._send_json(200, snapshot)

    return Handler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the loopback-only SPECTRA-32 basic-node behavior simulator."
    )
    parser.add_argument("--http-port", type=int, default=8080)
    parser.add_argument("--mqtt-port", type=int, default=1883)
    args = parser.parse_args()
    for name in ("http_port", "mqtt_port"):
        if not 1 <= getattr(args, name) <= 65535:
            parser.error(f"--{name.replace('_', '-')} must be between 1 and 65535")
    return args


def main() -> None:
    args = parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    node = VirtualNode()
    mqtt_link = MqttLink(node, host="127.0.0.1", port=args.mqtt_port)
    handler = make_http_handler(node, mqtt_link)
    server = ThreadingHTTPServer(("127.0.0.1", args.http_port), handler)
    server.daemon_threads = True

    mqtt_link.start()
    logging.info("virtual LED starts OFF")
    logging.info("web interface available at http://127.0.0.1:%d/", args.http_port)
    logging.info("MQTT command topic: %s", COMMAND_TOPIC)
    logging.info("MQTT status topic: %s", STATUS_TOPIC)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("stopping simulator")
    finally:
        server.server_close()
        mqtt_link.close()


if __name__ == "__main__":
    main()
