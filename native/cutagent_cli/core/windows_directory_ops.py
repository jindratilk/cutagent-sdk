"""Handle-bound Windows publication and cleanup of owned library stages."""

import ctypes
from ctypes import wintypes
import os
from pathlib import Path
from uuid import uuid4

from .windows_bound_file import bound_handle, extended_local_path
from ..windows_file_security import create_private_directory


def _set_information(handle, kind, buffer):
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.SetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    kernel.SetFileInformationByHandle.restype = wintypes.BOOL
    if not kernel.SetFileInformationByHandle(handle, kind, ctypes.byref(buffer), ctypes.sizeof(buffer)):
        raise ctypes.WinError(ctypes.get_last_error())


def _rename_no_replace(handle, target):
    # The caller holds every target ancestor without delete sharing, so this
    # absolute destination cannot be redirected while Windows resolves it.
    encoded = str(target.absolute()).encode("utf-16-le")
    class RenameInfo(ctypes.Structure):
        _fields_ = [("flags", wintypes.DWORD), ("root", wintypes.HANDLE), ("length", wintypes.DWORD), ("name", ctypes.c_byte * (len(encoded) + 2))]
    info = RenameInfo(0, None, len(encoded))  # ReplaceIfExists is false.
    ctypes.memmove(ctypes.addressof(info) + RenameInfo.name.offset, encoded, len(encoded))
    _set_information(handle, 3, info)


def _delete_handle(handle):
    disposition = wintypes.BOOLEAN(1)
    _set_information(handle, 4, disposition)


def remove_owned_tree(path, identity, *, ancestors=True):
    with bound_handle(path, identity, directory=True, delete=True, ancestors=ancestors) as (root, handle, _):
        for entry in os.scandir(root):
            observed = Path(entry.path).lstat()
            if entry.is_dir(follow_symlinks=False):
                remove_owned_tree(Path(entry.path), observed, ancestors=False)
            else:
                with bound_handle(Path(entry.path), observed, delete=True, ancestors=False) as (_, child, _):
                    _delete_handle(child)
        _delete_handle(handle)


def publish_owned_stage(stage, stage_identity, target, *, bound_regulars, published_regulars, expected_parent_identity=None):
    from . import project_library_ops as owner

    target = extended_local_path(target)
    parent = target.parent
    owner._assert_no_redirect_chain(parent, include_leaf=True, reason="library_target_parent_redirect")
    if expected_parent_identity is not None and owner._path_identity(parent) != expected_parent_identity:
        raise owner._validation("Project-library target parent differs from its carrier-owned identity.", reason="library_target_parent_identity_changed", parent=str(parent))
    if owner._path_identity(stage) != stage_identity:
        raise owner._validation("Private project-library staging identity changed before publication.", reason="internal_stage_identity_changed")
    with bound_handle(stage, stage_identity, directory=True) as (source_root, _, _), bound_handle(parent, expected_parent_identity, directory=True) as (_, parent_handle, _):
        hidden = parent / f".{target.name}.cutagent-publish-{uuid4().hex}.tmp"
        create_private_directory(hidden)
        hidden_identity = owner._path_identity(hidden)
        moved = False
        copied = {}
        seen = set()
        try:
            with bound_handle(hidden, hidden_identity, directory=True, delete=True, ancestors=False) as (_, hidden_handle, _):
                def copy_directory(source, destination):
                    for entry in os.scandir(source):
                        source_path, destination_path = Path(entry.path), destination / entry.name
                        observed = source_path.lstat()
                        if entry.is_dir(follow_symlinks=False):
                            with bound_handle(source_path, observed, directory=True, ancestors=False):
                                create_private_directory(destination_path)
                                with bound_handle(destination_path, directory=True, ancestors=False):
                                    copy_directory(source_path, destination_path)
                        else:
                            relative = source_path.relative_to(source_root)
                            if bound_regulars and relative not in bound_regulars:
                                raise owner._validation("Private staging gained an unvalidated file.", reason="internal_stage_inventory_changed")
                            captured = []
                            owner._copy_bound_regular(source_path, destination_path, sqlite_file=False, expected_identity=bound_regulars.get(relative), captured_identity=captured)
                            seen.add(relative)
                            copied[relative] = captured[0]
                copy_directory(source_root, hidden)
                if seen != set(bound_regulars):
                    raise owner._validation("Private staging lost a validated file.", reason="internal_stage_identity_changed")
                owner._assert_exact_bound_inventory(hidden, {hidden / relative: identity for relative, identity in copied.items()}, possible_mutation=False)
                try:
                    _rename_no_replace(hidden_handle, target)
                except OSError as error:
                    if error.winerror in {80, 183}:
                        raise owner._validation("Project-library target appeared during publication; overwrite is not supported.", reason="library_target_collision", target_root=str(target), overwrite_supported=False) from error
                    raise
                moved = True
            try:
                if owner._path_identity(target) != hidden_identity:
                    raise OSError("Published project-library identity changed.")
                owner._assert_exact_bound_inventory(target, {target / relative: identity for relative, identity in copied.items()}, possible_mutation=True)
            except Exception as error:
                raise owner.APICallFailed("Published project-library path could not be read back after exclusive publication.", details={"target_root": str(target), "possible_mutation": True}, recoverability="manual") from error
            if published_regulars is not None:
                published_regulars.update(copied)
            return hidden_identity
        finally:
            if not moved:
                try:
                    remove_owned_tree(hidden, hidden_identity, ancestors=False)
                except Exception as error:
                    raise owner.APICallFailed(
                        "Private project-library publication stage could not be removed safely.",
                        details={"possible_mutation": True, "manual_recovery_required": True, "hidden_stage": str(hidden)},
                        recoverability="manual",
                    ) from error
