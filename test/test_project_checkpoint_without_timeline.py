from pathlib import Path
import sys
import unittest
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "native"))

from cutagent_cli.core import version_ops


class _Project:
    def GetName(self):
        return "Empty SDK project"

    def GetUniqueId(self):
        return "native_project_empty"


class _Connection:
    project = _Project()
    timeline = None

    def require_timeline(self):
        raise AssertionError("A project checkpoint must not require a Timeline.")


class ProjectCheckpointWithoutTimelineTests(unittest.TestCase):
    def test_create_checkpoint_captures_project_db_without_active_timeline(self):
        events = []
        snapshot = {
            "state_hash": "sha256:" + "a" * 64,
            "db_hash": "sha256:" + "b" * 64,
            "snapshot_path": "/private/checkpoints/project.Project.db.gz",
            "snapshot_deduplicated": False,
            "db_size": 1024,
            "snapshot_size": 512,
        }
        with (
            patch.object(version_ops, "_checkpoint_store_dir"),
            patch.object(
                version_ops,
                "_resolve_project_db",
                side_effect=lambda _connection: (
                    events.append("resolve"),
                    {
                        "project_db_path": "/private/project/Project.db",
                        "DbName": "Local",
                        "DbType": "Disk",
                    },
                )[1],
            ),
            patch.object(
                version_ops,
                "_save_project",
                side_effect=lambda _connection: events.append("save") or True,
            ),
            patch.object(version_ops, "_create_db_snapshot", return_value=snapshot),
            patch.object(version_ops, "_upsert_checkpoint", side_effect=lambda row: row),
            patch.object(version_ops, "set_verification_status"),
            patch.object(version_ops, "set_recoverability"),
        ):
            checkpoint = version_ops.create_checkpoint(
                _Connection(),
                label="Before first Timeline",
                exact_checkpoint_id="chk_sdk_empty_project",
            )

        self.assertEqual(checkpoint["project_name"], "Empty SDK project")
        self.assertIsNone(checkpoint["timeline_name"])
        self.assertIsNone(checkpoint["timeline_id"])
        self.assertTrue(checkpoint["project_save_called"])
        self.assertEqual(events, ["save", "resolve"])


if __name__ == "__main__":
    unittest.main()
