from .registry import SkillRegistry

SKILL_NAME = "learning"


def get_skill():
    return SkillRegistry().get(SKILL_NAME)
