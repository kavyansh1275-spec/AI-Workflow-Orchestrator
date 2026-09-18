from __future__ import annotations
from dataclasses import dataclass
from .ai_provider import AIProviderManager
from .business_intelligence_pipeline_v2 import BusinessIntelligencePipelineV2
from .config import Config
from .creative_pipeline import CreativePipeline
from .database import Database
from .memory import Memory
from .planner import Planner
from .router import SkillRouter

@dataclass
class JarvisBrain:
    config: Config

    def __post_init__(self):
        self.database=Database(self.config.memory_path)
        self.memory=Memory(database=self.database)
        self.router=SkillRouter()
        self.planner=Planner(self.router)
        self.ai=AIProviderManager(self.config.provider,self.config.model)
        self.creative=CreativePipeline()
        self.business=BusinessIntelligencePipelineV2()

    def _build_prompt(self,request,skills):
        skill_text=", ".join(skills) or "general reasoning"
        recent=self.memory.recent(5)
        context="\n".join(f"- {item.category}: {item.request}" for item in recent) or "- no prior context"
        return ("You are JARVIS, a modular AI assistant. Answer the user's task clearly and safely. "
                f"Activated skills: {skill_text}. Recent memory:\n{context}\nUser task: {request}")

    def _creative_request(self,request):
        text=request.lower()
        return any(k in text for k in ("blender","3d cartoon","3d animation","render a scene","create a character","animate a character"))

    def _business_request(self,request):
        text=request.lower()
        return any(k in text for k in ("business","revenue","sales","profit","kpi","funnel","forecast","anomaly"))

    def _creative_plan(self,request):
        medium="animation" if any(k in request.lower() for k in ("animation","animate","cartoon","character")) else "3d"
        return self.creative.build("JARVIS Creative Project",medium,dry_run=True)

    def _business_status(self):
        return ("Business Intelligence: READY",
                "Capabilities: data normalization, KPIs, funnel analysis, anomaly detection, trends, forecasting, insights, decision priorities")

    def handle(self,request):
        skills=self.router.route(request)
        plan=self.planner.build(request,skills,self.config.max_steps)
        self.memory.remember(request,skills)
        response=self.ai.generate(self._build_prompt(request,skills))
        lines=[f"Intent: {plan.intent}",f"Skills: {', '.join(skills) or 'general'}",
               f"AI: {response.provider}/{response.model}","Plan:"]
        lines.extend(f"{i}. {step}" for i,step in enumerate(plan.steps,1))
        if self._creative_request(request):
            creative=self._creative_plan(request)
            lines += ["Creative Pipeline: READY",f"Medium: {creative.project.medium}",
                      f"Stages: {' -> '.join(creative.project.stages)}"]
        if self._business_request(request): lines.extend(self._business_status())
        lines += ["Response:",response.text]
        if response.used_fallback: lines.append("Note: configured AI provider was unavailable; local fallback was used.")
        if self.config.dry_run: lines.append("Mode: dry-run (execution tools are not enabled yet).")
        return "\n".join(lines)
