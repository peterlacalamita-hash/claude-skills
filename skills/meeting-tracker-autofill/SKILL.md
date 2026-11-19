---
name: meeting-tracker-autofill
description: Autofill an SDR's existing meeting pipeline tracker (shared via the Google Sheets connector or open in Claude in Chrome) against HubSpot and their Google Calendar — add newly booked meetings, update statuses (declined, cancelled, rescheduled, completed), fill in AEs, deal links, contact details and notes. Use whenever an SDR shares their meeting tracker / pipeline tracker sheet link and asks to "update it", "sync it", "sync it again", "refresh my tracker", "autofill my tracker", "update my meetings sheet from HubSpot", or asks why a meeting isn't on their tracker. Also use for recurring tracker syncs.
---

# Meeting Tracker Autofill

Keeps an SDR's monthly meeting tracker (Google Sheet) in line with what HubSpot and their calendar say. The sheet feeds quota attainment, show rate and SAO→SQO %, so wrong statuses or missing rows directly distort the SDR's numbers.

## The tracker comes from the user — never create one

This skill only fills in the user's **existing** tracker. Never create a new spreadsheet, Excel/.xlsx file, CSV, or copy of the sheet — not as a fallback, not as a "draft". A second file splits the SDR's numbers across two places and their manager won't see it.

The user shares their tracker one of two ways:
1. **Google Sheets connector (preferred):** they paste the sheet link. Read and write it with the Sheets editor tools.
2. **Claude in Chrome:** they have the tracker open in their browser (Google Sheets or Excel Online). Read it with the page tools and type updates directly into the cells in that tab.

If the user hasn't shared a tracker, or neither route is available (Sheets connector off and Chrome not connected), stop and ask them to either paste the link with the Google Sheets connector turned on, or open the tracker in Chrome with Claude in Chrome connected. Do nothing else until they do.

## Other required connectors

Google Calendar and HubSpot. If either is missing, tell the user which one to connect; you can still sync from whichever source is available, but say what was skipped.

## Expected sheet layout

The Campfire template has a "Read Me" tab and a meetings tab with one block per month stacked vertically:

- Summary row: `MONTH | attainment % | | Quota = | n | SQOs = | n | | | Meeting Show Rate = | % | SAO to SQO % = | %`
- Header row, then ~25 data rows:
  `A Account Name | B Contact Name | C Title | D IB V. OB | E Booking Date | F Meeting Date | G Pending v. Overdue | H Meeting Status | I Invite Accepted? | J SQO'd? | K Deal Owner (AE) | L Hubspot Deal Link | M Notes | N CL Notes`
- Status values: Scheduled, Completed, Rescheduling, No Showed, Cancelled.
- Column G and the summary row are formulas. **Never write to column G or the summary rows.**

Read the Read Me tab first if the layout looks different and adapt.

## Workflow

### 1. Read the sheet and identify the user
- `get_values` on the whole meetings tab. Record the **exact row number** of every existing row by counting from row 1 (empty rows count). Off-by-one row math is the most common failure — it overwrites neighbouring meetings. Before every write, confirm the target row's current column A matches what you expect.
- HubSpot `get_user_details` → the user's owner ID.

### 2. Build the candidate list from two sources
Meetings belong to the SDR if **either** is true:

**a) Book of business (primary):** companies where the HubSpot `sdr_owner` property = the user's owner ID. Search companies with `sdr_owner = ownerId` and `num_associated_deals >= 1`, then pull their deals created in the tracker's months, plus associated MEETING records (title, start time, outcome) and contacts (name, title, email, LinkedIn). A meeting counts even if a teammate booked it or another rep owns the deal/contact — the SDR owner is what matters.

**b) Calendar:** list events over the tracker's date range. Calendars are noisy (call reminders, 1:1s, internal meetings), so filter to events with an external (non-company-domain) attendee and a prospect-style title ("Campfire <> X: Introduction", "X <> Campfire | Intro"). Large results get saved to a file — grep it for `summary`, `start.dateTime`, external attendee emails and `responseStatus` rather than reading it whole, or re-query a narrow window with `fullText`.

### 3. Reconcile each candidate
| Signal | Sheet update |
|---|---|
| Not on sheet | Add to the first empty row of the month the **meeting date** falls in |
| Prospect declined the invite | Cancelled (or Rescheduling if there's evidence of a rebook) |
| HubSpot meeting outcome CANCELED / title "Canceled:" | Cancelled |
| Prospect accepted | Invite Accepted? = TRUE |
| Meeting moved | Update Meeting Date; note the original date in Notes |
| Deal stage moved to the SQO stage (check what stage existing SQO'd rows use) | Flag it — let the user tick SQO'd? unless they've asked you to |
| Past meeting, no outcome logged | Leave Scheduled and flag it ("confirm outcome") — don't guess Completed or No Showed |

AE = the calendar organizer from the company domain, or the name in the HubSpot meetings link (e.g. `/meetings/joe-clines/`). Deal link format: `https://app.hubspot.com/contacts/<portalId>/record/0-3/<dealId>`. Notes format: `Email: x | LinkedIn: y | Meeting: Day M/D h:mm-h:mm PM ET` plus anything notable (booked by a teammate, placeholder meeting, personal email).

### 4. Respect the user's own edits
On re-syncs, the user may have changed things by hand since the last sync. If the sheet disagrees with HubSpot/calendar on a field the user clearly set themselves (e.g. a status flipped back), **don't overwrite it** — flag the conflict and let them decide.

### 5. Write
- **Sheets connector:** write A–F and H–M as two separate `update_values` calls per block so column G's formula is never touched. Dates as `MM/DD/YYYY` strings; checkboxes as booleans.
- **Claude in Chrome:** click into each cell (use the Name Box to jump to e.g. `H37`) and type the value; skip column G; toggle checkboxes by selecting the cell and pressing Space. Work row by row and screenshot after each row to confirm it landed in the right place.

### 6. Verify and report
Re-read the rows you touched and confirm each landed on the right account. Then give a short summary:
- New rows added
- Rows updated (what changed and why)
- Things to check: conflicts with the user's edits, unlogged outcomes, unknown AEs, deals in the user's book that look like meetings but have no calendar event or meeting record

Keep the summary tight — the user can see the sheet.
