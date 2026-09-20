from types import SimpleNamespace

import pytest

from cutagent_cli.core import media_pool
from cutagent_cli.errors import ValidationError


class Clip:
    def __init__(self, identity, path):
        self.identity, self.path = identity, path

    def GetName(self):
        return "same.wav"

    def GetUniqueId(self):
        return self.identity

    def GetClipProperty(self):
        return {"File Path": self.path}


class Folder:
    def __init__(self, name, clips=(), children=()):
        self.name, self.clips, self.children = name, list(clips), list(children)

    def GetName(self):
        return self.name

    def GetClipList(self):
        return self.clips

    def GetSubFolderList(self):
        return self.children


@pytest.mark.parametrize("selector", ["path", "media_id"])
def test_exact_move_keeps_same_named_unrelated_asset(selector):
    old, new = Clip("old", "/old/same.wav"), Clip("new", "/new/same.wav")
    target = Folder("Audio")
    root = Folder("Master", [old, new], [target])
    calls = []

    def move(clips, folder):
        calls.append(clips)
        for item in clips:
            root.clips.remove(item)
            folder.clips.append(item)
        return True

    conn = SimpleNamespace(media_pool=SimpleNamespace(GetRootFolder=lambda: root, GetCurrentFolder=lambda: root, MoveClips=move))
    value = new.path if selector == "path" else new.identity
    result = media_pool.move_clips(conn, [{selector: value, "target": "Audio"}])
    assert result["changed_count"] == 1
    assert calls == [[new]]
    assert root.clips == [old]
    assert target.clips == [new]
    assert media_pool.move_clips(conn, [{selector: value, "target": "Audio"}])["changed_count"] == 0
    assert len(calls) == 1


def test_ambiguous_exact_path_never_moves_arbitrary_duplicate():
    clips = [Clip("a", "/same.wav"), Clip("b", "/same.wav")]
    root = Folder("Master", clips, [Folder("Audio")])
    conn = SimpleNamespace(media_pool=SimpleNamespace(GetRootFolder=lambda: root, GetCurrentFolder=lambda: root, MoveClips=lambda *args: pytest.fail("must not mutate")))
    with pytest.raises(ValidationError, match="exactly one"):
        media_pool.move_clips(conn, [{"path": "/same.wav", "target": "Audio"}])
