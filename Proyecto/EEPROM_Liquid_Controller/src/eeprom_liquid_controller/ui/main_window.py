"""Main desktop window."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

from eeprom_liquid_controller.config import (
    APP_TITLE,
    WINDOW_BACKGROUND,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from eeprom_liquid_controller.serial.ports import list_serial_ports
from eeprom_liquid_controller.ui.assets import load_asset
from eeprom_liquid_controller.ui.canvas_editor import CanvasTextEditor
from eeprom_liquid_controller.ui.widgets import (
    InteractiveCanvasImage,
    make_interactive_canvas_image,
)


PORT_REFRESH_MS = 3_000
MOCK_SERIAL_PORTS = ["COM1", "COM2", "COM3"]
DROP_ZONE = (69, 143, 731, 360)
EDITOR_RECT = (421, 189, 684, 347)
SCROLLBAR_X = 704
SCROLLBAR_TOP = 198
SCROLLBAR_BOTTOM = 338
PROGRESS_X1 = 107
PROGRESS_X2 = 386
PROGRESS_Y = 261
PROGRESS_LABEL_Y = 273
DEFAULT_ORG_PREVIEW = """// Configuracion de modos para el sistema de control
conf_ini

modo_fiesta
Mensaje en LCD: "Modo: FIESTA."
Ventilador: ON
LED'S: Alternandose

conf:fin
"""


class ConnectionState:
    DISCONNECTED = "disconnected"
    READY = "ready"
    ERROR = "error"


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
        self._button_refs: list[InteractiveCanvasImage] = []
        self.connection_state = ConnectionState.DISCONNECTED
        self.available_ports: list[str] = []
        self.selected_port_index: int | None = None
        self.port_slot_buttons: list[InteractiveCanvasImage] = []
        self.port_slot_text_ids: list[int] = []
        self.empty_ports_text_id: int | None = None
        self.connection_status_text_id: int | None = None
        self.connection_button: InteractiveCanvasImage | None = None
        self.selected_file_path: Path | None = None
        self.upload_button: InteractiveCanvasImage | None = None
        self.drop_zone_id: int | None = None
        self.file_loaded_item_ids: list[int] = []
        self.file_action_buttons: list[InteractiveCanvasImage] = []
        self.file_editor: CanvasTextEditor | None = None
        self.scrollbar_track_id: int | None = None
        self.scrollbar_thumb_id: int | None = None
        self.progress_track_id: int | None = None
        self.progress_fill_id: int | None = None
        self.progress_text_id: int | None = None
        self.progress_value = 0
        self._build_generated_layout()
        self.refresh_ports()

    def run(self) -> None:
        self.window.mainloop()

    def _photo(self, asset_name: str) -> tk.PhotoImage:
        image = tk.PhotoImage(file=load_asset(asset_name))
        self._image_refs.append(image)
        return image

    def _interactive_image(
        self,
        x: int,
        y: int,
        asset_name: str,
        command: Callable[[], None] | None = None,
    ) -> InteractiveCanvasImage:
        button = make_interactive_canvas_image(
            self.canvas,
            x,
            y,
            asset_name,
            command=command,
        )
        self._button_refs.append(button)
        return button

    def refresh_ports(self) -> None:
        self.available_ports = MOCK_SERIAL_PORTS
        if self.available_ports:
            self.connection_state = ConnectionState.READY
        elif self.connection_state != ConnectionState.ERROR:
            self.connection_state = ConnectionState.DISCONNECTED
        self._render_connection_panel()
        self.window.after(PORT_REFRESH_MS, self.refresh_ports)

    def retry_connection(self) -> None:
        self.connection_state = ConnectionState.DISCONNECTED
        self.available_ports = list_serial_ports()
        self.connection_state = (
            ConnectionState.READY if self.available_ports else ConnectionState.ERROR
        )
        self._render_connection_panel()

    def _render_connection_panel(self) -> None:
        if self.empty_ports_text_id is None or self.connection_status_text_id is None:
            return

        self._render_available_ports()
        self.canvas.itemconfig(
            self.connection_status_text_id,
            text=self._connection_status_label(),
        )
        if self.connection_button is not None:
            self.connection_button.set_asset(self._connection_button_asset())

    def _render_available_ports(self) -> None:
        if not self.available_ports:
            self.selected_port_index = None
            self.canvas.itemconfig(
                self.empty_ports_text_id,
                text="No se encontraron\npuertos",
                state="normal",
            )
            for button, text_id in zip(
                self.port_slot_buttons,
                self.port_slot_text_ids,
                strict=True,
            ):
                button.set_selected(False)
                self.canvas.itemconfig(button.image_id, state="hidden")
                self.canvas.itemconfig(text_id, state="hidden")
            return

        self.canvas.itemconfig(self.empty_ports_text_id, state="hidden")
        visible_ports = self.available_ports[:3]
        if self.selected_port_index is None or self.selected_port_index >= len(
            visible_ports
        ):
            self.selected_port_index = 0

        for index, (button, text_id) in enumerate(
            zip(
                self.port_slot_buttons,
                self.port_slot_text_ids,
                strict=True,
            )
        ):
            if index >= len(visible_ports):
                button.set_selected(False)
                self.canvas.itemconfig(button.image_id, state="hidden")
                self.canvas.itemconfig(text_id, state="hidden")
                continue

            is_selected = index == self.selected_port_index
            button.set_selected(is_selected)
            self.canvas.itemconfig(button.image_id, state="normal")
            self.canvas.itemconfig(
                text_id,
                text=self._fit_port_label(visible_ports[index]),
                state="normal",
                fill="#c77dff" if is_selected else "#ffffff",
            )

    def select_port(self, index: int) -> None:
        if index >= len(self.available_ports[:3]):
            return
        self.selected_port_index = index
        self._render_connection_panel()

    def _fit_port_label(self, port: str) -> str:
        label = port.rsplit("/", maxsplit=1)[-1]
        if len(label) <= 8:
            return label
        return f"{label[:3]}...{label[-2:]}"

    def _connection_status_label(self) -> str:
        if self.connection_state == ConnectionState.READY:
            return "Ready"
        if self.connection_state == ConnectionState.ERROR:
            return "Relink"
        return "No \nSignal"

    def _connection_button_asset(self) -> str:
        if self.connection_state == ConnectionState.READY:
            return "status_button_ready.png"
        if self.connection_state == ConnectionState.ERROR:
            return "status_button_error.png"
        return "status_button_inactive.png"

    def _build_generated_layout(self) -> None:
        """Build the current TkForge-generated canvas layout."""
        self.canvas.create_image(400, 300, image=self._photo("background_glow.png"))
        self.canvas.create_image(400, 302, image=self._photo("main_panel.png"))

        self.connection_button = make_interactive_canvas_image(
            self.canvas,
            585,
            101,
            "status_button_inactive.png",
            command=self.retry_connection,
        )
        self._button_refs.append(self.connection_button)

        self._build_port_slots()
        self.connection_status_text_id = self.canvas.create_text(
            668,
            101,
            anchor="center",
            text="No \nSignal",
            fill="#ffffff",
            justify="center",
            width=70,
            font=("Inter", 12 * -1),
        )

        self.canvas.create_image(158, 417, image=self._photo("status_badge_inactive.png"))
        self.canvas.create_text(
            625,
            414,
            anchor="nw",
            text="TIEMPO --:--:-- | ΔSINC --ms",
            fill="#ffffff",
            font=("Inter", 6 * -1),
        )
        self.canvas.create_image(399, 482, image=self._photo("bottom_panel.png"))

        self._build_file_upload_area()

    def _build_port_slots(self) -> None:
        slots = [
            (330, 101, "port_slot_left.png"),
            (403, 101, "port_slot_center.png"),
            (476, 101, "port_slot_right.png"),
        ]
        for index, (x, y, asset_name) in enumerate(slots):
            button = make_interactive_canvas_image(
                self.canvas,
                x,
                y,
                asset_name,
                command=lambda slot_index=index: self.select_port(slot_index),
            )
            text_id = self.canvas.create_text(
                x,
                y,
                anchor="center",
                text="",
                fill="#ffffff",
                justify="center",
                width=62,
                font=("Inter", 10 * -1),
            )
            self.canvas.tag_raise(button.image_id)
            self.canvas.tag_raise(text_id)
            button.bind_to_item(text_id)
            self._button_refs.append(button)
            self.port_slot_buttons.append(button)
            self.port_slot_text_ids.append(text_id)

        self.empty_ports_text_id = self.canvas.create_text(
            403,
            101,
            anchor="center",
            text="No se encontraron\npuertos",
            fill="#ffffff",
            justify="center",
            width=190,
            font=("Inter", 11 * -1),
        )

    def _build_file_upload_area(self) -> None:
        x1, y1, x2, y2 = DROP_ZONE
        self.drop_zone_id = self.canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill="",
            outline="",
        )
        self.canvas.tag_bind(
            self.drop_zone_id,
            "<ButtonRelease-1>",
            lambda _event: self.select_org_file(),
        )
        self.canvas.tag_bind(
            self.drop_zone_id,
            "<Double-Button-1>",
            lambda _event: self.load_sample_org_file(),
        )
        self.upload_button = self._interactive_image(
            399,
            267,
            "upload_org_button.png",
            command=self.select_org_file,
        )
        self.canvas.tag_bind(
            self.upload_button.image_id,
            "<Double-Button-1>",
            lambda _event: self.load_sample_org_file(),
        )
        self.canvas.tag_raise(self.upload_button.image_id)
        self.show_upload_empty_state()

    def select_org_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Seleccionar archivo .org",
            filetypes=[("Archivos ORG", "*.org"), ("Todos los archivos", "*.*")],
        )
        if not path:
            return
        self.load_org_file(Path(path))

    def load_org_file(self, path: Path) -> None:
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_text(encoding="latin-1")
        except OSError:
            content = DEFAULT_ORG_PREVIEW

        self.selected_file_path = path
        self.show_file_loaded_state(path.name, path.stat().st_size if path.exists() else 0, content)

    def load_sample_org_file(self) -> None:
        self.selected_file_path = None
        self.show_file_loaded_state("Firmware_v2.org", 20 * 1024, DEFAULT_ORG_PREVIEW)

    def show_upload_empty_state(self) -> None:
        self._clear_file_loaded_state()
        if self.upload_button is not None:
            self.canvas.itemconfig(self.upload_button.image_id, state="normal")
            self.canvas.tag_raise(self.upload_button.image_id)
        if self.drop_zone_id is not None:
            self.canvas.itemconfig(self.drop_zone_id, state="normal")

    def show_file_loaded_state(self, file_name: str, file_size: int, content: str) -> None:
        self._clear_file_loaded_state()
        if self.upload_button is not None:
            self.canvas.itemconfig(self.upload_button.image_id, state="hidden")
        if self.drop_zone_id is not None:
            self.canvas.itemconfig(self.drop_zone_id, state="hidden")

        self._add_loaded_canvas_item(
            self.canvas.create_image(564, 268, image=self._photo("file_editor_panel.png"))
        )
        self._add_loaded_canvas_item(
            self.canvas.create_image(122, 226, image=self._photo("file_org_icon.png"))
        )
        self._add_loaded_canvas_item(
            self.canvas.create_text(
                140,
                207,
                anchor="nw",
                text=file_name,
                fill="#ffffff",
                font=("Inter", 16 * -1),
                width=210,
            )
        )
        self._add_loaded_canvas_item(
            self.canvas.create_text(
                142,
                227,
                anchor="nw",
                text=self._format_file_size(file_size),
                fill="#ffffff",
                font=("Inter", 12 * -1),
            )
        )

        remove_button = make_interactive_canvas_image(
            self.canvas,
            372,
            225,
            "file_remove_button.png",
            command=self.show_upload_empty_state,
        )
        cancel_button = make_interactive_canvas_image(
            self.canvas,
            155,
            314,
            "file_cancel_button.png",
            command=self.show_upload_empty_state,
        )
        send_button = make_interactive_canvas_image(
            self.canvas,
            306,
            314,
            "file_send_button.png",
            command=self.simulate_file_send,
        )
        self._register_file_action_button(remove_button)
        self._register_file_action_button(cancel_button)
        self._register_file_action_button(send_button)

        self._build_file_editor(content)
        self._build_custom_scrollbar()
        self._build_upload_progress()

    def simulate_file_send(self) -> None:
        if self.file_editor is None:
            return
        self.progress_value = 0
        self._set_upload_progress(0)
        self._advance_upload_progress()

    def _advance_upload_progress(self) -> None:
        self.progress_value = min(100, self.progress_value + 8)
        self._set_upload_progress(self.progress_value)
        if self.progress_value < 100:
            self.window.after(80, self._advance_upload_progress)
            return
        self.canvas.itemconfig(
            self.connection_status_text_id,
            text="Ready",
        )

    def _build_file_editor(self, content: str) -> None:
        x1, y1, x2, y2 = EDITOR_RECT
        self.file_editor = CanvasTextEditor(
            self.canvas,
            (x1, y1, x2, y2),
            content,
            on_scroll=self._refresh_custom_scrollbar,
        )

    def _build_custom_scrollbar(self) -> None:
        self.scrollbar_track_id = self.canvas.create_line(
            SCROLLBAR_X,
            SCROLLBAR_TOP,
            SCROLLBAR_X,
            SCROLLBAR_BOTTOM,
            fill="#1a0a47",
            width=6,
            capstyle=tk.ROUND,
        )
        self.scrollbar_thumb_id = self.canvas.create_line(
            SCROLLBAR_X,
            SCROLLBAR_TOP,
            SCROLLBAR_X,
            SCROLLBAR_TOP + 42,
            fill="#8f4dff",
            width=6,
            capstyle=tk.ROUND,
        )
        self._add_loaded_canvas_item(self.scrollbar_track_id)
        self._add_loaded_canvas_item(self.scrollbar_thumb_id)
        self.canvas.tag_bind(
            self.scrollbar_track_id,
            "<Button-1>",
            self._scroll_editor_to_click,
        )
        self.canvas.tag_bind(
            self.scrollbar_thumb_id,
            "<B1-Motion>",
            self._drag_custom_scrollbar,
        )
        self._refresh_custom_scrollbar()

    def _build_upload_progress(self) -> None:
        self.progress_track_id = self.canvas.create_line(
            PROGRESS_X1,
            PROGRESS_Y,
            PROGRESS_X2,
            PROGRESS_Y,
            fill="#2d166f",
            width=7,
            capstyle=tk.ROUND,
        )
        self.progress_fill_id = self.canvas.create_line(
            PROGRESS_X1,
            PROGRESS_Y,
            PROGRESS_X1,
            PROGRESS_Y,
            fill="#35ffd2",
            width=7,
            capstyle=tk.ROUND,
        )
        self.progress_text_id = self.canvas.create_text(
            (PROGRESS_X1 + PROGRESS_X2) // 2,
            PROGRESS_LABEL_Y,
            anchor="center",
            text="Listo para transmitir",
            fill="#ffffff",
            font=("Inter", 9 * -1),
        )
        self._add_loaded_canvas_item(self.progress_track_id)
        self._add_loaded_canvas_item(self.progress_fill_id)
        self._add_loaded_canvas_item(self.progress_text_id)
        self._set_upload_progress(0)

    def _set_upload_progress(self, percent: int) -> None:
        if self.progress_fill_id is None or self.progress_text_id is None:
            return
        fill_x = PROGRESS_X1 + int((PROGRESS_X2 - PROGRESS_X1) * percent / 100)
        self.canvas.coords(
            self.progress_fill_id,
            PROGRESS_X1,
            PROGRESS_Y,
            fill_x,
            PROGRESS_Y,
        )
        label = "Listo para transmitir" if percent == 0 else f"Transmitiendo {percent}%"
        if percent == 100:
            label = "Transmision completada"
        self.canvas.itemconfig(self.progress_text_id, text=label)

    def _sync_custom_scrollbar(self, _first: str, _last: str) -> None:
        self._refresh_custom_scrollbar()

    def _refresh_custom_scrollbar(self) -> None:
        if self.file_editor is None or self.scrollbar_thumb_id is None:
            return
        first, last = self.file_editor.yview()
        track_height = SCROLLBAR_BOTTOM - SCROLLBAR_TOP
        thumb_top = SCROLLBAR_TOP + int(track_height * first)
        thumb_bottom = SCROLLBAR_TOP + int(track_height * last)
        if thumb_bottom - thumb_top < 30:
            thumb_bottom = thumb_top + 30
        if thumb_bottom > SCROLLBAR_BOTTOM:
            thumb_bottom = SCROLLBAR_BOTTOM
            thumb_top = max(SCROLLBAR_TOP, thumb_bottom - 30)
        self.canvas.coords(
            self.scrollbar_thumb_id,
            SCROLLBAR_X,
            thumb_top,
            SCROLLBAR_X,
            thumb_bottom,
        )

    def _scroll_editor_to_click(self, event: tk.Event) -> None:
        if self.file_editor is None:
            return
        ratio = (event.y - SCROLLBAR_TOP) / (SCROLLBAR_BOTTOM - SCROLLBAR_TOP)
        self.file_editor.yview_moveto(max(0, min(1, ratio)))
        self._refresh_custom_scrollbar()

    def _drag_custom_scrollbar(self, event: tk.Event) -> None:
        self._scroll_editor_to_click(event)

    def _clear_file_loaded_state(self) -> None:
        for item_id in self.file_loaded_item_ids:
            self.canvas.delete(item_id)
        self.file_loaded_item_ids.clear()

        for button in self.file_action_buttons:
            self.canvas.delete(button.image_id)
        self.file_action_buttons.clear()

        if self.file_editor is not None:
            self.file_editor.destroy()
            self.file_editor = None

    def _add_loaded_canvas_item(self, item_id: int) -> None:
        self.file_loaded_item_ids.append(item_id)

    def _register_file_action_button(self, button: InteractiveCanvasImage) -> None:
        self._button_refs.append(button)
        self.file_action_buttons.append(button)

    def _format_file_size(self, size: int) -> str:
        if size < 1024:
            return f"{size}B"
        if size < 1024 * 1024:
            return f"{round(size / 1024)}KB"
        return f"{size / (1024 * 1024):.1f}MB"
