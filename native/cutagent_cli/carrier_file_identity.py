"""Exact private Node.js filesystem identity values at the Python boundary."""

import os
import re
import stat


def carrier_lstat(path):
    observed = path.lstat()
    if os.name == "nt":
        from .core.windows_bound_file import bound_handle
        # fstat exposes the Windows change time consistently with libuv;
        # Python's path stat still exposes creation time as ctime.
        with bound_handle(path, observed, directory=stat.S_ISDIR(observed.st_mode)) as (_, _, opened):
            return opened
    return observed


def identity_component(value):
    if type(value) is int and 0 <= value <= 9_007_199_254_740_991:
        return value
    if isinstance(value, str) and re.fullmatch(r"0|[1-9][0-9]{0,38}", value):
        parsed = int(value)
        if parsed < 1 << 128:
            return parsed
    raise ValueError("Managed file identity component is invalid.")


def carrier_device(observed):
    # libuv uses the Win32 32-bit volume serial. Python 3.12+ exposes the
    # filesystem's extended 64-bit serial in st_dev on Windows.
    return observed.st_dev & 0xFFFFFFFF if os.name == "nt" else observed.st_dev


def matches_carrier_identity(observed, identity):
    try:
        return carrier_device(observed) == identity_component(identity["device"]) and observed.st_ino == identity_component(identity["inode"])
    except (ValueError, KeyError, TypeError):
        return False
