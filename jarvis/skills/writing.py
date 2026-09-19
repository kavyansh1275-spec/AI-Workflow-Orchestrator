from .registry import SkillRegistry

SKILL_NAME = "writing"

def get_skill():
    return SkillRegistry().get(SKILL_NAME)
