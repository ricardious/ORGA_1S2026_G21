"""Scene models for `.org` configuration files."""

from dataclasses import dataclass
from enum import StrEnum


class PowerState(StrEnum):
    ON = "ON"
    OFF = "OFF"


class LedPattern(StrEnum):
    ON = "ON"
    OFF = "OFF"
    ALTERNATING = "Alternandose"


@dataclass(frozen=True)
class Scene:
    name: str
    lcd_message: str | None
    fan: PowerState
    leds: LedPattern
