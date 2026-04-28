"""Main desktop window."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from threading import Thread
from time import monotonic
import tkinter as tk
from tkinter import filedialog

from eeprom_liquid_controller.config import (
    APP_ICON_ICO,
    APP_ICON_PNG,
    APP_TITLE,
    WINDOW_BACKGROUND,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from eeprom_liquid_controller.serial.client import (
    ArduinoSerialClient,
    SerialConfig,
    SerialSendError,
)
from eeprom_liquid_controller.serial.ports import list_serial_ports
from eeprom_liquid_controller.ui.assets import load_asset
from eeprom_liquid_controller.ui.dnd_support import create_dnd_window, parse_drop_paths
from eeprom_liquid_controller.ui.widgets import (
    InteractiveCanvasImage,
    make_interactive_canvas_image,
)


PORT_REFRESH_MS = 3_000
DROP_ZONE = (69, 143, 731, 360)
EDITOR_RECT = (421, 189, 684, 347)
EDITOR_RADIUS = 14
SCROLLBAR_X = 704
SCROLLBAR_TOP = 198
SCROLLBAR_BOTTOM = 338
PROGRESS_X1 = 107
PROGRESS_X2 = 386
PROGRESS_Y = 261
PROGRESS_LABEL_Y = 273
EDITOR_PANEL_BG = "#000018"
TERMINAL_RECT = (92, 445, 707, 517)
TERMINAL_LINES = [
    "> Sistema de carga listo.",
    "> Seleccione un puerto y cargue un archivo .org.",
]
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
        self.window, self.dnd_files_type = create_dnd_window()
        self.window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.window.configure(bg=WINDOW_BACKGROUND)
        self.window.title(APP_TITLE)
        self.window.resizable(False, False)
        self._app_icon: tk.PhotoImage | None = None
        self._apply_window_icon()
        self.window.after_idle(self._apply_window_icon)

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
        self.file_editor: tk.Text | None = None
        self.scrollbar_track_id: int | None = None
        self.scrollbar_thumb_id: int | None = None
        self.h_scrollbar_track_id: int | None = None
        self.h_scrollbar_thumb_id: int | None = None
        self.h_scrollbar_drag_offset = 0
        self.progress_track_id: int | None = None
        self.progress_fill_id: int | None = None
        self.progress_text_id: int | None = None
        self.progress_value = 0
        self.time_text_id: int | None = None
        self.terminal_text_ids: list[int] = []
        self.summary_text_id: int | None = None
        self.loaded_file_name: str | None = None
        self.transfer_status = "IDLE"
        self.file_loaded_at: float | None = None
        self.started_at = monotonic()
        self.last_sync_at = self.started_at
        self._build_generated_layout()
        self._register_external_drop()
        self.refresh_ports()

    def run(self) -> None:
        self.window.mainloop()

    def _apply_window_icon(self) -> None:
        icon_png = load_asset(APP_ICON_PNG)
        if icon_png.exists():
            self._app_icon = tk.PhotoImage(file=icon_png)
            self.window.iconphoto(True, self._app_icon)

        icon_ico = load_asset(APP_ICON_ICO)
        if icon_ico.exists():
            try:
                self.window.wm_iconbitmap(str(icon_ico))
            except tk.TclError:
                pass

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
        previous_port = self._selected_port()
        self.available_ports = list_serial_ports()
        if previous_port in self.available_ports:
            self.selected_port_index = self.available_ports.index(previous_port)
        elif self.available_ports and self.selected_port_index is None:
            self.selected_port_index = 0
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
        self.update_summary()

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
        self.update_summary()

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

        self._build_summary_card()
        self.time_text_id = self.canvas.create_text(
            595,
            414,
            anchor="nw",
            text="TIEMPO --:--:-- | ΔSINC --ms",
            fill="#ffffff",
            font=("Inter", 6 * -1),
            state="hidden",
        )
        self.canvas.create_image(399, 482, image=self._photo("terminal_panel.png"))
        self._build_terminal()

        self._build_file_upload_area()

    def _build_summary_card(self) -> None:
        self.summary_text_id = self.canvas.create_text(
            92,
            412,
            anchor="nw",
            text="",
            fill="#d8ccff",
            font=("Inter", 7 * -1),
        )
        self.update_summary()

    def update_summary(self) -> None:
        if self.summary_text_id is None:
            return
        port = self._selected_port_label()
        file_name = self.loaded_file_name or "--"
        self.canvas.itemconfig(
            self.summary_text_id,
            text=f"PUERTO {port}  |  ARCHIVO {file_name}  |  TX {self.transfer_status}",
        )

    def _selected_port(self) -> str | None:
        if self.selected_port_index is None or self.selected_port_index >= len(
            self.available_ports
        ):
            return None
        return self.available_ports[self.selected_port_index]

    def _selected_port_label(self) -> str:
        selected_port = self._selected_port()
        if selected_port is None:
            return "--"
        return self._fit_port_label(selected_port)

    def update_time_label(self) -> None:
        if self.time_text_id is None:
            return
        if self.file_loaded_at is None:
            self.canvas.itemconfig(self.time_text_id, state="hidden")
            return
        elapsed = int(monotonic() - self.file_loaded_at)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        sync_ms = int((monotonic() - self.last_sync_at) * 1000)
        self.canvas.itemconfig(
            self.time_text_id,
            text=f"TIEMPO {hours:02}:{minutes:02}:{seconds:02} | ΔSINC {sync_ms}ms",
            state="normal",
        )
        self.window.after(1000, self.update_time_label)

    def _build_terminal(self) -> None:
        x1, y1, _x2, _y2 = TERMINAL_RECT
        y = y1
        for line in [*TERMINAL_LINES, "", ""]:
            text_id = self.canvas.create_text(
                x1,
                y,
                anchor="nw",
                text=line,
                fill="#d8ccff",
                font=("Inter", 9 * -1),
            )
            self.terminal_text_ids.append(text_id)
            y += 18

    def append_terminal(self, line: str) -> None:
        TERMINAL_LINES.append(line)
        del TERMINAL_LINES[:-4]
        for text_id, text in zip(self.terminal_text_ids, TERMINAL_LINES, strict=False):
            self.canvas.itemconfig(text_id, text=text)

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

    def _register_external_drop(self) -> None:
        if self.dnd_files_type is None:
            return
        self.window.drop_target_register(self.dnd_files_type)
        self.window.dnd_bind("<<Drop>>", self._handle_external_drop)

    def _handle_external_drop(self, event: tk.Event) -> None:
        pointer_x = self.window.winfo_pointerx() - self.window.winfo_rootx()
        pointer_y = self.window.winfo_pointery() - self.window.winfo_rooty()
        x1, y1, x2, y2 = DROP_ZONE
        if not (x1 <= pointer_x <= x2 and y1 <= pointer_y <= y2):
            return

        paths = parse_drop_paths(event.data)
        if paths:
            self.load_org_file(paths[0])

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
        self.loaded_file_name = None
        self.transfer_status = "IDLE"
        self.file_loaded_at = None
        if self.time_text_id is not None:
            self.canvas.itemconfig(self.time_text_id, state="hidden")
        self.update_summary()
        if self.upload_button is not None:
            self.canvas.itemconfig(self.upload_button.image_id, state="normal")
            self.canvas.tag_raise(self.upload_button.image_id)
        if self.drop_zone_id is not None:
            self.canvas.itemconfig(self.drop_zone_id, state="normal")

    def show_file_loaded_state(self, file_name: str, file_size: int, content: str) -> None:
        self._clear_file_loaded_state()
        self.loaded_file_name = file_name
        self.transfer_status = "READY"
        self.file_loaded_at = monotonic()
        self.last_sync_at = self.file_loaded_at
        self.update_summary()
        self.update_time_label()
        if self.upload_button is not None:
            self.canvas.itemconfig(self.upload_button.image_id, state="hidden")
        if self.drop_zone_id is not None:
            self.canvas.itemconfig(self.drop_zone_id, state="hidden")

        self._add_loaded_canvas_item(
            self.canvas.create_image(564, 268, image=self._photo("file_editor_panel.png"))
        )
        self._add_loaded_canvas_item(
            self._create_round_rect(
                EDITOR_RECT,
                EDITOR_RADIUS,
                fill=EDITOR_PANEL_BG,
                outline="#1c1460",
            )
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
            command=self.send_file_to_arduino,
        )
        self._register_file_action_button(remove_button)
        self._register_file_action_button(cancel_button)
        self._register_file_action_button(send_button)

        self._build_file_editor(content)
        self._build_custom_scrollbar()
        self._build_upload_progress()

    def send_file_to_arduino(self) -> None:
        if self.file_editor is None:
            return
        selected_port = self._selected_port()
        if selected_port is None:
            self.transfer_status = "ERR"
            self.connection_state = ConnectionState.ERROR
            self.update_summary()
            self._render_connection_panel()
            self.append_terminal("> ERROR: seleccione un puerto Arduino.")
            return

        self.last_sync_at = monotonic()
        self.transfer_status = "SEND"
        self.update_summary()
        self.progress_value = 0
        self._set_upload_progress(0)
        self.append_terminal(f"> Enviando a {self._fit_port_label(selected_port)}...")

        payload = self.file_editor.get("1.0", "end-1c")
        Thread(
            target=self._send_file_worker,
            args=(selected_port, payload),
            daemon=True,
        ).start()

    def _send_file_worker(self, selected_port: str, payload: str) -> None:
        client = ArduinoSerialClient(SerialConfig(port=selected_port))
        try:
            client.send_text(
                payload,
                progress_callback=lambda percent: self.window.after(
                    0,
                    self._update_send_progress,
                    percent,
                ),
                log_callback=lambda message: self.window.after(
                    0,
                    self.append_terminal,
                    f"> {message}",
                ),
            )
        except SerialSendError as exc:
            self.window.after(0, self._handle_send_error, str(exc))
            return
        self.window.after(0, self._handle_send_success)

    def _handle_send_success(self) -> None:
        self.canvas.itemconfig(
            self.connection_status_text_id,
            text="Ready",
        )
        self.transfer_status = "OK"
        self.connection_state = ConnectionState.READY
        self.update_summary()
        self.append_terminal("> Transmision completada.")
        self.window.after(1400, self.show_upload_empty_state)

    def _handle_send_error(self, message: str) -> None:
        self.transfer_status = "ERR"
        self.connection_state = ConnectionState.ERROR
        self.update_summary()
        self._render_connection_panel()
        self.append_terminal(f"> ERROR: {message}")

    def _update_send_progress(self, percent: int) -> None:
        self.progress_value = percent
        self._set_upload_progress(percent)

    def _build_file_editor(self, content: str) -> None:
        x1, y1, x2, y2 = EDITOR_RECT
        editor = tk.Text(
            self.window,
            bg=EDITOR_PANEL_BG,
            fg="#ffffff",
            insertbackground="#c77dff",
            selectbackground="#5a2b8f",
            selectforeground="#ffffff",
            relief="flat",
            bd=0,
            highlightthickness=0,
            wrap="none",
            undo=True,
            maxundo=-1,
            autoseparators=True,
            font=("Inter", 10),
            padx=10,
            pady=8,
        )
        editor.configure(
            yscrollcommand=self._sync_custom_scrollbar,
            xscrollcommand=self._sync_horizontal_scrollbar,
        )
        editor.insert("1.0", content)
        editor.edit_reset()
        editor.place(x=x1, y=y1, width=x2 - x1, height=y2 - y1)
        editor.bind("<Control-y>", self._redo_editor)
        editor.bind("<Control-Y>", self._redo_editor)
        self.file_editor = editor

    def _create_round_rect(
        self,
        rect: tuple[int, int, int, int],
        radius: int,
        **kwargs: str,
    ) -> int:
        x1, y1, x2, y2 = rect
        points = [
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            x2,
            y1,
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            x2,
            y2,
            x2 - radius,
            y2,
            x1 + radius,
            y2,
            x1,
            y2,
            x1,
            y2 - radius,
            x1,
            y1 + radius,
            x1,
            y1,
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

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
        self._build_horizontal_scrollbar()

    def _build_horizontal_scrollbar(self) -> None:
        x1, _y1, x2, y2 = EDITOR_RECT
        track_x1 = x1 + 10
        track_x2 = x2 - 10
        track_y = y2 - 7
        self.h_scrollbar_track_id = self.canvas.create_line(
            track_x1,
            track_y,
            track_x2,
            track_y,
            fill="#2d166f",
            width=5,
            capstyle=tk.ROUND,
        )
        self.h_scrollbar_thumb_id = self.canvas.create_line(
            track_x1,
            track_y,
            track_x1 + 40,
            track_y,
            fill="#8f4dff",
            width=5,
            capstyle=tk.ROUND,
        )
        self._add_loaded_canvas_item(self.h_scrollbar_track_id)
        self._add_loaded_canvas_item(self.h_scrollbar_thumb_id)
        self.canvas.tag_bind(
            self.h_scrollbar_track_id,
            "<Button-1>",
            self._scroll_editor_x_to_click,
        )
        self.canvas.tag_bind(
            self.h_scrollbar_thumb_id,
            "<Button-1>",
            self._start_horizontal_scrollbar_drag,
        )
        self.canvas.tag_bind(
            self.h_scrollbar_thumb_id,
            "<B1-Motion>",
            self._drag_horizontal_scrollbar,
        )
        self._refresh_horizontal_scrollbar()

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

    def _sync_horizontal_scrollbar(self, _first: str, _last: str) -> None:
        self._refresh_horizontal_scrollbar()

    def _refresh_horizontal_scrollbar(self) -> None:
        if self.file_editor is None or self.h_scrollbar_thumb_id is None:
            return
        first, last = self.file_editor.xview()
        x1, _y1, x2, y2 = EDITOR_RECT
        track_x1 = x1 + 10
        track_x2 = x2 - 10
        track_y = y2 - 7
        track_width = track_x2 - track_x1
        thumb_x1 = track_x1 + int(track_width * first)
        thumb_x2 = track_x1 + int(track_width * last)
        if thumb_x2 - thumb_x1 < 32:
            thumb_x2 = thumb_x1 + 32
        if thumb_x2 > track_x2:
            thumb_x2 = track_x2
            thumb_x1 = max(track_x1, thumb_x2 - 32)
        self.canvas.coords(
            self.h_scrollbar_thumb_id,
            thumb_x1,
            track_y,
            thumb_x2,
            track_y,
        )

    def _scroll_editor_to_click(self, event: tk.Event) -> None:
        if self.file_editor is None:
            return
        ratio = (event.y - SCROLLBAR_TOP) / (SCROLLBAR_BOTTOM - SCROLLBAR_TOP)
        self.file_editor.yview_moveto(max(0, min(1, ratio)))
        self._refresh_custom_scrollbar()

    def _drag_custom_scrollbar(self, event: tk.Event) -> None:
        self._scroll_editor_to_click(event)

    def _scroll_editor_x_to_click(self, event: tk.Event) -> None:
        if self.file_editor is None:
            return
        x1, _y1, x2, _y2 = EDITOR_RECT
        track_x1 = x1 + 10
        track_x2 = x2 - 10
        ratio = (event.x - track_x1) / (track_x2 - track_x1)
        self.file_editor.xview_moveto(max(0, min(1, ratio)))
        self._refresh_horizontal_scrollbar()

    def _start_horizontal_scrollbar_drag(self, event: tk.Event) -> None:
        if self.h_scrollbar_thumb_id is None:
            return
        coords = self.canvas.coords(self.h_scrollbar_thumb_id)
        self.h_scrollbar_drag_offset = event.x - int(coords[0]) if coords else 0

    def _drag_horizontal_scrollbar(self, event: tk.Event) -> None:
        if self.file_editor is None or self.h_scrollbar_thumb_id is None:
            return
        x1, _y1, x2, _y2 = EDITOR_RECT
        track_x1 = x1 + 10
        track_x2 = x2 - 10
        coords = self.canvas.coords(self.h_scrollbar_thumb_id)
        thumb_width = int(coords[2] - coords[0]) if coords else 32
        movable_width = max(1, track_x2 - track_x1 - thumb_width)
        thumb_x = max(
            track_x1,
            min(track_x2 - thumb_width, event.x - self.h_scrollbar_drag_offset),
        )
        self.file_editor.xview_moveto((thumb_x - track_x1) / movable_width)
        self._refresh_horizontal_scrollbar()

    def _redo_editor(self, _event: tk.Event) -> str:
        if self.file_editor is None:
            return "break"
        try:
            self.file_editor.edit_redo()
        except tk.TclError:
            pass
        return "break"

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
