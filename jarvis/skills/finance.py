from .registry import SkillRegistry

SKILL_NAME = "finance"


def get_skill():
    return SkillRegistry().get(SKILL_NAME)
