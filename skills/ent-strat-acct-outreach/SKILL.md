---
name: "ent-strat-acct-outreach"
description: "Run Campfire SDR outbound end to end: research (HubSpot, Attention, Amplemarket), draft and AI-audit emails and LinkedIn notes, Gmail draft, Google Calendar reminders, HubSpot context note. Also audits any prospect-facing draft."
---

# Outreach (v2.1: team version, full outbound workflow + copy audit)

Works for any Campfire SDR. Nothing in this skill is tied to one rep: identity, signature, AE and personal proof points are resolved at run time (Step 0). Replaces the older `outreach-ai-audit` skill.

v2.1 changes: Gmail signature now comes from `includeSignature: true` on the draft (never rebuilt from a sent email); added a jargon rule to the copy audit.

Two jobs:

1. **Full workflow** (default when invoked as `/outreach` with a prospect, HubSpot link, job post or LinkedIn URL): rep setup, research, stakeholder check, draft, audit, Gmail draft, Google Calendar reminders, HubSpot note.
2. **Audit only** ("audit this", "de-AI this", "scan this draft", or a pasted draft with no prospect context): skip to Part B and return findings plus a clean version. Step 0 is only needed for the sign-off name and any rep proof point.

Modes inside the audit: **rewrite** (default: findings + clean version) or **detect** ("just flag", "scan": findings only).

Pattern catalog distilled from conorbronsdon/avoid-ai-writing (MIT, https://github.com/conorbronsdon/avoid-ai-writing), adapted for enterprise SDR outbound. Message structure from Scott Sowers' Enterprise Outbound Strategy (Q2 2026): Trigger, Problem, Relevance, Ask.

---

# Part A: Workflow

Keep a task list for the run. Order matters: rep setup, then research, then drafting, then any write to a system.

## Step 0. Rep setup (once per conversation)

Resolve who is sending. Never hard-code a rep's name, email, signature or background.

| Field | How to get it | Fallback |
|---|---|---|
| Rep name, email, HubSpot owner ID, portal ID | `mcp__HubSpot__get_user_details` (USER_INFORMATION). | Ask the rep. |
| Sign-off name | Rep's first name from HubSpot. | Ask. |
| HubSpot BCC logging address | `{portalId}@bcc.na2.hubspot.com`, built from the portal ID returned above (Campfire's is `39878266@bcc.na2.hubspot.com`). | If the rep says their BCC address differs, use theirs. |
| Email signature | Nothing to resolve up front. Step 4 sets `includeSignature: true` on `mcp__Gmail__create_draft`, which appends the rep's saved Gmail signature exactly. **Never rebuild the signature by copying it from a sent email:** sent copies carry HubSpot tracking-redirect links and pixels tied to that one send, and the result renders broken. | If the draft comes back without a signature (no signature saved in Gmail, or the parameter isn't supported), say so in the wrap-up and tell the rep to insert it in Gmail before sending. Never invent one, never reuse another rep's. |
| Pod AE | The **company owner** on the HubSpot account record. | Ask the rep. |
| Rep proof points (optional) | Only what the rep states in this conversation: prior employers, finance background, relationships they can reference. | Ask once: "Any personal background I can use as a proof point (prior role, employer, finance experience)? Say none to skip." If none, use only the company proof points in Part B. |

Ask all missing fields in **one** AskUserQuestion or plain-text question, not one at a time. Reuse the answers for the rest of the conversation.

## Step 1. Research (read-only, run in parallel)

| Source | What to pull | Notes |
|---|---|---|
| HubSpot signal / record link pasted | Signal type, owner, status (e.g. Sequenced), associated contacts | Custom object type IDs come from the URL (e.g. `2-232820898`). |
| HubSpot contact search | Is the prospect already a contact? Lifecycle, email, phone, last contacted | Search by last name + company. **Ignore the contact owner field**: it's a legacy artifact. Don't report it, flag it, or gate on it. |
| HubSpot company (by domain) | **SDR Owner** (the ownership gate), company owner (AE), open deals, last contacted, employee count | Watch for duplicate company records (different IDs for the same domain). Flag them, don't merge. |
| Amplemarket `enrich_person` (LinkedIn URL) | Title, start date, prior roles, location, active sequences | LinkedIn blocks WebFetch, so always enrich instead. |
| Job post | Responsibilities, systems named, governance scope | LinkedIn job pages block fetch. WebSearch the title + company and use the company careers page or a mirror. |
| Campfire changelog / assets | Any product update or asset the rep wants to reference | Fetch campfire.ai/changelog and confirm the entry, its date, and whether it's gated ("reach out to your CSM for access"). Describe gated features accordingly. |
| **Attention: prior demos and discovery calls** | Any call with this company, who ran it, what the buyer said, timelines named | See below. This step is mandatory. |

### Attention sweep (calls not logged in HubSpot)

1. Run `search_calls` twice: once with `title` = company name, once with `crm_field_entity_code="account"`, `crm_field_field_name="Name"`, `crm_field_values=[company]`. Merge by ID.
2. For each hit, `get_call_details`: date, Campfire attendees (SC, partnerships, AE), prospect attendees and titles, current ERP, pain stated in their words, timelines, who they plan to share it with.
3. Cross-check HubSpot: is there a deal, an AE, a company owner, a logged meeting? A call with no deal and no AE is an **orphaned warm opportunity**. Say so plainly at the top of the output.
4. Note landmines from the call (e.g. integrations Campfire lacks).
5. Do not quote a buyer's private pain from the call in outreach to a colleague. Mention the call happened; use public pain (job post, filings) for the problem statement.

## Step 2. Stakeholder and ownership check

**Ownership gate:** the only ownership field that matters is **SDR Owner on the company (account) record**. If it matches the rep's HubSpot owner ID from Step 0, the rep is clear to work every contact at the account. Contact-level owner fields are legacy artifacts: never gate on them, never flag a contact owner as a collision risk, and never create a reminder to confirm contact ownership. If SDR Owner on the account is someone else, stop and flag it before drafting.

Before drafting, decide who needs a heads-up:

- **Prior call ran by a Solutions Consultant or partnerships**: draft a Slack heads-up to whoever ran it (from the Attention attendees) in the same output. Tell them what you're doing, don't ask permission. Ask only the real question (e.g. partnerships: does a direct sales motion complicate the partner thread?).
- **Do not change the company owner field.** Ownership is decided separately.
- **Do not create a deal** until a meeting is booked.
- **Do not add the AE** to a Slack thread until there's a positive reply or a booked meeting. Then bring in the pod AE from Step 0 and do the standard handoff (meeting link + HubSpot deal link).
- If an email offers time with an SC, that SC must hear about it before the email goes out.

## Step 3. Draft

- Default deliverables: **LinkedIn connection note** + **email**. Add a cold fallback variant if a prior-call reference might not be cleared.
- If there's a prior call and a new hire who would own the evaluation, the email is a **routing email**: reference the call (who on Campfire's side, who on theirs, the timeline they named), name the context gap the new hire has, ask "is this yours to own?", offer 20 minutes with the SC. Leave the stat line out; a proof point turns routing into a pitch.
- Run Part B on every draft before showing it.

## Step 4. Gmail draft

When the email is approved (or the rep asks to push it to drafts), create it with `mcp__Gmail__create_draft`:

- **to:** prospect email from HubSpot (flag that Amplemarket didn't verify it if so; suggest an email reveal on bounce). If the address is new and the HubSpot contact has no email, tell the rep to add it to the contact before sending, so BCC logging doesn't create a duplicate contact.
- **bcc:** the HubSpot BCC address from Step 0, so the send logs to HubSpot. Every outbound email carries it.
- **subject:** lowercase, as audited.
- **htmlBody + body:** the clean email, signed with the rep's first name and nothing after it. Do not paste a signature block into the body.
- **Signature:** first touch (new thread) sets `includeSignature: true`, which appends the rep's saved Gmail signature. A reply or bump on an existing thread (`replyToMessageId` set) sets `includeSignature: false` and signs with the first name only, unless the rep says their reply default includes a signature. If the returned draft has no signature, flag it in the wrap-up (see Step 0 fallback).
- **HTML body:** wrap paragraphs in `<div>` with `<br>` between them. No bold, no bullets. Turn resource URLs into hyperlinks.
- **Send timing:** if the prospect is outside the rep's time zone, recommend a Gmail schedule-send time that lands in the prospect's morning on their next workday (e.g. Israel's workweek is Sunday to Thursday).

Return the draft link and remind the rep to check it before sending.

## Step 5. Google Calendar reminders

Create reminders as events on the rep's primary Google Calendar with `mcp__Google_Calendar__create_event` (load via ToolSearch). Don't use a task manager; the calendar is the surface every rep has.

For every event:
- `startTime` / `endTime` in local ISO with no offset (the server resolves the rep's time zone). Times below are in the rep's local time.
- `availability`: `AVAILABILITY_BUSY`.
- `overrideReminders`: `[{"method": "popup", "minutes": 10}]`.
- No attendees. These are personal reminders, never invites.
- `description` (HTML allowed): what the rep needs when the event fires, no conversation history. Always end with a link to the HubSpot contact.

Defaults:

| Event | When | Length | Description contents |
|---|---|---|---|
| Call [prospect] ([company]) | Same day 4:30 PM, unless the rep names a time or the prospect's local time makes that unworkable (then the next workday morning inside the prospect's business hours) | 15 min | Talk track (the core question), local-time conversion if abroad, phone status (if no number on file: "run Amplemarket phone reveal before dialing"), HubSpot contact link. |
| Check in with [stakeholder] | Next business day, 9:00 AM | 10 min | Only if a Slack heads-up is still awaiting a reply. The exact open question. |
| Bump [prospect] | ~5 business days after send, 9:00 AM | 10 min | Thread to reply on, the step-2 angle, any SC sign-off it needs. |
| Re-engage [prior call attendees] | Date the rep names, or just after the prospect's stated event (e.g. cutover) | 20 min | To: emails, goal, message beats, pre-send checklist, Attention recording link. |

Never create a reminder to confirm contact ownership. Return each event's `htmlLink`.

## Step 6. HubSpot context note

Create one note with `mcp__HubSpot__manage_crm_objects` (objectType `notes`), associated to the **contact** and the **company** (and the duplicate company record too, if one exists and still resolves). Invoking this workflow authorizes the note; when the rep says "just create it", skip the approval table and show the content in the reply.

- `hs_timestamp`: now (ISO, UTC).
- `hs_note_body` (HTML) sections, in this order:
  1. **Title:** `[Company] outbound plan: [Prospect] ([title], started [date], ex [prior co])`
  2. **Context:** prior calls (date, who ran them, who attended, ERP, timeline named, who they'd share with), CRM state (AE? deal? SDR Owner?), open threads (partnerships), material public news (acquisitions, layoffs, entity changes).
  3. **Drafted / Sent [date]:** what went out or is queued, which stakeholders were told and who replied, scheduled calls.
  4. **Decision tree:** one bullet per trigger (positive reply, redirect, no reply by [date], fixed re-engage date, stakeholder friction) with the move for each. Dates must match the calendar reminders.
  5. **Known gaps:** missing integrations, gated features, unverified claims.
  6. **Links:** Attention recording(s).

No prospect quotes from private calls in a way that would embarrass anyone if the note is shared internally; facts are fine.

## Step 7. Wrap-up

End with a short table: what was created (Gmail draft, calendar reminders, HubSpot note) with links, then one line on the most important open risk. No recap of steps.

## v2 (not yet active): LinkedIn account list note

Planned: add the same context (one or two lines plus the next step date) to the prospect's account in the rep's LinkedIn (Sales Navigator) account list via "Add note", using the built-in browser. When enabled: read the built-in-browser skill first, open the account in the list, click "Add note", paste a 2 to 3 line summary (trigger, last action, next step + date), and confirm it saved. Never send messages or connection requests from the browser without an explicit yes. Until this section is marked active, skip it and mention it as a manual step in the wrap-up.

---

# Part B: Copy audit

## Editing contract (non-negotiable)

1. **Source fidelity beats polish.** Never add a fact, metric, customer outcome, or capability that isn't in the rep's intel, the verified research, or the approved claims list. Flag gaps instead of filling them. Invented proof points are the most damaging error in outbound, because the prospect may test them in a demo.
2. **Minimal edits.** Change only flagged spans. If a draft is clean, say so and return it unchanged.
3. **Preserve quotes.** A prospect's own words quoted back stay verbatim (keep quotes under 15 words).
4. **Detection is not proof.** These are signals of autopilot writing, not verdicts.

## House copy rules (team defaults; a rep's explicit instruction in the conversation overrides)

- **Em dashes: zero.** Replace with parentheses, commas, periods, or two sentences. Catch both "—" and "--" (the signature delimiter "--" is exempt).
- **Parentheses are allowed for concrete asides** ("Karim Atiyeh (Ramp's cofounder)"). Still flag the hedge form: "(and, increasingly, X)", "(or, more precisely, Y)", "(and perhaps more importantly, Z)". Max two parentheticals per message.
- **Subject lines lowercase.** 2 to 6 words, reads like an internal email.
- **Length:** email body 80 to 130 words; LinkedIn DM 50 to 60 words; connection note under 300 characters with no pitch. Phone-readable: if a paragraph runs past 3 lines on a phone, split it.
- **Contractions throughout.** Casual, typed-on-a-phone register, not marketing.
- **One pain pillar per message** (Spreadsheet Tax, Summarization Tax, Customization Trap, AI Trust Gap, Scale Cliff, International/M&A Pain). Two pillars in one message is a finding.
- **No bullets in email prose.** Resource link lists are the only exception.
- **Close with a question or soft CTA,** never a summary.
- **Sign with the rep's first name** (Step 0).
- **No jargon the rep can't defend on a call.** Prospect-stack terms lifted from a job post (e.g. "planning cubes", "EPBCS", "Essbase", "intercompany eliminations") read credible only if the rep can go one level deeper when the prospect replies. Default to the plain version ("planning models", "Oracle EPM"). If a technical term stays in the copy, define it in one line in the commentary above the draft, with a source link, so the rep knows what they're sending. Flag any undefined system term as P1.

## Banned phrases specific to outbound (P1)

Omniscient-observer frames (these appear in Scott's templates; do not copy them):
- "the pattern I keep seeing", "I've been seeing", "something I've been seeing across", "what I'm hearing from", "across companies like yours", "the pattern is", "most finance leaders I talk to"

Fix: replace with a specific, declarative observation tied to this prospect's trigger.

Other outbound tells:
- "I hope this finds you well", "I wanted to reach out", "just following up", "circling back", "touching base"
- "Quick question" as an opener
- "I came across your profile"
- Referencing website visits or other tracking signals in prospect-facing copy
- Generic congrats with nothing after it ("Congrats on the funding!"). Congrats is fine only if the next sentence makes it specific.
- Flattery recap ("Your impressive career at X and Y...")
- "Would love to" stacked more than once
- Describing the prospect's own job post as if they were still a candidate ("the posting put X on you")

## Generic AI-tell catalog (distilled)

### P0: credibility killers (always fix)
- **Chatbot artifacts:** "Certainly!", "Great question", "I hope this helps", "Feel free to reach out", "Let me know if you have any questions".
- **Vague attributions:** "Experts believe", "Studies show", "Many CFOs agree". Cite or cut.
- **Significance inflation:** "a pivotal moment", "watershed", "game-changer" for routine events (a hire, a launch).
- **Unfilled placeholders:** [Name], [Company], {{merge tags}} that didn't resolve, "XX%".
- **Invented claims:** any metric, customer result or capability not in the source or the approved claims list. This includes figures an SC said on a call that aren't on the approved list.
- **Invented rep background:** any personal proof point the rep didn't state in Step 0 or the conversation.
- **Mischaracterized background:** e.g. saying someone "built the product" when they ran internal systems.

### P1: obvious AI smell
- **Tier 1 words (review every hit):** delve, landscape (metaphor), realm, paradigm, embark, testament to, robust, comprehensive, cutting-edge, leverage (verb), pivotal, underscores, meticulous, seamless/seamlessly, game-changer, nestled, vibrant, thriving, showcasing, deep dive / dive into, unpack, intricate, complexities, ever-evolving, holistic, actionable, impactful, learnings, best practices, at its core, synergy, interplay, keen, genuine/genuinely (intensifier), embrace (metaphor), journey (metaphor). Clarity edits: utilize, in order to, due to the fact that, serves as, boasts, features (verb).
- **Tier 2 words (flag when 2+ in one paragraph):** harness, navigate, foster, elevate, unleash, unlock, streamline, empower, bolster, spearhead, resonate, revolutionize, facilitate, crucial, ecosystem, myriad, transformative, cornerstone, paramount, poised.
- **Template constructions:** "Whether you're X or Y", "a [adj] step towards [adj] [noun]", "In today's [X]", "In an era where".
- **Negative parallelism:** "It's not X, it's Y" / "This isn't about X. It's about Y." Max one per message, and only if the contrast is real.
- **Infomercial hooks:** "The catch?", "Here's the thing.", "The kicker?", "Real talk:".
- **Lingering-attention claims:** "I keep coming back to", "can't stop thinking about", "stuck with me". Open on the thing itself.
- **Stock reaction framing:** "What struck me", "I was fascinated to", "Your timing is interesting".
- **Rhetorical question openers:** "What if there were a better way?" Lead with the claim.
- **Hedge stacks:** "could potentially", "may eventually". Pick one.
- **Real/actual inflation:** "real visibility", "actual automation", "a real evaluation". Drop the intensifier, add the specific.
- **Hollow intensifiers:** truly, genuinely, actually (as emphasis), exactly, really, quite frankly, to be honest.
- **Vague endorsement:** "worth a look", "worth exploring" with no reason. ("Worth 20 minutes?" as a CTA is fine.)
- **Narrated candor:** "I'll be upfront", "I want to be transparent".
- **Stacked asks:** two questions in the close. One question, then optionally a soft CTA.
- **Undefined system jargon:** see the jargon rule under House copy rules.

### P2: polish
- Compulsive rule of three (ornamental triads; real three-item lists pass).
- Transitions: Moreover, Furthermore, Additionally, That said, Notably, It's worth noting.
- Copula avoidance: "serves as" to "is", "boasts" to "has".
- Uniform sentence rhythm: every sentence 15 to 25 words. Mix in a short one.
- Hyphen stacking: "a scalable, AI-native, audit-ready, best-in-class platform".
- Unnecessary hyphenation: "in real-time" (adverb) to "in real time".
- Bold or emoji in an email body: remove.

## Structure check (Scott's framework)

Every email must pass all four, in order:
1. **Trigger:** why now, tied to a specific, verifiable signal (new role, post, filing, job posting, launch, prior call). Not generic congrats.
2. **Problem:** the prospect's likely pain, not Campfire's features. For routing emails, the problem can be the context gap (new owner lacks what was covered on a prior call).
3. **Relevance:** one proof point or insight: the approved stat line, a go-live-confirmed customer, a verified product update, the prior call itself, or a rep proof point from Step 0.
4. **Ask:** one low-friction question.

Flag any missing step, or any message that leads with the product.

Two writer-side tests:
- **Swap test:** could this email go to any CFO at any company by changing the name? If yes, the trigger is too weak.
- **Treadmill test:** what does each sentence add? Cut any sentence that restates the one before it.

## Claims guardrails

- Approved stat line only: customers close 5x faster on average, pull board-ready financials in under 30 seconds, and save $100K+ annually.
- Do not use the 40% NetSuite migration figure, or any migration share an SC mentions on a call.
- Name a customer only if go-live is confirmed with CS.
- Name a competitor's product or the prospect's ERP only if verified, and prefer public sources (job post, filings) over what was said on a private call.
- Superlatives, capability guarantees, and audit/ITGC outcomes need SC approval. Flag them for review.
- Product updates: cite only what the changelog entry says; flag gated features ("reach out to your CSM for access") so copy doesn't imply general availability.
- Integrations: name only those listed on campfire.ai/integrations.
- Rep proof points: use only what the rep stated. A Ramp background or Ramp-founder reference is valid only for reps who worked at Ramp, and is skipped for prospects who came from a direct Ramp competitor (e.g. BILL).

## Output format

**Rewrite mode:**
1. **Findings:** a table with Quote | Pattern | Severity (P0/P1/P2) | Fix. Put source-fidelity breaches first.
2. **Clean version:** the full message, ready to paste.
3. **Second pass:** reread the clean version and list anything that survived (or say "clean").
4. **Word count:** body words (email) or characters (connection note) against the target.

**Detect mode:** findings table plus a short line on which flags are judgment calls.

In full-workflow runs, put a research summary table and any pushback (stakeholders, landmines, ownership) above the drafts, and the audit below them. Keep the commentary short. The clean copy is the deliverable.

