"""
visual_review.py — Prompt for the VisualReviewer agent.
"""
from __future__ import annotations

from src.models import CapturedFeatures


def build_visual_review_prompt(
    features: CapturedFeatures,
    screenshot_routes: list[str],
) -> str:
    routes_list = "\n".join(f"- {r}" for r in screenshot_routes)

    return f"""You are a senior UI/UX reviewer with a sharp eye for design quality and consistency.

You are given:
1. Screenshots of a GENERATED website (first images)
2. Reference images the site was designed to match (last images)

## Target Design Spec
- Tone: {features.tone}
- Layout: {features.layout_style}
- Primary color: {features.color_palette.primary}
- Heading font: {features.font_styling.heading_font}
- Body font: {features.font_styling.body_font}
- Key sections expected: {', '.join(features.key_sections)}

## Pages Screenshotted
{routes_list}

## Your Task
Compare the generated screenshots vs the reference images. Evaluate:
1. **Color accuracy** — does the palette match?
2. **Typography** — are the right fonts used? Correct weights/sizes?
3. **Layout fidelity** — does the structure resemble the reference?
4. **Component completeness** — are all key sections present?
5. **Visual polish** — spacing, alignment, overall quality

Return this JSON:
{{
  "overall_score": 0.0,
  "page_diffs": [
    {{
      "route": "/",
      "score": 0.0,
      "issues": ["list of specific visual issues"],
      "suggestions": ["concrete code-level fix suggestions"]
    }}
  ],
  "summary": "Overall summary of what needs to change",
  "is_acceptable": false
}}

Scoring guide:
- 0.0–0.4: Major issues (wrong colors, missing sections, broken layout)
- 0.4–0.6: Moderate issues (some sections wrong, typography off)
- 0.6–0.8: Minor issues (small spacing problems, subtle color differences)
- 0.8–1.0: Acceptable (matches reference well)

Be SPECIFIC in suggestions — e.g., "Change hero background from #fff to #0f172a" not "fix colors".
The generated site is deemed acceptable (is_acceptable: true) if overall_score >= 0.75.
"""
