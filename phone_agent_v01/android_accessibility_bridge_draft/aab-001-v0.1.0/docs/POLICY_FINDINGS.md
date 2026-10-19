# Policy and feature findings (web research 2026-10-15 PT; not device-verified)
## OpenAI Terms of Use (effective 1 Jan 2026) — https://openai.com/policies/terms-of-use/
"What you cannot do… Automatically or programmatically extract data or Output (defined below)." → no scraping/accessibility reading of ChatGPT. Owner-initiated Share/Copy is used instead.
## ChatGPT Android share/copy — https://help.openai.com/en/articles/8142208-chatgpt-android-app-faq
Help Centre (as summarised in search results): "To select text, long-press a response and use the Android selection menu… Available actions vary by message and context and may include Copy, Good response, Bad response, Read aloud, Share, and Try again."
Android Authority (https://www.androidauthority.com/chatgpt-custom-share-sheet-and-more-3654439/): "Currently, when you tap on the share icon below a ChatGPT response, it will open the system share sheet"; a teardown of v1.2026.090 shows an in-app sheet with "Copy link and Share". → Whether Share sends **plain text** or a **link** is UNVERIFIED. Copy puts text on the clipboard (third-party guide: seekingtech.com).
Export (https://help.openai.com/en/articles/8167885): a ZIP sent by email, with the link expiring in 24 hours. Not usable for a live relay.
## xAI Acceptable Use Policy (effective 14 Aug 2026) — https://x.ai/legal/acceptable-use-policy
- "using bots to access, reverse engineer, decompile…" (under "Detrimentally impacting the Service")
- "Scraping, harvesting or reselling any Input or Output"
- "Accessing the Services through unauthorized automated or non-human means, whether through a bot, script, or otherwise"
→ Unattended UI automation of Grok (reading or sending) remains **unapproved**. User-initiated share intents and Share/Copy by the owner are the only methods used. Grok consumer Terms of Service (https://x.ai/legal/terms-of-service) were not separately reviewed in this pass.
## Grok package
`ai.x.grok`. This is the Google Play URL id (https://play.google.com/store/apps/details?id=ai.x.grok).
