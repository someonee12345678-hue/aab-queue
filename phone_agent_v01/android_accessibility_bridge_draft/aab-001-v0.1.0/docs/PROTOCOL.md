# Message protocol v1
Task ID: `AAB-YYYYMMDD-HHMMSS-xxxx` (UTC time, 4 random lower-case hex digits; regenerated if it already exists).
Operation ID: `<taskId>#<seq>`.

Composed text sent to an AI:
```
[AAB-HEADER]
{"v":1,"task":"AAB-20261015-220000-ab12","seq":1,"from":"OWNER","to":"CHATGPT","hash":"<sha256 of body>"}
[/AAB-HEADER]

<message body>

Please start your reply with this exact line: [AAB-REPLY task=AAB-20261015-220000-ab12 seq=1]
```
Parsing a returned reply (`Protocol.parse`): it takes the header if one is present (bad JSON is tolerated and ignored), finds every task ID anywhere in the text, reads `seq` from the AAB-REPLY tag, and strips the header, tag and instruction from the body.
Matching: if exactly one known task ID is found, the reply is attached to it. If none is found, the owner taps the pending task. When forwarding, `from` is the AI that produced the reply.
Hashes are SHA-256 of the whitespace-normalised text (CRLF→LF, trailing spaces removed, trimmed).
Target packages: ChatGPT `com.openai.chatgpt`; Grok `ai.x.grok`. Grok is verified against the Google Play URL https://play.google.com/store/apps/details?id=ai.x.grok, which a web search found on 2026-10-15. Whether either app accepts ACTION_SEND text/plain is **unverified on a device**.
