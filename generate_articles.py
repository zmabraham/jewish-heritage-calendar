#!/usr/bin/env python3
"""
Generate missing community articles using Claude API.
Run from the jewish-heritage-calendar directory.
"""

import json
import os
import sys
import time
import anthropic
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent
CONTENT_DIR = BASE_DIR / "content" / "communities"
DATA_FILE = BASE_DIR / "data" / "communities.json"

# Load missing list
MISSING = [
    "lyady","theresienstadt","babylonia","baghdad","komotini","hania","gallipoli",
    "dulcigno","kufa","hillah","nisibis","aphrodisias","aden","callinicum","mokka",
    "tadmor","bukhara","basra","herat","herodium","sanaa","hormuz","beth-shean",
    "narbata","borshchagovka","gibeon","shiloh","almah","banias","silwan",
    "trzebinia","rafah","letichev","nowy-sacz","otwock","wilicka","zywiec",
    "zawiercie","koluszki","kolki","aleppo","anopol","mecca","starokostiantyniv",
    "polonne","medina","pryluky","hrytsiv","kropyvnytskyi","iziaslav","radeshits",
    "plovdiv","bilgoraj","melitopol","zvenigorodka","jozefow","mszczonow","gateshead",
    "cranganore","quilon","pune","ningbo","amadiya","radashkovichy","blois","curacao",
    "limoges","barbados","jamaica","boston","richmond","cincinnati","washington-dc",
    "pittsburgh","detroit","st-louis","kutz","miami","los-angeles","montreal","toronto",
    "johannesburg","copenhagen","milan","dessau","padua","cochin","verona","bombay",
    "ferrara","calcutta","bari","kaifeng","otranto","shanghai","palermo","harbin",
    "syracuse","hong-kong","messina","trani","capua","ancona","saint-eustatius",
    "stolpce","akhaltsikhe","birobidzhan","krasyliv","kurenets","smorgonie",
    "lachovitz","sosnowiec","ladyzhyn","osowa-wyszka"
]

with open(DATA_FILE) as f:
    all_communities = json.load(f)

comm_map = {c["id"]: c for c in all_communities}

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

SAMPLE_ARTICLE = """---
id: casablanca
name: Casablanca
region: egypt-north-africa
country: Morocco
day: 100
founded: "c. 1912 (modern community)"
peak_population: "~80,000 (early 1950s)"
languages: "Judeo-Arabic, French, Hebrew"
status: "Active (small remnant community)"
---

# Casablanca

## Overview

Casablanca was home to the largest urban Jewish community in North Africa...

## Historical Origins

Jews began arriving in significant numbers from the 1910s onward...

## Golden Age

The 1930s through 1950s represent Casablanca Jewry's apex...

## Notable Figures

Rabbi Shaul Ibn Dannan served as senior halakhic authority...

## Institutions & Sacred Spaces

At its height, Casablanca supported dozens of synagogues...

## Cultural Life

Casablanca's size and diversity generated cultural production of unusual richness...

## Decline & Transformation

The 1948 Arab-Israeli War prompted the first major exodus wave...

## Legacy & Diaspora

Casablanca maintains a living Jewish community with active synagogues...
"""

def get_date_str(day_num, year=2026):
    if not day_num or day_num == "?":
        return ""
    try:
        dt = datetime(year, 1, 1) + timedelta(days=int(day_num) - 1)
        return dt.strftime("%B %-d, %Y")
    except:
        return ""

def generate_article(comm_id):
    comm = comm_map.get(comm_id, {})
    name = comm.get("name", comm_id)
    region = comm.get("region", "")
    country = comm.get("country", "")
    # Normalise Israel
    if country in ("Israel/Palestine", "Palestine"):
        country = "Israel"
    day = comm.get("dayOfYear") or comm.get("day")
    date_note = comm.get("dateNote", "")
    date_str = get_date_str(day)

    prompt = f"""Write a complete Jewish heritage calendar article for {name} ({country}).

This article will be published on {date_str or date_note or "its assigned day"} as "{name} Jewish Heritage Day."

Write in the style of a scholarly but engaging historical encyclopedia. Each section should be 3-6 substantial paragraphs. Total length should be approximately 1500-2500 words.

Return ONLY the markdown file content, starting with the YAML frontmatter, exactly matching this format:

---
id: {comm_id}
name: {name}
region: {region}
country: {country}
founded: "[estimate or 'Ancient']"
peak_population: "[number and date, or 'Unknown']"
languages: "[languages spoken by the community]"
status: "[Historical / Active / Small remnant / etc.]"
figures:
  - name: "[Name]"
    dates: "[birth–death or century]"
    description: "[1-2 sentence bio]"
  - name: "[Name]"
    dates: "[birth–death or century]"
    description: "[1-2 sentence bio]"
---

# {name}

## Overview
[3-5 paragraphs introducing the community's significance, character, and place in Jewish history]

## Historical Origins
[3-5 paragraphs on the community's founding and early centuries]

## Golden Age
[3-5 paragraphs on the height of the community's flourishing]

## Notable Figures
[3-4 paragraphs introducing the community's most significant personalities — also listed in frontmatter figures]

## Institutions & Sacred Spaces
[3-4 paragraphs on synagogues, academies, cemeteries, mikvot, and other institutions]

## Cultural Life
[3-4 paragraphs on religious practice, music, language, cuisine, distinctive customs]

## Decline & Transformation
[3-4 paragraphs on expulsion, emigration, Holocaust, or other causes of decline]

## Legacy & Diaspora
[3-4 paragraphs on where community members settled, what they carried with them, how they are remembered today]

Write factually and precisely. Use specific dates, names, and details where known. Do not invent facts — if something is uncertain, say so with appropriate hedging. This article will be read as the definitive short history of this community's Jewish heritage."""

    try:
        msg = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text
    except Exception as e:
        print(f"  ERROR generating {comm_id}: {e}", flush=True)
        return None

def main():
    # Filter to only truly missing ones
    truly_missing = [c for c in MISSING if not (CONTENT_DIR / f"{c}.md").exists()]
    print(f"Generating {len(truly_missing)} articles...", flush=True)

    for i, comm_id in enumerate(truly_missing):
        out_path = CONTENT_DIR / f"{comm_id}.md"
        comm = comm_map.get(comm_id, {})
        print(f"[{i+1}/{len(truly_missing)}] {comm_id} ({comm.get('name', '?')})...", end=" ", flush=True)

        content = generate_article(comm_id)
        if content:
            # Strip any accidental code fences
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```", 2)[-1].strip()
                if content.startswith("markdown"):
                    content = content[8:].strip()
            if content.endswith("```"):
                content = content[:-3].strip()

            out_path.write_text(content, encoding="utf-8")
            print("✓", flush=True)
        else:
            print("✗ FAILED", flush=True)

        # Small delay to avoid rate limits
        if i < len(truly_missing) - 1:
            time.sleep(0.5)

    print(f"\nDone. Generated articles saved to {CONTENT_DIR}", flush=True)

if __name__ == "__main__":
    main()
