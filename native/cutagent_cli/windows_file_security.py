"""Read file-handle DACLs without changing privileges or Windows policy.

GetSecurityInfo: https://learn.microsoft.com/windows/win32/api/aclapi/nf-aclapi-getsecurityinfo
"""

import ctypes
from contextlib import contextmanager
from ctypes import wintypes
import os
import stat
from pathlib import Path


def _native_path(path):
    value = str(Path(path).absolute())
    if value.startswith("\\\\?\\"):
        return value
    return "\\\\?\\UNC\\" + value[2:] if value.startswith("\\\\") else "\\\\?\\" + value


@contextmanager
def _private_security_attributes():
    advapi = ctypes.WinDLL("advapi32", use_last_error=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    pointer = ctypes.c_void_p
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.LocalFree.argtypes = [pointer]
    kernel.LocalFree.restype = pointer
    advapi.OpenProcessToken.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
    advapi.GetTokenInformation.argtypes = [wintypes.HANDLE, ctypes.c_int, pointer, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
    advapi.ConvertSidToStringSidW.argtypes = [pointer, ctypes.POINTER(wintypes.LPWSTR)]
    advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(pointer), pointer]

    class SecurityAttributes(ctypes.Structure):
        _fields_ = [("length", wintypes.DWORD), ("descriptor", pointer), ("inherit", wintypes.BOOL)]

    token, text, security = wintypes.HANDLE(), wintypes.LPWSTR(), pointer()
    try:
        if not advapi.OpenProcessToken(kernel.GetCurrentProcess(), 8, ctypes.byref(token)):
            raise ctypes.WinError(ctypes.get_last_error())
        size = wintypes.DWORD()
        advapi.GetTokenInformation(token, 1, None, 0, ctypes.byref(size))
        if not 0 < size.value <= 65536:
            raise OSError("Windows user identity is unavailable.")
        buffer = ctypes.create_string_buffer(size.value)
        if not advapi.GetTokenInformation(token, 1, buffer, size, ctypes.byref(size)) or not advapi.ConvertSidToStringSidW(pointer.from_buffer(buffer), ctypes.byref(text)):
            raise ctypes.WinError(ctypes.get_last_error())
        sddl = f"D:P(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)(A;OICI;FA;;;{text.value})"
        if not advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl, 1, ctypes.byref(security), None):
            raise ctypes.WinError(ctypes.get_last_error())
        attributes = SecurityAttributes(ctypes.sizeof(SecurityAttributes), security, False)
        yield attributes
    finally:
        if security:
            kernel.LocalFree(security)
        if text:
            kernel.LocalFree(ctypes.cast(text, pointer))
        if token:
            kernel.CloseHandle(token)


def create_private_directory(path: Path) -> None:
    """Create a new owned directory with a protected inheritable DACL."""
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateDirectoryW.argtypes = [wintypes.LPCWSTR, ctypes.c_void_p]
    with _private_security_attributes() as attributes:
        if not kernel.CreateDirectoryW(_native_path(path), ctypes.byref(attributes)):
            raise ctypes.WinError(ctypes.get_last_error())


def create_private_file(path: Path) -> int:
    """Return a new binary read/write descriptor, private before any write."""
    import msvcrt
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    with _private_security_attributes() as attributes:
        handle = kernel.CreateFileW(_native_path(path), 0xC0000000, 1, ctypes.byref(attributes), 1, 0x00200000, None)
        if handle == wintypes.HANDLE(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
    try:
        return msvcrt.open_osfhandle(handle, os.O_RDWR | os.O_BINARY)
    except OSError:
        kernel.CloseHandle(handle)
        raise


def _private_acl(owner: str, user: str, entries: list[tuple[int, int, int, str]]) -> bool:
    # Administrators and SYSTEM already have equivalent privileged access to
    # POSIX root. No ordinary group or other account may receive file access.
    trusted = {user, "S-1-5-18", "S-1-5-32-544"}
    if owner != user:
        return False
    user_access = False
    for ace_type, flags, mask, sid in entries:
        if flags & 0x08:  # INHERIT_ONLY_ACE does not apply to this file.
            continue
        if ace_type == 1:  # ACCESS_DENIED_ACE cannot widen access.
            continue
        if ace_type != 0:  # Unknown/object/callback grants are not proven safe.
            return False
        if mask and sid not in trusted:
            return False
        user_access |= sid == user and bool(mask)
    return user_access


def private_file_permissions(path: Path, observed: os.stat_result, *, seal_empty=False, seal_owned=False, owner_only=False) -> bool:
    import msvcrt

    advapi = ctypes.WinDLL("advapi32", use_last_error=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    pointer = ctypes.c_void_p
    advapi.GetSecurityInfo.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.DWORD] + [ctypes.POINTER(pointer)] * 5
    advapi.GetSecurityInfo.restype = wintypes.DWORD
    advapi.ConvertSidToStringSidW.argtypes = [pointer, ctypes.POINTER(wintypes.LPWSTR)]
    advapi.ConvertSidToStringSidW.restype = wintypes.BOOL
    advapi.GetAce.argtypes = [pointer, wintypes.DWORD, ctypes.POINTER(pointer)]
    advapi.GetAce.restype = wintypes.BOOL
    advapi.OpenProcessToken.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
    advapi.OpenProcessToken.restype = wintypes.BOOL
    advapi.GetTokenInformation.argtypes = [wintypes.HANDLE, ctypes.c_int, pointer, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
    advapi.GetTokenInformation.restype = wintypes.BOOL
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    kernel.LocalFree.argtypes = [pointer]
    kernel.LocalFree.restype = pointer
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, pointer, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(pointer), pointer]
    advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW.restype = wintypes.BOOL
    advapi.GetSecurityDescriptorDacl.argtypes = [pointer, ctypes.POINTER(wintypes.BOOL), ctypes.POINTER(pointer), ctypes.POINTER(wintypes.BOOL)]
    advapi.GetSecurityDescriptorDacl.restype = wintypes.BOOL
    advapi.SetSecurityInfo.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.DWORD, pointer, pointer, pointer, pointer]
    advapi.SetSecurityInfo.restype = wintypes.DWORD

    class Acl(ctypes.Structure):
        _fields_ = [("revision", wintypes.BYTE), ("reserved", wintypes.BYTE), ("size", wintypes.WORD), ("count", wintypes.WORD), ("reserved2", wintypes.WORD)]

    class AceHeader(ctypes.Structure):
        _fields_ = [("type", wintypes.BYTE), ("flags", wintypes.BYTE), ("size", wintypes.WORD)]

    def sid_string(sid):
        text = wintypes.LPWSTR()
        if not advapi.ConvertSidToStringSidW(sid, ctypes.byref(text)):
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            return text.value
        finally:
            kernel.LocalFree(ctypes.cast(text, pointer))

    descriptor = None
    security = pointer()
    token = wintypes.HANDLE()
    try:
        # Deny replacement while checking or sealing this exact reservation.
        sealing = seal_empty or seal_owned
        access = 0x00020080 if owner_only else 0x80020000 | (0x00040000 if sealing else 0)
        handle = kernel.CreateFileW(_native_path(path), access, 1 if sealing else 3, None, 3, 0x02200000, None)
        if handle == wintypes.HANDLE(-1).value:
            return False
        try:
            descriptor = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
        except OSError:
            kernel.CloseHandle(handle)
            raise
        opened = os.fstat(descriptor)
        if (opened.st_dev, opened.st_ino) != (observed.st_dev, observed.st_ino) or (not owner_only and not stat.S_ISREG(opened.st_mode)) or opened.st_file_attributes & 0x400:
            return False
        owner, dacl = pointer(), pointer()
        error = advapi.GetSecurityInfo(msvcrt.get_osfhandle(descriptor), 1, 0x05, ctypes.byref(owner), None, ctypes.byref(dacl), None, ctypes.byref(security))
        if error or not owner or (not owner_only and not dacl):
            return False
        if not advapi.OpenProcessToken(kernel.GetCurrentProcess(), 0x0008, ctypes.byref(token)):
            return False
        size = wintypes.DWORD()
        advapi.GetTokenInformation(token, 1, None, 0, ctypes.byref(size))
        if not 0 < size.value <= 65_536:
            return False
        buffer = ctypes.create_string_buffer(size.value)
        if not advapi.GetTokenInformation(token, 1, buffer, size, ctypes.byref(size)):
            return False
        user = sid_string(pointer.from_buffer(buffer))
        if owner_only:
            return sid_string(owner) == user
        if sealing:
            # Artifact reservations remain empty-only. The spool reader may
            # explicitly restore the DACL on its owned native response file.
            if (seal_empty and opened.st_size != 0) or opened.st_nlink != 1 or sid_string(owner) != user:
                return False
            sealed = pointer()
            try:
                if not advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW(f"D:P(A;;FA;;;SY)(A;;FA;;;BA)(A;;FA;;;{user})", 1, ctypes.byref(sealed), None):
                    return False
                present, defaulted, private_dacl = wintypes.BOOL(), wintypes.BOOL(), pointer()
                if not advapi.GetSecurityDescriptorDacl(sealed, ctypes.byref(present), ctypes.byref(private_dacl), ctypes.byref(defaulted)) or not present:
                    return False
                if (seal_empty and os.fstat(descriptor).st_size != 0) or advapi.SetSecurityInfo(handle, 1, 0x80000004, None, None, private_dacl, None):
                    return False
            finally:
                if sealed:
                    kernel.LocalFree(sealed)
            kernel.LocalFree(security)
            security = pointer()
            if advapi.GetSecurityInfo(handle, 1, 0x05, ctypes.byref(owner), None, ctypes.byref(dacl), None, ctypes.byref(security)) or not owner or not dacl:
                return False
        entries = []
        acl = ctypes.cast(dacl, ctypes.POINTER(Acl)).contents
        for index in range(acl.count):
            ace = pointer()
            if not advapi.GetAce(dacl, index, ctypes.byref(ace)):
                return False
            header = ctypes.cast(ace, ctypes.POINTER(AceHeader)).contents
            if header.type not in (0, 1) or header.size < 12:
                return False
            mask = wintypes.DWORD.from_address(ace.value + 4).value
            entries.append((header.type, header.flags, mask, sid_string(pointer(ace.value + 8))))
        return _private_acl(sid_string(owner), user, entries)
    except OSError:
        return False
    finally:
        if token:
            kernel.CloseHandle(token)
        if security:
            kernel.LocalFree(security)
        if descriptor is not None:
            os.close(descriptor)
