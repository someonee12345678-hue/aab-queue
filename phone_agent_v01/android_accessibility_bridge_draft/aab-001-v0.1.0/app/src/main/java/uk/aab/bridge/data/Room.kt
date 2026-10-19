package uk.aab.bridge.data

import android.content.Context
import androidx.room.*
import uk.aab.bridge.core.*
import uk.aab.bridge.core.Target

@Entity(tableName = "tasks") data class TaskE(@PrimaryKey val id: String, val createdAt: Long, val title: String, val body: String)
@Entity(tableName = "ops") data class OpE(@PrimaryKey val opId: String, val taskId: String, val seq: Int, val target: String, val state: String,
    val contentHash: String, val composedText: String, val attempts: Int, val updatedAt: Long, val note: String)
@Entity(tableName = "replies", indices = [Index(value = ["contentHash"], unique = true)])
data class ReplyE(@PrimaryKey(autoGenerate = true) val rowId: Long = 0, val taskId: String, val seq: Int, val from: String?, val text: String, val contentHash: String, val receivedAt: Long)
@Entity(tableName = "audit") data class AuditE(@PrimaryKey(autoGenerate = true) val seqNo: Long = 0, val at: Long, val taskId: String?, val event: String, val detail: String)
@Entity(tableName = "flags") data class FlagE(@PrimaryKey val key: String, val value: String)

@Dao interface BridgeDao {
    @Insert(onConflict = OnConflictStrategy.ABORT) suspend fun insertTask(t: TaskE)
    @Query("SELECT * FROM tasks WHERE id = :id") suspend fun task(id: String): TaskE?
    @Query("SELECT * FROM tasks ORDER BY createdAt DESC") suspend fun tasks(): List<TaskE>
    @Upsert suspend fun upsertOp(o: OpE)
    @Query("SELECT * FROM ops WHERE opId = :id") suspend fun op(id: String): OpE?
    @Query("SELECT * FROM ops ORDER BY updatedAt DESC") suspend fun ops(): List<OpE>
    @Query("SELECT * FROM ops WHERE taskId = :id") suspend fun opsForTask(id: String): List<OpE>
    @Insert(onConflict = OnConflictStrategy.IGNORE) suspend fun insertReply(r: ReplyE)
    @Query("SELECT COUNT(*) FROM replies WHERE contentHash = :h") suspend fun replyHashCount(h: String): Int
    @Query("SELECT * FROM replies WHERE taskId = :id") suspend fun replies(id: String): List<ReplyE>
    // Append-only: there is deliberately no UPDATE or DELETE for audit.
    @Insert suspend fun appendAudit(a: AuditE)
    @Query("SELECT * FROM audit ORDER BY seqNo") suspend fun audit(): List<AuditE>
    @Query("SELECT value FROM flags WHERE `key` = :k") suspend fun flag(k: String): String?
    @Upsert suspend fun setFlag(f: FlagE)
}

@Database(entities = [TaskE::class, OpE::class, ReplyE::class, AuditE::class, FlagE::class], version = 1, exportSchema = false)
abstract class BridgeDb : RoomDatabase() {
    abstract fun dao(): BridgeDao
    companion object {
        fun open(ctx: Context): BridgeDb = Room.databaseBuilder(ctx, BridgeDb::class.java, "aab.db")
            .addCallback(object : Callback() {
                override fun onCreate(db: androidx.sqlite.db.SupportSQLiteDatabase) {
                    // Enforce append-only audit at the SQLite level too.
                    db.execSQL("CREATE TRIGGER audit_no_update BEFORE UPDATE ON audit BEGIN SELECT RAISE(ABORT,'audit is append-only'); END")
                    db.execSQL("CREATE TRIGGER audit_no_delete BEFORE DELETE ON audit BEGIN SELECT RAISE(ABORT,'audit is append-only'); END")
                }
            }).build()
    }
}

class RoomRepository(private val d: BridgeDao) : Repository {
    private fun TaskE.m() = Task(id, createdAt, title, body)
    private fun OpE.m() = Operation(opId, taskId, seq, Target.valueOf(target), OpState.valueOf(state), contentHash, composedText, attempts, updatedAt, note)
    private fun ReplyE.m() = Reply(taskId, seq, from?.let { Target.valueOf(it) }, text, contentHash, receivedAt)
    override suspend fun insertTask(t: Task) = d.insertTask(TaskE(t.id, t.createdAt, t.title, t.body))
    override suspend fun task(id: String) = d.task(id)?.m()
    override suspend fun taskExists(id: String) = d.task(id) != null
    override suspend fun tasks() = d.tasks().map { it.m() }
    override suspend fun upsertOp(o: Operation) = d.upsertOp(OpE(o.opId, o.taskId, o.seq, o.target.name, o.state.name, o.contentHash, o.composedText, o.attempts, o.updatedAt, o.note))
    override suspend fun op(opId: String) = d.op(opId)?.m()
    override suspend fun ops() = d.ops().map { it.m() }
    override suspend fun opsForTask(taskId: String) = d.opsForTask(taskId).map { it.m() }
    override suspend fun insertReply(r: Reply) = d.insertReply(ReplyE(taskId = r.taskId, seq = r.seq, from = r.from?.name, text = r.text, contentHash = r.contentHash, receivedAt = r.receivedAt))
    override suspend fun replyHashExists(hash: String) = d.replyHashCount(hash) > 0
    override suspend fun replies(taskId: String) = d.replies(taskId).map { it.m() }
    override suspend fun appendAudit(a: AuditEntry) = d.appendAudit(AuditE(at = a.at, taskId = a.taskId, event = a.event, detail = a.detail))
    override suspend fun audit() = d.audit().map { AuditEntry(it.seqNo, it.at, it.taskId, it.event, it.detail) }
    override suspend fun getFlag(key: String) = d.flag(key)
    override suspend fun setFlag(key: String, value: String) = d.setFlag(FlagE(key, value))
}
