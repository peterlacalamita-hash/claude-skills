---
name: "thoughtful-linkedin-outreach"
description: "Peter's trigger-based LinkedIn outreach for Campfire: a new role, promotion, news item, or prior conversation with the prospect's team, written in his voice from his two model messages. Use when Peter names a prospect or pastes a LinkedIn URL and wants a \"thoughtful\" LinkedIn message, a congrats-on-the-new-role note, a follow-up DM that references past calls or an article, or asks to \"do my thoughtful outreach\" for a list of people."
---

# Thoughtful LinkedIn Outreach

Peter's LinkedIn messages for Campfire (AI-native ERP / close and consolidation for finance teams). Every message hangs on something real: a trigger event plus a specific detail that proves he did the homework. Use this skill instead of generic first-touch templates whenever Peter wants a "thoughtful" message.

## The two model messages (the voice to match)

**A. New role + prior conversations with their team**

> Hey Alyssa, just wanted to say congrats on the new role!  I know we haven't spoken before but I thought now would be a good time to reach out.  Last November we spoke with Ellie and a few others from the team and they shared that closed took 13 to 16 business days and the target was getting to 10 while Netsuite FX and consolidation is hard to audit, among a lot of other stuff.  With your new role is this a focus and curious if it makes sense to introduce you to Campfire?

**B. Follow-up + new role + public quote**

> Hey Joe, following up here again just wanted to say congrats on the new role over at Pearl River Resort. I was reading [this article](https://www.indiangaming.com/joe-castillo-named-interim-ceo-of-pearl-river-resort/) and I saw that Chief Ben said "We are entering the next chapter with someone who helped write the last one." I'm curious what are some of the financing and accounting initiatives you are thinking of revamping this year and next?

## The pattern

Four beats, in this order, usually 50 to 90 words:

1. **Trigger.** "Congrats on the new role", a promotion, a funding round, an acquisition, an ERP migration, a new CFO, a public post. It must be recent (ideally under 90 days) and true.
2. **Honest framing.** Say plainly where things stand: "I know we haven't spoken before" or "following up here again". No pretending to know them.
3. **The proof detail.** One specific thing only someone who did the work would know:
   - from Campfire's own past calls: who on their team we talked to, roughly when, and their numbers or pain in their words (close days, target, NetSuite FX, consolidation, audit trail, entity count, manual reconciliations);
   - or from public sources: a quote from an article or press release (linked), a line from their own LinkedIn post, a job posting that reveals a finance-system project.
4. **Bridge + soft ask.** Tie the detail to their new seat and ask one question: "With your new role is this a focus?", "curious if it makes sense to introduce you to Campfire?", or an open question about their initiatives this year and next. One ask only.

### Voice rules

- Casual, peer-to-peer, lightly run-on, like it was typed on a phone. Don't over-polish Peter's natural rhythm ("just wanted to say", "among a lot of other stuff", "I'm curious").
- Start with "Hey {First name},". No sign-off needed.
- Numbers stay as the prospect's team said them ("13 to 16 business days", "target was getting to 10").
- Campfire can be named in the ask (example A) or left out entirely in favor of a pure question (example B). Default: name it when there's prior call history; leave it out when the hook is purely public news.
- Banned: "Hope this finds you well", "In today's fast-paced...", "I'd love to", "quick question", "synergy", "streamline", "unlock", "leverage", em dashes, three-item lists of benefits, feature pitches, calendar links, more than one question.

## Workflow

Keep a short task list. Research first, draft second, never send anything.

### 1. Identify the prospect
Get name, company, title, and LinkedIn URL if Peter gave one. If he only gave a name + company, find the profile.

### 2. Research (run independent lookups in parallel)

| Source | What to pull |
|---|---|
| LinkedIn (Claude in Chrome, where Peter is signed in) | Current title + start date, previous role, recent posts or reposts, mutual context. Confirms the trigger. |
| HubSpot | Contact + company record, SDR owner (flag if it's not Peter), lifecycle stage, past deals and closed-lost reason, last activity. |
| Attention | `search_calls` on the company name/domain, then `ask_attention` over the returned call IDs to extract: who attended, date, close timeline (current vs. target), ERP/GL, FX/consolidation/intercompany pain, entity count, audit issues, why it stalled. |
| Amplemarket | `enrich_person` for job-change date and verified title if LinkedIn is unclear. |
| Web search | Announcement of the role, press releases, funding, M&A, earnings, interviews, quotes from leadership about the person. Capture the exact quote and URL. |

If the account is closed-lost, run the `cl-winback-audit` skill before drafting. If HubSpot shows another rep owns it, stop and tell Peter.

### 3. Pick the hook
Choose the single strongest proof detail, in this priority:
1. Specific numbers/pain from Campfire's own calls with their team (example A).
2. A direct quote about them or their mandate from an article (example B).
3. Something they posted or said themselves.
4. A finance-systems signal (job post for NetSuite admin, new entity, acquisition, IPO prep).

If nothing specific turns up, say so and suggest waiting for a better trigger rather than writing a generic message.

### 4. Draft
Deliver:
- **Primary message** in the four-beat pattern.
- **Alternate** using a different hook or a different ask (Campfire-named vs. pure question).
- **Connection-request version** under 300 characters, in case they're not connected yet.

### 5. Self-check before showing Peter
- Every fact, name, number, date and quote traces to a source listed below the draft. Never invent or round a metric, never paraphrase a quote inside quotation marks.
- Call details are operational (close days, systems, process pain). Never repeat pricing, competitor evaluations, budget, personnel complaints, or anything said in confidence.
- Named colleagues (like "Ellie") must have actually been on the call, and should still be at the company or be clearly referenced in the past.
- One question, under ~90 words, no banned phrases, reads like Peter typed it.
- Run the `avoid-ai-writing` skill in casual voice if anything sounds polished.

### 6. Output format

```
**{Name} — {Title}, {Company}**
Trigger: {what + date}

Primary:
{message}

Alternate:
{message}

Connection note (≤300 chars):
{message}

Sources:
- [Attention call, {date}]({link}) — {what was used}
- [{Article title}]({url}) — {quote used}
- [HubSpot record]({link})
```

For a batch, repeat the block per person and put a one-line summary table at the top (name, trigger, hook used, any flags).

### 7. After drafting
Offer, don't do automatically: log a HubSpot note on the contact with the trigger and hook, or set a follow-up reminder 5 to 7 business days out. Never send LinkedIn messages or emails.

