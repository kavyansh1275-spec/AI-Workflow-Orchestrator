from .registry import SkillRegistry

SKILL_NAME = "content_creation"

def get_skill():
    return SkillRegistry().get(SKILL_NAME)
