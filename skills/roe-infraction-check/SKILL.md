---
name: "roe-infraction-check"
description: "Campfire SDR attribution in one skill: audit mode sweeps a rep's book (or the team's) for meetings and deals this month booked by someone else with missing or foreign SDR credit, including the HubSpot \"Hot Soup\" logic; check mode builds the ROE case for one account and drafts the ask to Jake. Never sends."
---

# ROE Infraction Check

Two modes, one skill.

| Mode | Trigger | Output |
|---|---|---|
| **Audit** | "audit my book", "book audit", "attribution sweep", "run my hot soup", "find meetings on my accounts I didn't get credit for", or no account named | Ranked candidate table for the month, watch list, dropped list |
| **Check** | An account, deal or meeting is named: "ROE check on X", "is X an infraction", "should I get credit for X" | Verdict, evidence table, risks, draft message to Jake and Patrick |

Audit feeds Check: run Audit, then Check on the top candidates. Works for any Campfire SDR; identity is resolved at run time.

**Authority:** Jake Thompson (Head of SDR) is the final word on ROE and attribution. Patrick Williams and Trevor Lindemann are SDR leaders who escalate to him. The skill builds the case; Jake decides. Never present a verdict as settled policy.

**Never send anything.** Output is a draft. Slack drafts only if the rep asks, and only to the channel or DM they name. Read-only in HubSpot, Attention and Amplemarket.

---

## Step 0. Scope and policy refresh

| Input | Default | How to resolve |
|---|---|---|
| Rep | The invoking rep | `mcp__HubSpot__get_user_details` for owner ID and full name (what `sdr_sourced` stores). Example: Kyle Rodrigo = 162726725. |
| Team mode (Audit only) | Off | "all SDRs" or a list of names. `SELECT sdr_owner, COUNT(*) FROM COMPANY GROUP BY sdr_owner`, then `search_owners` on the IDs. Run once per rep. |
| Month | Current calendar month | Meetings with `hs_timestamp` in the month. Deals created or entering Product Demo since the first of the **prior** month, because prior-month bookings flip to SQO this month. |

The ROE lives in a Notion doc and in Slack rulings, and it changes. Before applying the knowledge base at the bottom:

1. Notion: fetch the Rules of Engagement page (https://www.notion.so/meetcampfire/Rules-of-Engagement-SDR-34f4fe173c4a80b1bd6dd5bfb3e4ce0d) if the connector is connected. If it shows needs_reconnect, say so and continue.
2. Slack: search public and private, sorted by timestamp, for `ROE`, `"rules of engagement"`, `attribution`, `"SDR Owner"`, `"meeting credit"`, and `from:` Jake, Patrick, Trevor since the newest date in the knowledge base. Read threads where Jake replied; his replies change rules (e.g. "ignore Acquisition Channel").
3. A newer ruling wins. Tell the rep what changed and offer to update this skill.

State the scope in one line, create a task list, then start.

---

## Audit mode

### A1. Two pulls (HubSpot SQL, never search)

A book is 2,000+ accounts; `search_crm_objects` pages 200 at a time and blows the context. Use `mcp__HubSpot__query_crm_data` (call `tool_guidance` once first).

**Meeting sweep** (catches bookings with no deal, which Hot Soup cannot see):

```
SELECT hs_object_id, hs_meeting_title, hs_timestamp, hs_createdate, hubspot_owner_id, hs_meeting_outcome, hs_created_by_user_id, COMPANY.name, COMPANY.hs_object_id, COMPANY.hubspot_owner_id FROM MEETING WHERE COMPANY.sdr_owner = '<OWNER_ID>' AND hs_timestamp >= '<YYYY-MM-01>' ORDER BY hs_timestamp DESC LIMIT 300
```

**Hot Soup pass.** Mirrors the team's HubSpot "ROE Hot Soup" segments (Kyle's is list 3161; most SDRs have a clone named with their initials). Segment logic: account where `sdr_owner` = the rep, AND an associated deal was created OR entered Product Demo in a window, AND that deal's `sdr_sourced` is not the rep. The lists use a rolling window of about 7 days, so never rely on the list for a monthly audit. Reproduce it month-to-date:

```
SELECT hs_object_id, dealname, dealstage, pipeline, createdate, hs_date_entered_226142785, hubspot_owner_id, sdr_sourced, sourced_by__gtm_motion_, COMPANY.name, COMPANY.hs_object_id, COMPANY.hubspot_owner_id FROM DEAL WHERE COMPANY.sdr_owner = '<OWNER_ID>' AND sdr_sourced != '<Rep Full Name>' AND createdate >= '<first of prior month>' ORDER BY createdate DESC LIMIT 150
```

`!=` returns blank attribution and other names. Blank is the Collectors/Tide pattern; another SDR's name is the Docker pattern. Keep rows where `createdate` or `hs_date_entered_226142785` falls in the window. To compare against the rep's actual list, preview it with `query_segments` (`IN_LIST(list = <id>)`).

Resolve unfamiliar owner IDs with one batched `search_owners`. Keep the map; AE vs SDR decides the case.

Known gap: a meeting associated only to a contact and not the company is missed. If a known call is absent, search MEETING associated to the attendee contact IDs.

### A2. Strip the noise

Drop: deals with Acquisition Channel Partnerships (list under dropped with the channel; Inbound on the rep's book is a case C candidate, not noise); partner and implementation accounts (Connor Group, Deloitte, HCVT, ADP, Wipfli, Paylocity integrations) and titles with Weekly Sync, Status Call, Kickoff, KT, Internal, Office Hours, POC, or Implementation Pipeline; webinars and vendor calls (Zoom, Sybill, Notion POC); duplicate summary rows ("Meeting Summary via sybill.ai", "[Granola]"); meetings the rep created and deals already attributed to the rep; meetings dated after today (watch list); mis-associated junk companies.

### A3. Classify

Merge the two pulls by company and fill, per candidate: booker (`hs_created_by_user_id`, never the attendees), booker role, AE company owner and `hubspot_owner_assigneddate` (blank or same-day as deal creation = GitLab pattern), deal state (none / blank / foreign name), stage dates, Attention confirmation (`search_calls` by title and CRM account name, candidates only), and the rep's **owned** touches (EMAIL and CALL associated to the company, filtered on `hubspot_owner_id` = the rep, with last pre-booking touch and gap in days).

Assign a case letter (Check mode table) and strength: **Strong** (A or B, 8+ owned touches, activity inside 14 days of meeting creation, no deal or blank or foreign attribution), **Moderate** (A or B with thin or stale touches), **Drop** (booker sourced it on their own thread and the rep has one or two touches; Partnerships; already attributed).

### A4. Output

1. Scope line (rep, month, accounts, meetings and deals pulled, Hot Soup list ID if compared).
2. Candidates table, strongest first, with HubSpot links. Flag anything time-sensitive at the top: a meeting today, a deal not yet created.
3. Watch list: future meetings on the book created by someone else; Meeting Booked deals older than 14 days; prior-month deals that entered Product Demo this month without attribution.
4. Checked and dropped, one line each with the reason.
5. Peers working the account: another SDR's owned emails or sequences into the book (Unify sends owned by another rep). That is its own issue under Jake's Oct 27 PSA.
6. Offer to run Check mode on the top candidates and draft one bundled message.

Team mode: one table per rep, then a roll-up by booker. Do not rank reps against each other.

---

## Check mode

### C1. Facts (read-only, in parallel)

| Fact | Where | Gotcha |
|---|---|---|
| SDR Owner | Company `sdr_owner` | Contact owner is legacy. Ignore it. |
| AE company owner | Company `hubspot_owner_id`, `hubspot_owner_assigneddate` | Blank = unowned. Same-second as deal creation = AE self-assigned. |
| Who booked | Meeting `hs_created_by_user_id`, `hs_createdate`, `hs_meeting_source`, `hs_attendee_owner_ids`; resolve with `search_owners` | Do not infer from attendees. Collectors (Oct 2026): Sultan attended, Andy booked. |
| Meeting created date | Same record | The 14-day test runs from creation. State the margin in days. |
| Deal | By name, by company, by attendee contacts | `sdr_sourced` and `sourced_by__gtm_motion_`. No deal is itself a finding. |
| Channel | Deal channel; contact `hs_object_source_detail_1`, `hs_analytics_source`; inbound channels (#inbound-leads, #gated-content-leads, Champagne bookings) | Decides which test applies. |
| Rep's touches | EMAIL and CALL associated to the company, **filtered on `hubspot_owner_id` = the rep** | Unify and Data Tools sends owned by others are not touches. Smile Doctors (Oct 2026): 14 emails counted that belonged to Trevor. Amplemarket skipped steps are not touches. Exclude personal addresses. |
| Data issues | Duplicate company records; attendee's company and email domain; Amplemarket `owner_email` on the account | Amplemarket maps HubSpot AE owner, not SDR Owner, so accounts look unowned to other reps. Explains collisions; does not change the rule. |
| The call | Attention `search_calls` (title + CRM account), `get_call_details` | Outcome, attendees, any mention of sourcing. |
| Precedents | The rep's prior flags in Slack DMs with Jake or Patrick; then `sdr_sourced` on those deals | A resolved precedent with the same AE or setup is the strongest evidence. List unresolved ones too. |

### C2. Classify

| Case | Booker | Account | Governing rule |
|---|---|---|---|
| A. AE booked on SDR's book | AE | Rep is SDR Owner; AE owner blank or self-assigned after the rep's activity | Jake Sep 23 flag process + Oct 27 symmetry. Strongest case. |
| B. OB vs OB | Another outbound SDR | Rep is SDR Owner | ROE Rule 5: credit to the account owner. No touch or recency test. |
| C. IB vs OB | Inbound SDR, inbound demo request, Champagne booking | Rep is SDR Owner | Jake Oct 27: rep needs 8 touches AND activity within 14 days of meeting creation. |
| D. Rep on AE-owned account | The rep | AE is company owner, rep not SDR Owner | Oct 27 PSA: credit goes to the AE unless the rep had written permission and was made SDR Owner. |
| E. Unclear | Unknown | Any | Do not assert a case. Ask the AE or Jake how it was sourced first. |

If the booker or channel is unconfirmed, say so and stop short of calling it an infraction.

### C3. Output

1. Verdict line: case letter, whether the rep likely has a claim, the one fact it hinges on.
2. Evidence table: test, requirement, rep's record, pass/fail, HubSpot links.
3. Risks: thin margins, unconfirmed booker, stale rule text, anything Jake could cite against it, and the rep's own exposure (e.g. sequencing into an account with an active AE deal).
4. Draft to Jake (cc Patrick), audited with the outreach-ai-audit copy rules: no em dashes, no hedges on the core claim, max two parentheticals, asks framed as asks not questions, HubSpot company and deal links, under 90 words. Structure: what was booked and by whom, ownership and activity, precedent, the ask (create the deal / set SDR Attribution). Bundle unresolved precedents.
5. If the rep chooses to concede (quota optics, systems gap), draft the concession so it is logged as a one-time exception and not a precedent, plus a one-line heads-up to the peer.
6. Offer to save as a Slack draft. Recommend a fresh group DM with only Jake and Patrick, or the existing attribution thread if one is open.

---

## Knowledge base (as of Oct 28, 2026; refresh in Step 0)

| Date | Source | Rule |
|---|---|---|
| Apr 28, 2026 | Adarsh, #sdr | ROE doc launched in Notion. 30-day engagement period went live after the Amplemarket rollout. |
| May 4, 2026 | Harry To, #sdr-channel (ROE changelog) | Rule 5: meeting credit goes to the account owner if a meeting is booked on someone else's account. Rule 6: if you're working an account, put it in your name, all tiers; Tier 3 needs logged activity to hold; blank accounts are fair game. |
| Sep 23, 2026 | Harry To for Jake, #all-sdr | SDRs should find deals on their accounts where an AE outbounded and booked after book distribution without SDR credit, and flag them to Jake (CSV preferred). Jake: ignore Acquisition Channel and review everything booked on your accounts. |
| Sep 23, 2026 | Precedent: GitLab | Andy Mitchell self-assigned company owner 9/9 and created the deal 9/10 on Kyle's book. Flagged; SDR Attribution = Kyle Rodrigo. |
| Sep 23, 2026 | Precedent: Tide, Apollo | Flagged the same day; still blank as of Oct 28. Acknowledged ("sounds good") but never actioned and never captured in a 1:1 doc. Ask for a decision with a date, not an acknowledgment. |
| Oct 21, 2026 | Trevor, #sdrs-gtme | Applied "normal RoE" as contact within 14 days and 4 touches on a different dispute. Not reconciled with Jake's 8-touch test. |
| Oct 26 to 27, 2026 | Docker group DM (Patrick, Jake, Hannah, Kyle) | Patrick applied the OB ROE to keep Docker with Kyle. Jake overruled: the OB ROE is for OB vs OB only; Hannah's Champagne bookings are IB demo requests, so the rep needed 8 touches AND activity within 14 days of meeting creation. Kyle had no activity in 14 days; Hannah kept credit. |
| Oct 27, 2026 | Jake, #all-sdr PSA (enforced) | SDRs may not work AE-owned accounts without the AE's explicit permission and being made SDR Owner by Adarsh or an SDR leader. If broken, ownership is stripped and credit goes to the AE, "same as we would if they booked on one of your accounts" (symmetric). |
| Oct 28, 2026 | Patrick, attribution group DM | Attribution is logged on a BizOps sheet, not only on the deal field. Setting `sdr_sourced` does not finish the job; Patrick's entry does. |
| Oct 28, 2026 | Precedent: Collectors | Andy booked (10/19) and ran (10/23) an intro on Kyle's book with no deal. Flagged with 29 touches; Patrick logging to BizOps, Jake pending. |
| Oct 28, 2026 | Precedent: Smile Doctors | Bianca (outbound SDR) booked on Kyle's book; the account showed `owner_email: null` in Amplemarket because SDR Owner does not sync. Kyle conceded as a one-time exception for optics; systems gap raised for Adarsh. |

### Other context

- Enterprise meeting attribution requires 8 touches on the account for an SDR to claim a meeting (Kyle, Oct 2026).
- SDR ownership is decided by SDR Owner on the company record; account claims follow activity ownership, not contact ownership.
- AE company owner (`hubspot_owner_id`) is always an AE at Campfire; SDRs are identified only by `sdr_owner`.

## Field and ID reference (Campfire HubSpot, portal 39878266)

- Company: `sdr_owner`, `hubspot_owner_id` (AE), `hubspot_owner_assigneddate`. Deal: `sdr_sourced` (rep full name), `sourced_by__gtm_motion_` (Outbound, Inbound, Partnerships, Event), `hs_date_entered_226142785` (Product Demo entry), `hs_v2_date_entered_current_stage`.
- Pipelines: Qualification 2445405889 (Meeting Booked 4046476020 = SAO, Disqualified 4045098726), Sales default (Product Demo 226142785 = SQO, Solutioning 226142786, Pricing and Negotiation 3442856680), Implementation 2172348152.
- Hot Soup segments: `query_segments` search "Hot Soup"; Kyle's is list 3161.
- Links: company `https://app-na2.hubspot.com/contacts/39878266/record/0-2/<id>`, deal `.../0-3/<id>`, contact `.../0-1/<id>`; Attention `https://app.attention.tech/conversations/<id>`.

## Lessons (the oops list)

- Hot Soup needs a deal to exist and looks back about a week. The meeting sweep and a month-to-date window cover what it misses.
- `sdr_sourced` can be blank or another rep's name. Both are findings; say which.
- Filter touches by email owner, not by company association. Shared accounts carry other reps' Unify sends.
- Check `hs_created_by_user_id` on the meeting before naming a booker. Attendance is not sourcing.
- Don't cite Rule 5 for an AE booking; use Jake's AE-booking process. Don't apply the IB 8/14 test to an OB vs OB case; Jake drew that line himself on Docker.
- Don't quote a rule back to Jake as a gotcha. Lead with process and precedent; hold the rule text for pushback. Rule text from old changelogs may be stale; flag it as unverified unless confirmed.
- Deal creation month decides the booking month. Stage-flip month is a question for Jake. A deal that does not exist yet is the most time-sensitive finding; raise it the same day, before the demo.
- Message the AE before creating a deal on their name, even with manager support.
- A flag that gets "sounds good" is not resolved. Ask for a decision with a date and track open asks in one place.
- Keep unrelated people out of the thread (e.g. a Collectors case does not belong in the Docker DM with Hannah).
- Don't draft prospect outreach on an account with an active AE motion. Run Check first.
- Run Audit around the 25th and again on the first business day for the prior month.