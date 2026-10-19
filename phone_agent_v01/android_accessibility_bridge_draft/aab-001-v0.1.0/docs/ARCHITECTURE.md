# Architecture
```
 UI (MainActivity, Compose) ──► Coordinator (pure Kotlin, no Android) ──► Repository port
        │                             │                                     ├─ RoomRepository (device)
        │ ACTION_SEND in (share target)│ TargetAdapter port                  └─ InMemoryRepository (tests)
        ▼                             ├─ ShareIntentAdapter (ACTION_SEND + setPackage)
   receiveReply()                     └─ ClipboardAdapter (fallback: copy + open app)
```
- **core/** has no Android dependencies, so it is unit-tested on the JVM. Model, TaskIds, Protocol, StateMachine, Repository and Coordinator.
- **TargetAdapter** is the swap point: `deliver(target, text): Dispatch`. A future official-API adapter only implements this interface, and the coordinator is unchanged. Each target can use a different adapter.
- **Write-ahead:** an operation is saved as INTENDED *before* it is handed to an adapter. Then it becomes SENT (handed over) or FAILED. A reply carrying the ID makes it CONFIRMED.
- **Recovery:** on the first activity start after a process launch, `recover()` turns every INTENDED op into UNKNOWN. These are **never resent automatically**, and the owner taps Retry. A late reply can still confirm an UNKNOWN op.
- **Bounded retries:** at most 3 attempts per operation (`StateMachine.MAX_ATTEMPTS`).
- **Duplicates:** a send is blocked if the same task+target+content hash already has a non-FAILED op. A reply is ignored if its hash was already stored (a unique index in Room).
- **STOP:** a persisted flag. While it is set, the coordinator refuses prepareSend, dispatch and retry, and this survives a restart.
- **Audit:** Room table with Insert only in the DAO, plus SQLite triggers that abort UPDATE/DELETE. It can be exported as JSON via the share sheet.
