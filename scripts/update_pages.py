#!/usr/bin/env python3
"""
Update all 365 community pages with:
1. Wikipedia images embedded in overview section (for pages that have them)
2. Expanded content for thin pages (single-section articles)

Uses wiki_cache.json created by fetch_wikipedia.py
"""

import json
import os
import re
import sys
import textwrap

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_FILE = os.path.join(BASE_DIR, 'scripts', 'wiki_cache.json')
COMMUNITY_DIR = os.path.join(BASE_DIR, 'community')

# CSS to add for community images — injected into each page's <style> block
IMAGE_CSS = """
  /* Wikipedia community image */
  .community-image {
    float: right;
    margin: 0 0 1.5rem 2rem;
    max-width: 320px;
    border: 1px solid #e8d5a3;
    border-radius: 6px;
    overflow: hidden;
    background: #f5eed9;
  }

  .community-image img {
    width: 100%;
    height: auto;
    display: block;
  }

  .community-image figcaption {
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
    color: #6b5d4f;
    line-height: 1.4;
    background: #faf8f5;
  }

  .community-image figcaption a {
    color: #1a3a5c;
    font-size: 0.75rem;
  }

  @media (max-width: 600px) {
    .community-image {
      float: none;
      margin: 1rem 0;
      max-width: 100%;
    }
  }
"""

def get_image_html(wiki_data, city_name):
    """Generate figure HTML for Wikipedia image."""
    img_url = wiki_data.get('thumbnail', '')
    if not img_url:
        return ''

    # Use a larger thumbnail by adjusting the width in the URL
    # Wikipedia thumbnail URLs contain /320px- or similar — upgrade to 640px
    img_url_large = re.sub(r'/(\d+)px-', '/640px-', img_url)

    wiki_url = wiki_data.get('wiki_url', '')
    attr_link = f'<a href="{wiki_url}" target="_blank" rel="noopener">Wikipedia</a>' if wiki_url else 'Wikipedia'

    return f'''<figure class="community-image">
          <img src="{img_url_large}" alt="{city_name}" loading="lazy" onerror="this.parentElement.style.display='none'">
          <figcaption>{city_name} — via {attr_link} / Wikimedia Commons</figcaption>
        </figure>'''

def build_expansion_sections(wiki_data, existing_extract_paragraphs=None):
    """
    Build additional HTML sections from Wikipedia extract for thin pages.
    Returns a string of <section> elements to inject.
    """
    extract = wiki_data.get('extract', '')
    wiki_url = wiki_data.get('wiki_url', '')
    if not extract or len(extract) < 60:
        return ''

    # Use extract_html which has proper HTML formatting
    extract_html = wiki_data.get('extract_html', '')
    if not extract_html:
        return ''

    attribution = ''
    if wiki_url:
        attribution = f'\n        <p class="wiki-source"><em>Additional context sourced from <a href="{wiki_url}" target="_blank" rel="noopener">Wikipedia</a> (CC BY-SA)</em></p>'

    section_html = f'''
      <section id="general-information">
        <h2>General Information</h2>
        {extract_html}{attribution}
      </section>'''

    return section_html

def add_css_to_page(html):
    """Inject image CSS into the page's <style> block."""
    if 'community-image' in html:
        return html  # Already has image CSS
    # Insert before the closing </style> tag
    return html.replace('</style>', IMAGE_CSS + '\n</style>', 1)

def add_wiki_source_css(html):
    """Add wiki-source attribution paragraph styling."""
    if 'wiki-source' in html:
        return html
    extra_css = '''
  .wiki-source {
    font-size: 0.85rem;
    color: #8a7a6d;
    font-style: italic;
    margin-top: 1rem;
    padding-top: 0.75rem;
    border-top: 1px solid #e8d5a3;
  }
'''
    return html.replace('</style>', extra_css + '\n</style>', 1)

def inject_image_into_overview(html, image_html):
    """Inject figure HTML after the first <p> in the overview section."""
    # Don't add if image already exists in overview
    if '<figure class="community-image">' in html:
        return html

    # Find the overview section and its first paragraph
    overview_match = re.search(
        r'(<section id="overview">.*?<h2>Overview</h2>\s*<p>.*?</p>)',
        html,
        re.DOTALL
    )
    if not overview_match:
        return html

    # Insert image right after the first paragraph
    end_pos = overview_match.end()
    return html[:end_pos] + '\n        ' + image_html + html[end_pos:]

def inject_expansion_sections(html, sections_html):
    """Inject new sections before the day-nav div."""
    # Don't add if general-information section already exists
    if '<section id="general-information">' in html:
        return html
    return html.replace(
        '      <!-- Day Navigation -->',
        sections_html + '\n\n      <!-- Day Navigation -->'
    )

def process_community(cid, name, wiki_data, is_thin):
    """Process a single community page. Returns (modified, changes_description)."""
    path = os.path.join(COMMUNITY_DIR, f'{cid}.html')
    if not os.path.exists(path):
        return False, 'file not found'

    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    original = html
    changes = []

    # 1. Add image CSS if we have image data
    if wiki_data and wiki_data.get('thumbnail'):
        html = add_css_to_page(html)
        html = add_wiki_source_css(html)

        # 2. Inject image into overview section
        image_html = get_image_html(wiki_data, name)
        if image_html:
            new_html = inject_image_into_overview(html, image_html)
            if new_html != html:
                html = new_html
                changes.append('image')

    # 3. For thin pages, inject expansion sections
    if is_thin and wiki_data:
        sections = re.findall(r'<section id=', html)
        if len(sections) == 1:  # still thin (hasn't been expanded)
            expansion = build_expansion_sections(wiki_data)
            if expansion and '<!-- Day Navigation -->' in html:
                html = inject_expansion_sections(html, expansion)
                changes.append('expanded')

    if html != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        return True, ', '.join(changes) if changes else 'modified'

    return False, 'no changes'

def main():
    # Load cache
    if not os.path.exists(CACHE_FILE):
        print(f'ERROR: Cache file not found at {CACHE_FILE}')
        print('Run fetch_wikipedia.py first.')
        sys.exit(1)

    with open(CACHE_FILE) as f:
        cache = json.load(f)

    # Load communities
    with open(os.path.join(BASE_DIR, 'data', 'communities.json')) as f:
        communities = json.load(f)

    # Determine which pages are thin
    thin_ids = set()
    for c in communities:
        path = os.path.join(COMMUNITY_DIR, f'{c["id"]}.html')
        if os.path.exists(path):
            with open(path) as f:
                content = f.read()
            sections = re.findall(r'<section id=', content)
            if len(sections) == 1:
                thin_ids.add(c['id'])

    print(f'Found {len(thin_ids)} thin pages to expand')
    print(f'Cache has {len(cache)} entries')

    stats = {'images': 0, 'expanded': 0, 'unchanged': 0, 'no_data': 0, 'errors': 0}
    total = len(communities)

    for i, c in enumerate(communities):
        cid = c['id']
        name = c['name']
        wiki_data = cache.get(cid)
        is_thin = cid in thin_ids

        try:
            modified, reason = process_community(cid, name, wiki_data, is_thin)
            if modified:
                if 'image' in reason:
                    stats['images'] += 1
                if 'expanded' in reason:
                    stats['expanded'] += 1
                print(f'[{i+1}/{total}] ✓ {name}: {reason}')
            elif not wiki_data:
                stats['no_data'] += 1
            else:
                stats['unchanged'] += 1
        except Exception as e:
            stats['errors'] += 1
            print(f'[{i+1}/{total}] ✗ {name}: ERROR — {e}')

    print(f'\n=== Summary ===')
    print(f'Images added: {stats["images"]}')
    print(f'Articles expanded: {stats["expanded"]}')
    print(f'Unchanged: {stats["unchanged"]}')
    print(f'No Wikipedia data: {stats["no_data"]}')
    print(f'Errors: {stats["errors"]}')

if __name__ == '__main__':
    main()
