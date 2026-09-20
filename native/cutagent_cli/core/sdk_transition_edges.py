"""Exact native custody for video-only clip-edge transition batches."""
from ..errors import SdkMutationStaleRevision, ValidationError
from .db_timeline_selection import LiveItemRef


def require_clip_edges(*, expected, selected, live_video):
    if not isinstance(expected, dict) or set(expected) != {"kind", "target", "placement", "scope", "durationFrames", "transitionType"}:
        raise ValidationError("SDK clip-edge transition custody is malformed.")
    if expected["kind"] != "clip_edges" or expected["scope"] != "video" or not isinstance(expected["placement"], str) or expected["placement"] not in {"start", "end", "both"}:
        raise ValidationError("SDK clip-edge transitions require explicit video-only scope and placement.")
    if type(expected["durationFrames"]) is not int or expected["durationFrames"] < 1 or not isinstance(expected["transitionType"], str) or not expected["transitionType"]:
        raise ValidationError("SDK clip-edge transition parameters are malformed.")
    target = expected["target"]
    keys = {"id", "trackType", "trackIndex", "recordStartFrame", "recordEndFrame", "name", "linkedItemIds"}
    if not isinstance(target, dict) or set(target) != keys:
        raise ValidationError("SDK clip-edge target is malformed.")
    integers = (target["trackIndex"], target["recordStartFrame"], target["recordEndFrame"])
    links = target["linkedItemIds"]
    if (any(type(value) is not int or value < 0 or value > 9_007_199_254_740_991 for value in integers)
            or target["trackIndex"] < 1 or target["recordEndFrame"] <= target["recordStartFrame"]
            or target["trackType"] != "video"
            or any(not isinstance(target[key], str) or not target[key] for key in ("id", "name"))
            or not isinstance(links, list)
            or any(not isinstance(link, str) or not link for link in links)
            or len(set(links)) != len(links)):
        raise ValidationError("SDK clip-edge target is malformed.")
    matches = [item for item in live_video if (
        item.item_id == target["id"] and item.track_type == "video"
        and item.track_index == target["trackIndex"] and item.name == target["name"]
        and item.start == target["recordStartFrame"] and item.end == target["recordEndFrame"]
    )]
    if len(matches) != 1:
        raise SdkMutationStaleRevision("The exact SDK clip-edge target changed before mutation.")
    live = matches[0]
    if expected["durationFrames"] > live.duration:
        raise ValidationError("SDK clip-edge transition exceeds the target duration.")
    if live.linked_item_ids is None or set(live.linked_item_ids) != set(links):
        raise SdkMutationStaleRevision("SDK clip-edge target linkage changed before mutation.")
    planned = selected.get("video")
    if selected.get("audio") is not None:
        raise SdkMutationStaleRevision("SDK video-only clip-edge transition selected audio.")
    fields = ("item_id", "track_type", "track_index", "name", "start", "duration")
    if not isinstance(planned, LiveItemRef) or any(getattr(planned, key) != getattr(live, key) for key in fields):
        raise SdkMutationStaleRevision("SDK clip-edge private selection drifted from its exact target.")
    return {"video": live, "audio": None}
