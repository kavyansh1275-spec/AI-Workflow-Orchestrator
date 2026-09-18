from .registry import SkillRegistry

SKILL_NAME = "copywriting"


def get_skill():
    return SkillRegistry().get(SKILL_NAME)
