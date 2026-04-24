"""Serial transport placeholder for Arduino USB communication."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SerialConfig:
    port: str
    baudrate: int = 9600
    timeout: float = 2.0


class ArduinoSerialClient:
    """Small boundary object for future pyserial integration."""

    def __init__(self, config: SerialConfig) -> None:
        self.config = config

    def send_text(self, payload: str) -> None:
        """Send text to Arduino over serial.

        This is intentionally unimplemented until the project chooses the exact
        serial dependency and protocol framing.
        """
        raise NotImplementedError("Serial communication is not implemented yet.")
