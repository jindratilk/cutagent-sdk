"""Keep a local Windows SQLite pathname bound to its opened file identity.

SQLite's Windows VFS opens a pathname, not a CRT descriptor. Holding every
ancestor and the leaf without FILE_SHARE_DELETE prevents rename/replacement
while the VFS uses that path. Reparse points are rejected on opened handles.
"""

from contextlib import contextmanager
import ctypes
from ctypes import wintypes
import os
from pathlib import Path


def extended_local_path(path):
    absolute = Path(os.path.abspath(path))
    drive = absolute.drive
    if drive.startswith("\\\\?\\"):
        drive = drive[4:]
    if len(drive) != 2 or drive[1] != ":" or not drive[0].isalpha():
        raise OSError("File binding requires a local Windows volume.")
    return absolute if absolute.drive.startswith("\\\\?\\") else Path("\\\\?\\" + str(absolute))


@contextmanager
def bound_handle(path: Path, expected=None, *, directory=False, delete=False, ancestors=True):
    import msvcrt

    absolute = Path(os.path.abspath(path))
    extended_local_path(absolute)  # Validate the volume before opening ancestors.
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    kernel.GetFileInformationByHandleEx.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    kernel.GetFileInformationByHandleEx.restype = wintypes.BOOL

    class AttributeTag(ctypes.Structure):
        _fields_ = [("attributes", wintypes.DWORD), ("tag", wintypes.DWORD)]

    handles = []
    descriptor = None
    try:
        for entry in ([*reversed(absolute.parents), absolute] if ancestors else [absolute]):
            leaf = entry == absolute
            access = (0x80 if directory else 0x80000000) | (0x10000 if delete else 0)
            handle = kernel.CreateFileW(str(extended_local_path(entry)), access if leaf else 0x80, 3, None, 3, 0x02200000, None)
            if handle == wintypes.HANDLE(-1).value:
                raise ctypes.WinError(ctypes.get_last_error())
            handles.append(handle)
            info = AttributeTag()
            if not kernel.GetFileInformationByHandleEx(handle, 9, ctypes.byref(info), ctypes.sizeof(info)):
                raise ctypes.WinError(ctypes.get_last_error())
            if info.attributes & 0x400 or bool(info.attributes & 0x10) != (directory if leaf else True):
                raise OSError("SQLite binding rejects redirected or incompatible entries.")
        descriptor = msvcrt.open_osfhandle(handles[-1], os.O_RDONLY | os.O_BINARY)
        handles.pop()  # The CRT descriptor now owns the leaf handle.
        observed = os.fstat(descriptor)
        identity = (expected.st_dev, expected.st_ino) if isinstance(expected, os.stat_result) else expected
        if identity is not None and (observed.st_dev, observed.st_ino) != identity:
            raise OSError("SQLite source identity changed before pathname binding.")
        yield absolute, msvcrt.get_osfhandle(descriptor), observed
    finally:
        if descriptor is not None:
            os.close(descriptor)
        for handle in reversed(handles):
            kernel.CloseHandle(handle)


@contextmanager
def bound_sqlite_path(path: Path, expected: os.stat_result):
    with bound_handle(path, expected) as (absolute, _handle, _observed):
        yield absolute
