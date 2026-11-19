---
name: "book-overlap-check"
description: "Find meetings, deals, or bookings that a teammate made on accounts in the running user's own book (HubSpot SDR Owner = user), so overlaps can be sorted out under ROE. Use when the user asks \"did anyone book my accounts\", \"check if someone booked in my book\", \"find accidental bookings on my territory\", \"book overlap check\", \"ROE conflicts on my accounts\", or wants this run as a recurring morning check."
---

# Book Overlap Check

Find meetings, deals, and bookings that **someone other than the user running this skill** created on accounts in that user's book. These are usually honest accidents. Nooks shows stale companies, deals get created without being linked to a company, and contacts change jobs. The goal is to surface overlaps quickly so they can be sorted out under ROE, not to assign blame. Keep the report factual and neutral.

No single source catches everything, so run every search below and merge the results.

**Read-only.** Never reassign records, edit HubSpot, or post in Slack. Report what you find and let the user act.

## Setup (every run)

1. **Identify the user.** Call HubSpot `get_user_details` and take `ownerId`. Confirm that COMPANY, CONTACT, DEAL and MEETING_EVENT are readable. Get the user's Slack user ID from the Slack search tool description, or from `slack_read_user_profile`.
2. **Define the book.** It is the set of COMPANY records where `sdr_owner` = the user's ownerId. Check with `search_properties` (keywords `sdr_owner`, `bdr_owner`, `account_owner`) that this property exists. If it doesn't, or the user isn't an SDR, ask which ownership field defines their book.
   - Never pull the whole book into context; books run to thousands of accounts. Always combine the owner filter with a narrowing filter in the same filterGroup, so HubSpot does the intersection.
3. **Set the window.** Default to the last 14 days. If the user names a window, use theirs. Convert it to a Unix timestamp with bash `date -d '<date> EDT' +%s` for Slack's `oldest` parameter.
4. **Find the channels.** Use `slack_list_user_channels` with `name_prefix` to get IDs. The defaults are:
   - Nooks booking feed: a channel containing `nooks`
   - Inbound meeting feed: `inbound-leads`
   - Deal and demo alerts: `deal-updates`, `disco-to-demo-alerts`
   - Wins and ROE chatter: `outbound-wins`, `sdr-handoff-notes`, `territory-feedback-sdr`

   If a channel isn't found or the user isn't a member, say so in the report. Don't skip it silently.

Large tool results get saved to a file. Use Grep with `-o` and tight regexes on that file instead of reading it whole.

## Searches

Run all of them. Throughout, exclude anything the user booked themselves: Nooks posts where the booker is the user, and HubSpot meetings created by their ownerId.

### A. Nooks headline company names
Read the Nooks channel over the window with `slack_read_channel` (use `oldest`/`latest`, and page until "no more messages"). Extract bookings with:
```
\*[^*]{1,60}\* just booked a meeting with \*[^*]{1,60}\* \(_[^_]{0,120}_\) at \*[^*]{1,80}\*
```
Collect the company names, leaving out the user's own bookings. Search COMPANY with `sdr_owner = ownerId` AND `name IN [names]`. Include obvious variants, such as with and without "Inc." or "LLC".

### B. Emails in Nooks notes and summaries (catches job-changers)
Nooks headlines often show the contact's *previous* company. Reps record the real current email in "Notes from …" or the AI summary. Extract every domain from the same Nooks text:
```
@[A-Za-z0-9][A-Za-z0-9-]*\.[A-Za-z.]{2,}
```
Drop `slack-bots.com`, the company's own domain, and free-mail domains (gmail, outlook, hotmail, yahoo, icloud, and misspellings like gamil). Strip trailing dots and lowercase everything. Search COMPANY with `sdr_owner = ownerId` AND `domain IN [domains]`. This is the highest-value search, so never skip it.

Also scan the channel for messages a person posted, rather than the Nooks bot, about a call that didn't sync (e.g. "my call is not populating in nooks… can you pull up X at Y"). Check those companies too.

### C. Inbound meeting feed
Read the inbound channel over the window. Extract lead emails, from `<mailto:x@domain|...>` or a bare address, and company names. Search COMPANY with `sdr_owner = ownerId` AND (`domain IN [...]` OR `name IN [...]`), using two filterGroups. Skip free-mail domains for the domain match.

### D. Slack DMs from teammates
Search DMs since the window start for messages *not from the user* that contain HubSpot links or ROE language:
- `slack_search_public_and_private`, keywords `["hubspot"]`, filters `is:dm after:YYYY-MM-DD -from:<@USER_ID>`
- A second pass with keywords like `book`, `ROE`, `booked`, `SQO`
- Pull company record IDs from links matching `record/0-2/(\d+)`. Fetch them with `get_crm_objects` (COMPANY, properties `name, domain, sdr_owner`) and keep the ones where `sdr_owner` = ownerId.
- When a DM has no context, read the surrounding messages in that DM before reporting it.

### E. Your accounts with recent meetings or open deals
Search COMPANY with three OR'd filterGroups, each containing `sdr_owner = ownerId` plus one of:
- `hs_last_booked_meeting_date GTE <window start ISO>`
- `notes_next_activity_date GTE <window start ISO>`
- `hs_num_open_deals GTE 1`

Properties: `name, hs_last_booked_meeting_date, notes_next_activity_date, hs_num_open_deals, hubspot_owner_id`.

### F. Who created those meetings
For the accounts from E that aren't already explained, search MEETING_EVENT with `associatedWith` companies IN [those IDs] (max 100 per filter) AND `hs_createdate GTE <window start minus ~7 days>`. Properties: `hs_meeting_title, hs_meeting_start_time, hs_createdate, hubspot_owner_id, hs_created_by_user_id`.
- Flag any meeting where `hs_created_by_user_id` is not the user.
- Resolve user IDs to names with a USER search on `hs_internal_user_id IN [...]`.
- Recurring syncs, and AE-run meetings on deals that already exist, are usually not overlaps. List them as "ruled out" with the reason.

### G. Deals not linked to the company
Search DEAL with `createdate GTE <window start>`, properties `dealname, hubspot_owner_id, createdate` only, and keep the limit low (page through if needed). Compare each deal name against the user's accounts: for each distinctive word in a deal name, run COMPANY `sdr_owner = ownerId` AND `name CONTAINS_TOKEN <word>`. Also scan the deal and demo alert channels for deal names.

### H. Duplicate company records (optional)
For each flagged account, search COMPANY `name CONTAINS_TOKEN <distinctive word>` with no owner filter. A second record owned by a different SDR means bookings may be landing on the duplicate. Report it as a note.

## What not to do
- Don't use Amplemarket or other enrichment tools to work out current employers. Their data lags job changes, so it misses exactly the job-changers search B catches, and each lookup costs credits and a lot of output.
- Don't search HubSpot contacts by last name alone. Common names return thousands of records.
- Don't report "nothing found" if a channel read failed or came back empty. Report it as a failure to look.
- Don't frame overlaps as wrongdoing. State who booked it, how and when, and let the user follow ROE.

## Report

Keep it short and lead with the matches:

```
N accounts in your book have activity from a teammate · <window>

• <Account> — <who> · <how: Nooks / meeting created / DM / deal> · <date>
  <one line of evidence, e.g. "rep note shows @domain — contact changed companies">
  <HubSpot record link from urlTemplate>

POSSIBLE (verify)
• <Account> — <why it's uncertain>

RULED OUT
• <Account> — <reason: your booking / AE recurring sync / existing deal>

Checked: <n> Nooks bookings · <n> note domains · <n> inbound leads · <n> DMs · <n> accounts with recent meetings/deals
Gaps: <bookings with no email noted, free-mail leads, channels that weren't found>
```

Use the record URL from the search result's `urlTemplate`; don't build one by hand. End by offering to run this as a weekday morning scheduled task covering "since last run".

