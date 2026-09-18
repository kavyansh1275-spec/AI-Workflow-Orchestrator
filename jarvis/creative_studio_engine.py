from __future__ import annotations
from dataclasses import dataclass

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

class CreativeStudioEngine:
    """Dependency-free creative workflow planner for graphics, 3D, animation and video."""

    MEDIUMS = {
        "image": ("concept", "composition", "render", "export"),
        "3d": ("concept", "model", "materials", "lighting", "camera", "render"),
        "animation": ("storyboard", "assets", "rig", "keyframes", "lighting", "render"),
        "video": ("script", "storyboard", "assets", "edit", "audio", "export"),
    }

    def create_project(self, name: str, medium: str) -> CreativeProject:
        medium = medium.strip().lower()
        stages = self.MEDIUMS.get(medium)
        if not stages:
            raise ValueError(f"Unsupported medium: {medium}")
        return CreativeProject(name.strip() or "Untitled", medium, stages)

    def add_asset(self, name: str, asset_type: str, **metadata: str) -> CreativeAsset:
        return CreativeAsset(name.strip() or "Untitled", asset_type.strip().lower(), dict(metadata))

    def validate_project(self, project: CreativeProject) -> tuple[str, ...]:
        errors = []
        if not project.name.strip(): errors.append("Project name is required")
        if project.medium not in self.MEDIUMS: errors.append("Unsupported medium")
        if not project.stages: errors.append("Project must contain stages")
        return tuple(errors)

    def blender_workflow(self) -> tuple[str, ...]:
        return ("create/import assets", "build scene", "apply materials",
                "configure lighting", "animate", "set camera", "render", "export")

    def video_workflow(self) -> tuple[str, ...]:
        return ("script", "storyboard", "generate/collect visuals",
                "edit timeline", "add narration/music", "review", "export")
