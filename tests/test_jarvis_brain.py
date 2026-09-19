from brain import JarvisBrain


def test_brain_routes_workflow_and_emits_events():
    events = []
    result = JarvisBrain().execute(
        "Receive a webhook and send a Slack message",
        emit=events.append,
    )

    assert result["status"] == "completed"
    assert result["result"]["workflow"]["steps"][0]["app"] == "webhook"
    assert any(event.stage == "understand" for event in events)
    assert any(event.stage == "test" for event in events)
    assert events[-1].stage == "complete"


def test_brain_exposes_clarification_instead_of_faking_configuration():
    events = []
    result = JarvisBrain().execute(
        "Receive a form submission, analyze it with AI, and send the result to Gmail",
        emit=events.append,
    )

    assert result["status"] == "needs_clarification"
    assert "email recipient" in result["missing"]
    assert events[-1].status == "blocked"


def test_skill_registry_has_non_creative_target_surface():
    from core.skill_registry import SKILLS

    assert len(SKILLS) == 42
    assert not any(skill.category == "Creative Studio" for skill in SKILLS)
