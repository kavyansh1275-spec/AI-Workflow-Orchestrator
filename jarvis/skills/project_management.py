from .registry import SkillRegistry

SKILL_NAME = "project_management"


def get_skill():
    return SkillRegistry().get(SKILL_NAME)
