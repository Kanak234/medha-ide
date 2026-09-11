import os
import json
import tempfile
from pathlib import Path
from medha.core.workspace import ScratchpadSession, ProjectWorkspace, HybridWorkspaceController

def test_scratchpad_session():
    session = ScratchpadSession("/workspace/main.c")
    assert session.file_path == "/workspace/main.c"
    assert session.is_standalone() is True
    assert session.is_dirty is False

def test_project_workspace():
    with tempfile.TemporaryDirectory() as tmpdir:
        proj = ProjectWorkspace("SampleProj", tmpdir)
        proj.sources = ["main.c", "util.c"]
        proj.headers = ["util.h"]
        assert proj.save() is True

        proj_file = Path(tmpdir) / "SampleProj.medhaproj"
        assert proj_file.exists()

        data = json.loads(proj_file.read_text())
        assert data["name"] == "SampleProj"
        assert data["sources"] == ["main.c", "util.c"]
        assert data["headers"] == ["util.h"]

def test_hybrid_workspace_controller(qapp):
    controller = HybridWorkspaceController()
    assert controller.active_mode == "scratchpad"

    modes = []
    controller.mode_changed.connect(lambda m: modes.append(m))

    controller.set_scratchpad_file("/tmp/quick.py")
    assert controller.scratchpad.file_path == "/tmp/quick.py"
    assert modes == ["scratchpad"]

    with tempfile.TemporaryDirectory() as tmpdir:
        proj_file = Path(tmpdir) / "TestApp.medhaproj"
        proj_file.write_text("{}")
        success = controller.open_project(str(proj_file))
        assert success is True
        assert controller.active_mode == "project"
        assert controller.active_project.name == "TestApp"
        assert "project" in modes
