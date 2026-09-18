from .registry import SkillRegistry

SKILL_NAME = "sales"


def get_skill():
    return SkillRegistry().get(SKILL_NAME)
