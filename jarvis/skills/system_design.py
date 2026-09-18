from .registry import SkillRegistry

SKILL_NAME = "system_design"

def get_skill():
    return SkillRegistry().get(SKILL_NAME)
