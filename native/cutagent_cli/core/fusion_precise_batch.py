"""One recoverable DB placement session for already prepared Fusion holders.

Staging/import and public SDK dispatch are owned by the caller. This module
never creates holders or accepts SQL from a caller.
"""
from __future__ import annotations

from typing import Any

from ..errors import ValidationError, APICallFailed
from . import db_session


def move_prepared_fusion_holders(conn: Any, *, moves: list[dict[str, Any]], api: Any) -> dict[str, Any]:
    if not isinstance(moves, list) or not moves:
        raise ValidationError("Fusion placement batch requires at least one prepared holder.")
    target = moves[0].get("timeline_name")
    source = moves[0].get("source_timeline_name")
    if not target or not source or target == source:
        raise ValidationError("Fusion batch requires distinct target and staging timelines.")
    identities: set[str] = set()
    intervals: dict[int, list[tuple[int, int]]] = {}
    for move in moves:
        if move.get("timeline_name") != target or move.get("source_timeline_name") != source:
            raise ValidationError("Fusion batch requires one target and one staging timeline.")
        identity = str(move.get("staging_readback", {}).get("timeline_item_id") or "")
        if not identity or identity in identities:
            raise ValidationError("Fusion batch requires unique exact staged item identities.")
        identities.add(identity)
        track, start, duration = (move.get(key) for key in ("target_track", "target_record_frame", "target_duration_frames"))
        if any(type(value) is not int for value in (track, start, duration)) or track < 1 or start < 0 or duration < 1:
            raise ValidationError("Fusion batch placement ranges must be positive frame-domain integers.")
        intervals.setdefault(track, []).append((start, start + duration))
    for ranges in intervals.values():
        ordered = sorted(ranges)
        if any(left[1] > right[0] for left, right in zip(ordered, ordered[1:])):
            raise ValidationError("Fusion batch placements overlap on a target track.")
    if api._timeline_name(conn.timeline) != target:
        raise ValidationError("The exact target timeline must be active before Fusion batch placement.")
    shared = {"before_rows": api._enumerated_video_items(conn), "reindex_tracks": set(), "inserted_ids": identities}
    for row in shared["before_rows"]:
        observed = row["readback"]
        for start, end in intervals.get(observed.get("track_index"), []):
            if observed["start"] < end and observed["start"] + observed["duration"] > start:
                raise ValidationError("Fusion batch would overlap an existing target item.")
    prepared = [api._prepare_native_precise_holder_move(conn, **move, batch_context=shared) for move in moves]

    def writer(connection, cursor, session):
        results = [item["writer"](connection, cursor, session) for item in prepared]
        if {row.get("item_id") for row in results} != identities:
            raise APICallFailed("Fusion batch writer did not preserve exact staged identities.")
        for track_id in sorted(shared["reindex_tracks"]):
            db_session.rebuild_track_item_indices(cursor, track_id=track_id)
        return {"items": results}

    def verifier(fresh, mutation, session):
        if api._timeline_name(fresh.timeline) != target:
            api.timeline_ops.switch_timeline(fresh, name=target)
        shared["after_rows"] = api._enumerated_video_items(fresh)
        results = [item["verifier"](fresh, row, session) for item, row in zip(prepared, mutation["items"], strict=True)]
        return {"status": "verified", "checks": [check for row in results for check in row["checks"]], "items": results}

    result = db_session.execute_sqlite_disk_db_mutation(conn, context="Batch precise Fusion holder placement", writer=writer, verifier=verifier, allow_project_name_inference=True)
    from ..connection import ResolveConnection
    ResolveConnection.reset()
    result["connection_reloaded"] = True
    return result
