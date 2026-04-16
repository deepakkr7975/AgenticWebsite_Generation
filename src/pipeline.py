"""
pipeline.py — High-level pipeline API wrapping the LangGraph graph.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from src.graph import build_graph, GraphState
from src.models import PipelineResult, GeneratedSite, GeneratedPage

load_dotenv()


class WebGenPipeline:
    """
    High-level API for the WebGen agentic pipeline.

    Usage:
        pipeline = WebGenPipeline(gemini_api_key="...")
        result = pipeline.run(
            user_requirement="Build a SaaS landing page",
            reference_sites=["https://linear.app"],
            reference_images=["./ref.png"],
            max_iterations=3,
            output_dir="./output/my-site"
        )
    """

    def __init__(
        self,
        gemini_api_key: str | None = None,
        similarity_threshold: float = 0.75,
    ):
        self.api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY required. Get one free at https://aistudio.google.com/app/apikey"
            )
        self.similarity_threshold = similarity_threshold
        self._graph = build_graph(
            gemini_api_key=self.api_key,
            similarity_threshold=similarity_threshold,
        )

    def run(
        self,
        user_requirement: str,
        reference_sites: list[str] | None = None,
        reference_images: list[str] | None = None,
        max_iterations: int = 3,
        output_dir: str = "./output/site",
    ) -> PipelineResult:
        """
        Run the full agentic pipeline.

        Args:
            user_requirement: Natural language description of the desired website.
            reference_sites: List of URLs to scrape for design inspiration.
            reference_images: Paths to local image files as visual references.
            max_iterations: Maximum number of generation+review cycles.
            output_dir: Directory where the final Next.js site will be written.

        Returns:
            PipelineResult with pages, score, and output directory.
        """
        # Validate image paths
        image_paths = []
        for p in (reference_images or []):
            path = Path(p)
            if path.exists():
                image_paths.append(str(path))
            else:
                print(f"⚠️  Reference image not found, skipping: {p}")

        initial_state: GraphState = {
            "user_requirement": user_requirement,
            "reference_sites": reference_sites or [],
            "reference_image_paths": image_paths,
            "output_dir": output_dir,
            "max_iterations": max_iterations,
            "similarity_threshold": self.similarity_threshold,
            "captured_features": None,
            "iterations": [],
            "current_iteration": 0,
            "accumulated_feedback": [],
            "final_score": 0.0,
            "status": "pending",
            "error": None,
        }

        # Run the graph
        final_state = self._graph.invoke(initial_state)

        # Extract result
        if final_state["status"] == "failed":
            raise RuntimeError(f"Pipeline failed: {final_state.get('error')}")

        pages = []
        if final_state["iterations"]:
            best = max(
                final_state["iterations"],
                key=lambda r: (r.get("review") or {}).get("overall_score", 0),
            )
            site = GeneratedSite(**best["site"])
            pages = site.pages

        return PipelineResult(
            pages=pages,
            final_score=final_state["final_score"],
            iterations_used=final_state["current_iteration"],
            output_dir=str(Path(output_dir) / "final"),
            status=final_state["status"],
        )
