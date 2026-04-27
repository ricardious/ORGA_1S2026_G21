"""Application-wide constants."""

from pathlib import Path

APP_TITLE = "EEPROM Liquid Controller"
WINDOWS_APP_ID = "orga1.g21.eeprom_liquid_controller"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_BACKGROUND = "#000000"
APP_ICON_PNG = "app_icon.png"
APP_ICON_ICO = "app_icon.ico"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = PROJECT_ROOT / "assets"
