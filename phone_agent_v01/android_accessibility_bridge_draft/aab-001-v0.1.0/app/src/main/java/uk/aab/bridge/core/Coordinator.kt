package uk.aab.bridge.core

import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

/** Result returned by an adapter. The coordinator never knows HOW a message is delivered. */
sealed class Dispatch {
    data object HandedOver : Dispatch()
    data class Unavailable(val reason: String) : Dispatch()
    data class Error(val reason: String) : Dispatch()
}

/** Swappable per-target delivery method (share intent today; an official API adapter could be added later). */
interface TargetAdapter {
    val name: String
    fun isAvailable(target: Target): Boolean
    fun deliver(target: Target, text: String): Dispatch
}

sealed class SendResult {
    data class Ready(val op: Operation) : SendResult()
    data class Rejected(val reason: String) : SendResult()
}

sealed class ReplyResult {
    data class Confirmed(val taskId: String, val opId: String?) : ReplyResult()
    data class NeedsPick(val text: String, val pendingTaskIds: List<String>) : ReplyResult()
    data class Duplicate(val taskId: String?) : ReplyResult()
    data class Rejected(val reason: String) : ReplyResult()
}

class Coordinator(private val repo: Repository, private val clock: () -> Long = System::currentTimeMillis) {
    companion object { const val STOP_FLAG = "relay_stopped" }

    private suspend fun log(taskId: String?, event: String, detail: String) =
        repo.appendAudit(AuditEntry(at = clock(), taskId = taskId, event = event, detail = detail))

    suspend fun isStopped() = repo.getFlag(STOP_FLAG) == "true"
    suspend fun stop() { repo.setFlag(STOP_FLAG, "true"); log(null, "STOP", "Relay halted by user") }
    suspend fun resume() { repo.setFlag(STOP_FLAG, "false"); log(null, "RESUME", "Relay resumed by user") }

    suspend fun createTask(title: String, body: String): Task {
        val id = TaskIds.generate(clock()) { false }.let { first ->
            if (!repo.taskExists(first)) first else {
                var c: String; do { c = TaskIds.generate(clock()) } while (repo.taskExists(c)); c
            }
        }
        val t = Task(id, clock(), title.ifBlank { "Task" }, Protocol.normalise(body))
        repo.insertTask(t)
        log(id, "TASK_CREATED", "title=${t.title}")
        return t
    }

    /** Step 1 of a send: record INTENDED before anything leaves the app (write-ahead). */
    suspend fun prepareSend(taskId: String, target: Target, body: String, from: String = "OWNER"): SendResult {
        if (isStopped()) return SendResult.Rejected("Relay is stopped").also { log(taskId, "SEND_BLOCKED", "stopped") }
        repo.task(taskId) ?: return SendResult.Rejected("Unknown task $taskId")
        val existing = repo.opsForTask(taskId)
        val seq = (existing.maxOfOrNull { it.seq } ?: 0) + 1
        val composed = Protocol.compose(taskId, seq, from, target, body)
        val hash = Protocol.sha256(body)
        val dup = existing.firstOrNull { it.target == target && it.contentHash == hash && it.state != OpState.FAILED }
        if (dup != null) {
            log(taskId, "DUPLICATE_BLOCKED", "op=${dup.opId} state=${dup.state}")
            return SendResult.Rejected("Already sent to ${target.label} (operation ${dup.opId}, ${dup.state})")
        }
        val op = Operation("$taskId#$seq", taskId, seq, target, OpState.INTENDED, hash, composed, 0, clock())
        repo.upsertOp(op)
        log(taskId, "INTENDED", "op=${op.opId} to=${target.name} hash=${hash.take(12)}")
        return SendResult.Ready(op)
    }

    /** Step 2: hand the composed text to an adapter, with bounded attempts. */
    suspend fun dispatch(opId: String, adapter: TargetAdapter): Operation {
        var op = repo.op(opId) ?: error("Unknown op $opId")
        if (isStopped()) return op
        if (op.state != OpState.INTENDED) error("Op $opId is ${op.state}, not INTENDED")
        if (op.attempts >= StateMachine.MAX_ATTEMPTS) return move(op, OpState.FAILED, "max attempts")
        op = op.copy(attempts = op.attempts + 1); repo.upsertOp(op)
        return when (val r = adapter.deliver(op.target, op.composedText)) {
            is Dispatch.HandedOver -> move(op, OpState.SENT, "via ${adapter.name}")
            is Dispatch.Unavailable -> move(op, OpState.FAILED, "${adapter.name}: ${r.reason}")
            is Dispatch.Error -> move(op, OpState.FAILED, "${adapter.name}: ${r.reason}")
        }
    }

    suspend fun retry(opId: String): SendResult {
        if (isStopped()) return SendResult.Rejected("Relay is stopped")
        val op = repo.op(opId) ?: return SendResult.Rejected("Unknown op")
        if (!StateMachine.canRetry(op)) return SendResult.Rejected("Retry not allowed (state ${op.state}, attempts ${op.attempts}/${StateMachine.MAX_ATTEMPTS})")
        return SendResult.Ready(move(op, OpState.INTENDED, "retry"))
    }

    private suspend fun move(op: Operation, to: OpState, note: String): Operation {
        check(StateMachine.canMove(op.state, to)) { "Illegal transition ${op.state} -> $to" }
        val n = op.copy(state = to, updatedAt = clock(), note = note)
        repo.upsertOp(n)
        log(op.taskId, to.name, "op=${op.opId} $note")
        return n
    }

    suspend fun activeOps() = repo.ops().filter { StateMachine.isPending(it.state) || StateMachine.canRetry(it) }
    suspend fun pendingOps() = repo.ops().filter { StateMachine.isPending(it.state) }

    /** A reply arrived via the share sheet. pickedTaskId is used when the text carries no ID. */
    suspend fun receiveReply(text: String, pickedTaskId: String? = null, from: Target? = null): ReplyResult {
        if (text.isBlank()) return ReplyResult.Rejected("Empty text")
        val parsed = Protocol.parse(text)
        val known = parsed.taskIds.filter { repo.taskExists(it) }
        val taskId = pickedTaskId ?: known.singleOrNull()
            ?: return ReplyResult.NeedsPick(text, pendingOps().map { it.taskId }.distinct())
        if (!repo.taskExists(taskId)) return ReplyResult.Rejected("Unknown task $taskId")
        val hash = Protocol.sha256(text)
        if (repo.replyHashExists(hash)) { log(taskId, "REPLY_DUPLICATE", "hash=${hash.take(12)}"); return ReplyResult.Duplicate(taskId) }
        val ops = repo.opsForTask(taskId)
        val op = (parsed.replySeq?.let { s -> ops.firstOrNull { it.seq == s } }
            ?: ops.filter { it.state == OpState.SENT || it.state == OpState.UNKNOWN }.maxByOrNull { it.seq })
        val src = from ?: op?.target
        repo.insertReply(Reply(taskId, op?.seq ?: 0, src, parsed.body, hash, clock()))
        log(taskId, "REPLY_STORED", "from=${src?.name} hash=${hash.take(12)} chars=${parsed.body.length}")
        if (op != null && StateMachine.canMove(op.state, OpState.CONFIRMED)) move(op, OpState.CONFIRMED, "reply received")
        return ReplyResult.Confirmed(taskId, op?.opId)
    }

    /** One-tap forward: latest reply of a task goes to the other AI as a new INTENDED op. */
    suspend fun prepareForward(taskId: String): SendResult {
        val last = repo.replies(taskId).maxByOrNull { it.receivedAt } ?: return SendResult.Rejected("No reply stored yet")
        val to = (last.from ?: Target.CHATGPT).other()
        return prepareSend(taskId, to, last.text, from = last.from?.name ?: "UNKNOWN")
    }

    /** After process death: an INTENDED op may or may not have reached the target app, so mark it UNKNOWN (never resend blindly). */
    suspend fun recover(): Int {
        var n = 0
        repo.ops().filter { it.state == OpState.INTENDED }.forEach { move(it, OpState.UNKNOWN, "recovered after restart"); n++ }
        log(null, "RECOVERY", "intended->unknown=$n")
        return n
    }

    suspend fun exportJson(): String = Json { prettyPrint = true }.encodeToString(
        mapOf("tasks" to Json.encodeToJsonElement(kotlinx.serialization.builtins.ListSerializer(Task.serializer()), repo.tasks()),
              "operations" to Json.encodeToJsonElement(kotlinx.serialization.builtins.ListSerializer(Operation.serializer()), repo.ops()),
              "audit" to Json.encodeToJsonElement(kotlinx.serialization.builtins.ListSerializer(AuditEntry.serializer()), repo.audit())))
}
