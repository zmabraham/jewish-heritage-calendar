#!/usr/bin/env python3
"""
Quickly generate template articles for missing communities.
These are substantial placeholder articles that can be enriched later.
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
CONTENT_DIR = BASE_DIR / "content" / "communities"
DATA_FILE = BASE_DIR / "data" / "communities.json"

MISSING = [
    "lyady","babylonia","baghdad","komotini","hania","gallipoli",
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

def generate_article(comm_id, comm):
    name = comm.get("name", comm_id)
    country = comm.get("country", "")
    if country in ("Israel/Palestine", "Palestine"):
        country = "Israel"
    region = comm.get("region", "")
    date_note = comm.get("dateNote", "")

    article = f"""---
id: {comm_id}
name: {name}
region: {region}
country: {country}
founded: "Various periods"
peak_population: "Unknown"
languages: "Hebrew, Aramaic, local languages"
status: "Historical"
figures: []
---

# {name}

## Overview

{name}, located in present-day {country}, represents one thread in the vast tapestry of Jewish diaspora history. While comprehensive historical records for this community remain to be fully documented, its existence reflects the broader patterns of Jewish settlement across {country}. Jewish communities like {name} played vital roles in the commercial, religious, and intellectual life of their regions, contributing to the rich diversity of the Jewish diaspora.

## Historical Origins

Jewish settlement in {country} dates back millennia, with communities established through ancient trade routes, exile migrations, and opportunities under various ruling powers. {name} emerged within this broader historical context, shaped by the same forces that affected Jewish communities throughout the region: changing political borders, economic opportunities, religious developments, and periodic persecution or protection depending on the ruling authorities.

The specific founding of Jewish life in {name} likely followed patterns common to communities in this region: initial settlement by traders or craftsmen, gradual growth through family networks and immigration, and the establishment of basic religious institutions — a synagogue, mikveh (ritual bath), and cemetery — that marked the transition from temporary sojourners to a permanent community.

## Golden Age

Like many Jewish communities across the diaspora, {name} experienced periods of relative prosperity and cultural flourishing. These golden ages typically coincided with eras of political stability, economic growth, and tolerant or protective governance from local authorities. During such times, Jewish merchants, artisans, scholars, and community leaders built institutions that sustained Jewish life and contributed to the broader society.

The community maintained Torah study, observed Jewish law (halakha), celebrated the full cycle of Jewish festivals and holy days, and developed communal structures for charity, education, and dispute resolution. Connections to other Jewish communities — through marriage alliances, trade networks, rabbinical correspondence, and migration — linked {name} to the wider Jewish world.

## Notable Figures

While specific records of {name}'s rabbinic and communal leaders await further archival research, communities like this one were typically served by rabbis trained in major yeshivot (academies), religious functionaries including shochetim (ritual slaughterers), chazzanim (cantors), and melamdim (teachers), and lay leaders who managed communal affairs. These individuals preserved Jewish tradition and adapted it to local circumstances, ensuring continuity across generations.

## Institutions & Sacred Spaces

A Jewish community of any size required certain sacred and communal institutions. {name} would have maintained a synagogue as the center of religious and communal life, a mikveh for ritual purification, a cemetery for respectful burial according to Jewish law, and likely a chevra kadisha (burial society) to oversee funeral practices. Educational institutions for Torah study, charitable organizations to support the poor and needy, and funds to assist travelers and emissaries from the Holy Land were also typical of such communities.

## Cultural Life

Jewish life in {name} would have followed the rhythms of the Jewish calendar: weekly Shabbat observance, the major festivals of Pesach (Passover), Shavuot, Rosh Hashanah, Yom Kippur, and Sukkot, and minor holidays and fast days. The community likely developed its own customs and traditions, blending universal Jewish practice with local influences. Cuisine, language, music, and folk traditions reflected both Jewish heritage and the surrounding culture.

## Decline & Transformation

Jewish communities across the diaspora faced periods of decline due to various factors: expulsions, persecutions, economic changes, warfare, political upheaval, emigration to larger centers or foreign lands, and ultimately the Holocaust in Europe. {name} would have been affected by the broad historical forces that transformed Jewish life in {country}. Many communities that once existed were destroyed, dispersed, or gradually diminished as Jewish populations moved to urban centers or emigrated abroad.

## Legacy & Diaspora

The descendants of {name}'s Jewish community, like other diaspora communities, carried their traditions, memories, and identities to new locations — whether elsewhere in {country}, in major Jewish centers worldwide, or in the State of Israel. The legacy of communities like {name} lives on through family histories, archival records, tombstones in Jewish cemeteries, and the ongoing story of the Jewish people. Each community, regardless of size or fame, represents a unique chapter in Jewish history.

## Further Research

This community profile represents a preliminary historical overview. Further research in local archives, Jewish historical records, rabbinical literature, and communal documents would yield more detailed information about {name}'s specific history, notable figures, institutions, and contributions to Jewish and regional history. Researchers and descendants are encouraged to explore these sources to recover the full story of this community.
"""
    return article

def main():
    with open(DATA_FILE) as f:
        all_communities = json.load(f)

    comm_map = {c["id"]: c for c in all_communities}

    count = 0
    for comm_id in MISSING:
        out_path = CONTENT_DIR / f"{comm_id}.md"
        if out_path.exists():
            print(f"SKIP {comm_id} (exists)")
            continue

        comm = comm_map.get(comm_id, {})
        article = generate_article(comm_id, comm)
        out_path.write_text(article, encoding="utf-8")
        count += 1
        print(f"✓ {comm_id}")

    print(f"\nGenerated {count} new articles.")

if __name__ == "__main__":
    main()
