"""Application-wide constants."""

from pathlib import Path

APP_TITLE = "EEPROM Liquid Controller"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_BACKGROUND = "#000000"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = PROJECT_ROOT / "assets"
