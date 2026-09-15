"""Prepare completed settings together, then place them in one DB session."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from ..errors import APICallFailed, ValidationError
from .fusion_precise_batch import move_prepared_fusion_holders


def insert_prepared_settings_batch(conn: Any, *, items: list[dict[str, Any]], api: Any) -> dict[str, Any]:
    if not isinstance(items, list) or not items:
        raise ValidationError("Fusion staging batch requires at least one setting.")
    for item in items:
        if not Path(str(item.get("path", ""))).is_file():
            raise ValidationError("Prepared Fusion setting file is unavailable.")
        if not isinstance(item.get("clip_name"), str) or not item["clip_name"].strip():
            raise ValidationError("Prepared Fusion setting requires a clip name.")
        for key in ("track", "record_frame", "duration_frames"):
            if type(item.get(key)) is not int or item[key] < (0 if key == "record_frame" else 1):
                raise ValidationError("Prepared Fusion setting has invalid placement timing.")
    target_name = api._timeline_name(conn.timeline)
    if not target_name:
        raise ValidationError("Fusion batch requires an active target timeline.")
    original_rows = api._enumerated_video_items(conn)
    intervals: dict[int, list[tuple[int, int]]] = {}
    for item in items:
        start, end = item["record_frame"], item["record_frame"] + item["duration_frames"]
        ranges = intervals.setdefault(item["track"], [])
        if any(start < right and end > left for left, right in ranges):
            raise ValidationError("Prepared Fusion settings overlap on a track.")
        for row in original_rows:
            observed = row["readback"]
            if observed["track_index"] == item["track"] and start < observed["end"] and end > observed["start"]:
                raise ValidationError("Prepared Fusion setting overlaps an existing target item.")
        ranges.append((start, end))
    playhead = api.timeline_ops.get_playhead(conn)
    scratch_name = api._unique_validate_scratch_timeline_name(conn)
    format_settings = api._current_timeline_format(conn)
    for track in sorted(intervals):
        api._ensure_video_track(conn, track)
    created = False
    mutation_started = False
    cleaned = False
    try:
        api.timeline_ops.create_timeline(conn, scratch_name, **format_settings)
        created = True
        conn.refresh()
        if api._timeline_name(conn.timeline) != scratch_name or api._enumerated_video_items(conn):
            raise APICallFailed("Fusion staging timeline did not become current and empty.")
        next_frame = api._connection_start_frame(conn)
        staged = []
        for item in items:
            holder, _ = api._insert_native_holder_at_frame(conn, holder="Fusion Composition", holder_kind="fusion", record_frame=next_frame)
            prepared = api._prepare_setting_import(item["path"])
            try:
                if not holder.ImportFusionComp(str(prepared.get("import_path") or item["path"])):
                    raise APICallFailed("Prepared Fusion setting failed to import into staging.")
            finally:
                api._cleanup_prepared_setting(prepared)
            api._apply_timeline_item_name_and_duration(holder, name=item["clip_name"], duration_frames=item["duration_frames"])
            x, y = item.get("position_x"), item.get("position_y")
            if x is not None or y is not None:
                api._apply_timeline_item_position(holder, x, y)
            identity = str(holder.GetUniqueId() or "")
            if not identity or any(row[0] == identity for row in staged):
                raise APICallFailed("Fusion staging requires unique native holder identities.")
            end = holder.GetEnd()
            if end is None or int(end) <= next_frame:
                raise APICallFailed("Fusion staging holder has unreadable duration.")
            staged.append((identity, item))
            next_frame = int(end) + 1
        # One enumeration proves all staged holders, never requested values.
        rows = api._enumerated_video_items(conn)
        by_id = {str(row["readback"].get("timeline_item_id") or ""): row for row in rows}
        if len(rows) != len(staged) or set(by_id) != {identity for identity, _ in staged}:
            raise APICallFailed("Fusion staged holder enumeration did not match the batch.")
        moves = []
        for identity, item in staged:
            row = by_id[identity]
            summary = api._summarize_imported_fusion_tools(row["item"])
            if summary.get("accessible") is False or int(summary.get("tool_count") or 0) <= 0:
                raise APICallFailed("Staged Fusion composition has no readable tools.")
            readback = dict(row["readback"])
            readback["db_start_candidates"] = api._project_db_start_candidates(conn, readback["start"])
            moves.append(dict(timeline_name=target_name, source_timeline_name=scratch_name, staging_readback=readback, target_track=item["track"], target_record_frame=item["record_frame"], target_duration_frames=item["duration_frames"], clip_name=item["clip_name"], holder="Fusion Composition", holder_kind="fusion", require_fusion_tools=True))
        api.timeline_ops.switch_timeline(conn, name=target_name)
        mutation_started = True
        result = move_prepared_fusion_holders(conn, moves=moves, api=api)
        from ..connection import ResolveConnection
        fresh = ResolveConnection.get()
        fresh.connect()
        cleanup = api._cleanup_native_precise_scratch_timeline(fresh, target_timeline_name=target_name, scratch_timeline_name=scratch_name, target_playhead=playhead)
        cleaned = cleanup.get("ok") is True
        if not cleaned:
            raise APICallFailed("Fusion batch placement completed but staging cleanup failed.", details={"cleanup": cleanup}, recoverability="manual")
        return {"placement": result, "cleanup": cleanup, "item_count": len(items)}
    finally:
        # Once DB mutation starts, its recovery owns project state. Do not delete
        # staging evidence or reopen a possibly failed recovery in this finally.
        if created and not mutation_started and not cleaned:
            cleanup = api._cleanup_native_precise_scratch_timeline(conn, target_timeline_name=target_name, scratch_timeline_name=scratch_name, target_playhead=playhead)
            if cleanup.get("ok") is not True:
                raise APICallFailed("Fusion staging failed and cleanup requires manual recovery.", details={"cleanup": cleanup}, recoverability="manual")
