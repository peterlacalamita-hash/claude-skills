---
name: signal-send
description: Set up or open "Signal → Send (ENT)", Campfire's Enterprise SDR outbound drafter that writes LinkedIn messages and cold emails from the ENT SDR playbook, after checking HubSpot (SDR Owner, lifecycle, fit) and Attention (prior calls). Use when the user says "signal send", "set up the outbound drafter", "draft outreach with the ENT playbook", or wants to install or reopen this tool.
---

# Signal → Send (ENT)

This skill installs the drafting page into the user's OWN Claude account so it runs on their own HubSpot and Attention connectors.

## First run: publish the page

1. Look for an existing copy first: Artifact `action: "list"` and check for a title starting "Signal → Send". If one exists, Artifact `action: "open"` it and stop.
2. Otherwise publish `assets/signal-send.html` (in this skill's folder: `${CLAUDE_SKILL_DIR}/assets/signal-send.html`). Copy it into the working directory first if the Artifact tool needs it there. Publish with:
   - `icon`: "mail"
   - `description`: "Enterprise SDR outbound drafter built on the Campfire ENT playbook, with a HubSpot/Attention ROE check."
   - `capabilities`:
     ```json
     {"mcp": {"servers": [
       {"server": "HubSpot", "tools": ["search_crm_objects", "get_properties", "get_user_details", "search_owners"]},
       {"server": "Attention", "tools": ["search_calls", "get_call_details"]}
     ]}, "sample": {}}
     ```
   Publish the file exactly as bundled. Do not edit the prompt or logic.
3. Tell the user in two or three lines:
   - The page is private to them.
   - HubSpot and Attention must be connected in claude.ai Settings → Connectors (named exactly "HubSpot" and "Attention"). The first time they generate, they'll be asked to allow the page to use those connectors and to ask Claude.
   - Ownership is checked against their own HubSpot user. If they aren't on the SDR Owner list yet, the page says so; RevOps can add them.

## If the user can't publish artifacts

Fall back to drafting in chat: use the system prompt inside `assets/signal-send.html` (the `SYSTEM_PROMPT` constant) as the rules, run the same HubSpot gate (SDR Owner vs. the user's own owner ID from get_user_details, lifecycle not Customer/Churned/SAL/SAO/SQO, Temporary Disqualified, FTE 500–5,000) and the Attention call lookup with the user's connectors, then write the drafts. Stop and ask before drafting if the account belongs to another SDR.
