"""Reviewed lowering for already compiled setting batches."""
from __future__ import annotations

from typing import Any, Mapping


def compiled_setting_items(value: Mapping[str, Any], lowerings: list[Mapping[str, Any]]) -> list[dict[str, Any]] | None:
    items = []
    for requested, lowering in zip(value["items"], lowerings, strict=True):
        kwargs = lowering.get("handlerKwargs", {})
        # Template substitutions still need the single handler's renderer. The
        # personal skill compiles these offline and therefore uses this batch.
        if kwargs.get("text") is not None or kwargs.get("image") is not None or kwargs.get("render_template") is not None or kwargs.get("params"):
            return None
        if not requested.get("clipName") or requested.get("videoTrackIndex") is None:
            return None
        items.append({
            "path": kwargs["path"], "clip_name": requested["clipName"],
            "track": requested["videoTrackIndex"],
            "record_frame": int(requested["recordPosition"]["value"]["value"]),
            "duration_frames": int(requested["clipDuration"]["value"]["value"]),
            "position_x": kwargs.get("position_x"), "position_y": kwargs.get("position_y"),
        })
    return items


def execute_compiled_setting_batch(conn: Any, items: list[dict[str, Any]]) -> dict[str, Any]:
    from ..commands import fusion as api
    from ..core.fusion_staging_batch import insert_prepared_settings_batch

    api.enforce_mutation_policy("fusion.setting_insert", intended_engine="workaround_setting", mutating=True)
    api.set_execution_engine("workaround_setting")
    result = insert_prepared_settings_batch(conn, items=items, api=api)
    return {"items": result["placement"]["verification"]["items"], "batchPlacement": result}
