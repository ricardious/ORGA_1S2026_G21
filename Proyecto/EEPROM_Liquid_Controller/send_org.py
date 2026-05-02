"""Interactive helper for sending the default .org file over serial."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from eeprom_liquid_controller.serial.client import (  # noqa: E402
    ArduinoSerialClient,
    SerialConfig,
    SerialSendError,
)

DEFAULT_ORG_PATH = ROOT_DIR / "examples" / "modos_completos.org"


def read_org_file() -> str:
    try:
        return DEFAULT_ORG_PATH.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return DEFAULT_ORG_PATH.read_text(encoding="latin-1")


def main() -> int:
    print("")
    print("Envio de archivo .org al Arduino")
    print(f"Archivo: {DEFAULT_ORG_PATH}")
    print("")

    port = input("Escribe el puerto COM (ejemplo: COM3): ").strip()
    if not port:
        print("[ERROR] No ingresaste un puerto.")
        return 1

    try:
        payload = read_org_file()
        client = ArduinoSerialClient(
            SerialConfig(
                port=port,
                baudrate=9600,
            )
        )
        print(f"[INFO] Puerto: {port}")
        print("[INFO] Enviando archivo...")
        client.send_text(
            payload,
            progress_callback=lambda percent: print(f"[PROGRESS] {percent}%"),
            log_callback=lambda message: print(f"[SERIAL] {message}"),
        )
    except SerialSendError as exc:
        print(f"[ERROR] {exc}")
        return 1

    print("[OK] Archivo enviado correctamente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
