"""Exact-ID clip marker batch command registration."""
from __future__ import annotations

import json
from pathlib import Path

import typer

from ..connection import get_connection
from ..core.clip_marker_batch import apply_clip_marker_batch
from ..core.resolve_state_lock import exclusive_resolve_state_operation
from ..errors import ValidationError, handle_errors
from ..output import is_dry_run, mutation_payload, output, set_execution_engine, set_recoverability, set_verification_status
from ..policy import enforce_mutation_policy


@clip_markers_app.command("batch")
@handle_errors
def clip_marker_batch(
    batch: str = typer.Option(..., "--batch", help="JSON file containing exact V1 clip marker entries"),
    timeline_id: str = typer.Option(..., "--timeline-id", help="Required native ID of the active target timeline"),
):
    """Insert clip markers in one batch using exact IDs and clip-local offsets.

    Entries require timeline_item_id, record_start, record_end, offset,
    duration, color, name and note. Different existing markers at requested
    positions fail preflight; identical existing markers are reused.
    Retimed, reversed, mixed-rate, or unproven source mappings are rejected
    before writes. Source and timeline frame rates must be known and match.
    """
    try:
        file = Path(batch).expanduser()
        if file.stat().st_size > 16 * 1024 * 1024:
            raise ValueError("batch exceeds size limit")
        data = json.loads(file.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValidationError("Clip marker batch requires a readable JSON file up to 16 MiB.") from exc
    entries = data.get("entries") if isinstance(data, dict) else data
    if not isinstance(entries, list) or any(not isinstance(entry, dict) for entry in entries):
        raise ValidationError("Clip marker batch requires an entries array of objects.")
    dry_run = is_dry_run()
    set_execution_engine("api_native")
    set_recoverability("manual")
    set_verification_status("not_requested")
    enforce_mutation_policy("clip.marker", intended_engine="api_native", mutating=not dry_run)
    with exclusive_resolve_state_operation(operation="timeline.clip_markers.batch"):
        conn = get_connection(require_project=True, require_timeline=True)
        result = apply_clip_marker_batch(conn.timeline, timeline_id=timeline_id, entries=entries, dry_run=dry_run, conn=conn)
    set_verification_status("not_requested" if dry_run else "verified")
    output(mutation_payload(action="timeline.clip_markers.batch", target={"kind": "timeline", "id": timeline_id},
                            changed=not dry_run and bool(result.get("attempts")), **result), title="Timeline clip marker batch")
