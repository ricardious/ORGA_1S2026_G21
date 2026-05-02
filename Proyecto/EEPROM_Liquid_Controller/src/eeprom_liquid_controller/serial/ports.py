"""Serial port discovery utilities."""

from __future__ import annotations

from glob import glob
from os.path import exists
import re
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
    return _sort_ports(set(ports + _development_ports()))


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
    return _sort_ports(set(ports))


def _sort_ports(ports: set[str]) -> list[str]:
    if platform == "win32":
        return sorted(ports, key=_windows_port_sort_key)
    return sorted(ports)


def _windows_port_sort_key(port: str) -> tuple[int, str]:
    match = re.fullmatch(r"COM(\d+)", port)
    if match:
        return (int(match.group(1)), port)
    return (10_000, port)


def _development_ports() -> list[str]:
    if not platform.startswith("linux"):
        return []
    return [port for port in LINUX_PROTEUS_PORTS if exists(port)]
