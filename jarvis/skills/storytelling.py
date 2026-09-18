from .registry import SkillRegistry

SKILL_NAME = "storytelling"

def get_skill():
    return SkillRegistry().get(SKILL_NAME)
