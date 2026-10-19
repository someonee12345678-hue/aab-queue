package uk.aab.bridge.core

/** Persistence port. RoomRepository (on device) and InMemoryRepository (tests) implement it. Audit is append-only. */
interface Repository {
    suspend fun insertTask(t: Task)
    suspend fun task(id: String): Task?
    suspend fun taskExists(id: String): Boolean
    suspend fun tasks(): List<Task>
    suspend fun upsertOp(o: Operation)
    suspend fun op(opId: String): Operation?
    suspend fun ops(): List<Operation>
    suspend fun opsForTask(taskId: String): List<Operation>
    suspend fun insertReply(r: Reply)
    suspend fun replyHashExists(hash: String): Boolean
    suspend fun replies(taskId: String): List<Reply>
    suspend fun appendAudit(a: AuditEntry)
    suspend fun audit(): List<AuditEntry>
    suspend fun getFlag(key: String): String?
    suspend fun setFlag(key: String, value: String)
}

class InMemoryRepository : Repository {
    private val tasks = linkedMapOf<String, Task>()
    private val ops = linkedMapOf<String, Operation>()
    private val replies = mutableListOf<Reply>()
    private val audit = mutableListOf<AuditEntry>()
    private val flags = mutableMapOf<String, String>()
    override suspend fun insertTask(t: Task) { tasks[t.id] = t }
    override suspend fun task(id: String) = tasks[id]
    override suspend fun taskExists(id: String) = id in tasks
    override suspend fun tasks() = tasks.values.toList()
    override suspend fun upsertOp(o: Operation) { ops[o.opId] = o }
    override suspend fun op(opId: String) = ops[opId]
    override suspend fun ops() = ops.values.toList()
    override suspend fun opsForTask(taskId: String) = ops.values.filter { it.taskId == taskId }
    override suspend fun insertReply(r: Reply) { replies += r }
    override suspend fun replyHashExists(hash: String) = replies.any { it.contentHash == hash }
    override suspend fun replies(taskId: String) = replies.filter { it.taskId == taskId }
    override suspend fun appendAudit(a: AuditEntry) { audit += a.copy(seqNo = audit.size + 1L) }
    override suspend fun audit() = audit.toList()
    override suspend fun getFlag(key: String) = flags[key]
    override suspend fun setFlag(key: String, value: String) { flags[key] = value }
}
