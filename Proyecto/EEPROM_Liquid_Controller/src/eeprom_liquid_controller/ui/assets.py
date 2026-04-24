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
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(0.8)


def pil_to_photoimage(img: Image.Image) -> tk.PhotoImage:
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return tk.PhotoImage(data=encoded)
