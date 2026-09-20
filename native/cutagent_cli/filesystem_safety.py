"""Reject filesystem redirections consistently across supported platforms."""

from pathlib import Path
import stat


def is_redirected_path(path: Path) -> bool:
    """Inspect the entry itself, including Windows junctions and reparse points."""
    try:
        observed = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(observed.st_mode) or bool(
        getattr(observed, "st_file_attributes", 0) & 0x400
    )
