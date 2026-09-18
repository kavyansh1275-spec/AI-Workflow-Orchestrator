from __future__ import annotations
import json
import shutil
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class CreativeProject:
    name: str
    medium: str
    stages: tuple[str, ...]

@dataclass(frozen=True)
class CreativeAsset:
    name: str
    asset_type: str
    metadata: dict[str, str]

@dataclass(frozen=True)
class RenderPlan:
    command: tuple[str, ...]
    output: str
    dry_run: bool

class CreativeStudioEngine:
    """Creative workflow engine with safe local project and Blender planning."""
    MEDIUMS = {
        "image": ("concept","composition","render","export"),
        "3d": ("concept","model","materials","lighting","camera","render"),
        "animation": ("storyboard","assets","rig","keyframes","lighting","render"),
        "video": ("script","storyboard","assets","edit","audio","export"),
    }
    def __init__(self, workspace="."):
        self.workspace=Path(workspace).resolve()

    def create_project(self,name,medium):
        medium=medium.strip().lower()
        if medium not in self.MEDIUMS: raise ValueError(f"Unsupported medium: {medium}")
        return CreativeProject(name.strip() or "Untitled",medium,self.MEDIUMS[medium])

    def add_asset(self,name,asset_type,**metadata):
        return CreativeAsset(name.strip() or "Untitled",asset_type.strip().lower(),dict(metadata))

    def validate_project(self,project):
        errors=[]
        if not project.name.strip(): errors.append("Project name is required")
        if project.medium not in self.MEDIUMS: errors.append("Unsupported medium")
        if not project.stages: errors.append("Project must contain stages")
        return tuple(errors)

    def blender_workflow(self):
        return ("create/import assets","build scene","apply materials","configure lighting","animate","set camera","render","export")

    def video_workflow(self):
        return ("script","storyboard","generate/collect visuals","edit timeline","add narration/music","review","export")

    def create_manifest(self,project,assets=()):
        payload={"name":project.name,"medium":project.medium,"stages":list(project.stages),
                 "assets":[{"name":a.name,"asset_type":a.asset_type,"metadata":a.metadata} for a in assets]}
        return json.dumps(payload,indent=2,sort_keys=True)

    def plan_blender_render(self,blend_file,output_file,blender_executable="blender",dry_run=True):
        blend=str((self.workspace/blend_file).resolve())
        output=str((self.workspace/output_file).resolve())
        if not (blend.endswith(".blend") and output):
            raise ValueError("Invalid Blender project or output path")
        if shutil.which(blender_executable) is None and blender_executable=="blender":
            return RenderPlan((blender_executable,"-b",blend,"-o",output,"-F","PNG","-f","1"),output,dry_run)
        return RenderPlan((blender_executable,"-b",blend,"-o",output,"-F","PNG","-f","1"),output,dry_run)

    def verify_output(self,path):
        p=(self.workspace/path).resolve()
        if self.workspace not in p.parents and p != self.workspace: return False
        return p.is_file() and p.stat().st_size > 0
