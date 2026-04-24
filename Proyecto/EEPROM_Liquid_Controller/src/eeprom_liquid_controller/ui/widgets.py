"""Reusable Tkinter widgets and canvas helpers."""

from __future__ import annotations

import tkinter as tk

from PIL import Image

from eeprom_liquid_controller.ui.assets import (
    create_hover_image,
    create_press_image,
    load_asset,
    pil_to_photoimage,
)


def make_interactive_canvas_image(
    canvas: tk.Canvas,
    x: int,
    y: int,
    asset_name: str,
) -> tuple[int, list[tk.PhotoImage]]:
    """Create a canvas image with hover and press visual states."""
    asset_path = load_asset(asset_name)
    original = Image.open(asset_path)
    normal_image = tk.PhotoImage(file=asset_path)
    hover_image = pil_to_photoimage(create_hover_image(original))
    press_image = pil_to_photoimage(create_press_image(original))

    image_id = canvas.create_image(x, y, image=normal_image)
    image_states = [normal_image, hover_image, press_image]
    state = {"hovered": False, "pressed": False}

    def set_image(image: tk.PhotoImage) -> None:
        canvas.itemconfig(image_id, image=image)

    def enter(_event: tk.Event) -> None:
        state["hovered"] = True
        canvas.config(cursor="hand2")
        if not state["pressed"]:
            set_image(hover_image)

    def leave(_event: tk.Event) -> None:
        state["hovered"] = False
        state["pressed"] = False
        canvas.config(cursor="")
        set_image(normal_image)

    def press(_event: tk.Event) -> None:
        state["pressed"] = True
        set_image(press_image)

    def release(_event: tk.Event) -> None:
        state["pressed"] = False
        set_image(hover_image if state["hovered"] else normal_image)

    canvas.tag_bind(image_id, "<Enter>", enter)
    canvas.tag_bind(image_id, "<Leave>", leave)
    canvas.tag_bind(image_id, "<ButtonPress-1>", press)
    canvas.tag_bind(image_id, "<ButtonRelease-1>", release)

    return image_id, image_states
