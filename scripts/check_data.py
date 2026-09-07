#!/usr/bin/env python3
"""
check_data.py – validate the YAML under data/ before the site is built.

The site is edited a handful of times a year, so the shape of these files is
never fresh in anyone's memory. A missing key renders as a blank space rather
than an error, which is easy to publish and hard to notice. This script turns
those into a failed build that says which file, which entry, and what to write.

Usage:
    python3 scripts/check_data.py

Exits 0 when everything checks out, 1 otherwise.
Requires PyYAML (`pip install pyyaml`).
"""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("check_data.py needs PyYAML. Install it with: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

SYLLABUS_YEAR_RANGE = range(2000, 2101)


def load(name):
    path = DATA / name
    if not path.exists():
        return None, [f"{name}: file is missing."]
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")), []
    except yaml.YAMLError as exc:
        return None, [f"{name}: not valid YAML.\n      {exc}"]


def get(entry, dotted):
    """Follow "title.ja" through nested dicts; None if any step is missing."""
    value = entry
    for key in dotted.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def require(entry, where, keys):
    """Report the keys that are absent or empty."""
    return [f"{where}: {key} is missing or empty." for key in keys
            if not get(entry, key)]


# --- per-file checks -------------------------------------------------------


def check_teaching():
    courses, problems = load("teaching.yml")
    if problems:
        return problems
    if not isinstance(courses, list):
        return ["teaching.yml: expected a list of courses."]

    seen = {}
    for i, course in enumerate(courses, 1):
        where = f"teaching.yml course {i}"
        if isinstance(course, dict) and course.get("code"):
            # Two entries can share a code (a course split across years), so
            # keep the position in the name or a duplicate reads as itself.
            where = f"teaching.yml course {i} ({course['code']})"

        problems += require(course, where,
                            ["code", "dept", "years",
                             "semester.ja", "level.ja", "title.ja"])

        dept = get(course, "dept")
        if dept is not None and not re.fullmatch(r"\d{2}", str(dept)):
            problems.append(
                f"{where}: dept is {dept!r}, but it must be the two-digit "
                f"faculty code\n"
                f"      that appears in the syllabus URL, quoted (e.g. \"03\").")

        # An English title without its English semester and level renders the
        # course on the English page with blanks where those two should be.
        if get(course, "title.en"):
            problems += require(course, where, ["semester.en", "level.en"])

        url = course.get("url") if isinstance(course, dict) else None
        if url and not str(url).startswith("http"):
            problems.append(f"{where}: url is {url!r}; it must be a full "
                            f"https:// address.")

        years = get(course, "years")
        if years is None:
            continue
        if not isinstance(years, list):
            problems.append(f"{where}: years must be a list, e.g. "
                            f"years: [2025, 2026].")
            continue
        for year in years:
            if not isinstance(year, int) or year not in SYLLABUS_YEAR_RANGE:
                problems.append(f"{where}: {year!r} is not a four-digit year.")
                continue
            key = (str(course.get("code")), year)
            if key in seen:
                problems.append(
                    f"{where}: {year} also appears in {seen[key]}.\n"
                    f"      A course-year may appear once. When a course "
                    f"changes, split the\n"
                    f"      entry and give each half its own years.")
            else:
                seen[key] = where
    return problems


def check_publications():
    entries, problems = load("publications.yml")
    if problems:
        return problems
    if not isinstance(entries, list):
        return ["publications.yml: expected a list of publications."]

    for i, entry in enumerate(entries, 1):
        where = f"publications.yml entry {i}"
        if isinstance(entry, dict) and entry.get("id"):
            where = f"publications.yml {entry['id']}"
        problems += require(entry, where, ["id", "year", "title", "authors"])

    # sync_publications.py carries hand-edited titles forward by reading them
    # back out of this file with a regex. If the file's shape ever drifts the
    # regex quietly matches nothing and the next sync replaces every title with
    # INSPIRE's own capitalisation — no error, no change in the entry count.
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import sync_publications
    except ImportError as exc:
        return problems + [f"cannot import sync_publications.py: {exc}"]

    # Mirror the lookup build_entry() performs, not just one half of it.
    carried = sync_publications.load_existing_titles()
    lost = [e["id"] for e in entries
            if isinstance(e, dict) and e.get("id")
            and not (carried.get(e["id"]) or carried.get(e.get("arxiv")))]
    if lost:
        problems.append(
            f"publications.yml: sync_publications.py can no longer read the "
            f"titles of\n"
            f"      {len(lost)} entries ({', '.join(lost[:3])}"
            f"{', ...' if len(lost) > 3 else ''}).\n"
            f"      The next sync would overwrite them with INSPIRE's "
            f"capitalisation.\n"
            f"      load_existing_titles() expects lines of the exact form:\n"
            f"          title: \"...\"   (two spaces of indent, double quotes)")
    return problems


def check_profile():
    profile, problems = load("profile.yml")
    if problems:
        return problems
    if not isinstance(profile, dict):
        return ["profile.yml: expected a mapping."]
    return problems + require(profile, "profile.yml", [
        "name.ja", "name.en", "position.ja", "position.en",
        "institution.ja", "institution.en", "email", "bio.ja", "bio.en",
        "avatar",
    ])


def check_research():
    items, problems = load("research.yml")
    if problems:
        return problems
    if not isinstance(items, list):
        return ["research.yml: expected a list of research topics."]
    for i, item in enumerate(items, 1):
        where = f"research.yml topic {i}"
        if isinstance(item, dict) and item.get("id"):
            where = f"research.yml {item['id']}"
        problems += require(item, where, ["id", "title.ja", "title.en",
                                          "description.ja", "description.en"])
    return problems


def check_career():
    items, problems = load("career.yml")
    if problems:
        return problems
    if not isinstance(items, list):
        return ["career.yml: expected a list of positions."]
    for i, item in enumerate(items, 1):
        problems += require(item, f"career.yml entry {i}",
                            ["year", "title.ja", "title.en"])
    return problems


def main():
    problems = (check_teaching() + check_publications() + check_profile()
                + check_research() + check_career())
    if problems:
        print("data/ has problems the site would render as blank spaces:",
              file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print("data/ looks fine.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
