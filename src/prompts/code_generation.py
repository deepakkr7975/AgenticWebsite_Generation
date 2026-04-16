"""
code_generation.py — Prompt for the CodeGenerator agent.
"""
from __future__ import annotations

import json

from src.models import CapturedFeatures


def build_code_gen_prompt(
    features: CapturedFeatures,
    feedback: list[str],
    iteration: int,
) -> str:
    feedback_section = ""
    if feedback:
        feedback_section = "\n\n## Feedback from Previous Iteration (MUST FIX)\n"
        for i, fb in enumerate(feedback, 1):
            feedback_section += f"{i}. {fb}\n"

    pages_list = "\n".join(f"- {p}" for p in features.pages)
    components_list = "\n".join(
        f"- {c.name}: {c.description}" for c in features.ui_components
    )
    sections_list = ", ".join(features.key_sections)
    css_vars = features.color_palette.to_css_vars()

    return f"""You are an expert Next.js / TypeScript developer. Generate a complete, production-quality Next.js 14 App Router website.

## Design Specification (Iteration {iteration})

**Tone**: {features.tone}
**Layout**: {features.layout_style}
**Key Sections**: {sections_list}

### Color Palette
- Primary: {features.color_palette.primary}
- Secondary: {features.color_palette.secondary}
- Accent: {features.color_palette.accent}
- Background: {features.color_palette.background}
- Text: {features.color_palette.text}
- Muted: {features.color_palette.muted}

### Typography
- Heading Font: {features.font_styling.heading_font}
- Body Font: {features.font_styling.body_font}
- Base size: {features.font_styling.base_font_size}
- Heading weight: {features.font_styling.font_weight_heading}

### Required UI Components
{components_list}

### Pages to Generate
{pages_list}

### Tailwind Notes
{features.tailwind_config_notes}
{feedback_section}

## Your Task
Generate a complete Next.js 14 App Router site with TypeScript/TSX. Return JSON with this structure:

{{
  "pages": [
    {{
      "route": "/",
      "filename": "page.tsx",
      "title": "Home",
      "tsx_code": "full TSX source code..."
    }},
    {{
      "route": "/about",
      "filename": "about/page.tsx",
      "title": "About",
      "tsx_code": "full TSX source code..."
    }}
  ],
  "components": {{
    "Navbar": "full TSX component source...",
    "Footer": "full TSX component source...",
    "HeroSection": "full TSX component source..."
  }},
  "globals_css": "full globals.css content...",
  "layout_tsx": "full app/layout.tsx content...",
  "tailwind_config": "full tailwind.config.ts content...",
  "package_json": "full package.json content...",
  "tsconfig": "full tsconfig.json content...",
  "next_config": "full next.config.js content..."
}}

## STRICT REQUIREMENTS

### Code Quality
- All TSX must be valid, complete, and compilable
- Use `"use client"` directive only where needed (interactivity)
- Every page must import and use Navbar + Footer components
- Use Next.js Link for internal navigation
- All images use next/image or plain <img> with proper alt text
- No placeholder "TODO" comments — write real implementations

### Design Quality  
- Implement the EXACT color palette using Tailwind CSS custom colors or inline styles
- Use the specified Google Fonts (import in layout.tsx head or globals.css @import)
- Every page must be visually stunning and match the "{features.tone}" aesthetic
- Include subtle animations (CSS transitions, hover effects)
- Fully responsive (mobile-first)
- Landing page MUST include all of: {sections_list}

### TypeScript
- Proper interfaces for all component props
- No `any` types
- Export default all page components

### Tailwind
- Extend tailwind.config.ts with custom colors matching the palette
- Use semantic class names

Generate ALL {len(features.pages)} pages completely. Do not truncate or skip any page.
"""
