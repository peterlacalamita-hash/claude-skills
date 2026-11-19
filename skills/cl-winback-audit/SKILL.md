---
name: "cl-winback-audit"
description: "Audit a Campfire closed-lost revival account or prospect-facing draft against the Q4 2026 Win-Back campaign: bucket, incentive, guardrails, holds, ownership. Run before drafting or sending any C/L revival outreach."
---

# C/L Win-Back Audit (Q4 2026)

Use this before drafting, and again before sending, any outreach to an account in the OB SDR C/L Revival list (HubSpot list 6073) or any account with a Win-Back field populated. Also use it when Kyle pastes a draft and asks if it's on-campaign.

Source of truth:
- Campaign deck: Q4 Closed-Lost Win-Back: SDR Enablement (Drive id 15Tm9xUS3ghkTPMEqKKVLlZLp9jaLiJ5V8khxED987xk)
- Universal Call Playbook V2 (Drive id 17BkyL714-Vr-mn24sq3fYAXy35JEUDPf9OvUz2pmOn0)
If either doc has changed, the doc wins over this skill. Re-read it when in doubt.

## Step 1: Pull the account fields (HubSpot company)

Read: name, sdr_owner, hubspot_owner_id, win_back_offer, win_back_tier, win_back_hold, win_back_closed_lost_reason, current_erp, erp_contract_end_date, erp_contract_end_date_confirmed, competitors_evaluated, notes_last_contacted. Also the most recent deal (owner, close date, stage) and any email or call on the company in the last 14 days.

## Step 2: Gates (stop and report if any fail)

| Gate | Rule |
|---|---|
| Hold | win_back_hold is not blank -> do not send. Report the hold and what would clear it. |
| SDR Owner | Must be Kyle (162726725). If blank, flag "request assignment before send". If someone else, stop. |
| Recent touch | Any Campfire email, call or sequence on the company in the last 7 days from someone else -> flag collision, name the sender. |
| Recent close | Deal closed lost in the last 30 days -> the closing AE must clear reopening first. |
| AE | Name the AE who stays on the account (deal owner or company owner). If they differ, flag it. |

## Step 3: Bucket and offer check

Map win_back_offer to bucket:

| win_back_offer | Bucket | Prospect-facing incentive language |
|---|---|---|
| Buyout (paid ERP) | Legacy ERP | "we're helping teams buy out existing ERP contracts so they don't have to wait for renewal" |
| Confirm incumbent | Legacy ERP (per deck) but confirm system first | No incentive until the current system is confirmed |
| Rillet win-back | Rillet Win-Back | Open on "how's it working out"; buyout help "for qualified teams" |
| EOY price (QBO/Xero) | QBO/Xero | "3 free months for qualifying teams that meet with us before year-end and make the switch" |

Then sanity-check the seeded offer against the facts:
- current_erp blank -> flag. Pull it from calls (Attention) and propose the value; ask before writing.
- Lost to Rillet (loss reason, competitors, or prospect said so) but offer is Buyout -> recommend Rillet bucket.
- Revenue-only or subledger-only scope where they keep the ERP as GL -> buyout does not fit. Flag mismatch.
- QBO/Xero account with buyout language, or ERP account with free-months language -> wrong bucket.

## Step 4: Copy guardrails (check every prospect-facing line)

P0, must fix:
- Any percentage or TCV math (internal caps: Legacy 50%, Rillet 100%). Never in copy or on calls.
- "Full coverage", "we'll cover your contract", or guaranteed eligibility. Always "help with" or "up to" with no number, and "depending on the agreement".
- A December 31 deadline attached to a buyout. Only the QBO/Xero offer has a year-end condition.
- QBO/Xero offer stated as unconditional, or as "15 months for the price of 12". It needs a completed meeting before Dec 31 and a purchase.
- Disparaging NetSuite, Rillet or any ERP (e.g. calling it legacy junk, saying Rillet falls short).
- Implying hands-off or guaranteed implementation timelines.
- Unverified intro, relationship or prior meeting (verify against email or Attention first).
- Unapproved stats (e.g. "200+ customers", "50% savings", "close in under 5 days").

P1, should fix:
- Incentive missing entirely on a touch where the account is in a buyout or free-months bucket. The campaign rule is "lead with the incentive, sell the problem". On a first email it can follow a specific trigger; by the second touch it must be present.
- Incentive with no problem attached. Every touch needs the unresolved problem from their own call.
- Assumes they're still on the same system with no question to confirm it.
- Ask is not a 20-minute re-evaluation.
- More than one question in the close.

P2: length outside 80-130 words for email, 60 for LinkedIn; em dashes; jargon.

## Step 5: Output

Return one table per account:

| Field | Finding |
|---|---|
| Gates | pass / which failed |
| Bucket | seeded offer -> recommended bucket, with reason |
| Data gaps | current_erp, contract end, etc., with proposed values from calls |
| Copy findings | quote, rule, severity, fix |
| Next touch | what the incentive line should be on the next email or call |

Then the corrected copy. Do not write to HubSpot without Kyle's approval. Never send.

## Approved incentive lines (reuse these)

Legacy ERP, email: "We're helping teams buy out existing ERP contracts, so a change doesn't have to wait for renewal. [AE] can walk through what that could look like for your agreement."

Rillet, email opener: "I know you went with Rillet. How's it actually working out?" Then: "We're now helping qualified teams buy out existing contracts, so you may not have to wait until renewal to take another look."

QBO/Xero, email: "We're offering 3 free months for qualifying teams that meet with us before year-end and make the switch."

Objection, "how much will you cover?": "It depends on your current agreement and what a move to Campfire would look like. Our team can walk through it once we understand your situation."