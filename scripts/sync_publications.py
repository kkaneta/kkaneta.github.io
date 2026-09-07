#!/usr/bin/env python3
"""
sync_publications.py – INSPIRE-HEP → data/publications.yml generator

Regenerates data/publications.yml from the author's INSPIRE-HEP record.
INSPIRE tracks both events that make the list go stale:

  * a new arXiv preprint appears        → a new record shows up
  * a preprint gets published           → publication_info / doi are filled in

so regenerating from scratch keeps both in sync.

Usage:
    python3 scripts/sync_publications.py            # rewrite data/publications.yml
    python3 scripts/sync_publications.py --check    # report drift, write nothing
    python3 scripts/sync_publications.py --stdout   # print YAML, write nothing

The sync refuses to write when the result looks wrong rather than publishing it:
see the "safety checks" section below.

No external dependencies (stdlib only).
"""

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

# --- configuration ---------------------------------------------------------

INSPIRE_BAI = "K.Kaneta.1"          # INSPIRE Bibliographic Author Identifier
API = "https://inspirehep.net/api/literature"
FIELDS = (
    "titles,authors,arxiv_eprints,publication_info,dois,"
    "document_type,texkeys,earliest_date"
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "publications.yml"
EXCLUDE_FILE = ROOT / "data" / "publications_exclude.yml"

# INSPIRE document_type → the `type` value used by layouts/publications/list.html.
# Only journal articles go on the site; conference papers and theses are left off.
DOC_TYPES = {
    "article": "article",
}

# INSPIRE abbreviations → full journal names, as used on the site.
JOURNAL_MAP = {
    "Phys.Rev.D": "Physical Review D",
    "Phys.Rev.B": "Physical Review B",
    "Phys.Rev.A": "Physical Review A",
    "Phys.Rev.Lett.": "Physical Review Letters",
    "Phys.Lett.B": "Physics Letters B",
    "JHEP": "Journal of High Energy Physics",
    "JCAP": "Journal of Cosmology and Astroparticle Physics",
    "Nucl.Phys.B": "Nuclear Physics B",
    "Eur.Phys.J.C": "European Physical Journal C",
    "Int.J.Mod.Phys.A": "International Journal of Modern Physics A",
    "Mod.Phys.Lett.A": "Modern Physics Letters A",
    "Europhys.Lett.": "Europhysics Letters",
    "EPL": "Europhysics Letters",
    "Acta Phys.Polon.B": "Acta Physica Polonica B",
}

# Journals whose INSPIRE "volume" is really an issue number (JHEP 05 (2026) 229).
# The site follows the publisher convention instead: volume = year, issue = month.
MONTH_AS_VOLUME = {"JHEP", "JCAP"}

# Refuse to rewrite the file if the freshly fetched list falls below this
# fraction of the list it would replace. The site publishes without review, so a
# query that silently stops matching must stop the sync, not empty the page.
SHRINK_TOLERANCE = 0.9


# --- helpers ---------------------------------------------------------------


def fetch_records():
    """Return all INSPIRE literature records for the configured author."""
    records, page, size = [], 1, 100
    while True:
        query = urllib.parse.urlencode(
            {
                "q": f"a {INSPIRE_BAI}",
                "fields": FIELDS,
                "size": size,
                "page": page,
                "sort": "mostrecent",
            }
        )
        req = urllib.request.Request(
            f"{API}?{query}",
            headers={
                "Accept": "application/json",
                # INSPIRE asks API clients to identify themselves.
                "User-Agent": "kkaneta.github.io publication sync (+https://kkaneta.github.io/)",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.load(resp)

        hits = payload["hits"]["hits"]
        records.extend(hits)
        if len(records) >= payload["hits"]["total"] or not hits:
            break
        page += 1

    return records


def load_excludes():
    """Read texkeys to keep off the site. Format: one `- texkey` per line."""
    if not EXCLUDE_FILE.exists():
        return set()
    keys = set()
    for line in EXCLUDE_FILE.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line.startswith("-"):
            keys.add(line[1:].strip().strip('"\''))
    return keys


def load_existing_titles():
    """Map {id: title} and {arxiv: title} from the current publications.yml.

    Titles on the site are copy-edited to a consistent title case, while
    INSPIRE's own capitalisation is uneven ("Freeze-in from Preheating" next to
    "Hillclimbing Higgs inflation"). Carrying the existing title over keeps that
    editing, and keeps the sync from rewriting 45 titles on its first run.
    """
    titles = {}
    if not OUT.exists():
        return titles
    for block in re.split(r"\n(?=- id:)", OUT.read_text(encoding="utf-8")):
        # The id sits on the entry's opening line ("- id:"), the rest are
        # indented; matching only the indented form left every title keyed by
        # arXiv number alone, so a record without a preprint lost its title.
        found = dict(re.findall(r'^(?:- |  )(id|title|arxiv): "(.*)"$',
                                block, re.M))
        if "title" not in found:
            continue
        for key in ("id", "arxiv"):
            if found.get(key):
                titles[found[key]] = found["title"]
    return titles


def clean_text(s):
    """Normalise INSPIRE title text for YAML output."""
    s = s.replace("\xa0", " ")          # INSPIRE uses NBSP inside titles
    s = s.replace("$", "")              # inline math markers: $g-2$ → g-2
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def pick_title(meta):
    """Prefer the arXiv title: it matches the capitalisation used on the site."""
    titles = meta.get("titles") or []
    for t in titles:
        if t.get("source") == "arXiv":
            return clean_text(t["title"])
    return clean_text(titles[0]["title"]) if titles else ""


def format_author(full_name):
    """INSPIRE gives "Kaneta, Kunio"; the site uses "Kunio Kaneta"."""
    if "," in full_name:
        last, first = full_name.split(",", 1)
        return f"{first.strip()} {last.strip()}".strip()
    return full_name.strip()


def pick_publication_info(meta):
    """Pick the entry that carries journal data; ignore conference-only stubs."""
    for info in meta.get("publication_info") or []:
        if info.get("journal_title"):
            return info
    return {}


def to_int(value):
    try:
        return int(str(value).lstrip("0") or "0")
    except (TypeError, ValueError):
        return None


def build_entry(meta, known_titles):
    """Convert one INSPIRE record into the site's publication dict."""
    doc_types = meta.get("document_type") or []
    pub_type = next((DOC_TYPES[d] for d in doc_types if d in DOC_TYPES), None)
    if pub_type is None:
        return None

    info = pick_publication_info(meta)
    journal_abbrev = info.get("journal_title")

    year = info.get("year")
    if not year:
        # Unpublished preprint: fall back to the arXiv submission year.
        year = to_int((meta.get("earliest_date") or "")[:4])
    if not year:
        return None

    volume = info.get("journal_volume")
    issue = info.get("journal_issue")
    if journal_abbrev in MONTH_AS_VOLUME and re.fullmatch(r"\d{1,2}", volume or ""):
        # JHEP 05 (2026) 229 → volume 2026, issue 5
        volume, issue = str(year), volume

    # A real page range wins; otherwise prefer the article id. INSPIRE sometimes
    # sets page_start to the issue number for article-id journals (Phys.Rev.D
    # 108 (2023) 11, 115027 arrives as page_start "11", artid "115027"), so
    # page_start alone must not outrank artid.
    if info.get("page_start") and info.get("page_end"):
        pages = f"{info['page_start']}-{info['page_end']}"
    else:
        pages = info.get("artid") or info.get("page_start")

    texkey = meta["texkeys"][0]
    arxiv = (meta.get("arxiv_eprints") or [{}])[0].get("value")
    title = known_titles.get(texkey) or known_titles.get(arxiv) or pick_title(meta)

    entry = {
        "id": texkey,
        "type": pub_type,
        "year": int(year),
        "authors": [format_author(a["full_name"]) for a in meta.get("authors", [])],
        "title": title,
    }

    if journal_abbrev and journal_abbrev not in JOURNAL_MAP:
        # Nothing downstream can catch this: the entry renders fine, just with
        # "SciPost Phys." sitting next to "Physical Review D". main() stops.
        entry["_unknown_journal"] = journal_abbrev
    journal_full = JOURNAL_MAP.get(journal_abbrev, journal_abbrev)
    if journal_full:
        entry["journal"] = journal_full
    if to_int(volume) is not None:
        entry["volume"] = to_int(volume)
    if to_int(issue) is not None:
        entry["issue"] = to_int(issue)
    if pages:
        entry["pages"] = str(pages)
    if meta.get("dois"):
        entry["doi"] = meta["dois"][0]["value"]
    if meta.get("arxiv_eprints"):
        entry["arxiv"] = meta["arxiv_eprints"][0]["value"]

    entry["_date"] = meta.get("earliest_date") or ""
    return entry


def quote(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def render(entries):
    """Emit YAML in the same shape as the hand-maintained file."""
    lines = [
        "# Generated by scripts/sync_publications.py from INSPIRE-HEP.",
        "#",
        "# Bibliographic fields (journal, volume, issue, pages, doi, arxiv, year)",
        "# are overwritten on every sync — edit them in INSPIRE, not here.",
        "# Titles are preserved: an edit made here survives later syncs.",
        f"# To keep a record off the site, list its id in {EXCLUDE_FILE.name}.",
    ]
    current_year = None
    for e in entries:
        if e["year"] != current_year:
            current_year = e["year"]
            lines.append("")
            lines.append(f"# {current_year}")
        lines.append(f'- id: {quote(e["id"])}')
        lines.append(f'  type: {quote(e["type"])}')
        lines.append(f'  year: {e["year"]}')
        if e["authors"]:
            lines.append("  authors:")
            lines.extend(f"    - {quote(a)}" for a in e["authors"])
        lines.append(f'  title: {quote(e["title"])}')
        if "journal" in e:
            lines.append(f'  journal: {quote(e["journal"])}')
        for key in ("volume", "issue"):
            if key in e:
                lines.append(f"  {key}: {e[key]}")
        for key in ("pages", "doi", "arxiv"):
            if key in e:
                lines.append(f"  {key}: {quote(e[key])}")
    return "\n".join(lines) + "\n"


# --- safety checks ---------------------------------------------------------
#
# data/publications.yml is published without a human reading it first, so each
# check below turns a failure that would reach the site into a failed workflow
# run and an email instead.


def count_existing_entries():
    """How many publications the current file holds (0 if it does not exist)."""
    if not OUT.exists():
        return 0
    return len(re.findall(r"^- id: ", OUT.read_text(encoding="utf-8"), re.M))


def check_entries(entries):
    """Report records INSPIRE returned without the fields the site renders."""
    problems = []
    for e in entries:
        if not e.get("authors"):
            problems.append(f"{e['id']}: INSPIRE returned no author list.")
        if not e.get("title"):
            problems.append(f"{e['id']}: INSPIRE returned no title.")
    return problems


def check_journals(entries):
    """Report journal abbreviations that JOURNAL_MAP does not spell out."""
    unknown = {}
    for e in entries:
        abbrev = e.get("_unknown_journal")
        if abbrev:
            unknown.setdefault(abbrev, []).append(e["id"])
    problems = []
    for abbrev, ids in sorted(unknown.items()):
        problems.append(
            f"unknown journal abbreviation {json.dumps(abbrev)} "
            f"(in {', '.join(ids)}).\n"
            f"      Without a mapping the site prints the abbreviation next to "
            f"the full\n"
            f"      names of every other journal. Add a line to JOURNAL_MAP in "
            f"{Path(__file__).name}:\n"
            f"          {json.dumps(abbrev)}: \"<full journal name>\","
        )
    return problems


def check_count(new_count, old_count, allow_shrink):
    """Refuse a drop large enough to look like a failed query."""
    if old_count == 0 or allow_shrink:
        return []
    if new_count >= old_count * SHRINK_TOLERANCE:
        return []
    return [
        f"INSPIRE returned {new_count} publications, replacing a file that "
        f"holds {old_count}.\n"
        f"      A drop this size usually means the query stopped matching — a "
        f"changed\n"
        f"      author identifier or a changed API — not that the papers went "
        f"away.\n"
        f"      Check https://inspirehep.net/authors/1078184 first. If the "
        f"shorter list\n"
        f"      is genuinely right (several papers excluded at once), re-run "
        f"with\n"
        f"      --allow-shrink."
    ]


# --- main ------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="exit 1 if the file is out of date; write nothing")
    parser.add_argument("--stdout", action="store_true",
                        help="print the generated YAML instead of writing it")
    parser.add_argument("--allow-shrink", action="store_true",
                        help="write even though the list shrank sharply; use "
                             "after excluding several papers on purpose")
    args = parser.parse_args()

    excludes = load_excludes()
    known_titles = load_existing_titles()
    entries = []
    skipped = []
    for record in fetch_records():
        meta = record["metadata"]
        texkey = meta["texkeys"][0]
        if texkey in excludes:
            skipped.append(texkey)
            continue
        entry = build_entry(meta, known_titles)
        if entry:
            entries.append(entry)

    # Newest first: by publication year, then by arXiv submission date.
    entries.sort(key=lambda e: (e["year"], e["_date"]), reverse=True)

    problems = check_entries(entries) + check_journals(entries)
    problems += check_count(len(entries), count_existing_entries(),
                            args.allow_shrink)

    for entry in entries:
        entry.pop("_date")
        entry.pop("_unknown_journal", None)

    yaml = render(entries)
    print(f"{len(entries)} publications ({len(skipped)} excluded)", file=sys.stderr)

    if problems:
        print("data/publications.yml was NOT updated:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        if args.stdout:
            sys.stdout.write(yaml)
        return 2

    if args.stdout:
        sys.stdout.write(yaml)
        return 0

    old = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    if old == yaml:
        print("data/publications.yml is up to date.", file=sys.stderr)
        return 0

    if args.check:
        print("data/publications.yml is OUT OF DATE.", file=sys.stderr)
        return 1

    OUT.write_text(yaml, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
