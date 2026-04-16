"""
models.py — Pydantic models for the WebGen Agent pipeline state.
"""
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────
#  Design Feature Models
# ─────────────────────────────────────────────

class ColorPalette(BaseModel):
    primary: str = Field(..., description="Primary brand color (hex)")
    secondary: str = Field(..., description="Secondary color (hex)")
    accent: str = Field(..., description="Accent / CTA color (hex)")
    background: str = Field(..., description="Background color (hex)")
    text: str = Field(..., description="Main text color (hex)")
    muted: str = Field(..., description="Muted / subtle text color (hex)")

    def to_css_vars(self) -> str:
        return f"""
  --color-primary: {self.primary};
  --color-secondary: {self.secondary};
  --color-accent: {self.accent};
  --color-bg: {self.background};
  --color-text: {self.text};
  --color-muted: {self.muted};"""


class FontStyling(BaseModel):
    heading_font: str = Field(..., description="Google Font name for headings")
    body_font: str = Field(..., description="Google Font name for body text")
    heading_size_scale: str = Field("1.25", description="Modular scale for headings")
    base_font_size: str = Field("16px", description="Base font size")
    font_weight_heading: str = Field("700", description="Heading font weight")
    font_weight_body: str = Field("400", description="Body font weight")


class UIComponent(BaseModel):
    name: str = Field(..., description="Component name e.g. 'HeroSection'")
    description: str = Field(..., description="What this component does")
    props: list[str] = Field(default_factory=list, description="Key props/data this component needs")


class CapturedFeatures(BaseModel):
    """Distilled design spec extracted from references + requirements."""
    color_palette: ColorPalette
    font_styling: FontStyling
    ui_components: list[UIComponent]
    layout_style: str = Field(..., description="Overall layout description")
    tone: str = Field(..., description="Design tone e.g. 'minimal dark SaaS'")
    key_sections: list[str] = Field(..., description="Page sections: Hero, Features, Pricing, etc.")
    pages: list[str] = Field(..., description="List of pages: landing, about, features, etc.")
    tailwind_config_notes: str = Field("", description="Custom Tailwind theme notes")


# ─────────────────────────────────────────────
#  Site Generation Models
# ─────────────────────────────────────────────

class GeneratedPage(BaseModel):
    route: str = Field(..., description="Route path e.g. '/', '/about', '/features'")
    filename: str = Field(..., description="File path relative to app/ dir")
    tsx_code: str = Field(..., description="Full TSX source code for the page")
    title: str = Field(..., description="Page title")


class GeneratedSite(BaseModel):
    pages: list[GeneratedPage]
    components: dict[str, str] = Field(default_factory=dict, description="component name -> TSX code")
    globals_css: str = Field("", description="globals.css content")
    layout_tsx: str = Field("", description="app/layout.tsx content")
    tailwind_config: str = Field("", description="tailwind.config.ts content")
    package_json: str = Field("", description="package.json content")
    tsconfig: str = Field("", description="tsconfig.json content")
    next_config: str = Field("", description="next.config.js content")


# ─────────────────────────────────────────────
#  Visual Review Models
# ─────────────────────────────────────────────

class VisualDiff(BaseModel):
    route: str
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score 0-1")
    issues: list[str] = Field(default_factory=list, description="List of visual issues found")
    suggestions: list[str] = Field(default_factory=list, description="Concrete improvement suggestions")


class ReviewResult(BaseModel):
    overall_score: float = Field(..., ge=0.0, le=1.0)
    page_diffs: list[VisualDiff]
    summary: str
    is_acceptable: bool = Field(..., description="True if score meets threshold")


# ─────────────────────────────────────────────
#  Pipeline State (LangGraph State)
# ─────────────────────────────────────────────

class IterationRecord(BaseModel):
    iteration_number: int
    site: GeneratedSite
    review: ReviewResult | None = None
    screenshot_paths: dict[str, str] = Field(default_factory=dict)


class PipelineState(BaseModel):
    # Inputs
    user_requirement: str
    reference_sites: list[str] = Field(default_factory=list)
    reference_image_paths: list[str] = Field(default_factory=list)
    output_dir: str = "output/site"
    max_iterations: int = 3
    similarity_threshold: float = 0.75

    # Extracted features
    captured_features: CapturedFeatures | None = None

    # Generation history
    iterations: list[IterationRecord] = Field(default_factory=list)
    current_iteration: int = 0

    # Feedback for next iteration
    accumulated_feedback: list[str] = Field(default_factory=list)

    # Final
    final_site: GeneratedSite | None = None
    final_score: float = 0.0
    status: str = "pending"  # pending | iterating | done | failed
    error: str | None = None

    class Config:
        arbitrary_types_allowed = True


class PipelineResult(BaseModel):
    pages: list[GeneratedPage]
    final_score: float
    iterations_used: int
    output_dir: str
    status: str
