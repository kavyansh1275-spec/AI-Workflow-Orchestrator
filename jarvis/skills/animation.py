from .registry import SkillRegistry

SKILL_NAME = "animation"

def get_skill():
    return SkillRegistry().get(SKILL_NAME)
