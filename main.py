"""
CLI entry point for the research assistant.

Usage:
    python main.py --topic "Your research topic" --blogs "https://blog1.com,https://blog2.com"
"""

from __future__ import annotations

import argparse
import os
import sys

from src.graph import run_research


def main():
    parser = argparse.ArgumentParser(
        description="🔬 Agentic Research Assistant — Generate research reports on any topic",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  python main.py --topic "Transformer architectures"\n'
            '  python main.py --topic "LLM Agents" --blogs "https://lilianweng.github.io/posts/2023-06-23-agent/"\n'
            '  python main.py --topic "RAG techniques" --output my_report.md\n'
        ),
    )
    parser.add_argument(
        "--topic", "-t",
        required=True,
        help="The research topic to investigate",
    )
    parser.add_argument(
        "--blogs", "-b",
        default="",
        help="Comma-separated list of blog/article URLs to include in research",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path for the report (default: output/report.md)",
    )

    args = parser.parse_args()

    # Parse blog URLs
    blog_urls = [u.strip() for u in args.blogs.split(",") if u.strip()]

    print("=" * 60)
    print("🔬 AGENTIC RESEARCH ASSISTANT")
    print("=" * 60)
    print(f"📌 Topic:  {args.topic}")
    if blog_urls:
        print(f"📄 Blogs:  {len(blog_urls)} URL(s)")
        for url in blog_urls:
            print(f"           • {url}")
    print("=" * 60)
    print()

    # Run the research pipeline
    print("🚀 Starting research pipeline...\n")

    try:
        final_state = run_research(args.topic, blog_urls)
    except Exception as e:
        print(f"\n❌ Research failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Print progress messages
    for msg in final_state.get("messages", []):
        print(f"  {msg}")

    # Print errors if any
    errors = final_state.get("errors", [])
    if errors:
        print(f"\n⚠️  {len(errors)} error(s) encountered:")
        for err in errors:
            print(f"  • {err}")

    # Get the report
    report = final_state.get("report", "")
    if not report:
        print("\n❌ No report was generated.", file=sys.stderr)
        sys.exit(1)

    # Save to file
    output_path = args.output or os.path.join("output", "report.md")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n✅ Report saved to: {output_path}")
    print(f"   ({len(report)} characters, {len(report.split())} words)")
    print()

    # Also print to stdout
    print("=" * 60)
    print("📄 RESEARCH REPORT")
    print("=" * 60)
    print(report)


if __name__ == "__main__":
    main()
