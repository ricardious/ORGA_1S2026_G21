"""Serial transport for Arduino USB communication."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from time import sleep


@dataclass(frozen=True)
class SerialConfig:
    port: str
    baudrate: int = 9600
    timeout: float = 2.0
    reset_delay: float = 2.0
    chunk_size: int = 64


class SerialSendError(RuntimeError):
    """Raised when the Arduino serial transfer fails."""


class ArduinoSerialClient:
    """Small boundary object for pyserial integration."""

    def __init__(self, config: SerialConfig) -> None:
        self.config = config

    def send_text(
        self,
        payload: str,
        progress_callback: Callable[[int], None] | None = None,
    ) -> None:
        """Send UTF-8 text to Arduino over serial."""
        if not payload.strip():
            raise SerialSendError("El archivo no contiene datos para transmitir.")

        data = payload if payload.endswith("\n") else f"{payload}\n"
        raw = data.encode("utf-8")
        total = len(raw)

        try:
            import serial
        except ImportError as exc:
            raise SerialSendError("pyserial no esta instalado.") from exc

        try:
            with serial.Serial(
                self.config.port,
                self.config.baudrate,
                timeout=self.config.timeout,
                write_timeout=self.config.timeout,
            ) as connection:
                sleep(self.config.reset_delay)
                connection.reset_input_buffer()
                connection.reset_output_buffer()

                sent = 0
                for offset in range(0, total, self.config.chunk_size):
                    chunk = raw[offset : offset + self.config.chunk_size]
                    written = connection.write(chunk)
                    connection.flush()
                    sent += written
                    if progress_callback is not None:
                        progress_callback(min(100, int(sent * 100 / total)))

                if progress_callback is not None:
                    progress_callback(100)
        except serial.SerialException as exc:
            raise SerialSendError(str(exc)) from exc
