from __future__ import annotations
import json, os, re
from typing import Any
from google import genai
from google.genai import types
from src.models import CapturedFeatures, ReviewResult

class GeminiClient:
    MODEL = "gemini-2.0-flash-lite"

    def __init__(self, api_key: str | None = None):
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY not set. Get one free at https://aistudio.google.com/app/apikey")
        self._client = genai.Client(api_key=key)

    def generate_text(self, prompt: str, max_tokens: int = 8192) -> str:
        response = self._client.models.generate_content(
            model=self.MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=max_tokens),
        )
        return response.text.strip()

    def generate_json(self, prompt: str, max_tokens: int = 8192) -> dict[str, Any]:
        full_prompt = prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown, no backticks, no explanation."
        text = self.generate_text(full_prompt, max_tokens)
        return self._parse_json(text)

    def extract_features(self, user_requirement: str, site_contents: list[str]) -> CapturedFeatures:
        sites = "\n".join(f"Site {i+1}:\n{c[:1500]}" for i, c in enumerate(site_contents))
        prompt = f"""You are a UI/UX analyst. Extract a design spec from these references.

User requirement: {user_requirement}

Reference sites:
{sites}

Return ONLY this JSON:
{{
  "color_palette": {{"primary":"#hex","secondary":"#hex","accent":"#hex","background":"#hex","text":"#hex","muted":"#hex"}},
  "font_styling": {{"heading_font":"Font Name","body_font":"Font Name","base_font_size":"16px","font_weight_heading":"700","font_weight_body":"400","heading_size_scale":"1.25"}},
  "ui_components": [{{"name":"ComponentName","description":"what it does","props":["prop1"]}}],
  "layout_style": "describe layout",
  "tone": "design tone in 3-5 words",
  "key_sections": ["Hero","Features","Pricing","CTA","Footer"],
  "pages": ["landing","about","features","pricing","contact"],
  "tailwind_config_notes": "custom theme notes"
}}"""
        raw = self.generate_json(prompt, 4096)
        return CapturedFeatures(**raw)

    def generate_site_code(self, features: CapturedFeatures, feedback: list[str], iteration: int) -> dict[str, Any]:
        fb = "\n".join(f"- {f}" for f in feedback) if feedback else "None"
        prompt = f"""You are an expert Next.js developer. Generate a complete Next.js 14 App Router site.

Tone: {features.tone}
Colors: primary={features.color_palette.primary}, accent={features.color_palette.accent}, bg={features.color_palette.background}
Fonts: heading={features.font_styling.heading_font}, body={features.font_styling.body_font}
Pages: {', '.join(features.pages)}
Sections: {', '.join(features.key_sections)}
Iteration: {iteration}
Feedback to fix: {fb}

Return ONLY this JSON (all pages complete, no truncation):
{{
  "pages": [{{"route":"/","filename":"page.tsx","title":"Home","tsx_code":"full tsx..."}}],
  "components": {{"Navbar":"full tsx...","Footer":"full tsx...","HeroSection":"full tsx..."}},
  "globals_css": "full css...",
  "layout_tsx": "full layout...",
  "tailwind_config": "full config...",
  "package_json": "full package.json...",
  "tsconfig": "full tsconfig...",
  "next_config": "full next.config.js..."
}}

Rules:
- All TSX must be valid and complete
- Use 'use client' only where needed
- Fully responsive with Tailwind
- Beautiful design matching the tone
- No placeholder comments"""
        return self.generate_json(prompt, 8192)

    def visual_review(self, routes: list[str], features: CapturedFeatures) -> ReviewResult:
        prompt = f"""You are a UI reviewer. Review a generated Next.js site.

Target design:
- Tone: {features.tone}
- Primary color: {features.color_palette.primary}
- Heading font: {features.font_styling.heading_font}
- Expected sections: {', '.join(features.key_sections)}
- Pages reviewed: {', '.join(routes)}

Score based on design spec completeness.
Return ONLY this JSON:
{{
  "overall_score": 0.8,
  "page_diffs": [{{"route":"/","score":0.8,"issues":[],"suggestions":[]}}],
  "summary": "Site looks good overall",
  "is_acceptable": true
}}"""
        raw = self.generate_json(prompt, 2048)
        return ReviewResult(**raw)

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:
        cleaned = re.sub(r"```(?:json)?\s*", "", text)
        cleaned = re.sub(r"```", "", cleaned).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise ValueError(f"Could not parse JSON: {text[:300]}")
