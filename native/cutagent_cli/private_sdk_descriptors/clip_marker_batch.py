"""Private exact-ID lowering and public receipt projection for clip markers.

The prepared-action owner supplies revision-validated native inventory rows.
This module never accepts a caller-provided native ID or selects by clip name.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..core.clip_marker_batch import apply_clip_marker_batch


def lower_updates(updates: list[dict[str, Any]], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(updates, list) or not 1 <= len(updates) <= 10000:
        raise ValueError("SDK clip marker batch requires 1 to 10000 markers.")
    by_id = {row["timelineItemId"]: row for row in rows}
    if len(by_id) != len(rows) or len({row["nativeId"] for row in rows}) != len(rows):
        raise ValueError("SDK clip marker inventory identities are ambiguous.")
    result = []
    positions = set()
    for update in updates:
        if not isinstance(update, Mapping) or set(update) != {
            "timelineItemId", "snapshotTimelineItemId", "trackType", "trackIndex", "recordStartFrame",
            "recordEndFrame", "name", "offsetFrames", "durationFrames", "color", "markerName", "note",
        }:
            raise ValueError("SDK clip marker update has an invalid field set.")
        row = by_id.get(update["timelineItemId"])
        if row is None or update["trackType"] != "video" or update["trackIndex"] != 1 or any(
            update[field] != row[native] for field, native in (
                ("trackType", "trackType"), ("trackIndex", "trackIndex"),
                ("recordStartFrame", "start"), ("recordEndFrame", "end"), ("name", "name"),
            )
        ):
            raise ValueError("SDK clip marker target changed after snapshot capture.")
        # snapshotTimelineItemId is validated against the captured public
        # snapshot by admission; native identity/range is revalidated here.
        if not isinstance(update["snapshotTimelineItemId"], str) or not update["snapshotTimelineItemId"].startswith("snapshot_timeline_item_"):
            raise ValueError("SDK clip marker requires a captured snapshot identity.")
        offset, duration = update["offsetFrames"], update["durationFrames"]
        if type(offset) is not int or type(duration) is not int or offset < 0 or duration < 1 or offset + duration > row["end"] - row["start"]:
            raise ValueError("SDK clip marker duration escapes the selected clip.")
        if any(not isinstance(update[field], str) for field in ("markerName", "note", "color")) or not update["markerName"] or not update["color"]:
            raise ValueError("SDK clip marker text and color must be explicit.")
        position = (row["nativeId"], offset)
        if position in positions:
            raise ValueError("SDK clip marker batch contains a duplicate position.")
        positions.add(position)
        result.append({"timeline_item_id": row["nativeId"], "record_start": row["start"], "record_end": row["end"],
                       "offset": offset, "duration": duration, "name": update["markerName"], "note": update["note"], "color": update["color"]})
    return result


def execute_batch(timeline: Any, *, native_timeline_id: str, updates: list[dict[str, Any]], rows: list[dict[str, Any]], conn: Any = None) -> dict[str, Any]:
    lowered = lower_updates(updates, rows)
    receipt = apply_clip_marker_batch(timeline, timeline_id=native_timeline_id, entries=lowered, conn=conn)
    observed = receipt.get("entries")
    if receipt.get("applied") is not True or receipt.get("dry_run") is not False or receipt.get("protected_markers_and_ranges") is not True:
        raise ValueError("SDK clip marker batch lacks protected native proof.")
    if not isinstance(observed, list) or len(observed) != len(lowered) or receipt.get("verified_count") != len(lowered):
        raise ValueError("SDK clip marker native receipt is incomplete.")
    markers = []
    for request, native, actual in zip(updates, lowered, observed):
        if actual.get("verified") is not True or any(actual.get(key) != native[key] for key in (
            "timeline_item_id", "offset", "duration", "name", "note", "color",
        )) or actual.get("record_frame") != native["record_start"] + native["offset"] or type(actual.get("reused")) is not bool:
            raise ValueError("SDK clip marker native readback differs from its exact request.")
        markers.append({"clipId": request["timelineItemId"], "recordFrame": actual["record_frame"],
                        "offsetFrames": actual["offset"], "durationFrames": actual["duration"], "name": actual["name"],
                        "note": actual["note"], "color": actual["color"], "reused": actual["reused"]})
    # No native ID, native source frame, filesystem path or native object crosses
    # the public result boundary. The owner adds the authoritative new revision.
    return {"markers": markers, "verified": True}
