# claude-skills

Peter's Claude skills, backed up from the old Campfire Enterprise account (`Claude Directory/Claude-Migration-Backup`).

## Layout

| Folder | What's in it |
|---|---|
| `skills/` | 16 custom skills, one folder each (`SKILL.md` plus any scripts, references, assets) |
| `zips/` | Ready-to-upload zips of the 15 Campfire/third-party skills (folder at the top of each zip) |
| `plugins/sales/` | Copy of Anthropic's `sales` plugin (v2.1.0, Apache-2.0). Reinstall it from the plugin catalog rather than uploading. |

## Skills

**Campfire SDR / AE**
- `ae-precall-notes` — SDR notes + AE Slack handoff for booked meetings
- `book-overlap-check` — teammate meetings/deals on accounts in your book
- `book-prioritization` — walk a rep through their book of business
- `campfire-qa` — answers for implementation/CX on how the Campfire ERP works
- `cl-winback-audit` — audit closed-lost revivals against the Q4 2026 Win-Back campaign
- `ent-strat-acct-outreach` — end-to-end ENT outbound: research, draft, audit, Gmail draft
- `inbound-lead-book-match` — match Slack inbound leads to your HubSpot accounts
- `linkedin-first-message` — opening DM after a connection accept
- `meeting-tracker-autofill` — fill the meeting tracker from HubSpot + Calendar
- `roe-infraction-check` — SDR attribution / rules-of-engagement audit
- `sdr-account-enrichment` — find finance contacts for ENT/MM accounts
- `sdr-hand-off-notes-jakes` — Jake's team-standard hand-off notes
- `signal-send` — Signal → Send (ENT) outbound drafter
- `thoughtful-linkedin-outreach` — trigger-based LinkedIn outreach

**General**
- `avoid-ai-writing` — strip AI-isms from writing (third-party)
- `claude-account-migration` — process a Claude data export into a migration package

## Adding a skill to a Claude account

Upload the matching zip from `zips/` as a custom skill. For `claude-account-migration`, zip `skills/claude-account-migration` with the folder at the top.
