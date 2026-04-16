"""
feature_extraction.py — Prompt for the FeatureExtractor agent.
"""


def build_feature_extraction_prompt(
    user_requirement: str,
    reference_site_contents: list[str],
) -> str:
    sites_section = ""
    if reference_site_contents:
        sites_section = "\n\n## Reference Site Content Summaries\n"
        for i, content in enumerate(reference_site_contents, 1):
            sites_section += f"\n### Site {i}\n{content[:2000]}\n"

    return f"""You are a UI/UX Design Analyst. Your job is to analyze design references and extract a structured design specification.

## User Requirement
{user_requirement}
{sites_section}

## Reference Images
(Images are attached. Analyze them carefully for: color palette, typography, layout patterns, UI components, spacing, and overall aesthetic.)

## Your Task
Extract and return a complete design specification as JSON. Be specific and opinionated — commit to clear design decisions.

Return this exact JSON structure:
{{
  "color_palette": {{
    "primary": "#hex",
    "secondary": "#hex",
    "accent": "#hex",
    "background": "#hex",
    "text": "#hex",
    "muted": "#hex"
  }},
  "font_styling": {{
    "heading_font": "Font Name (Google Fonts)",
    "body_font": "Font Name (Google Fonts)",
    "heading_size_scale": "1.25",
    "base_font_size": "16px",
    "font_weight_heading": "700",
    "font_weight_body": "400"
  }},
  "ui_components": [
    {{
      "name": "ComponentName",
      "description": "What this component does",
      "props": ["prop1", "prop2"]
    }}
  ],
  "layout_style": "Describe the overall layout approach",
  "tone": "Design tone in 3-5 words e.g. 'dark minimal SaaS'",
  "key_sections": ["Hero", "Features", "Testimonials", "CTA", "Footer"],
  "pages": ["landing", "about", "features", "pricing", "contact"],
  "tailwind_config_notes": "Custom color/font/animation notes for tailwind config"
}}

Rules:
- Choose SPECIFIC, distinctive fonts (not Arial, Inter, or Roboto)
- Extract exact hex colors from the reference images if visible
- Include at least 5 ui_components that represent the design
- pages list should include "landing" plus 2-4 outer pages
- Be creative and specific in the tone description
"""
