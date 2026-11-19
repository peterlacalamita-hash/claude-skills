# First-run setup

Setup answers three questions: who the user is in HubSpot, where inbound leads arrive, and which field marks an account as theirs. Do the investigation *before* asking anything, so the user picks from real options found in their own portal rather than typing field names from memory. Most people don't know whether their book runs on `hubspot_owner_id` or a custom property, and asking them cold produces wrong answers.

## 1. Identify the user

Call the HubSpot user-details tool. It returns `ownerId` (the value that appears in owner fields) and `accountId` (the portal ID). No question needed — this is just a lookup.

This doubles as the HubSpot connection check from Step 0a. Alongside identity it reports per-object read access: confirm **companies** and **contacts** are both readable, because the check is built on exactly those two. If either isn't, the user's HubSpot admin controls it — say which object and stop, rather than proceeding to an interview whose answers can't be used.

## 2. Find the inbound channels

Search Slack channels for likely names — `inbound`, `leads`, `demo`, `inbound-leads`, `demo-requests`, `gated-content` — across public and private channels.

Then read the last handful of messages in each plausible one and check whether they actually look like lead notifications: email addresses, company names, a repeated template from an integration. This sorts real feeds from channels that merely sound like one. A channel that reads as human conversation, or that has nothing in it but join notices, isn't the feed.

Bigger orgs routinely run **more than one** inbound feed — a website form-fill channel and a separate gated-content or paid-ads channel, with different message templates and very different lead quality. So don't stop at the first good hit. Present what you found and let the user pick one or several:

- **One strong candidate**: propose it and let the user confirm rather than assuming. Channel names are suggestive, not definitive.
- **Several**: show each with its volume and what the messages look like, note which are high- vs low-quality (a feed that's mostly free-mail addresses will only ever match on company name), and ask which to include.
- **None**: ask for the channel name directly, then look it up.

Store channel IDs, not just names — names get changed and IDs don't.

## 3. Find the ownership field — empirically

This is the step worth doing carefully, because it's where a plausible guess fails silently.

Search COMPANY properties for owner-ish names: `owner`, `sdr_owner`, `bdr_owner`, `account_owner`, `rep`, `assigned`. You'll typically get several hits, including `hubspot_owner_id` and one or more custom fields.

Then **test each candidate** by running a company search filtered on that property equal to the user's `ownerId`, and note the result count. This turns a guess into evidence: the field that holds their book returns hundreds or thousands of companies, the wrong ones return zero.

Present what you found, with counts:

```
Found two fields that could define your book:
  • Patch Owner (patch_owner) — 1,840 companies
  • Company owner (hubspot_owner_id) — 0 companies

Looks like Patch Owner is the one. Confirm?
```

(Illustration only — the field names and counts you find will be this portal's, not these.)

Cases worth handling explicitly:

- **Every candidate returns zero.** Their accounts may not be assigned yet, or their book may be defined some other way — a HubSpot list, a territory field, a team-level rollup. Say that plainly and ask how they'd identify their accounts. If it's a territory value rather than an owner ID (say a `territory_name` property holding something like "West 3"), that works fine: config stores a property and a value, and the value doesn't have to be an owner ID.
- **Two fields both return large counts.** Ask which one governs. A portal might have an AE owner and an SDR owner on the same company, and which one counts as "your book" depends on the user's role.
- **The counts look implausibly large** (say, the entire portal). The property is probably not an ownership field. Flag it rather than accepting it.

## 4. Ask about form fills

Inbound channels usually carry two kinds of message: someone booked a meeting, and someone submitted a form without booking. Ask whether the user wants both or only booked meetings.

Default to both. A form fill on an owned account is still the user's to chase, and it's easy to skim past a section they don't care about — whereas a missed lead they never saw is invisible. But someone with a noisy channel may want only meetings, so ask rather than deciding for them.

## 5. Write the config

Create the directory if needed and write:

The shape, with placeholder values — fill every one of them from what you actually found and what the user confirmed:

```json
{
  "version": 1,
  "hubspot": {
    "owner_id": "<owner id from the user-details lookup>",
    "portal_id": "<portal / account id from the same lookup>"
  },
  "slack": {
    "channels": [
      {"id": "<channel id>", "name": "<channel name>"}
    ]
  },
  "book": {
    "object_type": "COMPANY",
    "owner_property": "<property the user confirmed, e.g. patch_owner>",
    "owner_property_label": "<its human label>",
    "owner_value": "<usually the owner id; a territory name for a territory-based book>",
    "approximate_size": 0
  },
  "report": {
    "include_non_meeting_leads": true
  },
  "last_run_iso": null
}
```

Write it with the file-writing tool rather than a shell redirect, so it lands on the user's actual machine.

Preferred path is `~/Claude/inbound-lead-book-match/config.json`, because every future session and every scheduled run looks there first. That folder usually sits outside what a session can write to, so ask the user to grant access to `~/Claude` — explain that it's where the config will live so the check doesn't have to be re-set-up each time. If they'd rather not, write `inbound-lead-book-match-config.json` into the current working folder instead and tell them plainly that runs started from a different folder won't find it.

`owner_value` is separate from `hubspot.owner_id` on purpose — they're usually the same, but a territory-based book uses a territory name here, and keeping them separate means that case needs no special handling anywhere else.

`approximate_size` is only a sanity check: if a later run finds the book has collapsed to zero, that's worth mentioning, since it usually means a territory reassignment rather than a quiet week.

## 6. Confirm and offer to run

Summarize what was saved in plain language — channel, field, book size, whether form fills are included — so the user can catch a wrong answer immediately. Then offer to run the check now over the last 24 hours, which both proves the setup works and gives them something useful on the spot.
