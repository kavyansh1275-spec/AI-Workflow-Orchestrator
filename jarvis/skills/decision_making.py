from .registry import SkillRegistry

SKILL_NAME = "decision_making"


def get_skill():
    return SkillRegistry().get(SKILL_NAME)
