from .registry import SkillRegistry

SKILL_NAME = "automation"

def get_skill():
    return SkillRegistry().get(SKILL_NAME)
