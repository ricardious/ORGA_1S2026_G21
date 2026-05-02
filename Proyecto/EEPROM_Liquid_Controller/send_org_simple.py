"""Standalone serial uploader for .org files using pyserial directly."""

from __future__ import annotations

from pathlib import Path
from time import sleep, monotonic
import traceback

import serial

DEFAULT_FILE = Path(__file__).resolve().parent / "examples" / "modos_completos.org"
BAUDRATE = 9600
SERIAL_TIMEOUT = 2.0
RESET_DELAY = 2.0
RESPONSE_TIMEOUT = 30.0
LINE_DELAY = 0.03


def read_file(file_path: Path) -> str:
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return file_path.read_text(encoding="latin-1")


def log(level: str, message: str) -> None:
    print(f"[{level}] {message}")


def main() -> int:
    print("")
    print("Envio simple de archivo .org")
    print(f"Archivo: {DEFAULT_FILE}")
    print("")

    port = input("Puerto COM (ejemplo: COM3): ").strip()
    if not port:
        log("ERROR", "No ingresaste un puerto.")
        return 1

    payload = read_file(DEFAULT_FILE)
    lines = payload.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if not lines or lines[-1] != "":
        lines.append("")

    log("INFO", f"Abriendo {port} a {BAUDRATE} baud...")
    log("INFO", f"Timeout serial: {SERIAL_TIMEOUT}s")
    log("INFO", f"Delay de reset: {RESET_DELAY}s")
    log("INFO", f"Timeout de respuesta: {RESPONSE_TIMEOUT}s")
    log("INFO", f"Total de lineas a enviar: {len(lines)}")
    try:
        with serial.Serial(
            port,
            BAUDRATE,
            timeout=SERIAL_TIMEOUT,
            write_timeout=SERIAL_TIMEOUT,
        ) as connection:
            log("INFO", "Puerto abierto correctamente.")
            log("INFO", "Esperando reset del Arduino...")
            sleep(RESET_DELAY)
            log("INFO", "Limpiando buffers seriales...")
            connection.reset_input_buffer()
            connection.reset_output_buffer()

            for index, line in enumerate(lines, start=1):
                encoded_line = f"{line}\r\n".encode("utf-8")
                written = connection.write(encoded_line)
                connection.flush()
                log(
                    "TX",
                    f"linea {index}/{len(lines)} | bytes={written} | "
                    f"{line if line else '<vacia>'}",
                )
                sleep(LINE_DELAY)

            log("INFO", "Esperando confirmacion del Arduino...")
            deadline = monotonic() + RESPONSE_TIMEOUT
            while monotonic() < deadline:
                raw_line = connection.readline()
                if not raw_line:
                    continue

                response = raw_line.decode("utf-8", errors="replace").strip()
                log("RX", response if response else "<vacio>")
                if response == "UPLOAD_OK":
                    log("OK", "Archivo enviado correctamente.")
                    return 0
                if response.startswith("UPLOAD_ERROR:"):
                    log("ERROR", response)
                    return 1
    except serial.SerialException as exc:
        log("ERROR", f"Fallo serial: {exc}")
        log("TRACE", traceback.format_exc().strip())
        return 1
    except OSError as exc:
        log("ERROR", f"Fallo del sistema operativo: {exc}")
        log("TRACE", traceback.format_exc().strip())
        return 1
    except Exception as exc:
        log("ERROR", f"Error inesperado: {exc}")
        log("TRACE", traceback.format_exc().strip())
        return 1

    log("ERROR", "Arduino no confirmo la carga del archivo.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
