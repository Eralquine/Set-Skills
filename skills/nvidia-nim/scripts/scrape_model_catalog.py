#!/usr/bin/env python3
"""
Scrape build.nvidia.com's model catalog page with Scrapling (the
`scrapling-official` skill), capturing the SPA's internal XHR/fetch calls
instead of relying on fragile CSS selectors against rendered markup or a
scroll-and-hope approach.

Why this exists: build.nvidia.com and integrate.api.nvidia.com are both
blocked by this sandbox's network egress policy, so this could only be
written and syntax-checked here, never actually run against the live site.
Run it on a machine that CAN reach build.nvidia.com (your own machine).

Requires:
    pip install "scrapling[all]"
    scrapling install --force

Usage:
    python3 scrape_model_catalog.py [output_dir]

Output (default ./nvidia-catalog-capture/):
    page.md              - rendered page as clean markdown (always written,
                            useful even if no XHR call matches)
    xhr-index.txt         - one line per captured network call: index, status,
                            JSON-or-not, URL -- scan this first
    xhr/<i>-<url>.json    - body of every JSON XHR/fetch call, saved separately
                            so you can find which one is the model catalog API
                            (look for the biggest file, or a URL containing
                            "model"/"catalog"/"search")

Once you've identified the real catalog endpoint in xhr/, either:
  (a) paste its JSON shape back to Claude to fold into build_model_graph.py's
      category/provider graph, or
  (b) if it's simple enough, call that endpoint directly next time instead of
      re-scraping the whole page.
"""
import json
import re
import sys
from pathlib import Path

CATALOG_URL = "https://build.nvidia.com/models"


def scroll_to_load_everything(page):
    """build.nvidia.com's catalog is a large list, likely virtualized or
    paginated on scroll -- keep scrolling until page height stops growing."""
    last_height = 0
    for _ in range(40):  # generous cap; breaks out early once height stabilizes
        page.mouse.wheel(0, 2000)
        page.wait_for_timeout(400)
        height = page.evaluate("document.body.scrollHeight")
        if height == last_height:
            break
        last_height = height


def main():
    out_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "./nvidia-catalog-capture")
    (out_dir / "xhr").mkdir(parents=True, exist_ok=True)

    try:
        from scrapling.fetchers import DynamicFetcher
    except ImportError:
        print('Scrapling not installed. Run: pip install "scrapling[all]" && scrapling install --force', file=sys.stderr)
        sys.exit(1)

    print(f"Fetching {CATALOG_URL} with a stealth browser, capturing XHR/fetch calls...")
    page = DynamicFetcher.fetch(
        CATALOG_URL,
        network_idle=True,
        capture_xhr=r".*",  # broad on purpose: NVIDIA's internal API path isn't publicly documented
        page_action=scroll_to_load_everything,
        timeout=60000,
    )

    # Always write the rendered page as markdown -- a useful fallback even if
    # nothing in captured_xhr turns out to be the catalog data itself.
    (out_dir / "page.md").write_text(page.markdown(main_content_only=True), encoding="utf-8")
    print(f"Wrote {out_dir / 'page.md'} ({len(page.body)} bytes rendered HTML).")

    index_lines = []
    json_count = 0
    for i, xhr in enumerate(page.captured_xhr):
        content_type = (xhr.headers.get("content-type", "") if xhr.headers else "")
        is_json = "json" in content_type.lower()
        index_lines.append(f"[{i}] {xhr.status} {'JSON' if is_json else '    '} {xhr.url}")
        if is_json:
            safe_name = re.sub(r"[^a-zA-Z0-9]+", "_", xhr.url)[-120:]
            try:
                body = json.loads(xhr.body)
                (out_dir / "xhr" / f"{i}-{safe_name}.json").write_text(
                    json.dumps(body, indent=2, ensure_ascii=False), encoding="utf-8"
                )
                json_count += 1
            except (json.JSONDecodeError, UnicodeDecodeError):
                (out_dir / "xhr" / f"{i}-{safe_name}.raw").write_bytes(xhr.body)

    (out_dir / "xhr-index.txt").write_text("\n".join(index_lines), encoding="utf-8")
    print(f"Captured {len(page.captured_xhr)} network calls ({json_count} JSON) -> {out_dir / 'xhr'}/")
    print(f"Index: {out_dir / 'xhr-index.txt'}")
    print()
    print("Next: open xhr-index.txt, find the call that looks like the model catalog")
    print("(biggest JSON file, or a URL containing 'model'/'catalog'/'search'), then")
    print("paste its content back to fold into build_model_graph.py's graph.")


if __name__ == "__main__":
    main()
