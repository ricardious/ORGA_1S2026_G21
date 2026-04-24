"""Application bootstrap."""

from eeprom_liquid_controller.ui.main_window import MainWindow


def main() -> None:
    """Start the desktop application."""
    app = MainWindow()
    app.run()
