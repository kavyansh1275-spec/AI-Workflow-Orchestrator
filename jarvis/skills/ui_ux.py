from .registry import SkillRegistry

SKILL_NAME = "ui_ux"

def get_skill():
    return SkillRegistry().get(SKILL_NAME)
