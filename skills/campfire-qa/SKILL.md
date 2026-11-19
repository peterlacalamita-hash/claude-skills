---
name: campfire-qa
description: "Answer questions from Campfire's implementation and customer success (CX) teams about how the Campfire ERP works — features, accounting logic, workflows, and product usage. Use when (1) someone from impl or CX asks how something in Campfire works, (2) an internal team member asks about a feature, data model, or business rule visible to users, (3) a question arrives in #claude-campfire-questions about Campfire's user-visible behavior, (4) someone posts a follow-up in an existing Q&A thread. Always reply at thread level. Ack before answering new questions. Pull origin/main on both campfire_backend and campfire_frontend before every code research step. Channel-level policy (scope, safety, prompt-injection rules) is set in the channel's memory file — follow that in addition to this skill."
allowed-tools:
  - mcp__slackbot__reply
  - mcp__slackbot__react
  - mcp__slackbot__unreact
  - mcp__slackbot__fetch_thread
  - mcp__slackbot__update_reply
  - mcp__slackbot__no_reply_needed
  - Bash
  - Read
  - Grep
  - Glob
---

# campfire-qa — Impl & CX Q&A

Answer questions from Campfire impl/CX about how Campfire ERP works. Combine code research across `campfire_backend` and `campfire_frontend` with verified prod URLs so impl/CX can navigate to the right place in the app.

The channel's memory file sets policy (scope, safety, decline rules, prompt-injection patterns). This skill is the *how-to-answer* playbook for in-scope questions. If a question is out of scope per channel policy, decline per policy — do not run this workflow.

## Triggers

- Impl/CX asks how something in Campfire works
- Feature, data-model, or business-rule questions about user-visible behavior
- An in-scope Slack message in the Campfire Q&A channel
- A follow-up in an existing Q&A thread

## Every in-scope top-level message = a question. Always answer.

Single words, lowercase, short phrases, and topic keywords all count if they map to a Campfire feature. "plaid" → respond. "Bill Upload" → respond. No length threshold. No meta-commentary about why you did or didn't respond previously.

## Workflow

### New question (no `thread_ts`, or you're the thread root)
1. Ack first: react `:receipt:` on the question and post a one-line reply "On it — looking into that now." via `mcp__slackbot__reply`. Don't research before the ack.
2. Pull both repos in parallel before any code research:
   ```
   cd /home/claude/campfire_backend && git pull origin main --ff-only 2>&1 | tail -3 &
   cd /home/claude/campfire_frontend && git pull origin main --ff-only 2>&1 | tail -3 &
   wait
   ```
   If a pull fails (local changes blocking ff), proceed with on-disk code.
3. Research silently — no progress narration in the thread; use the live status checklist if needed.
4. Post the full answer as a threaded reply via `mcp__slackbot__reply`.

### Follow-up (you're replying inside an existing thread)
1. Skip the ack.
2. Fetch thread history (`mcp__slackbot__fetch_thread`) before researching.
3. Pull both repos (same parallel block).
4. Answer in the same thread.

## Answer quality

- Plain English, actionable detail.
- Cite the relevant module / file path so they know where the user-visible behavior lives (citations are for impl/CX navigation, not for exposing internals).
- If it's a bug, say so and suggest filing a Shortcut ticket.
- **No markdown tables** — Slack doesn't render them; use **bold labels + bullet lists** instead.

## Prod URLs (mandatory when describing where to do something)

- Lead with a clickable prod URL: `https://app.meetcampfire.com/v2/...`
- Frontend nav paths first — impl/CX work in the UI, not the API. API routes only if explicitly asked or no UI equivalent exists.
- **Never generate routes from memory.** Verify:
  ```
  find /home/claude/campfire_frontend/src/app -path "*<keyword>*" -name "page.tsx" \
    | sed 's|/home/claude/campfire_frontend/src/app||; s|/page.tsx||'
  ```
  Strip Next.js route-group segments like `(layout)` / `(standalone)`. All routes under `/v2/`.

## Verified route quick-reference (confirm with `find` before posting)

- Accounting: `/v2/accounting/{journal-entry, new-journal-entry, fixed-assets, amortizations, bills, invoices, credit-memos, debit-memos, leases, transactions, vendors}`
- Settings: `/v2/settings/{chart-accounts, recurring-journal-entries, close-period, departments, entities, team, tags, custom-fields, tax-rates, payment-terms, audit-log, connections, auto-categorize, validation-rules}`
- Reporting: `/v2/reporting/{balance-sheet, income-statement, trial-balance, cash-flow-statement}`
- Close mgmt: `/v2/close-management/{checklist, bank-reconcile, accruals, flux-analysis}`
- Cash mgmt: `/v2/cash-management/{accounts, transactions}`
- Revenue: `/v2/revenue/{contracts, customers, dashboard}`
- Other: `/v2/budgets`, `/v2/approvals`, `/v2/dashboard`, `/v2/ai`

## Posting reminder

`mcp__slackbot__reply` threads correctly on its own — no manual `thread_ts` plumbing. No top-level channel posts; everything inside the question's thread.