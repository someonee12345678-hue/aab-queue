# AAB-001 Android AI Bridge — Route 1 (one-tap relay)

An Android app that passes messages between the ChatGPT and Grok apps, using the phone's normal **Share** button. It gives every message a unique task ID, saves everything on the phone, prevents duplicates, recovers after a crash and keeps an append-only audit log.

It does **not** read either app's screen, use accessibility services, open a network server, store passwords, call paid APIs or use the internet (the app has no INTERNET permission).

You still press **Send** inside ChatGPT/Grok, and you **Share** each reply back to the bridge. That is the agreed Route 1: one tap per step, until a compliant automatic method exists.

Docs: PROJECT_STATE.md, docs/ARCHITECTURE.md, docs/PROTOCOL.md, TEST_RESULTS.md, KNOWN_LIMITATIONS.md, CHANGELOG.md, SETUP_ANDROID.md, MANUAL_STEPS.md, docs/POLICY_FINDINGS.md.

Build: `JAVA_HOME=/workspace/jdk17 ./gradlew testDebugUnitTest assembleDebug` → `app/build/outputs/apk/debug/app-debug.apk`.
