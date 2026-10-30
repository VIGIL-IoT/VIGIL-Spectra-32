"""Loopback integration checks for the standalone MQTT behavior model."""

from __future__ import annotations

import queue
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import unittest
from pathlib import Path

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

from simulator.vulnerable.basic_node import COMMAND_TOPIC, STATUS_TOPIC, MqttLink, VirtualNode


class NodeMqttIntegrationTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("mosquitto"), "Mosquitto is required for this integration test")
    def test_commands_update_virtual_state_and_publish_status(self) -> None:
        broker_port = self._available_port()
        with tempfile.TemporaryDirectory(prefix="spectra-mqtt-test-") as temp_dir:
            config_path = Path(temp_dir) / "mosquitto.conf"
            config_path.write_text(
                f"listener {broker_port} 127.0.0.1\nallow_anonymous true\npersistence false\n",
                encoding="utf-8",
            )
            broker = subprocess.Popen(
                [shutil.which("mosquitto") or "mosquitto", "-c", str(config_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            subscriber = mqtt.Client(
                callback_api_version=CallbackAPIVersion.VERSION2,
                client_id="spectra32-mqtt-test-subscriber",
                protocol=mqtt.MQTTv311,
            )
            subscribed = threading.Event()
            connect_failed = threading.Event()
            status_messages: queue.Queue[str] = queue.Queue()
            mqtt_link: MqttLink | None = None
            try:
                self._wait_for_broker(broker, broker_port)

                def on_connect(
                    client: mqtt.Client,
                    userdata: object,
                    flags: object,
                    reason_code: object,
                    properties: object,
                ) -> None:
                    del userdata, flags, properties
                    if reason_code != 0:
                        connect_failed.set()
                        return
                    client.subscribe(STATUS_TOPIC, qos=0)

                def on_subscribe(
                    client: mqtt.Client,
                    userdata: object,
                    mid: int,
                    reason_codes: object,
                    properties: object,
                ) -> None:
                    del client, userdata, mid, reason_codes, properties
                    subscribed.set()

                def on_message(
                    client: mqtt.Client,
                    userdata: object,
                    message: mqtt.MQTTMessage,
                ) -> None:
                    del client, userdata
                    status_messages.put(message.payload.decode("ascii"))

                subscriber.on_connect = on_connect
                subscriber.on_subscribe = on_subscribe
                subscriber.on_message = on_message
                self.assertEqual(subscriber.connect("127.0.0.1", broker_port, keepalive=30), 0)
                subscriber.loop_start()
                self.assertTrue(subscribed.wait(5), "status subscriber did not receive SUBACK")
                self.assertFalse(connect_failed.is_set(), "status subscriber connection was rejected")

                node = VirtualNode()
                mqtt_link = MqttLink(node, host="127.0.0.1", port=broker_port)
                mqtt_link.start()
                self.assertEqual(self._next_status(status_messages), "OFF")
                self.assertTrue(node.snapshot()["mqtt_connected"])

                publish = subscriber.publish(COMMAND_TOPIC, payload="ON", qos=0, retain=False)
                self.assertEqual(publish.rc, mqtt.MQTT_ERR_SUCCESS)
                self.assertEqual(self._next_status(status_messages), "ON")
                self.assertEqual(node.snapshot()["led"], "ON")
                self.assertEqual(node.snapshot()["commands_applied"], 1)

                invalid_publish = subscriber.publish(COMMAND_TOPIC, payload="TOGGLE", qos=0, retain=False)
                self.assertEqual(invalid_publish.rc, mqtt.MQTT_ERR_SUCCESS)
                time.sleep(0.25)
                self.assertEqual(node.snapshot()["led"], "ON")
                self.assertEqual(node.snapshot()["commands_applied"], 1)

                publish = subscriber.publish(COMMAND_TOPIC, payload="OFF", qos=0, retain=False)
                self.assertEqual(publish.rc, mqtt.MQTT_ERR_SUCCESS)
                self.assertEqual(self._next_status(status_messages), "OFF")
                self.assertEqual(node.snapshot()["led"], "OFF")
                self.assertEqual(node.snapshot()["commands_applied"], 2)
            finally:
                if mqtt_link is not None:
                    mqtt_link.close()
                subscriber.disconnect()
                subscriber.loop_stop()
                broker.terminate()
                try:
                    broker.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    broker.kill()
                    broker.wait(timeout=3)

    @staticmethod
    def _available_port() -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.bind(("127.0.0.1", 0))
            return int(listener.getsockname()[1])

    def _wait_for_broker(self, broker: subprocess.Popen[bytes], port: int) -> None:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if broker.poll() is not None:
                self.fail(f"Mosquitto exited before opening its loopback port (exit {broker.returncode})")
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                    return
            except OSError:
                time.sleep(0.05)
        self.fail("Mosquitto did not open its loopback port within five seconds")

    @staticmethod
    def _next_status(messages: queue.Queue[str]) -> str:
        return messages.get(timeout=5)


if __name__ == "__main__":
    unittest.main()
