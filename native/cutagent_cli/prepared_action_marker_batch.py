"""Collection readback for the prepared marker-create batch contract."""

from .prepared_action_marker import _digest, _existing_markers_preserved, _protected_timeline_state


def _matches(candidate, expected):
    return (
        candidate.get("position", {}).get("value", {}).get("value") == expected["recordFrame"]
        and candidate.get("duration", {}).get("value", {}).get("value") == expected["durationFrames"]
        and all(candidate.get(key) == expected[key] for key in ("color", "name", "note"))
    )


def _created(context, result):
    if result.get("normalizedState") is not True:
        raise ValueError("Prepared marker batches require authoritative normalized identities.")
    candidates = result["afterState"].get("markers", [])
    created = []
    for expected in context["exactRequestBinding"]["input"]["markers"]:
        matches = [candidate for candidate in candidates if _matches(candidate, expected)]
        if len(matches) != 1:
            raise ValueError("Prepared marker batch readback is missing or ambiguous.")
        created.append(matches[0])
    if len({marker["id"] for marker in created}) != len(created):
        raise ValueError("Prepared marker batch identities are not unique.")
    return created


def verify_batch(context, result):
    before, after = result["beforeState"], result["afterState"]
    protected_before = _protected_timeline_state(before)
    protected_after = _protected_timeline_state(after)
    protected = _digest(protected_before) == _digest(protected_after)
    expected = context["exactRequestBinding"]["input"]["markers"]
    before_markers, after_markers = before.get("markers", []), after.get("markers", [])
    try:
        created = _created(context, result)
        before_ids = {marker["id"] for marker in before_markers}
        matched = (
            all(marker["id"] not in before_ids for marker in created)
            and len(after_markers) == len(before_markers) + len(expected)
            and _existing_markers_preserved(before_markers, after_markers)
            and len(result["readbacks"]) == len(expected)
            and all(row.get("verified") is True for row in result["readbacks"])
        )
    except (ValueError, KeyError, TypeError):
        matched = False
    return {
        "outcome": "passed" if matched and protected else "failed",
        "evidence": [
            {"modality": "readback", "digest": _digest(after_markers), "summary": "CutAgent CLI compared the complete marker collection."},
            {"modality": "structural", "digest": _digest(protected_after), "summary": "CutAgent CLI compared the complete non-marker timeline state."},
        ],
        "protectedStatePreserved": protected,
    }


def project_batch_result(context, result):
    return {
        "action": "create",
        "markers": [{
            "id": marker["id"],
            "recordFrame": marker["position"]["value"]["value"],
            "durationFrames": marker["duration"]["value"]["value"],
            **{key: marker[key] for key in ("color", "name", "note")},
        } for marker in _created(context, result)],
        "previousMarkers": [],
        "timelineRevision": result["timelineRevision"],
    }
