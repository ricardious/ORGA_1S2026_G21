"""Application bootstrap."""

import sys

from eeprom_liquid_controller.config import WINDOWS_APP_ID
from eeprom_liquid_controller.ui.main_window import MainWindow


def _set_windows_app_id() -> None:
    """Ensure Windows uses the app icon instead of the default Python one."""
    if not sys.platform.startswith("win"):
        return

    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            WINDOWS_APP_ID
        )
    except Exception:
        pass


def main() -> None:
    """Start the desktop application."""
    _set_windows_app_id()
    app = MainWindow()
    app.run()
