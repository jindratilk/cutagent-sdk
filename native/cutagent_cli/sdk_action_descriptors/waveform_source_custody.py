"""Private, independently read-back custody for imported waveform source media.

Only carrier-admitted bindings and fresh project-media observations belong here.
This helper does not authorize an action or extend managed filesystem roots.
"""

import hashlib
import json
import os
from pathlib import Path
import stat
from typing import Mapping

from ..carrier_file_identity import carrier_lstat, identity_component, matches_carrier_identity
from ..errors import ValidationError


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _matches_file(observed, identity) -> bool:
    try:
        return (
            stat.S_ISREG(observed.st_mode)
            and matches_carrier_identity(observed, identity)
            and observed.st_size == identity_component(identity["size"])
            and observed.st_mtime_ns == identity_component(identity["modifiedNanoseconds"])
            and observed.st_ctime_ns == identity_component(identity["changedNanoseconds"])
        )
    except (KeyError, TypeError, ValueError):
        return False


def verify_waveform_project_source(captured: Mapping, observed: Mapping, *, project_id: str) -> dict:
    """Verify one prepared source against a fresh, carrier-owned media lookup."""
    required = {
        "stableId", "resolvedPath", "sourceIdentityDigest", "revision", "allowedRootId",
        "sourceProjectId", "sourceMediaPoolItemId", "sourceNativeId",
        "sourceMediaPoolRevision", "sourcePoolDigest", "sourceFileIdentity",
    }
    if not isinstance(captured, Mapping) or not required <= set(captured) or not isinstance(observed, Mapping):
        raise ValidationError("Waveform project source lacks exact private custody.")
    if (
        not isinstance(project_id, str) or not project_id
        or captured["sourceProjectId"] != project_id
        or captured["allowedRootId"] != "exact_project_media_source"
        or observed.get("mediaPoolItemId") != captured["sourceMediaPoolItemId"]
        or observed.get("nativeId") != captured["sourceNativeId"]
        or observed.get("sourcePath") != captured["resolvedPath"]
        or observed.get("revision") != captured["sourceMediaPoolRevision"]
        or observed.get("poolDigest") != captured["sourcePoolDigest"]
        or observed.get("kind") not in {"audio", "video"}
        or not all(isinstance(captured[key], str) and captured[key] for key in required - {"sourceFileIdentity"})
        or not isinstance(captured["sourceFileIdentity"], Mapping)
    ):
        raise ValidationError("Waveform source no longer matches the captured project media.")
    source = Path(captured["resolvedPath"])
    expected = captured["sourceFileIdentity"]
    try:
        if not source.is_absolute() or source.resolve(strict=True) != source or not _matches_file(carrier_lstat(source), expected):
            raise ValidationError("Waveform source path or file identity changed.")
        descriptor = os.open(source, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        try:
            if not _matches_file(os.fstat(descriptor), expected):
                raise ValidationError("Waveform source identity changed before reading.")
        finally:
            os.close(descriptor)
        if source.resolve(strict=True) != source or not _matches_file(carrier_lstat(source), expected):
            raise ValidationError("Waveform source path changed while reading.")
    except OSError as error:
        raise ValidationError("Waveform project source file is unavailable.") from error
    # Independently reproduce the exact file-identity binding. This is not a
    # digest of source bytes; managed content-addressed artifacts stay unchanged.
    components = ["waveform-project-source-v1", str(source), *[
        str(identity_component(expected[key])) for key in (
            "device", "inode", "size", "modifiedNanoseconds", "changedNanoseconds",
        )
    ]]
    identity_digest = "sha256:" + _sha(json.dumps(components, ensure_ascii=False, separators=(",", ":")))
    if (
        identity_digest != captured["sourceIdentityDigest"]
        or captured["stableId"] != f"artifact_{_sha(str(source))[:32]}"
        or captured["revision"] != f"revision_{_sha(str(source) + identity_digest)[:32]}"
    ):
        raise ValidationError("Waveform source identity custody changed.")
    return {
        "stableId": captured["stableId"], "revision": captured["revision"],
        "digest": identity_digest, "allowedRootId": captured["allowedRootId"],
        "resolvedPath": str(source),
    }
