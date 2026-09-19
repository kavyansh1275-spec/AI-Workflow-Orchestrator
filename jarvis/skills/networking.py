from .registry import SkillRegistry

SKILL_NAME = "networking"

def get_skill():
    return SkillRegistry().get(SKILL_NAME)
