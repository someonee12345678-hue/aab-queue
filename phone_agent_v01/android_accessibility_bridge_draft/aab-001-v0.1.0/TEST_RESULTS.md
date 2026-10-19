# Test results — 2026-10-15 (PT)

## JVM unit tests (logic only — NOT device tests; they use FakeAdapter and InMemoryRepository)
Command: `./gradlew testDebugUnitTest assembleDebug` → BUILD SUCCESSFUL
```
uk.aab.bridge.core.CoordinatorTests: 8 tests, 0 failures, 0 errors, 0 skipped
   PASS boundedRetries
   PASS recoveryMarksInterruptedSendsUnknownNotResent
   PASS stopHaltsRelayAndPersists
   PASS duplicateSendBlocked
   PASS duplicateReplyIgnored
   PASS auditIsAppendOnlyAndOrdered
   PASS replyWithoutIdNeedsOneTapPick
   PASS happyPathOneTapRelay
uk.aab.bridge.core.ProtocolTests: 6 tests, 0 failures, 0 errors, 0 skipped
   PASS corruptHeaderTolerated
   PASS hashIgnoresTrivialWhitespace
   PASS plainTextHasNoId
   PASS roundTrip
   PASS composeRejectsBadId
   PASS parsesReplyTagOnly
uk.aab.bridge.core.StateMachineTests: 2 tests, 0 failures, 0 errors, 0 skipped
   PASS illegalTransitions
   PASS legalTransitions
uk.aab.bridge.core.TaskIdTests: 5 tests, 0 failures, 0 errors, 0 skipped
   PASS formatMatches
   PASS avoidsExistingIds
   PASS rejectsBadIds
   PASS findsIdInText
   PASS manyIdsUnique
TOTAL 21 tests, 0 failed
```
First run: 1 real failure (ProtocolTests.roundTrip — the reply instruction leaked into the parsed body). Fixed in Protocol.parse and re-run: 21/21 pass.

## APK
app-debug.apk SHA-256 f13f2112931a4c309dcabc8b547d5398315654e0414f6b52dd48387b56432795. aapt2 permissions dump: only uk.aab.bridge.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION (added by androidx). **No INTERNET.**

## Emulator / device tests: NOT RUN
The emulator (AVD g34, Android 14) refused to start with 'x86_64 emulation currently requires hardware acceleration! This user doesn't have permissions to use KVM (/dev/kvm)'. /dev/kvm is root:rtkit 0660 and the box user is not in that group. So app launch, share resolution and Room on a device are **untested**. ChatGPT and Grok are not installed on any emulator image here in any case (no Google sign-in), so a real-interface test can only happen on the owner's phone.
