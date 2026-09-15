"""Production prepared-action binding for the fixed timeline marker mutation."""

from __future__ import annotations

import hashlib
import inspect
import json
import os
import re
import time
from collections.abc import Mapping
from collections import Counter
from typing import Any

from .connection import get_connection
from .core import timeline_ops
from .policy import _prepared_action_admission_scope

ACTION_ID = "cutagent.action.timeline.marker.add"
_IDENTITY_SUFFIX = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._~-]*$")


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _marker_content(markers):
    """Compare marker content independently of the enclosing snapshot revision."""
    return [{key: value for key, value in marker.items() if key != "snapshotRevision"} for marker in markers]


def _existing_markers_preserved(before, after):
    old = Counter(_digest(marker) for marker in _marker_content(before))
    new = Counter(_digest(marker) for marker in _marker_content(after))
    return all(new[key] == count for key, count in old.items())


def _protected_timeline_state(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Return timeline content without handles derived from its whole revision."""
    revision_bound_handles = {"snapshotId", "snapshotTrackId", "snapshotRevision"}

    def project(value: Any) -> Any:
        if isinstance(value, Mapping):
            return {
                key: project(item)
                for key, item in value.items()
                if key not in revision_bound_handles
            }
        if isinstance(value, list):
            return [project(item) for item in value]
        return value

    return project({
        key: value
        for key, value in snapshot.items()
        if key not in {"markers", "revision", "snapshotObservation"}
    })


class TimelineMarkerAddExecutionAuthority:
    """Calls the existing guarded CutAgent CLI timeline marker owner in-process."""

    def __init__(self, *, connection_factory=get_connection, marker_adder=timeline_ops.add_marker, mutation_guard=timeline_ops.require_sdk_marker_mutation_guard, state_inspector=timeline_ops.inspect_sdk_live_state):
        self._connection_factory = connection_factory
        self._marker_adder = marker_adder
        self._mutation_guard = mutation_guard
        self._state_inspector = state_inspector
        self._private_timeline_inspector = None

    def bind_private_timeline_inspector(self, callback):
        self._private_timeline_inspector = callback

    def _matches_carrier_admission(self, action_id, command_id, admitted_handler):
        return (
            action_id == ACTION_ID
            and command_id == "timeline.marker.add"
            and inspect.unwrap(self._marker_adder) is admitted_handler
        )

    def capture_state(self, context):
        if self._private_timeline_inspector is not None:
            binding = context["exactRequestBinding"]["identities"]
            inspected = self._private_timeline_inspector({
                "projectId": binding["projectId"],
                "timelineId": binding["timelineId"],
            })
            expected = context.get("timeline", {}).get("mutationGuard")
            if not isinstance(expected, str) or inspected.get("mutationGuard") != expected:
                raise ValueError("Prepared marker live timeline binding changed.")
            return {"mutationGuard": expected, "summary": inspected["snapshot"], "normalized": True}
        conn = self._connection_factory(require_timeline=True)
        inspected = self._state_inspector(
            conn,
            "timeline.snapshot",
            deadline_at_ms=int(time.time() * 1000) + 60_000,
        )
        expected = context.get("timeline", {}).get("mutationGuard")
        if not isinstance(expected, str) or inspected.get("mutation_guard") != expected:
            raise ValueError("Prepared marker live timeline binding changed.")
        return {"mutationGuard": expected, "summary": inspected["summary"]}

    def invoke_admitted_handler(self, action_id, context, prepared, handler_input):
        if action_id != ACTION_ID or context["actionId"] != ACTION_ID:
            raise ValueError("Prepared marker authority correlation failed.")
        request_binding = context["exactRequestBinding"]
        markers = handler_input["markers"] if "markers" in handler_input else [handler_input["marker"]]
        before = self.capture_state(context)
        timeline_start = int(before["summary"].get("start", {}).get("value", {}).get("value", 0))
        if any(marker["recordFrame"] < timeline_start for marker in markers):
            raise ValueError("Prepared marker frame precedes the live timeline start.")
        frames = [marker["recordFrame"] for marker in markers]
        if len(set(frames)) != len(frames):
            raise ValueError("Prepared marker destinations must be unique.")
        if before.get("normalized") and any(
            existing.get("position", {}).get("value", {}).get("value") in frames
            for existing in before["summary"].get("markers", [])
        ):
            raise ValueError("Prepared marker destination is already occupied.")
        conn = self._connection_factory(require_timeline=True)
        previous_guard = os.environ.get("CUTAGENT_SDK_MARKER_GUARD")
        os.environ["CUTAGENT_SDK_MARKER_GUARD"] = before["mutationGuard"]
        try:
            self._mutation_guard(conn)
            with _prepared_action_admission_scope(
                ACTION_ID,
                "timeline.marker.add",
                self,
                inspect.unwrap(self._marker_adder),
                context,
            ):
                results = [self._marker_adder(
                    conn, f"{marker['recordFrame'] - timeline_start}f",
                    marker["color"], marker["name"], marker["note"], marker["durationFrames"],
                ) for marker in markers]
        finally:
            if previous_guard is None:
                os.environ.pop("CUTAGENT_SDK_MARKER_GUARD", None)
            else:
                os.environ["CUTAGENT_SDK_MARKER_GUARD"] = previous_guard
        if self._private_timeline_inspector is not None:
            identities = context["exactRequestBinding"]["identities"]
            inspected_after = self._private_timeline_inspector({
                "phase": "verify",
                "projectId": identities["projectId"],
                "timelineId": identities["timelineId"],
            })
            after = inspected_after["snapshot"]
            normalized = True
        else:
            inspected_after = self._state_inspector(conn, "timeline.snapshot", deadline_at_ms=int(time.time() * 1000) + 60_000)
            after = inspected_after["summary"]
            normalized = False
        if "markers" in handler_input:
            return {
                "readbacks": results,
                "beforeState": before["summary"], "afterState": after,
                "normalizedState": normalized,
                "timelineRevision": after.get("revision", "revision_" + _digest(after)[7:39]),
            }
        result = results[0]
        target_id = request_binding["identities"]["targetIds"][0]
        readback = result["readback"]
        public_marker = {
            "id": target_id,
            "recordFrame": int(readback["record_frame"]),
            "color": readback["color"],
            "name": readback.get("name", ""),
            "note": readback.get("note", ""),
            "durationFrames": int(readback.get("duration", 1)),
        }
        return {
            "action": "create",
            "marker": public_marker,
            "previousMarker": None,
            "timelineRevision": after.get("revision", "revision_" + _digest(after)[7:39]),
            "readback": result,
            "beforeState": before["summary"],
            "afterState": after,
            "normalizedState": normalized,
        }


class TimelineMarkerAddDescriptor:
    operation_class = "mutation"
    version = 1
    capability_id = "timeline.marker_crud"

    def validate_input(self, value):
        if isinstance(value, Mapping) and "markers" in value:
            if set(value) != {"projectId", "timelineId", "timelineRevision", "markers"}:
                raise ValueError("Prepared marker input is invalid.")
            markers = value["markers"]
            if not isinstance(markers, list) or not 1 <= len(markers) <= 10_000:
                raise ValueError("Prepared marker batch size is invalid.")
            for marker in markers:
                self.validate_input({**{key: value[key] for key in ("projectId", "timelineId", "timelineRevision")}, "marker": marker})
            if len({marker["recordFrame"] for marker in markers}) != len(markers):
                raise ValueError("Prepared marker destinations must be unique.")
            return json.loads(json.dumps(value))
        required = {"projectId", "timelineId", "timelineRevision", "marker"}
        if not isinstance(value, Mapping) or set(value) != required or not isinstance(value["marker"], Mapping):
            raise ValueError("Prepared marker input is invalid.")
        marker = value["marker"]
        if set(marker) != {"recordFrame", "color", "name", "note", "durationFrames"}:
            raise ValueError("Prepared marker value is invalid.")
        if type(marker["recordFrame"]) is not int or not 0 <= marker["recordFrame"] <= 9_007_199_254_740_991 or type(marker["durationFrames"]) is not int or not 1 <= marker["durationFrames"] <= 2_147_483_647:
            raise ValueError("Prepared marker frame values are invalid.")
        if any(not isinstance(marker[key], str) or not minimum <= len(marker[key]) <= maximum for key, minimum, maximum in (("color", 1, 64), ("name", 0, 4096), ("note", 0, 65_536))):
            raise ValueError("Prepared marker text values are invalid.")
        return json.loads(json.dumps(value))

    def prepare(self, context, value):
        binding = context["exactRequestBinding"]
        timeline_id = binding["identities"]["timelineId"]
        timeline_revision = binding["revisions"]["timeline"]
        target = {"kind": "timeline", "stableId": timeline_id, "revision": timeline_revision, "projectId": binding["identities"]["projectId"], "timelineId": timeline_id}
        live = context["executionAuthority"].capture_state(context)
        return {
            "targets": [target],
            "preState": live,
            "impact": {
                **context["mutationBase"],
                "status": "mutation",
                "effects": [{"operation": "timeline.marker.add", "kind": "create", "trackTypes": [], "targets": [{"kind": "timeline", "stableId": timeline_id, "revision": timeline_revision}], "placementIntent": "marker", "broad": False, "ambiguous": False, "complete": True}],
                "closedComposition": True, "complete": True, "ambiguous": False, "broad": False,
                "executableStableTargetPrecondition": True,
                "verificationPolicy": {"minimumEvidence": ["readback"], "requireProtectedStatePreserved": True, "protectedTargetEvidence": "every_declared_target"},
            },
            "lowering": {"commandId": "timeline.marker.add", "inputDigest": _digest(value)},
            "verification": {"minimumEvidence": ["readback"]},
            "recovery": {"mode": "inspect"},
        }

    def resolve_current(self, context, prepared):
        return {"targets": prepared["targets"], "preState": context["executionAuthority"].capture_state(context)}

    def execute(self, context, prepared):
        return context["executionAuthority"].invoke_admitted_handler(ACTION_ID, context, prepared, context["exactRequestBinding"]["input"])

    def verify(self, context, prepared, result):
        if "markers" in context["exactRequestBinding"]["input"]:
            from .prepared_action_marker_batch import verify_batch
            return verify_batch(context, result)
        readback = result["readback"]
        marker = result["marker"]
        before = result["beforeState"]
        after = result["afterState"]
        before_markers = before.get("markers", [])
        after_markers = after.get("markers", [])
        protected_before = _protected_timeline_state(before)
        protected_after = _protected_timeline_state(after)
        protected = _digest(protected_before) == _digest(protected_after)
        matched = (
            readback.get("verified") is True
            and marker["recordFrame"] == readback["record_frame"]
            and len(after_markers) == len(before_markers) + 1
            and _existing_markers_preserved(before_markers, after_markers)
        )
        if result.get("normalizedState"):
            expected = context["exactRequestBinding"]["input"]["marker"]
            matches = [candidate for candidate in after_markers if (
                candidate.get("position", {}).get("value", {}).get("value") == expected["recordFrame"]
                and candidate.get("color") == expected["color"]
                and candidate.get("name") == expected["name"]
                and candidate.get("note") == expected["note"]
                and candidate.get("duration", {}).get("value", {}).get("value") == expected["durationFrames"]
            )]
            matched = matched and len(matches) == 1
        passed = matched and protected
        return {"outcome": "passed" if passed else "failed", "evidence": [{"modality": "readback", "digest": _digest(after_markers), "summary": "CutAgent CLI read back the complete marker collection."}, {"modality": "structural", "digest": _digest(protected_after), "summary": "CutAgent CLI compared the complete non-marker timeline state."}], "protectedStatePreserved": protected}

    def recover(self, context, prepared, failure):
        return {"outcome": "failed", "attempted": True, "manualActionRequired": True}

    def project_result(self, context, prepared, result):
        if "markers" in context["exactRequestBinding"]["input"]:
            from .prepared_action_marker_batch import project_batch_result
            return project_batch_result(context, result)
        if result.get("normalizedState"):
            expected = context["exactRequestBinding"]["input"]["marker"]
            matches = [candidate for candidate in result["afterState"].get("markers", []) if (
                candidate.get("position", {}).get("value", {}).get("value") == expected["recordFrame"]
                and candidate.get("color") == expected["color"]
                and candidate.get("name") == expected["name"]
                and candidate.get("note") == expected["note"]
                and candidate.get("duration", {}).get("value", {}).get("value") == expected["durationFrames"]
            )]
            if len(matches) != 1:
                raise ValueError("Prepared marker public identity is ambiguous.")
            marker = matches[0]
            return {"action": "create", "marker": {"id": marker["id"], "recordFrame": marker["position"]["value"]["value"], "color": marker["color"], "name": marker["name"], "note": marker["note"], "durationFrames": marker["duration"]["value"]["value"]}, "previousMarker": None, "timelineRevision": result["timelineRevision"]}
        return {key: result[key] for key in ("action", "marker", "previousMarker", "timelineRevision")}

    def validate_public_result(self, value):
        if isinstance(value, Mapping) and "markers" in value:
            if set(value) != {"action", "markers", "previousMarkers", "timelineRevision"} or value.get("previousMarkers") != []:
                return False
            markers = value["markers"]
            if not isinstance(markers, list) or not 1 <= len(markers) <= 10_000:
                return False
            if not all(self.validate_public_result({"action": value["action"], "marker": marker, "previousMarker": None, "timelineRevision": value["timelineRevision"]}) for marker in markers):
                return False
            return len({marker["id"] for marker in markers}) == len(markers)
        if (
            not isinstance(value, Mapping)
            or set(value) != {"action", "marker", "previousMarker", "timelineRevision"}
            or value.get("action") != "create"
            or value.get("previousMarker") is not None
        ):
            return False
        marker = value.get("marker")
        if not isinstance(marker, Mapping) or set(marker) != {
            "id", "recordFrame", "color", "name", "note", "durationFrames"
        }:
            return False
        marker_id = marker.get("id")
        revision = value.get("timelineRevision")
        if (
            not isinstance(marker_id, str)
            or not marker_id.startswith("marker_")
            or len(marker_id) > 160
            or _IDENTITY_SUFFIX.fullmatch(marker_id.removeprefix("marker_")) is None
            or not isinstance(revision, str)
            or not revision.startswith("revision_")
            or len(revision) > 160
            or _IDENTITY_SUFFIX.fullmatch(revision.removeprefix("revision_")) is None
        ):
            return False
        return (
            isinstance(marker.get("recordFrame"), int)
            and not isinstance(marker.get("recordFrame"), bool)
            and marker["recordFrame"] >= 0
            and isinstance(marker.get("durationFrames"), int)
            and not isinstance(marker.get("durationFrames"), bool)
            and 1 <= marker["durationFrames"] <= 2_147_483_647
            and isinstance(marker.get("color"), str)
            and 1 <= len(marker["color"]) <= 64
            and isinstance(marker.get("name"), str)
            and len(marker["name"]) <= 4096
            and isinstance(marker.get("note"), str)
            and len(marker["note"]) <= 65_536
        )


def marker_contribution():
    return {ACTION_ID: TimelineMarkerAddDescriptor()}


def marker_execution_authorities():
    return {ACTION_ID: TimelineMarkerAddExecutionAuthority()}
