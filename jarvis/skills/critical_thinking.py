from .registry import SkillRegistry

SKILL_NAME = "critical_thinking"


def get_skill():
    return SkillRegistry().get(SKILL_NAME)
