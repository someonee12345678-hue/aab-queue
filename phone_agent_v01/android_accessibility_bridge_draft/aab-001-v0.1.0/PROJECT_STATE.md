# Project state — 2026-10-15 (PT)
- Version 0.1.0 (versionCode 1), debug build. Package uk.aab.bridge, minSdk 26, targetSdk 34.
- APK: app/build/outputs/apk/debug/app-debug.apk, SHA-256 f13f2112931a4c309dcabc8b547d5398315654e0414f6b52dd48387b56432795 (8,422,498 bytes). A rebuild gives a different hash; the build directory is not committed.
- Gate B core: DONE (coordinator, Room, IDs, duplicates, recovery, audit, protocol, retries, STOP). 21/21 JVM unit tests pass.
- Device testing: NONE yet. The emulator could not start (no KVM permission). No real ChatGPT/Grok interface has been tested.
- Next: the owner sideloads the APK and runs the checks in MANUAL_STEPS.md, in order.
