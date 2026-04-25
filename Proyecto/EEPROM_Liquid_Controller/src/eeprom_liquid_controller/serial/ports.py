"""Serial port discovery utilities."""

from __future__ import annotations

from glob import glob
from os.path import exists
from sys import platform

LINUX_PROTEUS_PORTS = ["/tmp/COM_Python"]


def list_serial_ports() -> list[str]:
    """Return available serial port names.

    Prefer pyserial when installed, but keep a small fallback so the UI can still
    show likely Arduino ports before dependencies are installed.
    """
    try:
        from serial.tools import list_ports
    except ImportError:
        return _fallback_ports()

    ports = [
        port.device for port in list_ports.comports() if _is_supported_port(port.device)
    ]
    return sorted(set(ports + _development_ports()))


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

    ports: list[str] = _development_ports()
    for pattern in patterns:
        ports.extend(glob(pattern))
    return sorted(set(ports))


def _development_ports() -> list[str]:
    if not platform.startswith("linux"):
        return []
    return [port for port in LINUX_PROTEUS_PORTS if exists(port)]
