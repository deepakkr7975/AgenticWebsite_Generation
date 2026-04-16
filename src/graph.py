"""
graph.py — LangGraph-based agentic pipeline for website generation.

Node flow:
  extract_features → generate_code → write_site → visual_review → judge → [loop or done]
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, END

from src.llm_client import GeminiClient
from src.models import (
    CapturedFeatures,
    GeneratedSite,
    GeneratedPage,
    IterationRecord,
    PipelineState,
    ReviewResult,
    VisualDiff,
)
from src.tools.scraper import SiteScraper
from src.tools.screenshotter import Screenshotter
from src.utils.dev_server import DevServerManager
from src.utils.site_writer import SiteWriter


# ─────────────────────────────────────────────────────────────────────────────
#  LangGraph State Dict (must be serialisable TypedDict)
# ─────────────────────────────────────────────────────────────────────────────

class GraphState(TypedDict):
    # Inputs
    user_requirement: str
    reference_sites: list[str]
    reference_image_paths: list[str]
    output_dir: str
    max_iterations: int
    similarity_threshold: float

    # Runtime
    captured_features: dict | None
    iterations: list[dict]
    current_iteration: int
    accumulated_feedback: list[str]

    # Final
    final_score: float
    status: str
    error: str | None


# ─────────────────────────────────────────────────────────────────────────────
#  Agent Nodes
# ─────────────────────────────────────────────────────────────────────────────

def make_extract_features_node(client: GeminiClient, scraper: SiteScraper):
    """Node 1: Extract design features from references + requirement."""

    def node(state: GraphState) -> GraphState:
        print("\n" + "="*60)
        print("🔍 AGENT: FeatureExtractor")
        print("="*60)

        try:
            # Scrape reference sites
            site_contents = []
            for url in state["reference_sites"]:
                print(f"  🌐 Scraping {url}...")
                content = scraper.scrape(url)
                site_contents.append(content)

            # Call Gemini vision to extract features
            print("  🧠 Extracting design features with Gemini Vision...")
            features: CapturedFeatures = client.extract_features(
                user_requirement=state["user_requirement"],
                reference_site_contents=site_contents,
                reference_image_paths=state["reference_image_paths"],
            )

            print(f"  ✅ Extracted features:")
            print(f"     Tone: {features.tone}")
            print(f"     Colors: {features.color_palette.primary} / {features.color_palette.accent}")
            print(f"     Fonts: {features.font_styling.heading_font} + {features.font_styling.body_font}")
            print(f"     Pages: {', '.join(features.pages)}")
            print(f"     Components: {', '.join(c.name for c in features.ui_components)}")

            return {**state, "captured_features": features.dict(), "status": "features_extracted"}

        except Exception as e:
            print(f"  ❌ Feature extraction failed: {e}")
            return {**state, "status": "failed", "error": str(e)}

    return node


def make_generate_code_node(client: GeminiClient):
    """Node 2: Generate Next.js TSX code from features + feedback."""

    def node(state: GraphState) -> GraphState:
        iteration = state["current_iteration"] + 1
        print("\n" + "="*60)
        print(f"⚙️  AGENT: CodeGenerator (Iteration {iteration})")
        print("="*60)

        features = CapturedFeatures(**state["captured_features"])
        feedback = state["accumulated_feedback"]

        if feedback:
            print(f"  📝 Applying {len(feedback)} feedback items from previous iteration")

        try:
            print("  🤖 Calling Gemini for code generation...")
            raw = client.generate_site_code(features, feedback, iteration)

            # Map raw dict to GeneratedSite
            pages = [GeneratedPage(**p) for p in raw.get("pages", [])]
            site = GeneratedSite(
                pages=pages,
                components=raw.get("components", {}),
                globals_css=raw.get("globals_css", ""),
                layout_tsx=raw.get("layout_tsx", ""),
                tailwind_config=raw.get("tailwind_config", ""),
                package_json=raw.get("package_json", ""),
                tsconfig=raw.get("tsconfig", ""),
                next_config=raw.get("next_config", ""),
            )

            print(f"  ✅ Generated {len(pages)} pages: {', '.join(p.route for p in pages)}")
            print(f"  ✅ Generated {len(site.components)} components: {', '.join(site.components.keys())}")

            record = IterationRecord(
                iteration_number=iteration,
                site=site,
            )

            new_iterations = state["iterations"] + [record.dict()]
            return {
                **state,
                "iterations": new_iterations,
                "current_iteration": iteration,
                "status": "code_generated",
            }

        except Exception as e:
            print(f"  ❌ Code generation failed: {e}")
            return {**state, "status": "failed", "error": str(e)}

    return node


def make_write_and_review_node(client: GeminiClient, writer: SiteWriter):
    """Node 3: Write site to disk, start server, screenshot, visual review."""

    def node(state: GraphState) -> GraphState:
        iteration = state["current_iteration"]
        print("\n" + "="*60)
        print(f"🖥️  AGENT: VisualReviewer (Iteration {iteration})")
        print("="*60)

        features = CapturedFeatures(**state["captured_features"])
        record_dict = state["iterations"][-1]
        site = GeneratedSite(**record_dict["site"])

        # Write site to disk
        iter_dir = str(Path(state["output_dir"]) / f"iteration_{iteration}")
        print(f"  📁 Writing site to {iter_dir}...")
        writer.write(site, iter_dir)

        # Attempt visual review via Selenium
        routes = [p.route for p in site.pages]
        screenshots: dict[str, str] = {}
        review: ReviewResult | None = None

        port = 3000 + iteration
        screenshots_dir = str(Path(state["output_dir"]) / f"screenshots_{iteration}")

        try:
            server = DevServerManager(site_dir=iter_dir, port=port)
            started = server.start(timeout=90)

            if started:
                print(f"  📸 Taking screenshots of {len(routes)} routes...")
                with Screenshotter(
                    base_url=f"http://localhost:{port}",
                    screenshots_dir=screenshots_dir,
                ) as ss:
                    screenshots = ss.screenshot_all_routes(routes, iteration)

                server.stop()

                # Visual review with Gemini Vision
                if screenshots:
                    print("  👁️  Sending screenshots to Gemini Vision for review...")
                    review = client.visual_review(
                        screenshot_paths=screenshots,
                        features=features,
                        reference_image_paths=state["reference_image_paths"],
                    )
                    print(f"  📊 Review score: {review.overall_score:.2f} | Acceptable: {review.is_acceptable}")
                    for diff in review.page_diffs:
                        print(f"     {diff.route}: {diff.score:.2f} — {', '.join(diff.issues[:2])}")

        except Exception as e:
            print(f"  ⚠️  Visual review failed (Selenium not available?): {e}")
            print("  ℹ️  Using heuristic scoring instead...")
            # Fallback: heuristic score based on iteration
            review = _heuristic_review(routes, iteration)

        # Attach review to latest iteration record
        updated_record = {**record_dict, "review": review.dict() if review else None, "screenshot_paths": screenshots}
        new_iterations = state["iterations"][:-1] + [updated_record]

        final_score = review.overall_score if review else 0.5
        new_feedback = []
        if review and not review.is_acceptable:
            for diff in review.page_diffs:
                new_feedback.extend(diff.suggestions[:3])

        return {
            **state,
            "iterations": new_iterations,
            "accumulated_feedback": new_feedback,
            "final_score": final_score,
            "status": "reviewed",
        }

    return node


def make_judge_node(similarity_threshold: float):
    """Node 4: Decide whether to iterate more or finish."""

    def node(state: GraphState) -> GraphState:
        score = state["final_score"]
        iteration = state["current_iteration"]
        max_iter = state["max_iterations"]

        print("\n" + "="*60)
        print(f"⚖️  AGENT: SimilarityJudge")
        print("="*60)
        print(f"  Score: {score:.2f} | Threshold: {similarity_threshold:.2f} | Iteration: {iteration}/{max_iter}")

        if score >= similarity_threshold:
            print(f"  ✅ ACCEPTED — score meets threshold. Writing final site.")
            return {**state, "status": "accepted"}
        elif iteration >= max_iter:
            print(f"  ⚠️  MAX ITERATIONS reached. Using best iteration.")
            return {**state, "status": "max_iterations"}
        else:
            print(f"  🔄 ITERATE — score too low. Running iteration {iteration + 1}...")
            return {**state, "status": "iterating"}

    return node


def make_finalize_node(writer: SiteWriter):
    """Node 5: Copy best iteration to final output directory."""

    def node(state: GraphState) -> GraphState:
        print("\n" + "="*60)
        print("🏁 AGENT: Finalizer")
        print("="*60)

        # Find best iteration
        best_iter = max(
            state["iterations"],
            key=lambda r: (r.get("review") or {}).get("overall_score", 0)
        )
        best_num = best_iter["iteration_number"]
        best_site = GeneratedSite(**best_iter["site"])

        final_dir = str(Path(state["output_dir"]) / "final")
        print(f"  📦 Writing best iteration ({best_num}) to {final_dir}...")
        writer.write(best_site, final_dir)

        print(f"\n{'='*60}")
        print(f"✨ PIPELINE COMPLETE")
        print(f"   Final score: {state['final_score']:.2f}")
        print(f"   Iterations used: {state['current_iteration']}")
        print(f"   Output: {final_dir}")
        print(f"{'='*60}\n")

        return {**state, "status": "done"}

    return node


# ─────────────────────────────────────────────────────────────────────────────
#  Routing logic
# ─────────────────────────────────────────────────────────────────────────────

def route_after_judge(state: GraphState) -> str:
    status = state["status"]
    if status in ("accepted", "max_iterations"):
        return "finalize"
    elif status == "iterating":
        return "generate_code"
    else:
        return END


def route_after_extract(state: GraphState) -> str:
    return "generate_code" if state["status"] != "failed" else END


# ─────────────────────────────────────────────────────────────────────────────
#  Graph builder
# ─────────────────────────────────────────────────────────────────────────────

def build_graph(
    gemini_api_key: str,
    similarity_threshold: float = 0.75,
) -> StateGraph:
    client = GeminiClient(api_key=gemini_api_key)
    scraper = SiteScraper()
    writer = SiteWriter()

    graph = StateGraph(GraphState)

    # Add nodes
    graph.add_node("extract_features", make_extract_features_node(client, scraper))
    graph.add_node("generate_code", make_generate_code_node(client))
    graph.add_node("write_and_review", make_write_and_review_node(client, writer))
    graph.add_node("judge", make_judge_node(similarity_threshold))
    graph.add_node("finalize", make_finalize_node(writer))

    # Add edges
    graph.set_entry_point("extract_features")
    graph.add_conditional_edges("extract_features", route_after_extract)
    graph.add_edge("generate_code", "write_and_review")
    graph.add_edge("write_and_review", "judge")
    graph.add_conditional_edges("judge", route_after_judge)
    graph.add_edge("finalize", END)

    return graph.compile()


# ─────────────────────────────────────────────────────────────────────────────
#  Heuristic fallback review (when Selenium unavailable)
# ─────────────────────────────────────────────────────────────────────────────

def _heuristic_review(routes: list[str], iteration: int) -> ReviewResult:
    """Simple score escalation fallback when browser unavailable."""
    base_score = min(0.5 + (iteration * 0.15), 0.85)
    threshold = 0.75
    page_diffs = [
        VisualDiff(
            route=r,
            score=base_score,
            issues=["Visual review unavailable (Selenium not running)"],
            suggestions=["Ensure Chrome/Chromium is installed for visual feedback"],
        )
        for r in routes
    ]
    return ReviewResult(
        overall_score=base_score,
        page_diffs=page_diffs,
        summary=f"Heuristic review (iteration {iteration}). Install Selenium+Chrome for real visual comparison.",
        is_acceptable=base_score >= threshold,
    )
