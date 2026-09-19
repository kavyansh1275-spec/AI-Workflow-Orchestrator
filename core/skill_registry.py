from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Skill:
    name: str
    category: str
    status: str
    handler: str


# The registry is the contract between the brain/router and future specialist
# implementations. Status is intentionally explicit so the UI never presents
# roadmap items as if they were already autonomous.
SKILLS: tuple[Skill, ...] = (
    Skill("Research", "Intelligence", "implemented", "research"),
    Skill("Critical thinking", "Intelligence", "implemented", "brain"),
    Skill("Learning how to learn", "Intelligence", "foundation", "brain"),
    Skill("Debugging", "Intelligence", "implemented", "test_and_repair"),
    Skill("Decision making", "Intelligence", "implemented", "brain"),
    Skill("Writing", "Intelligence", "foundation", "brain"),
    Skill("System design", "Intelligence", "implemented", "design_solution"),
    Skill("Python", "Software Engineering", "implemented", "project_builder"),
    Skill("JavaScript / TypeScript", "Software Engineering", "foundation", "project_builder"),
    Skill("HTML / CSS", "Software Engineering", "implemented", "project_builder"),
    Skill("React", "Software Engineering", "foundation", "project_builder"),
    Skill("Backend development", "Software Engineering", "implemented", "project_builder"),
    Skill("SQL", "Software Engineering", "foundation", "project_builder"),
    Skill("Pandas", "Software Engineering", "foundation", "project_builder"),
    Skill("APIs / JSON", "Software Engineering", "implemented", "workflow"),
    Skill("Git/GitHub", "Software Engineering", "implemented", "project_builder"),
    Skill("Cybersecurity basics", "Software Engineering", "foundation", "brain"),
    Skill("AI/ML fundamentals", "AI Engineering", "foundation", "brain"),
    Skill("Neural networks", "AI Engineering", "foundation", "brain"),
    Skill("Transformers", "AI Engineering", "foundation", "brain"),
    Skill("Model training", "AI Engineering", "foundation", "brain"),
    Skill("AI agents", "AI Engineering", "implemented", "run_agent"),
    Skill("Tools", "AI Engineering", "implemented", "workflow"),
    Skill("Memory", "AI Engineering", "implemented", "brain"),
    Skill("Planning", "AI Engineering", "implemented", "brain"),
    Skill("Multi-agent systems", "AI Engineering", "implemented", "build_multi_project"),
    Skill("Workflow automation", "Automation & Operations", "implemented", "build_workflow"),
    Skill("Connecting applications", "Automation & Operations", "implemented", "workflow"),
    Skill("API integrations", "Automation & Operations", "implemented", "integration_intelligence"),
    Skill("Data processing", "Automation & Operations", "implemented", "workflow"),
    Skill("Project management", "Automation & Operations", "foundation", "brain"),
    Skill("Task execution", "Automation & Operations", "implemented", "execute"),
    Skill("Entrepreneurship", "Business", "foundation", "research"),
    Skill("Sales", "Business", "foundation", "brain"),
    Skill("Marketing", "Business", "foundation", "research"),
    Skill("Copywriting", "Business", "foundation", "brain"),
    Skill("Customer research", "Business", "implemented", "research"),
    Skill("Product design", "Business", "implemented", "design_solution"),
    Skill("Negotiation", "Business", "foundation", "brain"),
    Skill("Financial literacy", "Business", "foundation", "brain"),
    Skill("Networking", "Business", "foundation", "brain"),
    Skill("Product Builder", "Product Builder", "implemented", "build_project"),
)


def list_skills() -> list[dict[str, str]]:
    return [skill.__dict__.copy() for skill in SKILLS]
