from .registry import SkillRegistry

SKILL_NAME = "cybersecurity"

def get_skill():
    return SkillRegistry().get(SKILL_NAME)
