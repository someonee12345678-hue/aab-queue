# Remaining manual steps and untested device checks
## Taps per relay round (Route 1)
1. Type the message in AI Bridge → tap **Send to ChatGPT** (or Grok). *(1 tap)*
2. In ChatGPT/Grok the text is pre-filled → tap **Send**. *(1 tap)*
3. When the answer is done → tap **Share** under it → choose **AI Bridge**. *(2–3 taps)* If there's no ID in it → tap the task. *(+1)*
4. In AI Bridge → tap **Forward reply of … to other AI**. *(1 tap)* → repeat from step 2.

## Device checks still needed (owner's phone; record the results in TEST_RESULTS.md). Each must be tested separately.
- [ ] D1 App installs and opens; STOP button visible; tapping it shows "RELAY STOPPED".
- [ ] D2 "Send to ChatGPT" opens ChatGPT with the text pre-filled (or the app shows FAILED → try "Retry via clipboard" and paste).
- [ ] D3 "Send to Grok" does the same for Grok.
- [ ] D4 In ChatGPT, Share on a response: does **AI Bridge** appear, and does it receive the **text** or only a **link**? Also try long-press → Copy.
- [ ] D5 Same for Grok's share/copy.
- [ ] D6 Did the AI repeat the [AAB-REPLY …] line? Did the task become CONFIRMED?
- [ ] D7 Sharing the same reply twice shows "Already saved".
- [ ] D8 Force-stop AI Bridge mid-task, reopen, and check that the recovery message appears with no automatic resend.
- [ ] D9 Export log (JSON) opens the share sheet.
- [ ] D10 Full round trip ChatGPT → Grok → ChatGPT with synthetic text. Only claim "relay works" after this passes.
## Not done (by design or pending decision)
- No automatic reading or sending in either app (OpenAI terms; xAI AUP).
- A "paste from clipboard" button for link-only shares (add this if D4 shows the share is link-only).
