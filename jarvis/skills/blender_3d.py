from .registry import SkillRegistry

SKILL_NAME = "blender_3d"


def get_skill():
    return SkillRegistry().get(SKILL_NAME)
