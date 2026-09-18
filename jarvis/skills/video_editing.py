from .registry import SkillRegistry

SKILL_NAME = "video_editing"


def get_skill():
    return SkillRegistry().get(SKILL_NAME)
