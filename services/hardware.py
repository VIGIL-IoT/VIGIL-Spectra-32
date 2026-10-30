"""Read-only USB serial discovery and ESP chip identification for local use."""

from __future__ import annotations

import re
import subprocess
import sys
from typing import Literal, TypedDict


class SerialPort(TypedDict):
    device: str
    description: str
    vendor_id: int | None
    product_id: int | None


HardwareStatus = Literal["supported", "other_esp", "unidentified", "disconnected", "tool_missing"]


class ChipIdentification(TypedDict):
    status: HardwareStatus
    chip: str
    message: str


def list_serial_ports() -> tuple[list[SerialPort], str | None]:
    """List host serial ports without opening or resetting them."""
    try:
        from serial.tools import list_ports
    except ImportError:
        return [], "pySerial is not installed. Install simulator/requirements.txt and restart the app."

    try:
        ports = [
            SerialPort(
                device=str(port.device),
                description=str(port.description or "USB serial device"),
                vendor_id=port.vid,
                product_id=port.pid,
            )
            for port in list_ports.comports()
        ]
    except Exception:
        return [], "The host could not enumerate serial ports. Check USB drivers and permissions."

    return sorted(ports, key=lambda port: port["device"]), None


def classify_esptool_output(output: str) -> tuple[HardwareStatus, str]:
    """Classify an esptool chip response without exposing its full output."""
    patterns = (
        r"Detecting chip type\.{2,}\s*(ESP[A-Z0-9-]+)",
        r"\bChip is\s+(ESP[A-Z0-9-]+)",
        r"\bChip type:\s*(ESP[A-Z0-9-]+)",
    )
    chip = ""
    for pattern in patterns:
        match = re.search(pattern, output, flags=re.IGNORECASE)
        if match:
            chip = match.group(1).upper()
            break

    if not chip:
        return "unidentified", "A serial port responded, but esptool could not confirm an Espressif chip."

    # esptool may report the classic ESP32 target or a more specific module
    # name such as ESP32-D0WD-V3. Other ESP32 family targets stay unsupported.
    if chip == "ESP32" or chip.startswith("ESP32-D"):
        return "supported", chip
    return "other_esp", chip


def identify_esp_chip(port_name: str, timeout_seconds: int = 20) -> ChipIdentification:
    """Run esptool's chip-ID probe on one currently enumerated host port.

    The ROM-only probe can reset the board and enter its downloader, but it
    does not upload a stub or erase/write flash. The user explicitly clicks
    Identify in the UI.
    """
    ports, error = list_serial_ports()
    if error:
        status: HardwareStatus = "tool_missing" if "pySerial" in error else "unidentified"
        return {"status": status, "chip": "Unknown", "message": error}
    if not any(port["device"] == port_name for port in ports):
        return {
            "status": "disconnected",
            "chip": "Unknown",
            "message": "That serial port is no longer connected. Reconnect the board and retry.",
        }

    command = [
        sys.executable,
        "-m",
        "esptool",
        "--port",
        port_name,
        "--baud",
        "115200",
        "--no-stub",
        "chip-id",
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
    except FileNotFoundError:
        return {
            "status": "tool_missing",
            "chip": "Unknown",
            "message": "esptool is not installed. Install simulator/requirements.txt and restart the app.",
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "unidentified",
            "chip": "Unknown",
            "message": "No chip response before timeout. Confirm the port, close serial monitors, then retry; some boards need BOOT held during connect.",
        }
    except OSError:
        return {
            "status": "unidentified",
            "chip": "Unknown",
            "message": "The serial port could not be opened. Close other serial tools and check the USB driver.",
        }

    output = f"{result.stdout}\n{result.stderr}"
    if "No module named esptool" in output:
        return {
            "status": "tool_missing",
            "chip": "Unknown",
            "message": "esptool is not installed. Install simulator/requirements.txt and restart the app.",
        }
    if result.returncode != 0:
        return {
            "status": "unidentified",
            "chip": "Unknown",
            "message": "esptool could not complete the chip-identification request. Confirm the port, close serial monitors, and retry.",
        }
    status, chip = classify_esptool_output(output)
    if status == "supported":
        return {"status": status, "chip": chip, "message": "Classic ESP32 detected; supported by SPECTRA-32 v0.1."}
    if status == "other_esp":
        return {"status": status, "chip": chip, "message": f"Other ESP detected ({chip}); not supported by SPECTRA-32 v0.1 yet."}
    return {
        "status": "unidentified",
        "chip": "Unknown",
        "message": "Chip not identified. Confirm the port, close serial monitors, and retry; some boards need BOOT held during connect.",
    }
