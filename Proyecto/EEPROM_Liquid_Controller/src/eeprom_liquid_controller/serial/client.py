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
        log_callback: Callable[[str], None] | None = None,
    ) -> None:
        """Send UTF-8 text to Arduino over serial."""
        if not payload.strip():
            raise SerialSendError("El archivo no contiene datos para transmitir.")

        normalized = payload.replace("\r\n", "\n").replace("\r", "\n")
        lines = normalized.split("\n")
        if not lines or lines[-1] != "":
            lines.append("")

        encoded_lines = [(f"{line}\r\n").encode("utf-8") for line in lines]
        total = sum(len(line) for line in encoded_lines)

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
                if log_callback is not None:
                    log_callback(
                        f"TX open {self.config.port} @ {self.config.baudrate} baud"
                    )
                sleep(self.config.reset_delay)
                connection.reset_input_buffer()
                connection.reset_output_buffer()
                if log_callback is not None:
                    log_callback("TX buffers limpiados, iniciando envio")

                sent = 0
                for index, line_bytes in enumerate(encoded_lines, start=1):
                    written = connection.write(line_bytes)
                    connection.flush()
                    sent += written
                    if log_callback is not None:
                        preview = line_bytes.decode("utf-8", errors="replace").rstrip(
                            "\r\n"
                        )
                        log_callback(
                            f"TX line {index}: {preview if preview else '<vacia>'}"
                        )
                    if progress_callback is not None:
                        progress_callback(min(95, int(sent * 95 / total)))
                    sleep(self.config.chunk_delay)

                if log_callback is not None:
                    log_callback(f"TX enviado {sent} bytes, esperando confirmacion")

                self._wait_for_upload_result(connection, log_callback=log_callback)
                if progress_callback is not None:
                    progress_callback(100)
        except serial.SerialException as exc:
            raise SerialSendError(str(exc)) from exc

    def _wait_for_upload_result(
        self,
        connection: object,
        log_callback: Callable[[str], None] | None = None,
    ) -> None:
        deadline = monotonic() + self.config.response_timeout
        while monotonic() < deadline:
            raw_line = connection.readline()
            if not raw_line:
                continue

            line = raw_line.decode("utf-8", errors="replace").strip()
            if log_callback is not None:
                log_callback(f"RX {line if line else '<vacio>'}")
            if line == "UPLOAD_OK":
                return
            if line.startswith("UPLOAD_ERROR:"):
                reason = line.split(":", maxsplit=1)[1].strip()
                raise SerialSendError(reason or "Arduino rechazo el archivo .org.")

        raise SerialSendError("Arduino no confirmo la carga del archivo.")
