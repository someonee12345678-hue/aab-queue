# Known limitations
1. No device test yet. The emulator was blocked by KVM permissions, so launch, share sheet, Room on device and the UI are unverified.
2. Whether ChatGPT (`com.openai.chatgpt`) and Grok (`ai.x.grok`) accept ACTION_SEND text/plain with `setPackage` is **unverified**. If not, the app reports FAILED and the owner uses "Retry via clipboard".
3. A shared intent only *pre-fills* the text. The owner must still press Send in the AI app. SENT means "handed to the app", not "submitted to the AI".
4. Whether ChatGPT's Share button shares the response **text** or only a **link** is unverified. An Android Authority teardown (v1.2026.090) describes "Copy link" and "Share" options. If only a link is shared, the reply must be moved with Copy → open bridge → paste (that paste path is not built yet; see MANUAL_STEPS).
5. The AI may not repeat the `[AAB-REPLY …]` line. In that case the owner taps the task (one extra tap).
6. Grok unattended automation is **not implemented**. xAI's AUP forbids "Accessing the Services through unauthorized automated or non-human means, whether through a bot, script, or otherwise".
7. Debug-signed APK; Play Protect may warn when sideloading.
8. Audit view shows the latest 200 entries. Export carries everything (tasks, operations, audit; reply texts are stored but not exported in v0.1).
9. The duplicate check for sends allows a deliberate resend only after FAILED/UNKNOWN via Retry.
