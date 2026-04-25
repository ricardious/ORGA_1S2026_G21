"""Serial transport for Arduino USB communication."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from time import monotonic, sleep


@dataclass(frozen=True)
class SerialConfig:
    port: str
    baudrate: int = 9600
    timeout: float = 2.0
    reset_delay: float = 2.0
    response_timeout: float = 30.0
    chunk_size: int = 16
    chunk_delay: float = 0.03


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
                        progress_callback(min(95, int(sent * 95 / total)))
                    sleep(self.config.chunk_delay)

                self._wait_for_upload_result(connection)
                if progress_callback is not None:
                    progress_callback(100)
        except serial.SerialException as exc:
            raise SerialSendError(str(exc)) from exc

    def _wait_for_upload_result(self, connection: object) -> None:
        deadline = monotonic() + self.config.response_timeout
        while monotonic() < deadline:
            raw_line = connection.readline()
            if not raw_line:
                continue

            line = raw_line.decode("utf-8", errors="replace").strip()
            if line == "UPLOAD_OK":
                return
            if line.startswith("UPLOAD_ERROR:"):
                reason = line.split(":", maxsplit=1)[1].strip()
                raise SerialSendError(reason or "Arduino rechazo el archivo .org.")

        raise SerialSendError("Arduino no confirmo la carga del archivo.")
