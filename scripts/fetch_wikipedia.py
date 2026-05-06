#!/usr/bin/env python3
"""
Fetch Wikipedia summaries and images for all 365 communities.
Saves results to scripts/wiki_cache.json for later use by update_pages.py.
"""

import json
import time
import urllib.request
import urllib.parse
import urllib.error
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_FILE = os.path.join(BASE_DIR, 'scripts', 'wiki_cache.json')

# Wikipedia search title overrides for tricky community names
TITLE_OVERRIDES = {
    'candia': 'Heraklion',
    'ruschuk': 'Ruse, Bulgaria',
    'oswiecim': 'Oświęcim',
    'demotika': 'Didymoteicho',
    'oxyrhynchus': 'Oxyrhynchus',
    'nag-hammadi': 'Nag Hammadi',
    'fayyum': 'Faiyum',
    'rakhmistrivka': 'Rakhmystrivka',
    'zlatopolie': 'Zolotonosha',  # approximate
    'zhinkovets': 'Zhinkivtsi',
    'khodorovka': 'Khodoriv',
    'novofastov': 'Fastiv',  # approximate
    'ruzhin': 'Ruzhyn',
    'kleck': 'Kletsk',
    'druya': 'Druja',
    'eishyshok': 'Eišiškės',
    'kobryn': 'Kobryn',
    'pruzana': 'Pruzhany',
    'yekaterinoslav': 'Dnipro',
    'lizhansk': 'Leżajsk',
    'dinov': 'Dynów',
    'buczacz': 'Buchach',
    'katowice': 'Katowice',
    'jedwabne': 'Jedwabne pogrom',
    'marburg': 'Marburg',
    'hildesheim': 'Hildesheim',
    'tlemcen': 'Tlemcen',
    'balta': 'Balta, Ukraine',
    'plock': 'Płock',
    'san-nicandro': 'San Nicandro Garganico',
    'madeira': 'Madeira',
    'czestochowa': 'Częstochowa',
    'radom': 'Radom',
    'kielce': 'Kielce',
    'lubartow': 'Lubartów',
    'bedzin': 'Będzin',
    'kowel': 'Kovel',
    'zhitomir': 'Zhytomyr',
    'cherkassy': 'Cherkasy',
    'uman': 'Uman',
    'kremenets': 'Kremenets',
    'tulchin': 'Tulchyn',
    'shepetovka': 'Shepetivka',
    'pavoloch': 'Pavoloch',
    'st-petersburg': 'Saint Petersburg',
    'halle': 'Halle (Saale)',
    'sens': 'Sens, Yonne',
    'bonn': 'Bonn',
    'rome': 'Rome',
    'moscow': 'Moscow',
    'riga': 'Riga',
    'algiers': 'Algiers',
    'timbuktu': 'Timbuktu',
    'tripoli': 'Tripoli, Libya',
    'benghazi': 'Benghazi',
    'marseille': 'Marseille',
    'basel': 'Basel',
    'mashhad': 'Mashhad',
    'larissa': 'Larissa',
    'serres': 'Serres, Greece',
    'dupnitsa': 'Dupnitsa',
    'przysucha': 'Przysucha',
    'slutsk': 'Slutsk',
    'offenbach': 'Offenbach am Main',
    'kassel': 'Kassel',
    'brunswick': 'Brunswick, Germany',
    'lomza': 'Łomża',
    'opatow': 'Opatów',
    'rabat': 'Rabat',
    'zkhinvali': 'Gori, Georgia',  # approximate
}

def wiki_url(title):
    encoded = urllib.parse.quote(title.replace(' ', '_'))
    return f'https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}'

def fetch_summary(name, community_id):
    """Fetch Wikipedia summary for a community. Returns dict or None."""
    # Try override title first, then name, then simplified name
    titles_to_try = []
    if community_id in TITLE_OVERRIDES:
        titles_to_try.append(TITLE_OVERRIDES[community_id])
    titles_to_try.append(name)
    # Also try without parenthetical
    if '(' in name:
        clean = name.split('(')[0].strip()
        titles_to_try.append(clean)

    for title in titles_to_try:
        url = wiki_url(title)
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'JewishHeritageCalendar/1.0 (educational project)'
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                if data.get('type') == 'disambiguation':
                    continue
                return data
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue
            if e.code == 429:
                # Rate limited — wait longer and retry once
                print(f'  [rate limit] sleeping 5s for {title}')
                time.sleep(5)
                try:
                    req2 = urllib.request.Request(url, headers={
                        'User-Agent': 'JewishHeritageCalendar/1.0 (educational project)'
                    })
                    with urllib.request.urlopen(req2, timeout=10) as resp2:
                        data = json.loads(resp2.read())
                        if data.get('type') != 'disambiguation':
                            return data
                except Exception:
                    pass
                continue
            print(f'  HTTP {e.code} for {title}')
            continue
        except Exception as e:
            print(f'  Error fetching {title}: {e}')
            continue
    return None

def main():
    with open(os.path.join(BASE_DIR, 'data', 'communities.json')) as f:
        communities = json.load(f)

    # Load existing cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            cache = json.load(f)
        print(f'Loaded {len(cache)} cached entries')
    else:
        cache = {}

    total = len(communities)
    fetched = 0
    skipped = 0

    for i, c in enumerate(communities):
        cid = c['id']
        if cid in cache:
            skipped += 1
            continue

        name = c['name']
        sys.stdout.write(f'[{i+1}/{total}] {name}... ')
        sys.stdout.flush()

        data = fetch_summary(name, cid)
        if data:
            result = {
                'title': data.get('title', name),
                'extract': data.get('extract', ''),
                'extract_html': data.get('extract_html', ''),
                'thumbnail': data.get('thumbnail', {}).get('source', ''),
                'thumbnail_width': data.get('thumbnail', {}).get('width', 0),
                'thumbnail_height': data.get('thumbnail', {}).get('height', 0),
                'original_image': data.get('originalimage', {}).get('source', ''),
                'wiki_url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
            }
            print(f'✓ (img: {"yes" if result["thumbnail"] else "no"})')
        else:
            result = None
            print('✗ (not found)')

        cache[cid] = result
        fetched += 1

        # Save cache periodically
        if fetched % 20 == 0:
            with open(CACHE_FILE, 'w') as f:
                json.dump(cache, f, indent=2)
            print(f'  → Saved cache ({fetched} fetched so far)')

        time.sleep(1.0)  # Polite rate limiting (1s between requests)

    # Final save
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

    found = sum(1 for v in cache.values() if v is not None)
    with_img = sum(1 for v in cache.values() if v and v.get('thumbnail'))
    print(f'\nDone! {found}/{total} found, {with_img} with images, {skipped} skipped (cached)')

if __name__ == '__main__':
    main()
