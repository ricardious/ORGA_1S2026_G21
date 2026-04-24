"""Serial port discovery utilities."""

from __future__ import annotations

from glob import glob
from sys import platform


def list_serial_ports() -> list[str]:
    """Return available serial port names.

    Prefer pyserial when installed, but keep a small fallback so the UI can still
    show likely Arduino ports before dependencies are installed.
    """
    try:
        from serial.tools import list_ports
    except ImportError:
        return _fallback_ports()

    return sorted(
        port.device for port in list_ports.comports() if _is_supported_port(port.device)
    )


def _is_supported_port(device: str) -> bool:
    if platform.startswith("linux"):
        return device.startswith(("/dev/ttyACM", "/dev/ttyUSB"))
    if platform == "darwin":
        return device.startswith(("/dev/tty.usbmodem", "/dev/tty.usbserial"))
    if platform == "win32":
        return device.startswith("COM")
    return False


def _fallback_ports() -> list[str]:
    if platform.startswith("linux"):
        patterns = ["/dev/ttyACM*", "/dev/ttyUSB*"]
    elif platform == "darwin":
        patterns = ["/dev/tty.usbmodem*", "/dev/tty.usbserial*"]
    elif platform == "win32":
        patterns = [f"COM{index}" for index in range(1, 257)]
        return patterns
    else:
        return []

    ports: list[str] = []
    for pattern in patterns:
        ports.extend(glob(pattern))
    return sorted(ports)
