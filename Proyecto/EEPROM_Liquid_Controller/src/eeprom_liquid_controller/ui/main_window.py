"""Main desktop window."""

from __future__ import annotations

import tkinter as tk

from eeprom_liquid_controller.config import (
    APP_TITLE,
    WINDOW_BACKGROUND,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from eeprom_liquid_controller.ui.assets import load_asset
from eeprom_liquid_controller.ui.widgets import make_interactive_canvas_image


class MainWindow:
    """Tkinter shell for the PC configuration app."""

    def __init__(self) -> None:
        self.window = tk.Tk()
        self.window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.window.configure(bg=WINDOW_BACKGROUND)
        self.window.title(APP_TITLE)
        self.window.resizable(False, False)

        self.canvas = tk.Canvas(
            self.window,
            bg=WINDOW_BACKGROUND,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bd=0,
            highlightthickness=0,
            relief="ridge",
        )
        self.canvas.place(x=0, y=0)

        self._image_refs: list[tk.PhotoImage] = []
        self._build_generated_layout()

    def run(self) -> None:
        self.window.mainloop()

    def _photo(self, asset_name: str) -> tk.PhotoImage:
        image = tk.PhotoImage(file=load_asset(asset_name))
        self._image_refs.append(image)
        return image

    def _interactive_image(self, x: int, y: int, asset_name: str) -> int:
        image_id, image_states = make_interactive_canvas_image(
            self.canvas,
            x,
            y,
            asset_name,
        )
        self._image_refs.extend(image_states)
        return image_id

    def _build_generated_layout(self) -> None:
        """Build the current TkForge-generated canvas layout."""
        self.canvas.create_image(400, 300, image=self._photo("1.png"))
        self.canvas.create_image(400, 300, image=self._photo("2.png"))
        self.canvas.create_image(400, 302, image=self._photo("3.png"))

        self._interactive_image(585, 99, "4.png")

        self.canvas.create_text(
            408,
            84,
            anchor="nw",
            text="Escaneando \npuertos...",
            fill="#ffffff",
            justify="center",
            width=132,
            font=("Inter", 12 * -1),
        )
        self.canvas.create_text(
            653,
            84,
            anchor="nw",
            text="No \nSignal",
            fill="#ffffff",
            justify="center",
            width=70,
            font=("Inter", 12 * -1),
        )

        self.canvas.create_image(158, 417, image=self._photo("5.png"))
        self.canvas.create_text(
            625,
            414,
            anchor="nw",
            text="TIEMPO --:--:-- | ΔSINC --ms",
            fill="#ffffff",
            font=("Inter", 6 * -1),
        )
        self.canvas.create_image(399, 482, image=self._photo("6.png"))

        self._interactive_image(399, 267, "7.png")
