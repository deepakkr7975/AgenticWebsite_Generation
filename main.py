from __future__ import annotations
import os, sys, time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def main():
    import argparse
    parser = argparse.ArgumentParser(description="WebGen Agent — Agentic Next.js Generator")
    parser.add_argument("--requirement", "-r", required=True, help="What website to build")
    parser.add_argument("--reference-sites", "-s", nargs="*", default=[], help="Reference URLs")
    parser.add_argument("--reference-images", "-i", nargs="*", default=[], help="Reference image paths")
    parser.add_argument("--max-iterations", "-n", type=int, default=3)
    parser.add_argument("--output-dir", "-o", default="./output/site")
    args = parser.parse_args()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not set. Add it to your .env file.")
        print("Get a free key at: https://aistudio.google.com/app/apikey")
        sys.exit(1)

    print("\n" + "="*60)
    print("WebGen Agent — Agentic Next.js Generator")
    print("="*60)
    print(f"  Requirement  : {args.requirement}")
    print(f"  Ref sites    : {args.reference_sites}")
    print(f"  Max iters    : {args.max_iterations}")
    print(f"  Output dir   : {args.output_dir}")
    print("="*60 + "\n")

    from src.llm_client import GeminiClient
    from src.tools.scraper import SiteScraper
    from src.utils.site_writer import SiteWriter
    from src.models import GeneratedSite, GeneratedPage

    client = GeminiClient(api_key=api_key)
    scraper = SiteScraper()
    writer = SiteWriter()

    # Step 1: Scrape reference sites
    print("Step 1/4 — Scraping reference sites...")
    site_contents = [scraper.scrape(url) for url in args.reference_sites]

    # Step 2: Extract features
    print("Step 2/4 — Extracting design features with Gemini...")
    features = client.extract_features(args.requirement, site_contents)
    print(f"  Tone     : {features.tone}")
    print(f"  Colors   : {features.color_palette.primary} / {features.color_palette.accent}")
    print(f"  Fonts    : {features.font_styling.heading_font} + {features.font_styling.body_font}")
    print(f"  Pages    : {', '.join(features.pages)}")

    feedback = []
    best_site = None
    best_score = 0.0

    for i in range(1, args.max_iterations + 1):
        print(f"\nStep 3/4 — Code Generation (Iteration {i}/{args.max_iterations})...")
        raw = client.generate_site_code(features, feedback, i)

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
        print(f"  Generated {len(pages)} pages: {', '.join(p.route for p in pages)}")

        iter_dir = str(Path(args.output_dir) / f"iteration_{i}")
        writer.write(site, iter_dir)

        print(f"\nStep 4/4 — Visual Review (Iteration {i})...")
        review = client.visual_review([p.route for p in pages], features)
        print(f"  Score: {review.overall_score:.2f} | Acceptable: {review.is_acceptable}")
        print(f"  {review.summary}")

        if review.overall_score > best_score:
            best_score = review.overall_score
            best_site = site

        if review.is_acceptable:
            print(f"\nAccepted at iteration {i}!")
            break

        feedback = []
        for diff in review.page_diffs:
            feedback.extend(diff.suggestions[:3])

    # Write final
    final_dir = str(Path(args.output_dir) / "final")
    if best_site:
        writer.write(best_site, final_dir)

    print("\n" + "="*60)
    print("PIPELINE COMPLETE")
    print(f"   Final score : {best_score:.2f}")
    print(f"   Output      : {final_dir}")
    print("="*60)
    print(f"\nTo run your site:")
    print(f"  cd {final_dir}")
    print(f"  npm install && npm run dev")
    print(f"  open http://localhost:3000\n")

if __name__ == "__main__":
    main()
