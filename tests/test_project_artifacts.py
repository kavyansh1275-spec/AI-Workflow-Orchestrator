from pathlib import Path
from core.project_artifacts import ProjectArtifactBuilder
def test_project_artifacts_create_workspace(tmp_path,monkeypatch):
    monkeypatch.chdir(tmp_path)
    r=ProjectArtifactBuilder().build("Demo App","Build a website with a Python backend",{"steps":[]})
    root=Path(r["project_dir"])
    assert (root/"index.html").exists() and (root/"app.js").exists() and (root/"app.py").exists() and (root/"artifact_manifest.json").exists()
