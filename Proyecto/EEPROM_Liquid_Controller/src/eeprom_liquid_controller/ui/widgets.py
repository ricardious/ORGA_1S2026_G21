"""Reusable Tkinter widgets and canvas helpers."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

from PIL import Image

from eeprom_liquid_controller.ui.assets import (
    create_hover_image,
    create_press_image,
    create_selected_image,
    load_asset,
    pil_to_photoimage,
)


class InteractiveCanvasImage:
    """Canvas image button with hover, press and replaceable visual states."""

    def __init__(
        self,
        canvas: tk.Canvas,
        x: int,
        y: int,
        asset_name: str,
        command: Callable[[], None] | None = None,
    ) -> None:
        self.canvas = canvas
        self.x = x
        self.y = y
        self.command = command
        self.hovered = False
        self.pressed = False
        self.selected = False
        self.images: list[tk.PhotoImage] = []
        self.image_id = canvas.create_image(x, y)
        self.set_asset(asset_name)
        self._bind_events()

    def set_asset(self, asset_name: str) -> None:
        asset_path = load_asset(asset_name)
        original = Image.open(asset_path)
        normal_image = tk.PhotoImage(file=asset_path)
        hover_image = pil_to_photoimage(create_hover_image(original))
        press_image = pil_to_photoimage(create_press_image(original))
        selected_image = pil_to_photoimage(create_selected_image(original))

        self.images = [normal_image, hover_image, press_image, selected_image]
        self._set_current_image()

    def set_selected(self, selected: bool) -> None:
        self.selected = selected
        self._set_current_image()

    def _bind_events(self) -> None:
        self.bind_to_item(self.image_id)

    def bind_to_item(self, item_id: int) -> None:
        self.canvas.tag_bind(item_id, "<Enter>", self._enter)
        self.canvas.tag_bind(item_id, "<Leave>", self._leave)
        self.canvas.tag_bind(item_id, "<ButtonPress-1>", self._press)
        self.canvas.tag_bind(item_id, "<ButtonRelease-1>", self._release)

    def _set_current_image(self) -> None:
        if self.pressed:
            image = self.images[2]
        elif self.selected:
            image = self.images[3]
        elif self.hovered:
            image = self.images[1]
        else:
            image = self.images[0]
        self.canvas.itemconfig(self.image_id, image=image)

    def _enter(self, _event: tk.Event) -> None:
        self.hovered = True
        self.canvas.config(cursor="hand2")
        self._set_current_image()

    def _leave(self, _event: tk.Event) -> None:
        self.hovered = False
        self.pressed = False
        self.canvas.config(cursor="")
        self._set_current_image()

    def _press(self, _event: tk.Event) -> None:
        self.pressed = True
        self._set_current_image()

    def _release(self, _event: tk.Event) -> None:
        was_pressed = self.pressed
        self.pressed = False
        self._set_current_image()
        if was_pressed and self.hovered and self.command is not None:
            self.command()


def make_interactive_canvas_image(
    canvas: tk.Canvas,
    x: int,
    y: int,
    asset_name: str,
    command: Callable[[], None] | None = None,
) -> InteractiveCanvasImage:
    """Create a canvas image with hover and press visual states."""
    return InteractiveCanvasImage(canvas, x, y, asset_name, command)
