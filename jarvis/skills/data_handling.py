from .registry import SkillRegistry

SKILL_NAME = "data_handling"

def get_skill():
    return SkillRegistry().get(SKILL_NAME)
