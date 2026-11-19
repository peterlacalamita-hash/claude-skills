# Matching leads to the book

## Parser output

`scripts/extract_leads.py` reads a text dump of channel messages and writes a JSON array:

```json
[
  {
    "name": "Dana Whitfield",
    "company": "North Harbor Group",
    "email": "d.whitfield@northharbor.com",
    "domain": "northharbor.com",
    "is_freemail": false,
    "booked_meeting": true,
    "timestamp": "2026-09-14 08:16:10 EDT",
    "raw": "…original message text…"
  }
]
```

- `booked_meeting` is `true` when the message says a meeting was booked, `false` when it says one wasn't, and `null` when the wording doesn't make it clear. Treat `null` as "unknown" in the report rather than silently filing it under form fills — the user's workflow may word things differently than the patterns the parser knows.
- `is_freemail` marks consumer email domains: gmail, googlemail, yahoo, ymail, hotmail, outlook, live, msn, icloud, me, mac, aol, comcast, verizon, att, sbcglobal, protonmail, proton.me, gmx, mail.com, zoho, yandex, qq, 163, fastmail, hey.com, duck.com.
- Duplicates are collapsed by email, keeping the earliest message and preferring `booked_meeting: true` if the same person appears both ways.

Run `--help` for options. `--since ISO8601` filters by timestamp if you'd rather let the parser trim the window than page Slack precisely.

## Query shapes

These are written against HubSpot's CRM object search. The essential trick is putting the ownership filter and the lead filter **in the same filter group** — filters within a group are ANDed, separate groups are ORed. A common mistake is putting them in separate groups, which returns the user's entire book plus every company with that domain.

**Domain match within the book:**

```json
{
  "objectType": "COMPANY",
  "filterGroups": [{
    "filters": [
      {"propertyName": "<owner_property>", "operator": "EQ", "value": "<owner_value>"},
      {"propertyName": "domain", "operator": "EQ", "value": "northharbor.com"}
    ]
  }],
  "properties": ["name", "domain", "<owner_property>", "hs_object_id"]
}
```

Several domains at once — `IN` with a list of values on `domain`, same group as the ownership filter. Batching this way keeps the run to a handful of calls instead of one per lead, which matters on a busy morning.

**Contact lookup by email**, to find the company HubSpot already associates with the lead:

```json
{
  "objectType": "CONTACT",
  "filterGroups": [{"filters": [{"propertyName": "email", "operator": "EQ", "value": "d.whitfield@northharbor.com"}]}],
  "properties": ["email", "company", "hubspot_owner_id"]
}
```

Don't count on `associatedcompanyid` coming back — several portals return only default properties here and ignore the request, so a plan that depends on reading that field quietly yields nothing. Get the association from the other direction instead, with an association filter on the company search. This is the better query anyway: it does the join server-side and keeps the ownership filter applied, so one call answers "is this contact's company in the book?" outright.

```json
{
  "objectType": "COMPANY",
  "filterGroups": [{
    "filters": [{"propertyName": "<owner_property>", "operator": "EQ", "value": "<owner_value>"}],
    "associatedWith": [{"objectType": "contacts", "operator": "IN", "objectIdValues": [998877665544, 998877662211]}]
  }],
  "properties": ["name", "domain", "<owner_property>", "hs_object_id"]
}
```

Batch the contact IDs with `IN` — one call covers every lead that resolved to a contact. A hit means that company is in the book and is associated with one of those contacts; check which by looking at the returned company's associations or by falling back to the domain.

**Name match**, free-mail fallback only:

```json
{
  "objectType": "COMPANY",
  "filterGroups": [{
    "filters": [
      {"propertyName": "<owner_property>", "operator": "EQ", "value": "<owner_value>"},
      {"propertyName": "name", "operator": "CONTAINS_TOKEN", "value": "*northharbor*"}
    ]
  }]
}
```

Report anything found this way as unconfirmed. More than one hit means don't pick a winner — show the candidates.

Name matching on short or generic tokens is noisy in a way that's worth heading off: searching `*merchant*` or `*perk*` turns up MerchantCircle, CFG Merchant Solutions, Colman Perkins Law Group — companies that share a word and nothing else. **Use judgment and drop hits that are plainly different entities.** Padding a "nothing matched" report with three false candidates trains the user to skim past the section that matters on the morning something real lands. Keep a name hit when the whole name essentially matches (differing only by Inc/LLC/Ltd, punctuation, or an obvious abbreviation); drop it when only one common word overlaps. When you drop hits, no need to enumerate them — the report is better for their absence.

## Domain normalization

Before matching, lowercase the domain and strip a leading `www.`. Beyond that, leave it alone: `mail.acme.com` and `acme.com` are genuinely different domains and collapsing subdomains creates false matches. If a lead's subdomain doesn't match but the root does, surface it as unconfirmed rather than deciding.

Country domains are a known soft spot — someone at `acme.co.uk` won't match a book entry stored as `acme.com`. If a domain match fails and the company name is present, the name fallback catches some of these. It isn't worth building elaborate heuristics for; a missed match here shows up as a lead the user spots another way, whereas a wrong match sends them chasing someone else's account.

## What counts as a match

A match means the company behind the lead carries the user's owner value on the configured property. Two things that are *not* matches, and shouldn't be reported as one:

- The contact's `hubspot_owner_id` is the user but the company isn't in their book. That's a contact they touched, not an account they own.
- The domain matches a company that exists in HubSpot but is owned by someone else. That's someone else's lead. It can be worth a single line at the end if the user is curious, but only when the config says to include it — by default, leave it out.
