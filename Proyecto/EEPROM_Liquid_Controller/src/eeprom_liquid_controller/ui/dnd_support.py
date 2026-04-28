"""Optional native file drag-and-drop support for Tkinter."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from typing import Any


def create_dnd_window() -> tuple[tk.Tk, Any | None]:
    """Create a Tk root with native drop support when the local Tcl supports it."""
    if not _tkinterdnd_preflight():
        return tk.Tk(), None

    try:
        from tkinterdnd2 import DND_FILES, TkinterDnD

        return TkinterDnD.Tk(), DND_FILES
    except Exception:
        return tk.Tk(), None


def parse_drop_paths(data: str) -> list[Path]:
    """Parse TkDND file path payloads, including paths wrapped in braces."""
    matches = re.findall(r"\{([^}]+)\}|([^ ]+)", data)
    return [Path(match[0] or match[1]) for match in matches if match[0] or match[1]]


def _tkinterdnd_preflight() -> bool:
    """Probe TkDND in a subprocess so a failed Tcl extension cannot poison Tk."""
    script = """
from tkinterdnd2 import TkinterDnD
root = TkinterDnD.Tk()
root.destroy()
"""
    try:
        result = subprocess.run(
            [sys.executable, "-c", script],
            env=os.environ.copy(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=3,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0
