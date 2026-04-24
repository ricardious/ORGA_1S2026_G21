"""Command names shared by the PC app and Arduino protocol."""

from enum import StrEnum


class RemoteCommand(StrEnum):
    FIESTA = "modo_fiesta"
    RELAJADO = "modo_relajado"
    NOCHE = "modo_noche"
    ENCENDER_TODO = "encender_todo"
    APAGAR_TODO = "apagar_todo"
    ESTADO = "estado"
