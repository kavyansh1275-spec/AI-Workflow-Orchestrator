from .registry import SkillRegistry

SKILL_NAME = "ai_ml"


def get_skill():
    return SkillRegistry().get(SKILL_NAME)
