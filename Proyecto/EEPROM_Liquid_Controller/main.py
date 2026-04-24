"""Entry point for the EEPROM Liquid Controller desktop app."""

from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from eeprom_liquid_controller.app import main


if __name__ == "__main__":
    main()
