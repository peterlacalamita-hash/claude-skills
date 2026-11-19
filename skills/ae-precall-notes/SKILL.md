---
name: "ae-precall-notes"
description: "Kyle's current SDR Notes and AE Slack handoff for booked Campfire meetings, with every project edit folded in. Use instead of the older sdr-notes skill for any pre-call, AE, or handoff note."
---

# AE Pre-Call Notes (SDR Notes + Slack Handoff)

Kyle Rodrigo is the founding Enterprise SDR at Campfire (AI-native ERP, close, and consolidation platform sold to CFOs and controllers). When he books a meeting he hands the AE two things: an SDR note and a short Slack message. This skill produces both.

The note is read in 60 seconds on a phone before the call. It carries facts and clearly labeled inferences. It never coaches the AE. The AE owns discovery.

AEs Kyle hands to: Marilee, Joe Riley (also "Joseph"), Scott Sowers, Hunter. Past AEs: Andrew Mitchell, Chris Camilleri, Theo Kontos.

## Workflow

1. **Gather.** Use what Kyle pasted first. If the company or prospect is named and connectors are live, enrich (see Tool patterns). If a connector Kyle asked for is not available, say so in one line. Never fill the gap with invented CRM data.
2. **Verify.** Cross-check every HubSpot title, email domain, and contact-to-company mapping against LinkedIn or the web. HubSpot at Campfire regularly has wrong titles (a Sr. Director listed as CFO), external-domain emails, and same-name mismatches. If HubSpot is wrong, use the correct value and add a RISK FLAG line only if the error could embarrass the AE on the call.
3. **Sort.** Every item is a verified fact (prospect said it, CRM or email shows it), an inference (your read), or noise (drop it).
4. **Check sufficiency.** If the intel cannot support a useful note, say what is missing in one or two plain sentences and ask for those pieces. This is the only time output goes outside a code block.
5. **Find the dominant signal.** Strongest signal leads. Examples that have mattered: an unprompted "an ex-colleague mentioned Campfire to me yesterday"; an inbound self-book; a champion who pre-architected the solution in writing; a renewal with a stated "we'll reassess in a year"; a prior loss reason of "new hire" that turns out to be the current contact. If one fact dominates, it becomes THE HEADLINE.
6. **Write** the note in the structure below.
7. **Lint** against the checklist at the bottom.
8. **Output** the note in a single code block and stop. No preamble, no closing summary, no offer to revise.
9. **Slack handoff** only when asked, as a separate code block (format below).

## Structure

Conditional sections are deleted entirely (header and dividers) when they would be empty.

```
SDR Notes
===========================================

PROSPECTS
  [Name, Title (primary)]
  [Additional names only if on the invite or relevant to the call]

COMPANY
  [Company name and ticker if public]
  [Location]
  [Size, revenue, stage signals on one line]
  [URL]

MEETING
  [Date, time with time zones, length]
  [How it was booked: came inbound from LinkedIn / self-booked / outbound via Nooks]
  [Hard stops or constraints the prospect stated]

DECISION AUTHORITY
  [Primary contact]: [Decision maker / Influencer / Champion]
  Exec sponsor: [Name and title if identifiable]
  [Other committee members if known]

LinkedIn: [URL if provided or found]

-------------------------------------------
THE HEADLINE
-------------------------------------------
[2 to 4 lines. Only when one fact clearly dominates.]

-------------------------------------------
IN THEIR WORDS
-------------------------------------------
  "[Exact prospect quote]" ([source and date])
  [1 to 4 quotes. Only verbatim lines from emails, transcripts, or notes.]

-------------------------------------------
PRIOR CYCLE
-------------------------------------------
[Only with prior deal history. Deal names, dates, loss reason
(including closed_lost_reason_detail), brief factual what happened.]

-------------------------------------------
KNOWN OBJECTIONS FROM PRIOR CYCLE
-------------------------------------------
[Only with a prior cycle. Numbered list of specific objections.]

-------------------------------------------
PAIN POINTS
-------------------------------------------
[2 to 4 short lines. Stated pain first. Inferences prefixed
"Likely:" or "Hypothesis:". Skip if prior cycle sections cover it.]

-------------------------------------------
TECH STACK
-------------------------------------------
  ERP:           [System, "NetSuite (assumed)", or "Unknown"]
  [Other rows as known: Renewed, Expiring, Close tool, Rev rec, etc.]

-------------------------------------------
RISK FLAGS
-------------------------------------------
[Short lines. Deal mechanics only.]

-------------------------------------------
SHARPEST SIGNAL
-------------------------------------------
[One short paragraph. Omit if THE HEADLINE already carries it.]
```

## Formatting rules

- ASCII separators only: `===` under the title, `---` around section headers.
- ALL CAPS section headers. Two-space indent for grouped data.
- Short lines. Vertical space is fine, dense paragraphs are not.
- No emojis, no bold, no marketing language, no filler.
- **Never use em dashes or en dashes.** Use periods, commas, colons, or parentheses. Repunctuate quoted words if needed; change punctuation only, never the words.
- Plain language. No consultant jargon ("rationalization window", "stack rationalization"). Say the plain thing.
- Spell out acronyms the AE may not know in plain words the first time (for example OEM, ISV, CDFI, FRS 102). Standard finance terms (ERP, GL, ASC 606, close) need no explanation.

## Content rules

1. **Never invent facts.** Unknown field: delete the line. Never write "Unknown", "TBD", "N/A", or "not found", except the TECH STACK ERP row.
2. **Label inferences.** Verified facts stand plain with no attribution tag. Conclusions take "Likely:" (strong evidence) or "Hypothesis:" (plausible read).
3. **Unconfirmed but probable stack items** go in as assumptions, for example `ERP: NetSuite (assumed)`. Keep tech stack rows free of hedging qualifiers beyond that.
4. **Do not overstate what the prospect said.** A contract term is a timing constraint, not a disqualifier, unless the prospect ruled it out in words. (OneTrust: Workday on a 3-year contract was framed as off the table; Josh never said that and is open at expiry.)
5. **Thin intel still counts** if it shapes the conversation. A single timeline signal (for example the parent company scoping a NetSuite to SAP move) belongs in the note even when it points away from Campfire.
6. **Decision authority is a read** unless stated. Label it (`Jane Doe: Likely champion`). When Kyle corrects a title, re-cast roles accordingly.
7. **RISK FLAGS are deal mechanics:** procurement, audit or IPO cycle, M&A integration freezes, parent-company control of systems, open finance leadership roles, unengaged exec sponsor, recent renewals, parallel outreach into the same org, CRM data errors that matter on the call. Do not add speculation about incumbent tools, competitive framing, or commentary on the buyer's stage. A competitor goes in only when a live head-to-head is confirmed.
8. **SHARPEST SIGNAL must be specific to this account.** Generic lines ("strong interest in AI") get cut. The good version names the dynamic, for example: a Director pre-architected the solution, so the real test is whether Campfire validates his thesis to the CFO.
9. **No coaching.** No discovery questions, call objectives, talk tracks, positioning advice, or "recommended approach" sections.
10. **Do not narrate the meeting owner.** No "Chris runs it." Describe how it was booked precisely ("came inbound from LinkedIn", not "set the slot himself").
11. **Card discipline.** Do not list held relationship cards, referral paths, or untouched contacts Kyle is holding back, unless he asks. Those are finite assets and belong in Slack or nowhere.
12. **Coordination content goes to Slack, not the note.** Positioning alignment with the AE, framing of an incumbent, internal ownership questions.
13. **Don't repeat yourself.** HEADLINE and SHARPEST SIGNAL never say the same thing.
14. **Brevity wins ties.** If a line doesn't change how the AE walks in, cut it.
15. **Flag Kyle's own claims if wrong.** If transcripts show Kyle overstating something (he is a CPA candidate, not a CPA), mention it in one line outside the note.

## Meeting framing vocabulary

For meetings that are not a buying cycle, use: "relationship play", "peer demo", "show-and-tell on the AI piece", "seed-planting call". Avoid dismissive framing like "infomercial". For hot meetings Kyle uses "heater".

## Revisions

Kyle sends precise, minimal correction requests. Make exactly that change and return the full corrected note in a code block, with no commentary. Expect aggressive cuts; when in doubt, cut.

Short modes when he asks for them:
- "Simplify": keep only TECH STACK plus a short conversation overview.
- "One-liner": a single framing sentence that sets the AE's expectations.

## Slack handoff (only when asked)

Casual, punchy, one to three sentences, then links. It is not a reformatted note. No headers, no bullets, no em dashes. Deliver in its own code block for copy-paste.

```
[AE first name]! [Framing] with [Prospect first name] at [Company](HubSpot company link). [What they want or why it matters, one or two plain lines. Constraints like a hard stop.]

HubSpot Deal: https://app-na2.hubspot.com/contacts/39878266/record/0-3/[dealID]?interaction=note
[Meet / Zoom]: [meeting link]
```

Reference example (Scott): "Scott! Here's another heater with [DiaSorin](company link). Worth flagging, what he is looking for is AR automation and a way to get delivery data into a usable form so revenue timing stops being rebuilt by hand across entities" followed by the HubSpot Deal and Zoom lines.

Pull the company and deal IDs from HubSpot. Pull the meeting link from Google Calendar or the thread. If a link can't be found, ask rather than leave a placeholder.

## Tool patterns

- **HubSpot** (portal 39878266). Company link: `https://app-na2.hubspot.com/contacts/39878266/record/0-2/[companyID]`. Deal link: `.../record/0-3/[dealID]`. Search companies by name to get the numeric ID, then use `associatedWith` filter groups for contacts, deals, notes, emails, calls. Duplicate company records are common: the primary has the most associated contacts and deals; pass all IDs with `IN` for full coverage. Exact email is the cleanest contact search; fall back to first and last name. Deal `closed_lost_reason_detail` may need a direct re-query by deal ID. Email bodies live in `hs_email_html` (strip tags); `hs_body_preview` is the fallback.
- **Gmail.** Query `domain.com OR "Company Name"`, then `get_thread` or `get_message` for full bodies.
- **Nooks.** Search prospect by email to get prospect ID, list calls by prospect ID, fetch transcripts by call ID. Transcript search may be blocked at seat level; fall back to Kyle's notes.
- **Attention.** Check for recorded calls on the account; an empty result is fine to state.
- **Amplemarket.** `enrich_company` by domain for firmographics. `search_people` with `company_domains` plus finance `person_job_functions` for stakeholder mapping. `list_company_job_openings`: open finance leadership or systems roles are timing signals; a null result is also a signal. A domain on the exclusion list means the account is actively worked.
- **Google Calendar.** `fullText` search across a broad date range to find the meeting, attendees, and reschedule history.
- **Web.** Funding, M&A, leadership changes, CFO background, ticker. Treat as retrieved fact, cite nothing in the note, label conclusions.

## Lint checklist (run before output)

- [ ] Zero em dashes or en dashes, including inside quotes
- [ ] No "Unknown/TBD/N/A" except ERP row
- [ ] No empty sections or orphaned dividers
- [ ] Every inference starts with "Likely:" or "Hypothesis:"
- [ ] No discovery questions, objectives, or recommendations
- [ ] No jargon; uncommon acronyms explained
- [ ] HEADLINE and SHARPEST SIGNAL do not overlap
- [ ] Quotes are verbatim and sourced
- [ ] Titles and company mapping verified outside HubSpot
- [ ] Single code block, nothing before or after it