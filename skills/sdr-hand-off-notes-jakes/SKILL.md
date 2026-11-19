---
name: "sdr-hand-off-notes-jakes"
description: "Jake's team-standard version. Generate SDR Hand-Off Notes for a just-booked meeting as a skimmable AE briefing (what we know, open questions, relevant context) backed by a full HubSpot record, combining booking context with Campfire's enriched data (CRM, Closed-Lost history, calls, email, LinkedIn, recent wins). Checks SAL (Stage 1 Deal) criteria and makes the SDR confirm every SAL qualification requirement. Use when a Campfire SDR asks to write up hand-off notes, prep the AE, document the call, or hand a booked meeting to an AE."
---

# SDR Hand-Off Notes (Jake's)

The skill works like an intelligence analyst, not a sales manager. It does deep research behind the scenes, then presents it so an AE who only skims the top still understands the opportunity: what we know, what's still open, and the qualification risks. It surfaces what was learned. It never tells an experienced AE how to run Discovery.

There are two outputs with different jobs:
- **Slack** is the 30-second read: Deal Introduction, a one-line SAL alert if anything failed, the AE Briefing, and a link to the full notes.
- **HubSpot** (the deal's SDR Notes field) is the complete source of record: everything in Slack plus the formal SAL documentation and all supporting research.

The baseline standard from Campfire's Back-End Qualification training still holds: **if the AE has to ask it again, the hand-off failed.** Brevity changes where information appears, never whether it's captured.

The note also carries Campfire's **SAL (Stage 1 Deal) criteria** (effective November 2, 2026): the three gates (Access to Authority, Firmographic Fit, Demo Booking Window) and the six **Section 4 Qualification Needs** that every SAL must have in the Hand-Off Notes. Every requirement must be visibly answered or visibly marked "Not yet qualified," so the record is complete for whoever reviews it.

## Required inputs

**Time cutoff:** The note is the pre-meeting hand-off, so only use activity dated before the booked meeting's start time. If the skill is re-run after the meeting has happened, ignore the AE's own calls and emails from that meeting onward, and say so in the note.

Before drafting, confirm you have (or can get) these ten sources. Don't skip straight to drafting if one is missing — go get it, or flag it per the rules below.

1. **CRM firmographics (HubSpot)** — pull these, don't ask the SDR to repeat them:
   - Industry: **Industry Category L1** (`industry_category`, e.g. Retail & Consumer) and **Industry Category L2** (`industry_category_level_1`, e.g. Apparel & Fashion)
   - Account score
   - Headcount, revenue, country
   - Funding stage, whether currently raising, investors
   - Contact's title, seniority, persona
   These fields are typically already well-filled in HubSpot — the goal here is to retrieve them silently, not to spend SDR time confirming what the system already knows.
   Also check the L1/L2 industry against the SAL **Red** list (see Step 2d). Many accounts are tagged "Other" or have no L2, so treat the HubSpot tag as a lead, not a verdict.

   **Then enrich the company in Amplemarket** for:
   - Department headcount, especially finance and accounting. Use it as an estimate for Finance Team Size, labeled "(Amplemarket estimate, confirm)", until the prospect states the real number.
   - Detected technologies. Accounting or ERP tools found there (NetSuite, QuickBooks, Sage, etc.) are a lead for Current Tech Stack, labeled as detected, never as confirmed.
   - Open job openings, especially in finance and accounting. Active finance hiring is a possible compelling event.

2. **Closed-Lost context (HubSpot)** — for this exact company only (no comparable-account lookback):
   - Prior deal stage history and close/lost reason field
   - The objection or blocker recorded in deal notes at the time it stalled
   - Who previously worked the deal (rep), and roughly when
   - Deal amount and products/features discussed, if on record
   - Any competitor mentioned as the reason it was lost
   If there's no prior deal on this company, state that plainly rather than leaving the section implicitly blank.

   **When there is a prior deal, check Attention.** Search Attention for recorded calls with this company (by company name, contact, or opportunity) and pull what was actually said:
   - The objections or concerns the prospect raised, in their words
   - Which stakeholders were on those calls and what each cared about
   - What Campfire pitched or committed to, and where the conversation stalled
   - Anything the prospect said about timing ("revisit next year," "after our audit")
   Treat the recordings as the primary Closed-Lost source, ahead of the HubSpot lost-reason field, which is often blank or just says "timing." If the recordings and the lost-reason field disagree, show both. Use this to tell the AE what to avoid repeating and what may have changed since then.

3. **Booking context** — pulled from the calendar invite and whatever the SDR entered at time of scheduling:
   - Prospect attendee names, titles, and emails (exclude all Campfire personnel — the AE already knows who's on their side)
   - Meeting date/time
   - The booked contact's email domain. A personal or free address (e.g. @gmail.com) fails SAL Gate 1 (see Step 2d).
   - The date of the SDR's qualifying conversation (the day Gates 1 and 2 were confirmed), usually the connected call or the booking note's date. Needed for the 30-day booking window in Gate 3. If it's unclear, ask the SDR.
   - The SDR's own booking notes, read from the deal property **SDR Notes - If applicable** (`sdr_notes`). Always read this field first. It's often short, but it can hold the highest-signal context in the whole note (prior system history, competitors they're looking at, how cautious they are). Fold everything in it into the hand-off, since the finished note will replace it in Step 7.

4. **Call data (Nooks)** — the cold call(s) that led to the booking. Get the content in this order:
   1. **Nooks transcript.** Find the prospect's calls with the Nooks connector (search by prospect or account; prioritize connected calls with real duration over no-answers) and pull the transcript. This is the default source. HubSpot's "[Nooks Call]" logs are only a pointer to the call, never a substitute for it.
   2. **No transcript available.** Transcripts can lag the call by several hours, and they only exist for reps with a Nooks AI Coaching seat. If the booking call has no transcript, prompt the SDR: "The transcript for your call with [prospect] isn't available yet. Can you download the call recording from Nooks and upload it here?" When they upload it, transcribe the audio in the container (e.g. faster-whisper with ffmpeg) and extract from that. The audio transcription has no speaker labels, so tell rep and prospect apart from context, and only attribute a statement to the prospect when it's clearly theirs.
   If the only calls on record are no-answers or voicemails (the meeting was booked through another channel, like LinkedIn or a referral), don't ask for a recording. There's no conversation to analyze, so treat the call-dependent fields as gaps (see Step 5).
   3. **SDR can't upload it.** Mark the call-dependent gaps "(call transcript pending)," so the SDR knows to re-run the skill once the transcript lands.

   From whichever source, extract anything that answers the SAL Section 4 Qualification Needs (Step 2c) and the Gate 1 authority check, plus:
   - Whether a consultant/implementation partner is involved
   - Days to close the books (flag if over 4 days)
   Treat these as the highest-value extraction target from the call — they're the fields HubSpot almost never has filled. Whatever you find becomes the pre-filled answer the SDR confirms in Step 2c.

5. **Email correspondence (HubSpot)** — relevant thread(s) with the prospect:
   - Anything the prospect volunteered about their stack, pain, or timeline in writing
   - Scheduling back-and-forth that reveals availability/urgency
   - Other stakeholders introduced or cc'd via email
   - Any attachments or materials already shared

   **Plus outbound sequence engagement (Amplemarket).** Check whether the prospect was enrolled in an Amplemarket sequence, and pull:
   - Which sequence and step they engaged with or replied to, and what that step's message said
   - Their replies, from the Amplemarket inbox, in their own words
   - Any engagement signal leading up to the booking (opens, clicks, LinkedIn steps)
   This tells the AE which message actually landed, which feeds the AE Briefing. Amplemarket is temporary: once sequencing consolidates into Nooks, pull this from Nooks instead.

6. **Recent win and loss patterns (HubSpot)** — always pulled fresh at run time, so the skill reflects what Campfire is winning and losing on right now rather than a fixed list:
   - **Closed-won deals** that match the prospect on the capabilities they'll likely need (e.g. multi-entity, multi-currency, system being replaced, rev rec), not just on vertical. Read the deal descriptions for what scope Campfire actually delivered. Pull a small handful of the closest matches. If nothing matches on vertical, match on capability instead.
   - **Recent Closed-Lost deals across the pipeline** (not just this company): the lost reasons and objections. These show which needs Campfire is currently losing on, and feed the Cautions section.

6b. **Intent signals, last 180 days (HubSpot).** Find every HubSpot company record whose **Company Domain Name** (`domain`) matches the prospect's, since duplicates and older records often hold signals the main record doesn't. For each matching record, pull:
   - HubSpot buyer-intent signals for the last 180 days (the HubSpot intent-signals search, scoped to those company IDs)
   - Intent-related company properties: Unify intent level and plays, first and most recent conversion events, and website visits and page views with their dates
   - Recent conversion events on the contacts associated with those records
   Keep only signals dated within the last 180 days, de-duplicate across records, and list them newest first with a date and one line each. Use them in the AE Briefing and Why Now? when they point to timing or interest (e.g. visiting pricing or NetSuite-comparison pages). If none fall in the window, write "None in the last 180 days."

7. **Attribution** — see Step 1. Never inferred from the data; always comes from the SDR directly.

8. **LinkedIn engagement** — see Step 2. Never auto-pulled or inferred; always comes from the SDR directly.

9. **Miscellaneous notes** — see Step 2b. Always comes from the SDR directly.

10. **SAL Qualification Needs** — see Step 2c. Pre-filled from the sources above, but always confirmed by the SDR.

## Step 1: Ask the SDR for Attribution

Prompt the SDR to explicitly choose how the meeting was booked:

- Inbound
- Outbound
- Events
- Partnerships

This leads the note — it tells the AE how familiar the prospect already is with Campfire and how to pitch the opening of the call accordingly (a cold outbound booking gets a different intro than someone who came in through an event or a partner referral).

## Step 2: Ask the SDR for LinkedIn engagement

Prompt the SDR to share **screenshots** of any direct engagement — DMs or post/comment engagement with the prospect. Don't ask them to transcribe or summarize it in words; ask for the screenshot itself, e.g.:

- "Can you screenshot any DMs you had with them?"
- "Any post or comment engagement — can you grab a screenshot of that too?"

Read whatever's relevant out of the screenshots (who engaged, on what, when, any signal about timing or mutual connections) and fold it into the note.

## Step 2b: Ask the SDR for Miscellaneous Notes

Prompt the SDR for anything else the AE should know that doesn't fit the other fields, e.g.:

"Anything else the AE should know? This could be how the prospect came across (enthusiastic, skeptical, rushed), growth or company news they mentioned, personal rapport points, or anything that felt off."

Capture it in the SDR's own words under **Miscellaneous Notes**. It's optional: if the SDR has nothing to add, omit the line and don't treat it as a gap. Use it to inform the AE Briefing where relevant (for example, a skeptical tone belongs in Additional context).

## Step 2c: Confirm the SAL Qualification Needs with the SDR

Every SAL must have these items in the Hand-Off Notes. Prompt the SDR for **each one explicitly**, one at a time or as a short checklist. For each item, show what the sources already suggest (with its source tag) and give the SDR three options:

- **Confirm** the pre-filled answer
- **Fill in** or correct it
- **Mark "Not yet qualified"**

Never skip a required item, and never treat a detected or estimated value as confirmed without the SDR saying so.

| # | Item | Required | What to capture |
|---|---|---|---|
| 1 | Current tech stack | ERP/accounting system: yes. Other categories: capture what's known | ERP/GL system, plus its **renewal date** (strongly encouraged; the most useful timing signal for the AE). Then any of: spend/cards, AP automation, inventory or project accounting, billing/AR/revenue, FP&A, close management, procurement, lease accounting. |
| 2 | Finance team size | Yes | Headcount in finance/accounting, plus who does what (e.g. Controller + 2 staff accountants) |
| 3 | Domestic entity count | Yes | Number of US legal entities |
| 4 | Foreign entity count + countries | Yes | Number of non-US entities and which countries |
| 5 | Cited interest | Yes | The specific problem the prospect wants to solve, in their words |
| 6 | Problematic use cases | Yes | Yes or no on each of: inventory or BOM, project-based accounting or billing, deferred revenue, fund accounting. For any yes: how they handle it today and whether they're open to a partner covering it. |
| G1 | Authority (SAL Gate 1) | Yes | Whether the contact can speak to current ERP procedures. If they're below the line, the named or described Above-the-Line stakeholder (Director-level or above) tied to the ERP decision. |

**Cited interest must be specific.** "Our close takes 15 days and lives in spreadsheets" qualifies. "Just curious," "Leadership told us to look at AI," or "Our ERP works fine, but we'll take a look" do not. If the SDR's answer is general curiosity, say so plainly and flag it (see Step 2d); don't dress it up as a cited interest.

## Step 2d: Check the SAL gates

Check the meeting against the three SAL gates. **A failed gate never blocks the note.** Flag it, then continue and post as normal. Flags appear in two places: a one-line **SAL ALERT** directly under the Deal Introduction in Slack (only if something failed or is not yet qualified), and the full **SAL Flags** section in HubSpot, just below SAL Qualification Needs. If nothing is flagged, omit both.

- **Gate 1, Access to Authority.** Flag a personal or free email address, or a contact with no visibility into finance/accounting procedures. A finance contact below the line (e.g. a Controller or Senior Manager of Accounting) is a strong SAL contact, not a problem: keep that flag light. Write it as a single note that the team may want to pull in a more senior stakeholder for the Product Demo, if one can be identified, and name that person if you have one. Never word it as a disqualifier.
- **Gate 2, Firmographic Fit (Red).** Flag if the account falls in a Red L1/L2 industry: Government (or any public-sector org with FAR/DFARS-style compliance); Financial Services → Banks & Credit Unions; Healthcare → Hospitals or Medical Device; Manufacturing; Real Estate & Construction → Construction; Energy & Utilities or Agriculture & Natural Resources; Distribution or Import & Export; Education → Educational Institutions; or a partner-motion firm (route to Partnerships, not Sales). Verify against what the prospect said, not just the HubSpot tag.
- **Gate 3, Demo Booking Window.** Flag if the AE meeting is more than 30 days after the qualifying conversation. State the gap in days as a fact (e.g. "Gate 3: meeting is 42 days after the qualifying call"). The SAL criteria's hold-and-reconfirm process is the SDR's to run; don't restate it in the note.
- **Cited interest.** Flag if the only interest is exploratory.
- **Section 4 gaps.** Not a gate failure, but list every item marked "Not yet qualified" so the AE can request it before the meeting.

Write each flag as one bullet naming the gate and the reason, e.g. "Gate 2: Red industry (Manufacturing)." Keep the tone matter-of-fact.

**Never steer the deal decision.** Flags and gaps state facts; they never recommend what anyone should do with the meeting. Whether to take, request more from, or decline a meeting is the AE's call alone. Never write language that suggests accepting, rejecting, declining, disqualifying, or DQing a deal, or that the AE "may want to confirm X before accepting." For example, write "Cited interest: exploratory so far; no specific pain named yet," not "the AE may want to confirm a specific pain before accepting." This applies everywhere in both outputs: SAL ALERT, SAL Flags, the AE Briefing, and Cautions.

## Step 3: Build the AE Briefing

This is the core deliverable. Do the full analysis internally: prospect pain, business complexity, relevant Campfire capabilities, recurring industry pains, and what the closest wins show. Then publish only neutral, evidence-based observations. The briefing summarizes intelligence; it never coaches.

**First, review the top industry wins.**
1. Note the prospect's **L2 industry**: the HubSpot company property **Industry Category L2** (internal name `industry_category_level_1`; the internal name is misleading, so don't confuse it with `industry_category`, which is L1).
2. Find the **top 3 closed-won deals by ARR** at companies in that same L2 industry. Rank by the deal's Annual recurring revenue (`hs_arr`), falling back to Amount when ARR is empty. Count each customer once: skip the duplicate implementation ("- IMP") and renewal deals that mirror an original win. To find them, list the companies in that L2 industry, then search for closed-won deals associated with those companies. Don't filter on company-level flags like "most recently created deal is closed won" or "current customer," since the IMP deals created after a win make those flags unreliable.
3. For each of the 3 deals, review its **Attention** call history. Search by call title using the company name first (CRM-field and deal-ID lookups often miss), then confirm each call belongs to that customer by checking that participant email domains match the customer's domain. Similar names can collide: "Campus" calls are not "Campus Ink." If no recorded calls are found, say so and rely on the deal description. Review the matched calls for:
   - The pains the customer described, in their words
   - What specifically convinced them Campfire could solve those pains
   - Industry-specific requirements that came up (systems, workflows, compliance)
   - Objections raised and how the AE handled them
4. If fewer than 3 closed-won deals exist in the L2 industry, use what's there and fill the rest from the L1 industry (`industry_category`). Say so in the note, so the AE knows the comparison is broader. If there are none at either level, rely on the capability-matched wins from source #6.

These deals become the **Customer Proof** in HubSpot (one line each: pain → how Campfire solved it). Only the single closest match can appear in Slack's Additional context, and only if it matches the prospect on accounting system, complexity, or workflow, not just industry.

**Then build the briefing** by cross-referencing the booking context, the confirmed SAL answers from Step 2c, the industry wins above, recent win patterns (source #6), and the prospect's own words. It has three parts:

**What we know** (up to 3 bullets). The most important confirmed information: prospect-stated pain, current accounting system, business complexity, timing. Each bullet should be a meaningful insight, not a repeated CRM field.

**Open questions** (up to 3 bullets). The most consequential unknowns, including unconfirmed authority, the economic buyer, operational impact, urgency, and whether Campfire fits a named need. This one section replaces separate "don't know" and "confirm" lists. Phrase each as what's unknown, not as an instruction.

**Additional context** (up to 2 bullets; omit if nothing meaningful). Context that changes how to read the deal: relevant prior engagement, objections, signals that cut against the obvious pain (e.g. a 3-day close), contradictions in the data, the single closest customer proof point, or the top caution.

The whole briefing is typically 100–150 words. Never drop a critical qualification risk to hit that number.

**Writing standard: observations, not commands.** Never use "Lead with," "Probe," "Push on," "Position Campfire around," "Find the buyer," "Use this as an easy win," "Steer the conversation toward," "Recommend asking," or "Consider leading with." Write what the evidence shows: "Prospect indicated…," "…remains unconfirmed," "Current process is unclear," "CRM indicates…," "Historical context suggests…." For example, "Lead with multi-entity; dig into consolidation" becomes "Prospect called managing four QuickBooks entities difficult; specific consolidation and reporting challenges are unconfirmed."

**Evidence discipline.** Classify every insight internally: prospect-confirmed, CRM-recorded, research-derived, or hypothesis. Never present a hypothesis as confirmed pain, and never imply the prospect has a problem just because similar companies did. HubSpot tags every fact. Slack labels a source only when it changes how much to trust the line.

**Capability guardrail.** Only describe Campfire as a fit for a need when a recent closed-won deal shows Campfire actually delivering it, cited by name, with a description that evidences that capability. A likely pain with no proof behind it becomes an Open question, not a claim. Don't drop it: a pain that follows directly from the business model (e.g. royalty accounting for a licensed-goods company) always appears as an open question.

## Step 3b: Build the Cautions section

Cautions are topics the prospect is likely to raise where Campfire is weak today, or where Campfire's fit is unverified. Build them from these, in order:

1. **SAL problematic use cases** the SDR confirmed as "yes" in Step 2c, noting whether the prospect is open to a partner covering it.
2. **A Capabilities & Gaps doc, if one exists.** Search Google Drive and Notion for a doc titled "Capabilities & Gaps" (or close to it) and read it every run. If it marks a capability as generally available, drop that topic. If it lists a new gap, add it. If no such doc exists, skip this source.
3. **Deal evidence.** The topic shows up in recent Closed-Lost reasons or objections (source #6), or closed-won deals show Campfire solving it only alongside a separate system.
4. **Unverified fit.** A need the prospect named that no closed-won deal shows Campfire handling.

Write each as a neutral fact plus its implication (e.g. "Multi-jurisdiction sales tax: Campfire's fit is unverified; worth confirming internally before positioning against it"). At most 2. The top caution can surface in Slack's Additional context; the rest stay in HubSpot. If there's no evidence of a weak spot, omit the section.

## Step 4: Build the rest of the HubSpot record

**SAL Qualification Needs.** Put the SDR-confirmed answers from Step 2c in this block, in this order, and **always show every item**, with a confirmed answer or "Not yet qualified":

- **Current Tech Stack** — ERP/GL system and its renewal date, then other tools by category, in their words, not a dropdown value
- **Finance Team Size** — headcount plus who does what
- **Domestic Entities** — number of US legal entities
- **Foreign Entities** — count and countries
- **Cited Interest** — the specific problem, in their words
- **Problematic Use Cases** — yes/no on each of the four; for any yes, how they handle it today and whether they're open to a partner
- **Authority** — whether the contact speaks to ERP procedures, and the named ATL stakeholder if they're below the line

**Why Now?** sits just after the AE Briefing: the trigger behind the evaluation, in their words where possible.

**Relevant Context.** Discovery detail that adds meaning beyond the briefing: system relationships, operational specifics, hypotheses worth checking (tagged "hypothesis"). One bullet each, and only what isn't already said elsewhere.

**Customer Proof & Prior Engagement.** The industry wins from Step 3 (one line each) plus any prior engagement with this company. If there's none, say "none, first deal on the account."

**Supporting Research.** Other stakeholders, days to close (flag if over 4), locations and currencies if not covered above, firmographics (L1/L2 industry · founded · revenue), intent signals (newest first), LinkedIn signal and Miscellaneous Notes if provided, and an **Other gaps** line for missing non-SAL information.

## Step 5: Handle missing information

Every gap is captured once, in the right place, never guessed and never silently dropped.

- **SAL Qualification Needs** always appear in their block, with "Not yet qualified" where the SDR marked them so. Each "Not yet qualified" item also appears in SAL Flags as a Section 4 gap, and in Slack's SAL ALERT line.
- **The most consequential gaps** (authority, economic buyer, operational impact, urgency) go in the briefing's Open questions.
- **Other missing non-SAL information** goes on the **Other gaps** line in HubSpot's Supporting Research. It doesn't go in Slack.
- **Call transcript not available yet:** mark those gaps "(call transcript pending)," or "Not yet qualified (call transcript pending)" for SAL items, so the SDR knows to re-run.
- **Tool or permission limits** (e.g. intent signals unavailable) are noted in HubSpot only, never in Slack.
- **LinkedIn engagement and Miscellaneous Notes** are optional. If the SDR provides nothing, omit them and don't treat them as gaps.

**Source tags (HubSpot):** end every fact about the prospect with one of *(prospect said)*, *(SDR notes)*, *(CRM)*, *(detected)*, *(estimate)*, or *(hypothesis)*. Customer proof points don't need tags, since they name the deal they come from. Detected and estimated facts never count as confirmed, so the matching item stays open until the prospect confirms it.

## Step 6: SDR review

Show the SDR both drafts (Slack and HubSpot) before posting anything. Let them edit or correct it, and only proceed to Step 7 after they explicitly approve. Never write to HubSpot or send a Slack message without that approval.

## Step 7: Publish to both destinations (two different versions)

1. **HubSpot** — write the approved full record into the deal property **SDR Notes - If applicable** (internal name `sdr_notes`), which sits in the "SDR Notes - If applicable" section of the Deal page. If the field already has content, show the SDR what's there and confirm before overwriting. Write it as plain text — bold and other formatting won't render in the field.
2. **Slack** — post the short version to **#sdr-handoff-notes** (channel ID `C0C6MRCKRRC`), tagging the Deal Owner, the SDR who booked the meeting, and that SDR's direct manager at the top of the post. It is *not* a copy of the HubSpot record: Deal Introduction, SAL ALERT (if any), the AE Briefing, and a link to the full notes on the HubSpot deal (see the Slack template). Any follow-up from the AE or manager happens in that post's thread.

   **Before posting, check membership.** The post goes out as the SDR running the skill, through their own Slack connection, not as a Claude bot. Slack only lets someone post in a channel they've joined, even a public one. Inviting or adding the Claude app to the channel does nothing here, so never suggest `/invite @Claude` or adding the app from the channel's integrations.

   - **The SDR running the skill must be a member.** If they aren't (or the post fails with "not in channel"), tell them exactly this: "You're not in #sdr-handoff-notes yet. Open the channel in Slack and click **Join Channel**, then reply 'joined' and I'll post." Then wait and retry the post. Don't say they need someone else to add them; the channel is public, so they can join themselves.
   - **All three tagged people must be members** (Deal Owner, booking SDR, and that SDR's manager). A tag on a non-member doesn't notify them. If anyone is missing, tell the SDR who to add via the channel name → Add people, then post once they confirm.

**Which SDR counts:** the SDR who logged the booking (the owner of the booking note or booking call on the deal/company), not necessarily the person listed as SDR Owner on the company record. Cross-check against the deal's **SDR Attribution** property (`sdr_sourced`). If they conflict, or it's unclear who booked, ask the SDR running the skill.

**Finding the manager:** check the booking SDR's Slack profile for a manager. If none is listed, ask the SDR running the skill who their manager is before sending.

**Length and order.**
- **Slack:** about 150–225 words of narrative, excluding the Deal Introduction. A guideline, not a truncation rule: never hide a critical SAL risk to hit it. Order: tags, Deal Introduction, SAL ALERT, What we know, Open questions, Additional context, link to full notes.
- **HubSpot:** the complete record. Order: Deal Details, AE Briefing, Why Now?, SAL Qualification Needs, SAL Flags, Relevant Context, Cautions, Customer Proof & Prior Engagement, Supporting Research.
- Every section in both versions is bulleted, one item per bullet.
- Say each thing once per output. The briefing summarizes the biggest gaps; SAL Qualification Needs and SAL Flags hold the formal documentation; nothing is repeated elsewhere.
- Before showing the drafts to the SDR, re-read every line and cut any the AE wouldn't miss. No preamble, and no coaching.

## Step 7b: Draft the same-day confirmation email

The SAL criteria make the SDR responsible for attendance from booking until the meeting starts. After posting, draft the same-day confirmation email to the booked prospect:

- Recap their cited interest, in their own words
- Who they'll meet: the AE's name and title
- What to expect from the meeting, in a sentence or two
- Ask them to accept the invite if they haven't

Keep it short and in the SDR's voice. Show it to the SDR to edit and send themselves. Never send it on their behalf. If the SDR asks, save it as a draft in their email instead.

## Step 8 (optional): Post-meeting accuracy check

Run this only when someone asks for it after the meeting (e.g. "check the hand-off for [company]"). Compare the hand-off note against what the AE actually learned: their recap email (HubSpot), the meeting recording (Attention), or both. Reply in the original #sdr-handoff-notes thread with a short scorecard:

- Each AE Briefing observation, Open question, and Caution, marked right, partly right, or wrong, with one line on what the meeting showed
- Any detected or estimated facts that turned out wrong (e.g. detected tech stack vs. the real one)
- The biggest pain or requirement the note missed entirely

Keep it to 6 lines or fewer, factual, and framed as coaching rather than grading the SDR. Show the reply to the person who asked before posting it.

## Output templates

### Slack (#sdr-handoff-notes): the 30-second read

Use Slack formatting: bold section headers and hyperlinks.

```
@[Deal Owner] @[Booking SDR] @[SDR's manager]

DEAL INTRODUCTION
- Company: [Company Name](HubSpot company record URL)
- Deal: [Deal Name](HubSpot deal record URL)
- Employees: [headcount] · Accounting: [system, or "Not yet qualified"]
- Meeting: [day, date, time range, time zone]
- Attendee: [name, title] (one bullet per prospect attendee)
- Attribution: [Inbound / Outbound / Events / Partnerships] ([channel])

:warning: SAL ALERT: [each failed gate or not-yet-qualified item, separated by " · "] (omit the line if none)

WHAT WE KNOW
- [up to 3 confirmed insights]

OPEN QUESTIONS
- [up to 3 consequential unknowns, phrased as what's unknown]

ADDITIONAL CONTEXT
- [up to 2: counter-signals, closest proof point, top caution, prior engagement] (omit if none)

[Full hand-off notes in HubSpot →](HubSpot deal record URL)
```

### HubSpot (written to `sdr_notes`, plain text): the full record

```
DEAL DETAILS
- Meeting: [Company Name] — [day, date, time range, time zone]
- Attendee: [name — title]
- Attribution: [Inbound / Outbound / Events / Partnerships] ([channel])
- Employees: [headcount] (CRM)

AE BRIEFING
What we know
- [same insights as Slack, with source tags]
Open questions
- [same as Slack]
Additional context
- [same as Slack, with source tags] (omit if none)

WHY NOW?
- [trigger, in their words] (source tag)

SAL QUALIFICATION NEEDS
- Current Tech Stack: [ERP + renewal date; other tools by category — or "Not yet qualified"]
- Finance Team Size: [headcount + who does what — or "Not yet qualified"]
- Domestic Entities: [count — or "Not yet qualified"]
- Foreign Entities: [count + countries — or "Not yet qualified"]
- Cited Interest: [their words — or "Not yet qualified"]
- Problematic Use Cases: [inventory/BOM, project accounting, deferred revenue, fund accounting: yes/no each; open to partner? — or "Not yet qualified"]
- Authority: [speaks to ERP procedures? named ATL stakeholder — or "Not yet qualified"]

SAL FLAGS (omit if none)
- [Gate or Section 4 gap: reason, matter-of-fact. Below-the-line finance contact = "Consider pulling in a more senior stakeholder (e.g. [name, title]) for the Product Demo, if one can be identified."]

RELEVANT CONTEXT
- [discovery detail beyond the briefing; hypotheses tagged (hypothesis)]

CAUTIONS (omit if none)
- [topic: neutral fact + implication] (max 2)

CUSTOMER PROOF & PRIOR ENGAGEMENT
- [Customer] ([amount]): [pain] → [how Campfire solved it]
- Prior engagement: [history, or "none, first deal on the account"] (CRM)

SUPPORTING RESEARCH
- Other stakeholders: [name, title; one per bullet if several] (CRM)
- Days to close: [number; flag if over 4] (source tag)
- Locations / currencies: [if not covered above]
- Firmographics: [L1 / L2 industry · founded · revenue] (CRM)
- Intent signals (last 180 days): [date: signal, newest first; or "None in the last 180 days" / "unavailable (reason)"]
- LinkedIn signal: [omit if none]
- Miscellaneous notes: [omit if none]
- Other gaps: [missing non-SAL info] (omit if none)
```