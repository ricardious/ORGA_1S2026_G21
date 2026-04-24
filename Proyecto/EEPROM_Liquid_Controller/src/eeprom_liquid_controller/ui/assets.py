"""Helpers for loading image assets used by the Tkinter UI."""

from __future__ import annotations

import base64
import io
import sys
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageEnhance

from eeprom_liquid_controller.config import ASSETS_DIR


def assets_dir() -> Path:
    """Return the runtime asset directory, including PyInstaller support."""
    bundle_dir = getattr(sys, "_MEIPASS", None)
    if bundle_dir is not None:
        return Path(bundle_dir) / "assets"
    return ASSETS_DIR


def load_asset(path: str) -> Path:
    """Resolve an asset path from the configured asset directory."""
    return assets_dir() / path


def create_hover_image(img: Image.Image) -> Image.Image:
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(1.2)


def create_press_image(img: Image.Image) -> Image.Image:
    pressed = ImageEnhance.Brightness(img).enhance(1.08)
    pressed = ImageEnhance.Contrast(pressed).enhance(0.98)
    width, height = pressed.size
    scale = 0.94
    resized_size = (int(width * scale), int(height * scale))
    resized = pressed.resize(resized_size, Image.Resampling.LANCZOS)

    centered = Image.new("RGBA", pressed.size, (0, 0, 0, 0))
    centered.paste(
        resized,
        ((width - resized_size[0]) // 2, (height - resized_size[1]) // 2),
        resized if resized.mode == "RGBA" else None,
    )
    return centered


def pil_to_photoimage(img: Image.Image) -> tk.PhotoImage:
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return tk.PhotoImage(data=encoded)
