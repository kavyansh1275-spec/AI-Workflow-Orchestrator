from .registry import SkillRegistry

SKILL_NAME = "marketing"


def get_skill():
    return SkillRegistry().get(SKILL_NAME)
