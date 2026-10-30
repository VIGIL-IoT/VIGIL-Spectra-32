"""Loopback-only HTTP route checks for the standalone virtual node."""

from __future__ import annotations

from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
import threading
import unittest

from simulator.vulnerable.basic_node import VirtualNode, make_http_handler


class FakeMqttLink:
    def __init__(self) -> None:
        self.status_publications = 0

    def publish_status(self) -> None:
        self.status_publications += 1


class NodeHttpTests(unittest.TestCase):
    def setUp(self) -> None:
        self.node = VirtualNode()
        self.mqtt_link = FakeMqttLink()
        self.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), make_http_handler(self.node, self.mqtt_link)
        )
        self.server.daemon_threads = True
        self.server_thread = threading.Thread(
            target=self.server.serve_forever,
            name="spectra-http-test-server",
            daemon=True,
        )
        self.server_thread.start()
        self.port = self.server.server_address[1]

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.server_thread.join(timeout=2)

    def request(self, method: str, path: str, body: str | None = None) -> tuple[int, dict[str, object]]:
        connection = HTTPConnection("127.0.0.1", self.port, timeout=2)
        try:
            headers = {"Content-Type": "application/x-www-form-urlencoded"} if body is not None else {}
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            payload = json.loads(response.read().decode("utf-8"))
            return response.status, payload
        finally:
            connection.close()

    def test_state_route_reports_initial_virtual_state(self) -> None:
        status, body = self.request("GET", "/api/state")
        self.assertEqual(status, 200)
        self.assertEqual(body["led"], "OFF")
        self.assertEqual(body["runtime"], "software-simulation")

    def test_led_route_applies_only_one_valid_form_value(self) -> None:
        status, body = self.request("POST", "/api/led", "state=on")
        self.assertEqual(status, 200)
        self.assertEqual(body["led"], "ON")
        self.assertEqual(body["commands_applied"], 1)
        self.assertEqual(self.mqtt_link.status_publications, 1)

    def test_duplicate_or_invalid_form_values_are_rejected(self) -> None:
        for form in ("state=on&state=off", "state=toggle", "state=on&extra=1"):
            with self.subTest(form=form):
                status, body = self.request("POST", "/api/led", form)
                self.assertEqual(status, 400)
                self.assertIn("error", body)
        self.assertEqual(self.node.snapshot()["led"], "OFF")
        self.assertEqual(self.node.snapshot()["commands_applied"], 0)

    def test_unknown_route_is_not_found(self) -> None:
        status, body = self.request("GET", "/missing")
        self.assertEqual(status, 404)
        self.assertEqual(body["error"], "not found")


if __name__ == "__main__":
    unittest.main()
