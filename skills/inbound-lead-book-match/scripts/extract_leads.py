#!/usr/bin/env python3
"""Extract inbound leads from a raw dump of Slack channel messages.

The messages come from whatever HubSpot workflow the user's ops team built, so
the format varies between portals. This parser leans on the two things that are
nearly always present -- an email address and some indication of whether a
meeting was booked -- and treats labelled fields like "Company:" as a bonus
rather than a requirement.

Usage:
    python3 extract_leads.py raw_messages.txt --out leads.json
    python3 extract_leads.py raw_messages.txt --since 2026-09-12T09:30:00-04:00
    cat messages.txt | python3 extract_leads.py - --out leads.json

Exit codes: 0 on success (even with zero leads found), 1 on unreadable input.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone

# Slack renders timestamps with a zone abbreviation rather than an offset.
# Getting this wrong is not a cosmetic bug: read "08:42 EDT" as UTC and a
# --since cutoff silently discards the four most recent hours of the window,
# which is exactly the "leads vanish and nobody notices" failure this whole
# check exists to prevent. Abbreviations are ambiguous in general (IST, CST),
# so the map covers the common unambiguous ones and anything else falls back
# to a naive wall-clock comparison, which at worst keeps a few extra leads.
TZ_OFFSETS = {
    "UTC": 0, "GMT": 0, "Z": 0,
    "EST": -5, "EDT": -4, "CST": -6, "CDT": -5,
    "MST": -7, "MDT": -6, "PST": -8, "PDT": -7,
    "AKST": -9, "AKDT": -8, "HST": -10,
    "BST": 1, "CET": 1, "CEST": 2, "EET": 2, "EEST": 3,
    "AEST": 10, "AEDT": 11, "NZST": 12, "NZDT": 13,
    "JST": 9, "KST": 9, "SGT": 8, "HKT": 8,
}

FREEMAIL_DOMAINS = {
    "gmail.com", "googlemail.com", "yahoo.com", "yahoo.co.uk", "ymail.com",
    "hotmail.com", "hotmail.co.uk", "outlook.com", "live.com", "msn.com",
    "icloud.com", "me.com", "mac.com", "aol.com", "comcast.net",
    "verizon.net", "att.net", "sbcglobal.net", "bellsouth.net", "cox.net",
    "protonmail.com", "proton.me", "pm.me", "gmx.com", "gmx.de", "mail.com",
    "zoho.com", "yandex.com", "yandex.ru", "qq.com", "163.com", "126.com",
    "fastmail.com", "hey.com", "duck.com", "tutanota.com", "web.de",
    "orange.fr", "free.fr", "libero.it", "naver.com", "hanmail.net",
}

# Slack wraps addresses as <mailto:a@b.com|a@b.com>; also catch bare addresses.
EMAIL_RE = re.compile(
    r"<mailto:([^|>]+)(?:\|[^>]*)?>|([A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,})"
)

# Trailing "[2026-09-14 08:42:15 EDT]" stamp that the Slack reader appends.
TIMESTAMP_RE = re.compile(r"\[(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\s+[A-Z]{2,5})?)\]")

LABEL_RES = {
    "name": re.compile(r"^\s*(?:lead\s+name|name|contact|full\s+name)\s*:\s*(.*)$", re.I),
    "company": re.compile(r"^\s*(?:company|account|organi[sz]ation|employer)\s*:\s*(.*)$", re.I),
    "email": re.compile(r"^\s*(?:email|e-mail|email\s+address)\s*:\s*(.*)$", re.I),
}

BOOKED_PATTERNS = [
    r"\bbooked\s+a?\s*meeting\b", r"\bbooked\s+a?\s*demo\b", r"\bmeeting\s+booked\b",
    r"\bscheduled\s+a?\s*(?:meeting|demo|call)\b", r"\bdemo\s+scheduled\b",
    r"\bbooked\s+time\b",
]
NOT_BOOKED_PATTERNS = [
    r"\bdid\s*n[o']?t\s+book\b", r"\bnot\s+book(?:ed)?\b", r"\bwithout\s+booking\b",
    r"\bno\s+meeting\s+booked\b", r"\bform\s+fill\b(?![^.]*\bbooked\b)",
]

BOOKED_RE = re.compile("|".join(BOOKED_PATTERNS), re.I)
NOT_BOOKED_RE = re.compile("|".join(NOT_BOOKED_PATTERNS), re.I)

# A message block ends where the next one begins. Channel dumps separate
# messages with blank lines, but a single lead notification also contains blank
# lines between its fields -- so split on the timestamp stamp that closes each
# message, and fall back to blank-line splitting when there are no stamps.
def split_messages(text: str) -> list[str]:
    if TIMESTAMP_RE.search(text):
        chunks, start = [], 0
        for m in TIMESTAMP_RE.finditer(text):
            chunk = text[start:m.end()].strip()
            if chunk:
                chunks.append(chunk)
            start = m.end()
        tail = text[start:].strip()
        if tail:
            chunks.append(tail)
        return chunks
    return [c.strip() for c in re.split(r"\n\s*\n\s*\n", text) if c.strip()]


def clean_email(raw: str) -> str:
    return raw.strip().strip("<>|,;\"'").lower()


def find_emails(block: str) -> list[str]:
    out = []
    for m in EMAIL_RE.finditer(block):
        addr = clean_email(m.group(1) or m.group(2) or "")
        if addr and "@" in addr and addr not in out:
            out.append(addr)
    return out


def labelled(block: str, key: str) -> str | None:
    """Pull a 'Label: value' field. HubSpot's Slack template often puts the
    value on the line after the label, so look ahead when the line is bare."""
    lines = block.splitlines()
    for i, line in enumerate(lines):
        m = LABEL_RES[key].match(line)
        if not m:
            continue
        value = m.group(1).strip()
        if not value:
            for nxt in lines[i + 1:]:
                nxt = nxt.strip()
                if not nxt:
                    continue
                if any(r.match(nxt) for r in LABEL_RES.values()):
                    break
                value = nxt
                break
        value = re.sub(r"<mailto:[^|>]+\|([^>]*)>", r"\1", value)
        value = TIMESTAMP_RE.sub("", value).strip()
        return value or None
    return None


def booked_state(block: str) -> bool | None:
    if NOT_BOOKED_RE.search(block):
        return False
    if BOOKED_RE.search(block):
        return True
    return None


def parse_stamp(block: str) -> str | None:
    m = TIMESTAMP_RE.search(block)
    return m.group(1).strip() if m else None


def stamp_to_dt(stamp: str | None) -> tuple[datetime | None, bool]:
    """Return (datetime, zone_known). When the zone abbreviation is recognized
    the datetime is a true UTC instant; otherwise it is naive wall-clock time
    and the caller must compare it against wall-clock, not against UTC."""
    if not stamp:
        return None, False
    m = re.search(r"\s+([A-Z]{1,5})$", stamp)
    abbr = m.group(1) if m else None
    core = re.sub(r"\s+[A-Z]{1,5}$", "", stamp).replace("T", " ").strip()
    try:
        naive = datetime.strptime(core, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None, False
    if abbr in TZ_OFFSETS:
        tz = timezone(timedelta(hours=TZ_OFFSETS[abbr]))
        return naive.replace(tzinfo=tz).astimezone(timezone.utc), True
    return naive, False


def parse(text: str) -> list[dict]:
    leads: list[dict] = []
    for block in split_messages(text):
        emails = find_emails(block)
        if not emails:
            continue
        # Prefer the address on an explicit Email: line; templates often show a
        # display name containing a different (personal) address first.
        preferred = labelled(block, "email")
        preferred = clean_email(preferred) if preferred and "@" in preferred else None
        email = preferred if preferred in emails else emails[-1]

        domain = email.split("@")[-1].lower().removeprefix("www.")
        name = labelled(block, "name")
        if name:
            name = re.sub(r"\S+@\S+", "", name).strip(" -–—,")
        leads.append({
            "name": name or None,
            "company": labelled(block, "company") or None,
            "email": email,
            "domain": domain,
            "is_freemail": domain in FREEMAIL_DOMAINS,
            "booked_meeting": booked_state(block),
            "timestamp": parse_stamp(block),
            "raw": " ".join(block.split())[:600],
        })
    return dedupe(leads)


def dedupe(leads: list[dict]) -> list[dict]:
    """One entry per email. Keep the earliest sighting, but let a booked
    meeting win over a form fill -- someone who filled a form and then booked
    should read as booked."""
    by_email: dict[str, dict] = {}
    for lead in leads:
        prior = by_email.get(lead["email"])
        if prior is None:
            by_email[lead["email"]] = lead
            continue
        if lead["booked_meeting"] and not prior["booked_meeting"]:
            lead["timestamp"] = prior["timestamp"] or lead["timestamp"]
            by_email[lead["email"]] = lead
        elif not prior.get("company") and lead.get("company"):
            prior["company"] = lead["company"]
    return list(by_email.values())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="Text file of channel messages, or - for stdin")
    ap.add_argument("--out", help="Write JSON here (default: stdout)")
    ap.add_argument("--since", help="Drop leads with a timestamp before this ISO 8601 moment")
    args = ap.parse_args()

    try:
        text = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    except OSError as exc:
        print(f"Could not read input: {exc}", file=sys.stderr)
        return 1

    leads = parse(text)

    if args.since:
        try:
            cutoff = datetime.fromisoformat(args.since)
        except ValueError:
            print(f"Ignoring unparseable --since value: {args.since}", file=sys.stderr)
            cutoff = None
        if cutoff is not None:
            cutoff_utc = (cutoff.astimezone(timezone.utc) if cutoff.tzinfo
                          else cutoff.replace(tzinfo=timezone.utc))
            cutoff_wall = cutoff.replace(tzinfo=None)

            def keep(lead: dict) -> bool:
                dt, zone_known = stamp_to_dt(lead["timestamp"])
                if dt is None:
                    # Unparseable timestamp: keep it. A stray old lead in the
                    # report is a nuisance; a silently dropped new one is the
                    # failure that makes someone stop trusting the check.
                    return True
                return dt >= (cutoff_utc if zone_known else cutoff_wall)

            leads = [l for l in leads if keep(l)]

    leads.sort(key=lambda l: (l["booked_meeting"] is not True, l["timestamp"] or ""))
    payload = json.dumps(leads, indent=2, ensure_ascii=False)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(payload + "\n")
        booked = sum(1 for l in leads if l["booked_meeting"] is True)
        unclear = sum(1 for l in leads if l["booked_meeting"] is None)
        print(f"{len(leads)} leads ({booked} booked a meeting, {unclear} unclear) -> {args.out}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
