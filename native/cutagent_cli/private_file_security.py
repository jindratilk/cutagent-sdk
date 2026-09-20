"""Platform-native privacy checks for reserved SDK artifact files."""

import os
from pathlib import Path
import stat


def private_file_permissions(path: Path, observed: os.stat_result, *, seal_empty=False) -> bool:
    if os.name != "nt":
        return not bool(stat.S_IMODE(observed.st_mode) & 0o077)
    from .windows_file_security import private_file_permissions as windows_private
    return windows_private(path, observed, seal_empty=seal_empty)
