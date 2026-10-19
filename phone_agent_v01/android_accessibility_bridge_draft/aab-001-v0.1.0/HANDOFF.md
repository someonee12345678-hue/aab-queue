# AAB-001 v0.1.0 source handoff

- Repository path (on builder's computer): /workspace/aab-001 (local git, no remote)
- Branch: master
- Source commit: 60e0787 (working tree clean when archived; archive made with `git archive 60e0787`, no rebuild)
- Build command: `JAVA_HOME=<path to JDK 17> ./gradlew testDebugUnitTest assembleDebug` (needs Android SDK; set sdk.dir in local.properties or ANDROID_HOME)
- APK SHA-256: f13f2112931a4c309dcabc8b547d5398315654e0414f6b52dd48387b56432795

## Omitted files and why
- local.properties: machine-specific Android SDK path, git-ignored; recreate locally.
- build/, app/build/, .gradle/: generated build output and caches.
- APK: delivered separately; hash above.
- gradlew.bat: never created (builds were on Linux); Windows builders can run `gradle wrapper` to generate it.
- res/ folder: none exists; the app uses no resource files (UI is Compose, label set in manifest).
- No signing keystore: debug build uses the standard Android debug key, not included.

## Secrets
None. A keyword scan for password/api key/token/secret matched only README/SETUP text stating the app stores no passwords.

## Test status
21 JUnit logic tests passed at build time (not rerun for this handoff; source unchanged). No real-device or emulator test has been run. See TEST_RESULTS.md and MANUAL_STEPS.md.

## Note
The archive SHA-256 can't be inside itself; it is reported alongside the download.
