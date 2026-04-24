"""A small transparent text editor drawn directly on a Tk canvas."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import font as tkfont


class CanvasTextEditor:
    """Minimal editable text area that does not cover the canvas background."""

    def __init__(
        self,
        canvas: tk.Canvas,
        rect: tuple[int, int, int, int],
        content: str,
        on_scroll: Callable[[], None] | None = None,
    ) -> None:
        self.canvas = canvas
        self.x1, self.y1, self.x2, self.y2 = rect
        self.on_scroll = on_scroll
        self.tag = f"canvas_editor_{id(self)}"
        self.font = tkfont.Font(family="Inter", size=10)
        self.line_height = self.font.metrics("linespace") + 2
        self.max_chars = max(8, (self.x2 - self.x1 - 20) // max(1, self.font.measure("M")))
        self.lines = self._wrap_content(content)
        self.cursor_line = 0
        self.cursor_col = 0
        self.scroll_line = 0
        self.focused = False
        self._cursor_id: int | None = None

        self.canvas.bind("<Button-1>", self._handle_click, add="+")
        self.canvas.bind_all("<Key>", self._handle_key, add="+")
        self.canvas.bind_all("<MouseWheel>", self._handle_mousewheel, add="+")
        self.render()

    def destroy(self) -> None:
        self.canvas.delete(self.tag)

    def get_content(self) -> str:
        return "\n".join(self.lines)

    def yview(self) -> tuple[float, float]:
        total = max(1, len(self.lines))
        visible = self._visible_line_count()
        first = self.scroll_line / total
        last = min(1.0, (self.scroll_line + visible) / total)
        return first, last

    def yview_moveto(self, fraction: float) -> None:
        total = max(1, len(self.lines))
        visible = self._visible_line_count()
        max_scroll = max(0, total - visible)
        self.scroll_line = max(0, min(max_scroll, int(total * fraction)))
        self.render()
        self._notify_scroll()

    def render(self) -> None:
        self.canvas.delete(self.tag)
        visible = self._visible_line_count()
        y = self.y1 + 8
        for line in self.lines[self.scroll_line : self.scroll_line + visible]:
            self.canvas.create_text(
                self.x1 + 10,
                y,
                anchor="nw",
                text=line,
                fill="#ffffff",
                font=self.font,
                width=self.x2 - self.x1 - 20,
                tags=self.tag,
            )
            y += self.line_height
        if self.focused:
            self._draw_cursor()

    def _draw_cursor(self) -> None:
        visible_line = self.cursor_line - self.scroll_line
        if visible_line < 0 or visible_line >= self._visible_line_count():
            return
        line = self.lines[self.cursor_line] if self.lines else ""
        cursor_x = self.x1 + 10 + self.font.measure(line[: self.cursor_col])
        cursor_y = self.y1 + 8 + visible_line * self.line_height
        self._cursor_id = self.canvas.create_line(
            cursor_x,
            cursor_y,
            cursor_x,
            cursor_y + self.line_height - 2,
            fill="#c77dff",
            width=1,
            tags=self.tag,
        )

    def _handle_click(self, event: tk.Event) -> None:
        self.focused = self.x1 <= event.x <= self.x2 and self.y1 <= event.y <= self.y2
        if not self.focused:
            self.render()
            return
        line_index = self.scroll_line + max(0, (event.y - self.y1 - 8) // self.line_height)
        self.cursor_line = max(0, min(len(self.lines) - 1, line_index))
        line = self.lines[self.cursor_line]
        relative_x = max(0, event.x - self.x1 - 10)
        self.cursor_col = self._nearest_col(line, relative_x)
        self.canvas.focus_set()
        self.render()

    def _handle_key(self, event: tk.Event) -> None:
        if not self.focused:
            return
        if event.keysym == "BackSpace":
            self._backspace()
        elif event.keysym == "Return":
            self._insert_newline()
        elif event.keysym == "Left":
            self.cursor_col = max(0, self.cursor_col - 1)
        elif event.keysym == "Right":
            self.cursor_col = min(len(self.lines[self.cursor_line]), self.cursor_col + 1)
        elif event.keysym == "Up":
            self.cursor_line = max(0, self.cursor_line - 1)
            self.cursor_col = min(self.cursor_col, len(self.lines[self.cursor_line]))
            self._ensure_cursor_visible()
        elif event.keysym == "Down":
            self.cursor_line = min(len(self.lines) - 1, self.cursor_line + 1)
            self.cursor_col = min(self.cursor_col, len(self.lines[self.cursor_line]))
            self._ensure_cursor_visible()
        elif event.char and event.char.isprintable():
            self._insert_text(event.char)
        self.render()
        self._notify_scroll()

    def _handle_mousewheel(self, event: tk.Event) -> None:
        pointer_x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
        pointer_y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
        if not (self.x1 <= pointer_x <= self.x2 and self.y1 <= pointer_y <= self.y2):
            return
        delta = -1 if event.delta > 0 else 1
        self._scroll(delta)

    def _scroll(self, delta: int) -> None:
        max_scroll = max(0, len(self.lines) - self._visible_line_count())
        self.scroll_line = max(0, min(max_scroll, self.scroll_line + delta))
        self.render()
        self._notify_scroll()

    def _insert_text(self, text: str) -> None:
        line = self.lines[self.cursor_line]
        self.lines[self.cursor_line] = line[: self.cursor_col] + text + line[self.cursor_col :]
        self.cursor_col += len(text)

    def _insert_newline(self) -> None:
        line = self.lines[self.cursor_line]
        self.lines[self.cursor_line] = line[: self.cursor_col]
        self.lines.insert(self.cursor_line + 1, line[self.cursor_col :])
        self.cursor_line += 1
        self.cursor_col = 0
        self._ensure_cursor_visible()

    def _backspace(self) -> None:
        if self.cursor_col > 0:
            line = self.lines[self.cursor_line]
            self.lines[self.cursor_line] = line[: self.cursor_col - 1] + line[self.cursor_col :]
            self.cursor_col -= 1
            return
        if self.cursor_line == 0:
            return
        previous = self.lines[self.cursor_line - 1]
        current = self.lines.pop(self.cursor_line)
        self.cursor_line -= 1
        self.cursor_col = len(previous)
        self.lines[self.cursor_line] = previous + current
        self._ensure_cursor_visible()

    def _ensure_cursor_visible(self) -> None:
        visible = self._visible_line_count()
        if self.cursor_line < self.scroll_line:
            self.scroll_line = self.cursor_line
        elif self.cursor_line >= self.scroll_line + visible:
            self.scroll_line = self.cursor_line - visible + 1

    def _nearest_col(self, line: str, x: int) -> int:
        for index in range(len(line) + 1):
            if self.font.measure(line[:index]) >= x:
                return index
        return len(line)

    def _visible_line_count(self) -> int:
        return max(1, (self.y2 - self.y1 - 16) // self.line_height)

    def _wrap_content(self, content: str) -> list[str]:
        lines: list[str] = []
        for raw_line in content.splitlines() or [""]:
            if not raw_line:
                lines.append("")
                continue
            while len(raw_line) > self.max_chars:
                lines.append(raw_line[: self.max_chars])
                raw_line = raw_line[self.max_chars :]
            lines.append(raw_line)
        return lines or [""]

    def _notify_scroll(self) -> None:
        if self.on_scroll is not None:
            self.on_scroll()
