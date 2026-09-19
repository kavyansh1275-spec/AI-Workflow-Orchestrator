from .registry import SkillRegistry

SKILL_NAME = "debugging"


def get_skill():
    return SkillRegistry().get(SKILL_NAME)
