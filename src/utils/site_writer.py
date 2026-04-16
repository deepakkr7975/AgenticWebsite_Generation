"""
site_writer.py — Writes generated Next.js site files to disk.
"""
from __future__ import annotations

import json
from pathlib import Path

from src.models import GeneratedSite


class SiteWriter:
    """Writes a GeneratedSite to disk as a real Next.js 14 project."""

    def write(self, site: GeneratedSite, output_dir: str) -> Path:
        """
        Write all site files to output_dir.
        Returns the output directory Path.
        """
        root = Path(output_dir)
        root.mkdir(parents=True, exist_ok=True)

        # ── Core config files ──────────────────────────
        self._write(root / "package.json", site.package_json or self._default_package_json())
        self._write(root / "tsconfig.json", site.tsconfig or self._default_tsconfig())
        self._write(root / "next.config.js", site.next_config or self._default_next_config())
        self._write(root / "tailwind.config.ts", site.tailwind_config or self._default_tailwind())
        self._write(root / "postcss.config.js", self._postcss())

        # ── App directory ──────────────────────────────
        app_dir = root / "app"
        app_dir.mkdir(exist_ok=True)

        self._write(app_dir / "globals.css", site.globals_css or self._default_globals_css())
        self._write(app_dir / "layout.tsx", site.layout_tsx or self._default_layout())

        # ── Pages ──────────────────────────────────────
        for page in site.pages:
            page_path = app_dir / page.filename
            page_path.parent.mkdir(parents=True, exist_ok=True)
            self._write(page_path, page.tsx_code)

        # ── Components ─────────────────────────────────
        components_dir = root / "components"
        components_dir.mkdir(exist_ok=True)

        for comp_name, comp_code in site.components.items():
            self._write(components_dir / f"{comp_name}.tsx", comp_code)

        # ── Public ─────────────────────────────────────
        (root / "public").mkdir(exist_ok=True)

        print(f"\n✅ Site written to: {root.resolve()}")
        self._print_tree(root)
        return root

    # ─────────────────────────────────────────────
    #  Helpers
    # ─────────────────────────────────────────────

    @staticmethod
    def _write(path: Path, content: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    @staticmethod
    def _print_tree(root: Path, prefix: str = "", max_depth: int = 3, depth: int = 0):
        if depth > max_depth:
            return
        items = sorted(root.iterdir(), key=lambda p: (p.is_file(), p.name))
        for i, item in enumerate(items):
            connector = "└── " if i == len(items) - 1 else "├── "
            print(f"{prefix}{connector}{item.name}")
            if item.is_dir() and depth < max_depth:
                extension = "    " if i == len(items) - 1 else "│   "
                SiteWriter._print_tree(item, prefix + extension, max_depth, depth + 1)

    # ─────────────────────────────────────────────
    #  Defaults (used when LLM doesn't generate them)
    # ─────────────────────────────────────────────

    @staticmethod
    def _default_package_json() -> str:
        return json.dumps({
            "name": "webgen-site",
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint"
            },
            "dependencies": {
                "next": "14.2.3",
                "react": "^18",
                "react-dom": "^18"
            },
            "devDependencies": {
                "@types/node": "^20",
                "@types/react": "^18",
                "@types/react-dom": "^18",
                "autoprefixer": "^10",
                "postcss": "^8",
                "tailwindcss": "^3",
                "typescript": "^5"
            }
        }, indent=2)

    @staticmethod
    def _default_tsconfig() -> str:
        return json.dumps({
            "compilerOptions": {
                "target": "es5",
                "lib": ["dom", "dom.iterable", "esnext"],
                "allowJs": True,
                "skipLibCheck": True,
                "strict": True,
                "noEmit": True,
                "esModuleInterop": True,
                "module": "esnext",
                "moduleResolution": "bundler",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "jsx": "preserve",
                "incremental": True,
                "plugins": [{"name": "next"}],
                "paths": {"@/*": ["./*"]}
            },
            "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
            "exclude": ["node_modules"]
        }, indent=2)

    @staticmethod
    def _default_next_config() -> str:
        return """/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: '**' }
    ]
  }
}

module.exports = nextConfig
"""

    @staticmethod
    def _default_tailwind() -> str:
        return """import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          primary: 'var(--color-primary)',
          secondary: 'var(--color-secondary)',
          accent: 'var(--color-accent)',
        }
      }
    },
  },
  plugins: [],
}
export default config
"""

    @staticmethod
    def _postcss() -> str:
        return """module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"""

    @staticmethod
    def _default_globals_css() -> str:
        return """@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --color-primary: #6366f1;
  --color-secondary: #1e1b4b;
  --color-accent: #f59e0b;
  --color-bg: #0f0f1a;
  --color-text: #f8fafc;
  --color-muted: #94a3b8;
}

* {
  box-sizing: border-box;
  padding: 0;
  margin: 0;
}

html,
body {
  max-width: 100vw;
  overflow-x: hidden;
  background-color: var(--color-bg);
  color: var(--color-text);
}

a {
  color: inherit;
  text-decoration: none;
}
"""

    @staticmethod
    def _default_layout() -> str:
        return """import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'WebGen Site',
  description: 'Generated by WebGen Agent',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
"""
