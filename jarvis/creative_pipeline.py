from __future__ import annotations
from dataclasses import dataclass
from .creative_studio_engine import CreativeStudioEngine, CreativeProject, CreativeAsset, RenderPlan

@dataclass(frozen=True)
class PipelineResult:
    project: CreativeProject
    manifest: str
    render_plan: RenderPlan | None
    valid: bool
    errors: tuple[str, ...]

class CreativePipeline:
    """High-level V10 pipeline for planning and optionally rendering creative projects."""
    def __init__(self, workspace="."): self.engine=CreativeStudioEngine(workspace)
    def build(self,name,medium,assets=(),blend_file=None,output_file=None,dry_run=True):
        project=self.engine.create_project(name,medium)
        errors=self.engine.validate_project(project)
        manifest=self.engine.create_manifest(project,assets)
        plan=None
        if blend_file is not None or output_file is not None:
            if not blend_file or not output_file: errors=errors+("Both blend_file and output_file are required",)
            else: plan=self.engine.plan_blender_render(blend_file,output_file,dry_run=dry_run)
        return PipelineResult(project,manifest,plan,not errors,tuple(errors))
