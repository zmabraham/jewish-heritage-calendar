#!/usr/bin/env python3
"""
Jewish Heritage Calendar — Static Site Generator
Generates HTML pages for all 365 communities and 12 regions from markdown content.

Usage:
    python generate.py                  # Generate all pages
    python generate.py --communities    # Generate community pages only
    python generate.py --regions        # Generate region pages only
    python generate.py --check          # Check for missing content files

Content directory structure:
    content/communities/<id>.md         # One file per community
    content/regions/<id>.md             # One file per region
"""

import json
import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CONTENT_DIR = BASE_DIR / "content"
COMMUNITY_TEMPLATE = BASE_DIR / "community" / "template.html"
REGION_TEMPLATE = BASE_DIR / "region" / "template.html"
COMMUNITY_OUT_DIR = BASE_DIR / "community"
REGION_OUT_DIR = BASE_DIR / "region"


# ─── Markdown → HTML ──────────────────────────────────────────────────────────

def markdown_to_html(text: str) -> str:
    """
    Convert a subset of Markdown to HTML.
    Handles: headings (##, ###), bold, italic, unordered lists,
    ordered lists, horizontal rules, and paragraphs.
    """
    if not text:
        return ""

    lines = text.split("\n")
    html_parts = []
    in_ul = False
    in_ol = False
    paragraph_buffer = []

    def flush_paragraph():
        nonlocal paragraph_buffer
        if paragraph_buffer:
            content = " ".join(paragraph_buffer).strip()
            if content:
                html_parts.append(f"<p>{inline_markdown(content)}</p>")
            paragraph_buffer = []

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            html_parts.append("</ul>")
            in_ul = False
        if in_ol:
            html_parts.append("</ol>")
            in_ol = False

    for line in lines:
        # Heading 2
        if line.startswith("## "):
            flush_paragraph()
            close_lists()
            content = line[3:].strip()
            html_parts.append(f"<h2>{inline_markdown(content)}</h2>")

        # Heading 3
        elif line.startswith("### "):
            flush_paragraph()
            close_lists()
            content = line[4:].strip()
            html_parts.append(f"<h3>{inline_markdown(content)}</h3>")

        # Heading 4
        elif line.startswith("#### "):
            flush_paragraph()
            close_lists()
            content = line[5:].strip()
            html_parts.append(f"<h4>{inline_markdown(content)}</h4>")

        # Heading 1
        elif line.startswith("# "):
            flush_paragraph()
            close_lists()
            content = line[2:].strip()
            html_parts.append(f"<h1>{inline_markdown(content)}</h1>")

        # Unordered list item
        elif re.match(r"^[-*+] ", line):
            flush_paragraph()
            if not in_ul:
                close_lists()
                html_parts.append("<ul>")
                in_ul = True
            content = line[2:].strip()
            html_parts.append(f"  <li>{inline_markdown(content)}</li>")

        # Ordered list item
        elif re.match(r"^\d+\. ", line):
            flush_paragraph()
            if not in_ol:
                close_lists()
                html_parts.append("<ol>")
                in_ol = True
            content = re.sub(r"^\d+\. ", "", line).strip()
            html_parts.append(f"  <li>{inline_markdown(content)}</li>")

        # Horizontal rule
        elif re.match(r"^[-*_]{3,}$", line.strip()):
            flush_paragraph()
            close_lists()
            html_parts.append("<hr>")

        # Blank line — paragraph break
        elif line.strip() == "":
            flush_paragraph()
            close_lists()

        # Regular line — accumulate into paragraph
        else:
            close_lists()
            paragraph_buffer.append(line.strip())

    flush_paragraph()
    close_lists()

    return "\n".join(html_parts)


def inline_markdown(text: str) -> str:
    """Apply inline markdown: **bold**, *italic*, `code`, [link](url)."""
    # Links: [text](url)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    # Bold: **text** or __text__
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)
    # Italic: *text* or _text_
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"_(.+?)_", r"<em>\1</em>", text)
    # Code: `text`
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text


# ─── Frontmatter Parsing ──────────────────────────────────────────────────────

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """
    Parse YAML-style frontmatter from a markdown file.
    Returns (metadata_dict, body_text).

    Frontmatter format:
        ---
        key: value
        list_key:
          - item1
          - item2
        ---
    """
    if not content.startswith("---"):
        return {}, content

    end = content.find("\n---", 3)
    if end == -1:
        return {}, content

    frontmatter_text = content[3:end].strip()
    body = content[end + 4:].strip()

    metadata = {}
    current_key = None
    current_list = None

    for line in frontmatter_text.split("\n"):
        # List item under a key
        if line.startswith("  - ") or line.startswith("- "):
            item = line.lstrip("- ").strip()
            if current_list is not None:
                current_list.append(item)
            continue

        # Key: value pair
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()

            # If value is empty, this is a list key
            if not value:
                current_list = []
                metadata[key] = current_list
                current_key = key
            else:
                current_key = key
                current_list = None
                # Remove surrounding quotes
                value = value.strip('"\'')
                metadata[key] = value

    return metadata, body


# ─── Figures HTML ─────────────────────────────────────────────────────────────

def build_figures_html(figures: list, region_color: str) -> str:
    """Build HTML for the notable figures grid from a list of figure dicts."""
    if not figures:
        return ""
    cards = []
    for fig in figures:
        name = fig.get("name", "")
        dates = fig.get("dates", "")
        description = fig.get("description", "")
        cards.append(f"""    <div class="figure-card" style="border-left-color: {region_color}">
      <div class="figure-name">{name}</div>
      <div class="figure-dates">{dates}</div>
      <div class="figure-description">{description}</div>
    </div>""")
    return "\n".join(cards)


# ─── Timeline HTML ────────────────────────────────────────────────────────────

def build_timeline_html(periods: list) -> str:
    """Build HTML timeline items from a list of {period, description} dicts."""
    if not periods:
        return ""
    items = []
    for p in periods:
        period = p.get("period", "")
        desc = p.get("description", "")
        items.append(f"""    <div class="timeline-item">
      <div class="timeline-period">{period}</div>
      <div class="timeline-description">{desc}</div>
    </div>""")
    return "\n".join(items)


# ─── Key Facts HTML ───────────────────────────────────────────────────────────

def build_key_facts_html(facts: list) -> str:
    """Build HTML key facts grid from a list of strings."""
    if not facts:
        return ""
    cards = []
    for fact in facts:
        cards.append(f"""    <div class="fact-card">
      <p>{fact}</p>
    </div>""")
    return "\n".join(cards)


# ─── Template Rendering ───────────────────────────────────────────────────────

def render_template(template_html: str, replacements: dict) -> str:
    """Replace all {{KEY}} placeholders in template_html with values from replacements."""
    result = template_html
    for key, value in replacements.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result


# ─── Coming Soon Page ─────────────────────────────────────────────────────────

COMING_SOON_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — Jewish Heritage Calendar</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Source+Serif+4:wght@300;400;600&display=swap" rel="stylesheet">
<style>
  body {{ font-family:'Source Serif 4',Georgia,serif; background:#fdf6e3; color:#2c1810; margin:0; }}
  nav {{ position:sticky;top:0;background:white;border-bottom:2px solid #e8d5a3;padding:1rem 2rem;display:flex;justify-content:space-between;align-items:center;z-index:1000;box-shadow:0 2px 8px rgba(0,0,0,0.08); }}
  .nav-logo {{ font-family:'Playfair Display',serif;font-size:1.4rem;font-weight:700;color:#1a3a5c;display:flex;align-items:center;gap:0.5rem; }}
  .nav-links {{ display:flex;gap:2rem; }}
  .nav-links a {{ color:#2c1810;font-weight:600;font-size:0.95rem;text-decoration:none; }}
  .container {{ max-width:700px;margin:5rem auto;padding:0 2rem;text-align:center; }}
  h1 {{ font-family:'Playfair Display',serif;font-size:2.5rem;color:#1a3a5c;margin-bottom:1rem; }}
  p {{ color:#6b5d4f;font-size:1.1rem;margin-bottom:1.5rem; }}
  .badge {{ display:inline-block;background:{color};color:white;padding:0.5rem 1.5rem;border-radius:25px;font-weight:600;font-size:0.9rem;margin-bottom:2rem; }}
  .back-link {{ display:inline-block;background:#1a3a5c;color:#e8d5a3;padding:0.9rem 2rem;border-radius:5px;font-weight:600;text-decoration:none; }}
  footer {{ background:#1a3a5c;color:#e8d5a3;padding:2rem;text-align:center;margin-top:5rem; }}
</style>
</head>
<body>
  <nav>
    <div class="nav-logo"><span>✡</span><span>Jewish Heritage Calendar</span></div>
    <div class="nav-links">
      <a href="../index.html">Today</a>
      <a href="../calendar.html">Calendar</a>
      <a href="../regions.html">Regions</a>
    </div>
  </nav>
  <div class="container">
    <div class="badge">Heritage Day {day_of_year} of 365</div>
    <h1>{name}</h1>
    <p><em>{country}</em></p>
    <p>The full heritage story for this community is being written. Check back soon — each of the 365 communities will receive a complete historical profile.</p>
    <a href="../index.html" class="back-link">← Return to Today's Heritage Day</a>
  </div>
  <footer><p>Celebrating 365 Jewish Communities Worldwide</p></footer>
</body>
</html>
"""


# ─── Community Page Generation ────────────────────────────────────────────────

def _build_maps_url(community: dict) -> str:
    """Build a Google Maps search URL for the community."""
    name = community.get("name", "").strip()
    country = community.get("country", "").strip()
    # Normalise Israel
    if country in ("Israel/Palestine", "Palestine"):
        country = "Israel"

    # Use coordinates if available, otherwise name+country
    coords = community.get("coordinates")
    if coords and len(coords) == 2:
        lat, lng = coords
        return f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"

    query = f"{name} {country}".replace(" ", "+")
    return f"https://www.google.com/maps/search/?api=1&query={query}"


def generate_community_page(community: dict, regions: list, template_html: str,
                             all_communities: list) -> str:
    """Generate a complete community HTML page from data and optional markdown content."""

    community_id = community.get("id", "unknown")
    content_file = CONTENT_DIR / "communities" / f"{community_id}.md"

    # Find region
    region = next((r for r in regions if r["id"] == community.get("regionId")), None)
    if not region:
        # Try matching by month
        region = next((r for r in regions if r["month"] == community.get("month")), None)
    if not region:
        region = regions[0]  # fallback

    region_color = region.get("color", "#1a3a5c")

    # Find prev/next communities by dayOfYear
    day = community.get("dayOfYear", 1)
    sorted_communities = sorted(all_communities, key=lambda c: c.get("dayOfYear", 0))
    total = len(sorted_communities)
    current_idx = next((i for i, c in enumerate(sorted_communities)
                        if c.get("id") == community_id), 0)
    prev_community = sorted_communities[(current_idx - 1) % total]
    next_community = sorted_communities[(current_idx + 1) % total]

    # Calculate calendar date for this day
    year = datetime.now().year
    try:
        from datetime import timedelta
        cal_dt = datetime(year, 1, 1) + timedelta(days=day - 1)
        cal_date = cal_dt.strftime("%B %-d")          # "May 5"
        cal_month = cal_dt.strftime("%B")             # "May"
        cal_day = cal_dt.strftime("%-d")              # "5"
        cal_date_full = cal_dt.strftime("%B %-d, %Y") # "May 5, 2026"
    except Exception:
        cal_date = f"Day {day}"
        cal_month = ""
        cal_day = str(day)
        cal_date_full = f"Day {day}, {year}"

    # Coming soon page if no content file
    if not content_file.exists():
        return COMING_SOON_TEMPLATE.format(
            name=community.get("name", "Heritage Community"),
            day_of_year=day,
            country=community.get("country", ""),
            color=region_color
        )

    # Parse content file
    with open(content_file, "r", encoding="utf-8") as f:
        raw = f.read()

    meta, body = parse_frontmatter(raw)

    # Split body into named sections using ## headings
    sections = {}
    current_section = "overview"
    current_lines = []

    for line in body.split("\n"):
        m = re.match(r"^## (.+)$", line)
        if m:
            sections[current_section] = "\n".join(current_lines).strip()
            heading = m.group(1).lower().replace(" ", "-").replace("&", "and")
            heading = re.sub(r"[^a-z0-9-]", "", heading)
            current_section = heading
            current_lines = []
        else:
            current_lines.append(line)
    sections[current_section] = "\n".join(current_lines).strip()

    def get_section(key: str) -> str:
        return markdown_to_html(sections.get(key, ""))

    # Build figures HTML
    figures = meta.get("figures", [])
    figures_html = ""
    figures_intro = ""
    if isinstance(figures, list) and figures:
        # If figures is a list of dicts (parsed from frontmatter)
        figures_intro = "<p>This community produced figures of lasting significance to Jewish history.</p>"
        fig_list = []
        for fig in figures:
            if isinstance(fig, dict):
                fig_list.append(fig)
            elif isinstance(fig, str):
                # Try to parse "Name (dates) — description" format
                m = re.match(r"^(.+?)\s*\(([^)]+)\)\s*—?\s*(.*)$", fig)
                if m:
                    fig_list.append({"name": m.group(1), "dates": m.group(2), "description": m.group(3)})
                else:
                    fig_list.append({"name": fig, "dates": "", "description": ""})
        figures_html = build_figures_html(fig_list, region_color)

    # Normalise country: never show "Israel/Palestine" or "Palestine" — always "Israel"
    def normalise_country(raw: str) -> str:
        raw = raw.strip()
        if raw in ("Israel/Palestine", "Palestine"):
            return "Israel"
        return raw

    # Build replacements dict
    replacements = {
        "COMMUNITY_NAME": community.get("name", "Heritage Community"),
        "REGION_NAME": region.get("name", ""),
        "REGION_ID": region.get("id", ""),
        "REGION_COLOR": region_color,
        "COUNTRY": normalise_country(community.get("country", "")),
        "CALENDAR_DATE": cal_date,
        "CALENDAR_DATE_FULL": cal_date_full,
        "CALENDAR_MONTH": cal_month,
        "CALENDAR_DAY": cal_day,
        "CALENDAR_YEAR": str(year),
        "DAY_OF_YEAR": day,  # kept for backward-compat but not shown in template
        "FOUNDED": meta.get("founded", community.get("founded", "Ancient")),
        "PEAK_POPULATION": meta.get("peak_population", community.get("peakPopulation", "Unknown")),
        "LANGUAGES": meta.get("languages", community.get("languages", "Hebrew, Aramaic, local vernacular")),
        "STATUS": meta.get("status", community.get("status", "Historical")),
        "YEAR": year,
        "GOOGLE_MAPS_URL": _build_maps_url(community),
        "PREV_COMMUNITY_ID": prev_community.get("id", ""),
        "PREV_COMMUNITY_NAME": prev_community.get("name", "Previous"),
        "NEXT_COMMUNITY_ID": next_community.get("id", ""),
        "NEXT_COMMUNITY_NAME": next_community.get("name", "Next"),
        "OVERVIEW_CONTENT": get_section("overview"),
        "ORIGINS_CONTENT": get_section("historical-origins"),
        "GOLDEN_AGE_CONTENT": get_section("golden-age"),
        "FIGURES_INTRO": figures_intro,
        "FIGURES_HTML": figures_html,
        "INSTITUTIONS_CONTENT": get_section("institutions-sacred-spaces"),
        "CULTURAL_CONTENT": get_section("cultural-life"),
        "DECLINE_CONTENT": get_section("decline-and-transformation"),
        "LEGACY_CONTENT": get_section("legacy-and-diaspora"),
    }

    return render_template(template_html, replacements)


# ─── Region Page Generation ───────────────────────────────────────────────────

def generate_region_page(region: dict, template_html: str, communities: list) -> str:
    """Generate a complete region HTML page."""

    region_id = region.get("id", "")
    content_file = CONTENT_DIR / "regions" / f"{region_id}.md"

    region_color = region.get("color", "#1a3a5c")
    year = datetime.now().year

    # Parse content file if it exists
    historical_arc = ""
    timeline_html = ""
    cultural_content = ""
    key_facts_html = build_key_facts_html(region.get("keyFacts", []))

    if content_file.exists():
        with open(content_file, "r", encoding="utf-8") as f:
            raw = f.read()

        meta, body = parse_frontmatter(raw)

        sections = {}
        current_section = "overview"
        current_lines = []

        for line in body.split("\n"):
            m = re.match(r"^## (.+)$", line)
            if m:
                sections[current_section] = "\n".join(current_lines).strip()
                heading = m.group(1).lower().replace(" ", "-").replace("&", "and")
                heading = re.sub(r"[^a-z0-9-]", "", heading)
                current_section = heading
                current_lines = []
            else:
                current_lines.append(line)
        sections[current_section] = "\n".join(current_lines).strip()

        historical_arc = markdown_to_html(sections.get("overview", sections.get("historical-arc", "")))
        cultural_content = markdown_to_html(sections.get("cultural-heritage", sections.get("cultural-life", "")))

        # Build timeline from metadata
        timeline_periods = meta.get("timeline", [])
        if timeline_periods:
            timeline_items = []
            for item in timeline_periods:
                if isinstance(item, str):
                    # "Period: description" format
                    parts = item.split(":", 1)
                    if len(parts) == 2:
                        timeline_items.append({"period": parts[0].strip(), "description": parts[1].strip()})
                elif isinstance(item, dict):
                    timeline_items.append(item)
            timeline_html = build_timeline_html(timeline_items)

        # Override key facts from content if provided
        facts_from_meta = meta.get("key_facts", [])
        if facts_from_meta:
            key_facts_html = build_key_facts_html(facts_from_meta)

    # If no timeline built, use the region's historical periods
    if not timeline_html:
        periods = region.get("historicalPeriods", [])
        timeline_items = [{"period": p, "description": ""} for p in periods]
        timeline_html = build_timeline_html(timeline_items)

    # Default content if nothing was loaded
    if not historical_arc:
        historical_arc = f"<p>{region.get('heroDescription', '')}</p>"

    if not cultural_content:
        cultural_content = "<p>This region's cultural heritage spans music, literature, religious scholarship, cuisine, and distinctive liturgical traditions. Full cultural heritage content will be added as content files are created.</p>"

    replacements = {
        "REGION_NAME": region.get("name", ""),
        "REGION_ID": region_id,
        "REGION_COLOR": region_color,
        "MONTH_NAME": region.get("monthName", ""),
        "REGION_MONTH": region.get("month", 1),
        "TAGLINE": region.get("tagline", ""),
        "HERO_DESCRIPTION": region.get("heroDescription", ""),
        "COMMUNITY_COUNT": region.get("communities", 0),
        "HISTORICAL_ARC_CONTENT": historical_arc,
        "TIMELINE_HTML": timeline_html,
        "KEY_FACTS_HTML": key_facts_html,
        "CULTURAL_CONTENT": cultural_content,
        "YEAR": year,
    }

    return render_template(template_html, replacements)


# ─── Main ─────────────────────────────────────────────────────────────────────

def load_json(path: Path) -> list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_dirs():
    COMMUNITY_OUT_DIR.mkdir(exist_ok=True)
    REGION_OUT_DIR.mkdir(exist_ok=True)
    (CONTENT_DIR / "communities").mkdir(parents=True, exist_ok=True)
    (CONTENT_DIR / "regions").mkdir(parents=True, exist_ok=True)


def generate_communities(communities, regions, template_html, verbose=True):
    total = len(communities)
    generated = 0
    skipped = 0

    for i, community in enumerate(sorted(communities, key=lambda c: c.get("dayOfYear", 0)), 1):
        community_id = community.get("id", f"community-{i}")
        out_path = COMMUNITY_OUT_DIR / f"{community_id}.html"

        try:
            html = generate_community_page(community, regions, template_html, communities)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html)
            if verbose:
                print(f"  Generated {i}/{total}: {community_id}.html")
            generated += 1
        except Exception as e:
            print(f"  ERROR generating {community_id}: {e}", file=sys.stderr)
            skipped += 1

    return generated, skipped


def generate_regions(regions, template_html, communities, verbose=True):
    total = len(regions)
    generated = 0

    for i, region in enumerate(regions, 1):
        region_id = region.get("id", f"region-{i}")
        out_path = REGION_OUT_DIR / f"{region_id}.html"

        try:
            html = generate_region_page(region, template_html, communities)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html)
            if verbose:
                print(f"  Generated {i}/{total}: {region_id}.html")
            generated += 1
        except Exception as e:
            print(f"  ERROR generating {region_id}: {e}", file=sys.stderr)

    return generated


def check_missing(communities):
    """Report which communities are missing content files."""
    missing = []
    for c in communities:
        cid = c.get("id", "")
        if not (CONTENT_DIR / "communities" / f"{cid}.md").exists():
            missing.append(cid)
    return missing


def main():
    parser = argparse.ArgumentParser(description="Jewish Heritage Calendar — Static Site Generator")
    parser.add_argument("--communities", action="store_true", help="Generate community pages only")
    parser.add_argument("--regions", action="store_true", help="Generate region pages only")
    parser.add_argument("--check", action="store_true", help="Check for missing content files")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-file output")
    args = parser.parse_args()

    verbose = not args.quiet

    # Validate required files
    if not (DATA_DIR / "communities.json").exists():
        print("ERROR: data/communities.json not found. Create it before running.", file=sys.stderr)
        sys.exit(1)

    if not (DATA_DIR / "regions.json").exists():
        print("ERROR: data/regions.json not found.", file=sys.stderr)
        sys.exit(1)

    # Load data
    communities = load_json(DATA_DIR / "communities.json")
    regions = load_json(DATA_DIR / "regions.json")

    print(f"Loaded {len(communities)} communities, {len(regions)} regions.")

    # Check mode
    if args.check:
        missing = check_missing(communities)
        if missing:
            print(f"\nMissing content files ({len(missing)}/{len(communities)}):")
            for cid in missing:
                print(f"  content/communities/{cid}.md")
        else:
            print("All community content files present!")
        return

    ensure_dirs()

    # Load templates
    if not COMMUNITY_TEMPLATE.exists():
        print("ERROR: community/template.html not found.", file=sys.stderr)
        sys.exit(1)
    if not REGION_TEMPLATE.exists():
        print("ERROR: region/template.html not found.", file=sys.stderr)
        sys.exit(1)

    with open(COMMUNITY_TEMPLATE, "r", encoding="utf-8") as f:
        community_template = f.read()
    with open(REGION_TEMPLATE, "r", encoding="utf-8") as f:
        region_template = f.read()

    # Generate
    do_communities = args.communities or (not args.communities and not args.regions)
    do_regions = args.regions or (not args.communities and not args.regions)

    if do_communities:
        print(f"\nGenerating community pages ({len(communities)} total)...")
        gen, skip = generate_communities(communities, regions, community_template, verbose)
        print(f"  Done: {gen} generated, {skip} errors.")

    if do_regions:
        print(f"\nGenerating region pages ({len(regions)} total)...")
        gen = generate_regions(regions, region_template, communities, verbose)
        print(f"  Done: {gen} generated.")

    print("\nSite generation complete.")
    print(f"  Communities: community/*.html")
    print(f"  Regions:     region/*.html")


if __name__ == "__main__":
    main()
