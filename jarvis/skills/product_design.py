from .registry import SkillRegistry

SKILL_NAME = "product_design"


def get_skill():
    return SkillRegistry().get(SKILL_NAME)
