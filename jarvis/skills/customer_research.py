from .registry import SkillRegistry

SKILL_NAME = "customer_research"


def get_skill():
    return SkillRegistry().get(SKILL_NAME)
