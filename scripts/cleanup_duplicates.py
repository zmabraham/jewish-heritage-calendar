#!/usr/bin/env python3
"""
Remove duplicate images and fix remaining issues from the update process.
"""

import re
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMUNITY_DIR = os.path.join(BASE_DIR, 'community')

def fix_page(path):
    """Fix a single page: remove duplicate images, fix spacing."""
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    original = html
    changes = []

    # Remove duplicate community-image figures (keep only the first one)
    overview_match = re.search(
        r'(<section id="overview">.*?</section>)',
        html,
        re.DOTALL
    )

    if overview_match:
        overview_html = overview_match.group(1)
        figures = re.findall(r'<figure class="community-image">.*?</figure>', overview_html, re.DOTALL)

        if len(figures) > 1:
            # Keep only the first figure
            new_overview = re.sub(
                r'(<figure class="community-image">.*?</figure>)\s*(<figure class="community-image">.*?</figure>)+',
                r'\1',
                overview_html,
                flags=re.DOTALL
            )
            html = html.replace(overview_html, new_overview)
            changes.append(f'removed {len(figures) - 1} duplicate images')

    # Fix excessive blank lines (reduce multiple blank lines to at most 2)
    html = re.sub(r'\n\s*\n\s*\n+(?=\s*<[a-z/])', '\n\n', html)

    # Fix broken CSS where wiki-source might be added twice
    if html.count('.wiki-source {') > 1:
        # Remove duplicate wiki-source CSS block
        css_match = re.search(r'(<style>.*?)(\.wiki-source \{.*?\})(.*?\.wiki-source \{.*?\})(.*?</style>)', html, re.DOTALL)
        if css_match:
            new_css = css_match.group(1) + css_match.group(2) + css_match.group(4)
            html = html.replace(css_match.group(0), new_css)
            changes.append('removed duplicate wiki-source CSS')

    # Remove duplicate community-image CSS blocks
    if html.count('.community-image {') > 1:
        # Keep only the first occurrence
        css_match = re.search(
            r'(<style>.*?)(/[*] Wikipedia community image [*].*?@media \(max-width: 600px\) \{[^}]*\}\s*\})(.*?/[*] Wikipedia community image [*].*?@media \(max-width: 600px\) \{[^}]*\})(.*?</style>)',
            html,
            re.DOTALL
        )
        if css_match:
            new_css = css_match.group(1) + css_match.group(2) + css_match.group(4)
            html = html.replace(css_match.group(0), new_css)
            changes.append('removed duplicate community-image CSS')

    if html != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        return ', '.join(changes) if changes else 'modified'

    return 'unchanged'

def main():
    import json
    with open(os.path.join(BASE_DIR, 'data', 'communities.json')) as f:
        communities = json.load(f)

    stats = {'fixed': 0, 'unchanged': 0, 'errors': 0}

    for i, c in enumerate(communities):
        path = os.path.join(COMMUNITY_DIR, f'{c["id"]}.html')
        if not os.path.exists(path):
            continue

        try:
            result = fix_page(path)
            if result != 'unchanged':
                stats['fixed'] += 1
                print(f'[{i+1}/365] ✓ {c["name"]}: {result}')
            else:
                stats['unchanged'] += 1
        except Exception as e:
            stats['errors'] += 1
            print(f'[{i+1}/365] ✗ {c["name"]}: ERROR — {e}')

    print(f'\n=== Summary ===')
    print(f'Fixed: {stats["fixed"]}')
    print(f'Unchanged: {stats["unchanged"]}')
    print(f'Errors: {stats["errors"]}')

if __name__ == '__main__':
    main()
