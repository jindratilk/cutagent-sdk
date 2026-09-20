"""Bounded native clip-marker insertion for a prepared, exact-ID batch.

This is an owning-layer primitive, not a public SDK entry point. Its caller
must supply the captured native timeline ID and serialize native mutations.
No playhead selection, media-pool mutation, source rewriting, or DB edit.
"""
from __future__ import annotations

from copy import deepcopy
import math
from typing import Any

from ..errors import APICallFailed, ValidationError
from .sdk_live_inspection import documented_unique_id
from .timeline_source_range import ordinary_source_mapping_proven, _properties, _source_fps


def _integer(value: Any, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or int(value) != value or value < minimum:
        raise ValidationError("Clip marker batch requires integer frame values.", details={"field": label})
    return int(value)


def _markers(item: Any) -> dict[int, dict[str, Any]]:
    # An unavailable readback is not an empty marker set.
    raw = item.GetMarkers()
    if not isinstance(raw, dict):
        raise APICallFailed("DaVinci Resolve did not return clip marker readback.")
    result = {}
    for frame, row in raw.items():
        frame = _integer(frame, "marker source frame")
        if frame in result or not isinstance(row, dict):
            raise APICallFailed("DaVinci Resolve returned ambiguous clip markers.")
        result[frame] = deepcopy(row)
    return result


def _matches(row: dict[str, Any] | None, wanted: dict[str, Any]) -> bool:
    return row is not None and all(row.get(key) == wanted[key] for key in ("color", "name", "note", "duration"))


def apply_clip_marker_batch(timeline: Any, *, timeline_id: str, entries: list[dict[str, Any]], dry_run: bool = False, conn: Any = None) -> dict[str, Any]:
    """Insert exact clip-local offsets, rejecting all collisions before writes.

    Each entry binds timeline_item_id, record_start, record_end, offset,
    duration, color, name, note. Collisions must be resolved in the prepared
    plan, never silently shifted here. Exact existing markers are reused.
    A partial native failure returns evidence in APICallFailed.details; callers
    must reconcile that retained receipt rather than re-dispatch blindly.
    """
    if not timeline_id or documented_unique_id(timeline) != timeline_id:
        raise ValidationError("Clip marker batch timeline identity changed.")
    if not isinstance(entries, list) or not entries:
        raise ValidationError("Clip marker batch requires at least one entry.")
    items = timeline.GetItemListInTrack("video", 1)
    if not isinstance(items, list):
        raise APICallFailed("DaVinci Resolve did not return V1 clips.")
    by_id: dict[str, list[Any]] = {}
    for item in items:
        identity = documented_unique_id(item)
        if identity:
            by_id.setdefault(identity, []).append(item)
    captures: dict[str, dict[str, Any]] = {}
    planned = []
    occupied = set()
    for entry in entries:
        identity = entry.get("timeline_item_id")
        matches = by_id.get(identity, [])
        if len(matches) != 1:
            raise ValidationError("Clip marker batch requires one exact V1 clip identity.")
        if identity not in captures:
            item = matches[0]
            if conn is None or not ordinary_source_mapping_proven(conn, item):
                raise ValidationError("Clip markers require a proven normal forward time map; retimed or reversed clips are unsupported.")
            source_fps = _source_fps(_properties(item.GetMediaPoolItem()), float("nan"))
            timeline_fps = float(conn.fps)
            if not (math.isfinite(source_fps) and source_fps > 0 and math.isfinite(timeline_fps)
                    and timeline_fps > 0 and math.isclose(source_fps, timeline_fps, rel_tol=0, abs_tol=0.0001)):
                raise ValidationError("Clip markers require known matching source and timeline frame rates.")
            start = _integer(item.GetStart(), "record start")
            end = _integer(item.GetEnd(), "record end")
            # Do not assume zero if the source-range API is unavailable.
            source = _integer(item.GetSourceStartFrame(), "source start")
            captures[identity] = {"item": item, "start": start, "end": end, "source": source, "markers": _markers(item)}
        capture = captures[identity]
        if (_integer(entry.get("record_start"), "record_start"), _integer(entry.get("record_end"), "record_end")) != (capture["start"], capture["end"]):
            raise ValidationError("Clip marker batch clip range changed.")
        offset = _integer(entry.get("offset"), "offset")
        duration = _integer(entry.get("duration"), "duration", 1)
        if offset + duration > capture["end"] - capture["start"]:
            raise ValidationError("Clip marker batch marker crosses a clip boundary.")
        wanted = {key: entry.get(key) for key in ("color", "name", "note")}
        if any(not isinstance(value, str) for value in wanted.values()) or not wanted["name"] or not wanted["color"]:
            raise ValidationError("Clip marker batch requires explicit marker text and color.")
        wanted["duration"] = duration
        frame = capture["source"] + offset
        if (identity, frame) in occupied:
            raise ValidationError("Clip marker batch contains a duplicate marker position.")
        occupied.add((identity, frame))
        existing = capture["markers"].get(frame)
        if existing is not None and not _matches(existing, wanted):
            raise ValidationError("Clip marker batch position is occupied by a different marker.")
        planned.append({"timeline_item_id": identity, "source_frame": frame, "offset": offset,
                        "record_frame": capture["start"] + offset, **wanted, "reused": existing is not None})
    if dry_run:
        return {"dry_run": True, "applied": False, "entries": planned}
    attempts = []
    failure = None
    for row in planned:
        if row["reused"]:
            continue
        # Capture attempts before the API call, including an uncertain exception.
        attempts.append({"timeline_item_id": row["timeline_item_id"], "source_frame": row["source_frame"]})
        try:
            result = captures[row["timeline_item_id"]]["item"].AddMarker(row["source_frame"], row["color"], row["name"], row["note"], row["duration"])
            if not result:
                failure = "native_add_rejected"
                break
        except Exception:
            failure = "native_add_uncertain"
            break
    verified = []
    protected = True
    try:
        after = {identity: _markers(capture["item"]) for identity, capture in captures.items()}
        for identity, capture in captures.items():
            protected = protected and all(after[identity].get(frame) == marker for frame, marker in capture["markers"].items())
            protected = protected and capture["item"].GetStart() == capture["start"] and capture["item"].GetEnd() == capture["end"]
            protected = protected and capture["item"].GetSourceStartFrame() == capture["source"]
        for row in planned:
            verified.append({**row, "verified": _matches(after[row["timeline_item_id"]].get(row["source_frame"]), row)})
    except Exception:
        failure = failure or "native_readback_unavailable"
        protected = False
    protected = protected and documented_unique_id(timeline) == timeline_id
    receipt = {"entries": verified, "attempts": attempts, "protected_markers_and_ranges": protected,
               "requested_count": len(planned), "verified_count": sum(row["verified"] for row in verified)}
    if failure or not protected or receipt["verified_count"] != len(planned):
        raise APICallFailed("DaVinci Resolve clip marker batch requires reconciliation.",
                            details={**receipt, "reason": failure or "readback_mismatch", "mutation_started": bool(attempts)})
    return {**receipt, "applied": True, "dry_run": False}
