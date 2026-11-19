---
name: linkedin-first-message
description: Research a LinkedIn lead in the browser and write the opening DM sent after they accept a connection request. Use this whenever the user pastes a LinkedIn profile URL and wants a message, mentions a post-connect DM, a first touch, an opener, an InMail, or outreach to a new LinkedIn connection — and also when they ask to personalize or tweak a LinkedIn message for a specific account or person. Covers message one only, not follow-ups.
---

# LinkedIn First Message

Write the opening DM sent to a lead a few days after they accept a connection request. One profile in, one message out — researched in the browser, written so it does not sound like it came from an AI or a sequencer.

The whole job is to earn a reply, not a meeting. A reply is the only thing message one can realistically win, and every choice below serves it.

---

## Sender context

This block is the only company-specific part of the skill. Swap it when someone else uses this.

**Company:** campfire.ai — lets revenue teams build AI agents, automate workflows, and connect data silos without writing code.
**Target buyers:** VPs of Sales, RevOps leaders, Sales Enablement directors.
**Voice:** sharp, casual, peer-to-peer. Never corporate.
**Hard rule:** campfire.ai is never named or hinted at in message one. The moment a prospect knows what you sell, they stop answering your question and start evaluating a vendor. Selling starts in message three at the earliest.

---

## The move: borrowed authority from an adjacent role

Every message uses the same shape, because it solves the three problems a cold DM has all at once.

> "Most of my conversations are with [adjacent role]. They keep telling me [specific, slightly unflattering complaint]. Does that hold at [Company]?"

Why this works, so you can bend it intelligently rather than fill it in like a form:

- **"Most of my conversations are with X"** is social proof without a brag. It says you talk to a lot of people in their world, and it does it in passing.
- **The complaint does the heavy lifting.** It has to be something you could only know from actually talking to people. A marketing line ("teams struggle with data silos") gets ignored. A detail that sounds like a Tuesday ("their build queue is 40 deep and half of it is stuff sales asked for two quarters ago") gets a reply, because the prospect recognizes their own life in it.
- **Asking about the adjacent role's complaint invites them to correct the record.** People reply to defend their function far more readily than they reply to a benefit statement. This is the engine of the whole thing.
- **Putting them one rung above you** — you're the curious one, they're the expert — removes the thing they're braced for.

A useful side effect: a sender who is new to the industry can run this honestly. Curiosity is the actual posture, not a tactic bolted on top of one.

### Adjacent-role pairings

| Writing to | Borrow authority from | Complaint that lands |
|---|---|---|
| VP Sales / CRO | RevOps leads | requests sit in a queue for quarters and nothing ships |
| RevOps leader | VPs of Sales, CROs | every ask needs an engineer, so RevOps gets called a black hole |
| Sales Enablement | enablement managers, frontline AEs | content goes stale faster than anyone can rewrite it |
| Anyone | their direct peers at similar-stage companies | the AI pilot went fine and then never left pilot |

Pick the pairing by role, then let the research make the complaint specific to their situation. The table is a starting point, not the answer.

---

## Step 1 — Research the profile

Use Claude in Chrome (`mcp__claude-in-chrome__*` tools), not the built-in browser pane. LinkedIn only shows profile detail to a logged-in session, and Chrome is where the sender is already signed in. Load the tools in one call before starting:

`ToolSearch` with `select:mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__read_page`

Then, per lead:

1. Navigate to the profile URL and `get_page_text`.
2. Navigate to `<profile-url>/recent-activity/all/` and `get_page_text`. This is usually where the good material is — posts, comments, and reposts show what they care about right now, while the profile body only shows what they want to look like.
3. If the company is unfamiliar, open its LinkedIn company page for headcount, hiring, and recent announcements.

Reading pages with `get_page_text` beats screenshots here. You want the words, not the pixels.

**What to look for, roughly in order of value:**

- A role change in the last six months. New leaders are rebuilding and openly looking for ideas. This is the single best trigger.
- An opinion they posted, or a comment they left on someone else's post. Their own words are the strongest thing to reflect back.
- Hiring, especially a burst of AE or ops reqs — it means a process is about to break.
- Funding, a new tool in the stack, a reorg, an acquisition.
- A tenure long enough that they have opinions about how things got this way.

**What to ignore:** work anniversaries, "I'm humbled to share," generic reposts with no added comment, certifications, and anything a hundred other people already congratulated them on. Referencing those marks the message as automated, because automated messages are the only things that reference them.

### When the profile is thin

Say so. Do not manufacture a specific-sounding detail — a hollow personalization line ("loved your recent post!") is worse than no personalization, because it reads as a mail merge that half-worked and it costs the sender credibility they cannot get back.

Write the generic version instead, flag which detail was missing, and suggest where two more minutes of looking might pay off (company news, a press release, the careers page).

---

## Step 2 — Write it

**Shape:** four short blocks, under 75 words total, no more than five lines on a phone screen.

1. One line acknowledging the connection plus the real detail found in research.
2. The borrowed-authority setup.
3. The specific complaint.
4. A question answerable in one to four words, then an explicit release valve ("not a pitch", "one word is fine", "asking selfishly").

**The micro-ask is load-bearing.** A binary or near-binary question ("ship or sit?", "solved or still broken?", "headcount or tooling?") gets answered because answering costs nothing. "Would love to hear your thoughts on how you're approaching this" gets nothing, because it is an essay request from a stranger.

Timing worth passing along to the sender: two to three days after the connection is accepted. Same-hour messages read as automation no matter how good the copy is.

---

## Voice: how to not sound like an AI

This is the part that decides whether the message works. Good LinkedIn DMs read like a slightly too blunt text message from a colleague. Write it, then cut a fifth of the words.

**Do:**

- Vary sentence length hard. Mostly short. One longer sentence per message, maximum.
- Let one fragment through. "Asking selfishly." "Which I assume is unfair."
- Use one more contraction than feels correct.
- Prefer a real number to a vague quantity. "40 deep" over "a significant backlog."
- Allow a small aside that admits something — mild self-deprecation, a guess stated as a guess. It signals a person wrote it.
- Use periods where the instinct says em-dash.

**Don't** — these are the specific tells that get a message read as machine-written:

- Em-dashes. LinkedIn DMs do not contain em-dashes. Use a period.
- "Not just X, but Y." "It's not about X. It's about Y." Any antithesis construction.
- Three-item lists, especially three adjectives. The rule of three is the loudest tell there is.
- A rhetorical question followed by its own answer.
- "I couldn't help but notice", "I hope this finds you well", "Hope you're doing well", "In today's landscape", "excited to", "thrilled to", "I'd love to".
- Explaining their own job back to them. "As a VP of Sales, you know pipeline visibility is critical" tells them nothing and burns the only three seconds you get.
- Corporate verbs: leverage, utilize, streamline, unlock, empower, robust, seamless, holistic, journey, space (as in "the RevOps space").
- More than one exclamation mark in the whole message. Ideally zero.
- A sign-off. No "Best", no "Cheers", no name. It is a DM; the name is already on it.
- Symmetry. If two sentences share a rhythm, break one.

A fast check: read it out loud. If it sounds like something being *presented*, rewrite it. It should sound like something being *said*.

---

## Step 3 — Output

Per lead, in the reply (not a file, unless asked):

```
**[Name] — [Title] at [Company]**

> [message, exactly as it should be pasted]

**Hook used:** [the specific detail, and where it came from]
**Adjacent role borrowed:** [role] → [complaint]
**Expected reply:** [the one to four words they will probably send back]
```

Then one alternate version with a different hook or a different complaint, so the sender can pick by feel. Two options is the right number. More than that turns a decision into a task.

If several leads are handled at once, do not reuse the same complaint across all of them. Prospects talk, and varying it is also how the sender learns which complaints actually pull.

**Before handing anything over, check:**

- Is campfire.ai absent? (It must be.)
- Under 75 words?
- Is the hook a real detail from research, or did it drift into something plausible-sounding that was not actually on the page? Only the first is acceptable.
- Can the question be answered in four words?
- Zero em-dashes, zero tricolons, no sign-off?
- Would the sender be fine with this getting screenshotted and posted? On LinkedIn that is the real bar.
