# WebGen Agent — Agentic Website Design Generation System
An agentic pipeline that transforms reference images, reference sites, and user requirements into a deployable **Next.js (TypeScript/TSX)** website, with an iterative visual feedback loop.
---
## Architecture Overview
Reference Images ──┐
Reference Sites  ──┼──► Captured Features ──► Agentic Engine ──► Iterations (1..n)
User Requirements ─┘                                │                    │
                                                    │              View & Review
                                               Similar Site?      (Vision/Screenshot)
                                                    │                    │
                                                    ▼                    ▼
                                            Next.js Site         Feedback Loop
                                      (Landing + Outer Pages)
## Tech Stack
| Role | Technology |
|------|-----------|
| **LLM** | Google Gemini 1.5 Pro (via `google-generativeai`) |
| **Agentic Framework** | LangGraph (stateful multi-agent graph) |
| **Vision / Feedback** | Selenium + Gemini Vision (screenshot → review) |
| **Output** | Next.js 14 App Router, TypeScript (TSX) |
| **Feature Extraction** | Gemini Vision — UI components, color palette, fonts |
---
## Setup
### 1. Install Dependencies
pip install -r requirements.txt
### 2. Configure Environment
cp .env.example .env
# Fill in your GEMINI_API_KEY from https://aistudio.google.com/
### 3. Install ChromeDriver (for Selenium visual review)
# Ubuntu/Debian
sudo apt-get install chromium-driver
# macOS
brew install chromedriver
---
## Usage
### Basic Run
python main.py \
  --requirement "Build a modern SaaS landing page for a project management tool" \
  --reference-sites "https://linear.app" "https://notion.so" \
  --reference-images ./refs/design1.png ./refs/design2.png \
  --max-iterations 3 \
  --output-dir ./output/my-site
### Python API
from src.pipeline import WebGenPipeline
pipeline = WebGenPipeline(gemini_api_key="YOUR_KEY")
result = pipeline.run(
    user_requirement="A portfolio site for a product designer",
    reference_sites=["https://stripe.com"],
    reference_images=["./refs/portfolio.png"],
    max_iterations=3,
    output_dir="./output/portfolio"
)
print(f"Generated {len(result.pages)} pages")
print(f"Similarity score: {result.final_score:.2f}")
---
## Output Structure
output/my-site/
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.ts
├── app/
│   ├── layout.tsx          ← Root layout
│   ├── page.tsx            ← Landing page
│   ├── globals.css
│   ├── about/page.tsx      ← Outer page
│   ├── features/page.tsx   ← Outer page
│   └── contact/page.tsx    ← Outer page
├── components/
│   ├── ui/                 ← Reusable UI components
│   ├── Navbar.tsx
│   └── Footer.tsx
└── public/
---
## Agent Roles (LangGraph Nodes)
| Agent | Role |
|-------|------|
| `FeatureExtractor` | Analyzes reference images + sites → structured design spec |
| `CodeGenerator` | Writes Next.js TSX pages from spec + feedback |
| `VisualReviewer` | Screenshots rendered site, sends to Gemini Vision for diff |
| `FeedbackSynthesizer` | Converts visual diff into actionable code improvement instructions |
| `SimilarityJudge` | Decides if output is similar enough to stop iterating |
---
## Iteration Loop
Features ──► Generate v1 ──► Screenshot ──► Vision Review ──► Score ≥ 0.8? ──► Done
                 ▲                                   │              │
                 └───────── Feedback ────────────────┘              │
                                                               No: iterate

