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

    canvas.tag_bind(
        image_id,
        "<Enter>",
        lambda event, target=image_id, hover=hover_image: canvas.itemconfig(
            target, image=hover
        ),
    )
    canvas.tag_bind(
        image_id,
        "<Leave>",
        lambda event, target=image_id, normal=normal_image: canvas.itemconfig(
            target, image=normal
        ),
    )
    canvas.tag_bind(
        image_id,
        "<ButtonPress-1>",
        lambda event, target=image_id, press=press_image: canvas.itemconfig(
            target, image=press
        ),
    )
    canvas.tag_bind(
        image_id,
        "<ButtonRelease-1>",
        lambda event, target=image_id, normal=normal_image: canvas.itemconfig(
            target, image=normal
        ),
    )

    return image_id, image_states
