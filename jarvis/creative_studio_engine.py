from __future__ import annotations
import json
import shutil
import subprocess
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
    """Safe creative pipeline: projects, manifests, Blender renders and verification."""
    MEDIUMS={"image":("concept","composition","render","export"),
             "3d":("concept","model","materials","lighting","camera","render"),
             "animation":("storyboard","assets","rig","keyframes","lighting","render"),
             "video":("script","storyboard","assets","edit","audio","export")}
    def __init__(self,workspace="."): self.workspace=Path(workspace).resolve()

    def _safe(self,path):
        p=(self.workspace/path).resolve()
        if p!=self.workspace and self.workspace not in p.parents: raise ValueError("Path escapes workspace")
        return p

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
        return json.dumps({"name":project.name,"medium":project.medium,"stages":list(project.stages),
            "assets":[{"name":a.name,"asset_type":a.asset_type,"metadata":a.metadata} for a in assets]},indent=2,sort_keys=True)

    def save_manifest(self,project,assets=(),filename="creative_manifest.json"):
        p=self._safe(filename); p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(self.create_manifest(project,assets),encoding="utf-8"); return str(p)

    def plan_blender_render(self,blend_file,output_file,blender_executable="blender",dry_run=True):
        blend=self._safe(blend_file); output=self._safe(output_file)
        if blend.suffix.lower()!=".blend": raise ValueError("blend_file must be a .blend file")
        return RenderPlan((blender_executable,"-b",str(blend),"-o",str(output),"-F","PNG","-f","1"),str(output),dry_run)

    def render_blender(self,plan,timeout=300):
        if plan.dry_run: return False,"DRY RUN: render not executed"
        if shutil.which(plan.command[0]) is None: return False,"Blender executable not found"
        try:
            p=subprocess.run(plan.command,cwd=self.workspace,capture_output=True,text=True,timeout=timeout,check=False)
        except subprocess.TimeoutExpired: return False,"Blender render timed out"
        return p.returncode==0,(p.stdout+p.stderr).strip()[-4000:]

    def verify_output(self,path):
        p=self._safe(path); return p.is_file() and p.stat().st_size>0
