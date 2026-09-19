from .registry import SkillRegistry

SKILL_NAME = "ai_agents"

def get_skill():
    return SkillRegistry().get(SKILL_NAME)
