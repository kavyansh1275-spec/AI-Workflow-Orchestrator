from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AIResponse:
    text: str
    provider: str
    model: str
    used_fallback: bool = False


class AIProvider(Protocol):
    name: str

    def generate(self, prompt: str) -> AIResponse:
        ...


class LocalProvider:
    """Dependency-free fallback that keeps JARVIS usable without an API key."""

    name = "local"

    def __init__(self, model: str = "local-router"):
        self.model = model

    def generate(self, prompt: str) -> AIResponse:
        clean = " ".join(prompt.split())
        if not clean:
            return AIResponse("I need a task to work on.", self.name, self.model)
        return AIResponse(
            f"Local reasoning mode: I received this task and can plan it safely: {clean}",
            self.name,
            self.model,
        )


class GeminiProvider:
    name = "gemini"

    def __init__(self, model: str):
        self.model = model

    def generate(self, prompt: str) -> AIResponse:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")

        try:
            from google import genai
        except ImportError as exc:
            raise RuntimeError("google-genai is not installed") from exc

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=self.model, contents=prompt)
        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("Gemini returned an empty response")
        return AIResponse(text.strip(), self.name, self.model)


class AIProviderManager:
    """Selects a configured provider and always has a safe local fallback."""

    def __init__(self, provider_name: str = "gemini", model: str = "gemini-3.6-flash"):
        self.provider_name = provider_name.lower()
        self.model = model

    def generate(self, prompt: str) -> AIResponse:
        if self.provider_name == "local":
            return LocalProvider().generate(prompt)

        if self.provider_name == "gemini":
            try:
                return GeminiProvider(self.model).generate(prompt)
            except Exception:
                fallback = LocalProvider().generate(prompt)
                return AIResponse(
                    fallback.text,
                    fallback.provider,
                    fallback.model,
                    used_fallback=True,
                )

        fallback = LocalProvider().generate(prompt)
        return AIResponse(
            fallback.text,
            fallback.provider,
            fallback.model,
            used_fallback=True,
        )
