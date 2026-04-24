"""Parser placeholder for project `.org` configuration files."""

from pathlib import Path

from eeprom_liquid_controller.domain.scenes import Scene


class OrgParseError(ValueError):
    """Raised when a `.org` file does not match the project syntax."""


def parse_org_file(path: Path) -> list[Scene]:
    """Parse a `.org` configuration file.

    The concrete syntax will be implemented when the upload flow is wired.
    Keeping this module separate avoids coupling validation rules to Tkinter.
    """
    raise NotImplementedError("The .org parser is not implemented yet.")
