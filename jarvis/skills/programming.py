from .registry import SkillRegistry

SKILL_NAME = "programming"


def get_skill():
    return SkillRegistry().get(SKILL_NAME)
