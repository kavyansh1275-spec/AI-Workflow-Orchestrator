from .registry import SkillRegistry

SKILL_NAME = "entrepreneurship"


def get_skill():
    return SkillRegistry().get(SKILL_NAME)
