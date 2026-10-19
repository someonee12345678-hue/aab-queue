package uk.aab.bridge.core

import kotlinx.serialization.Serializable

/** The AI apps the bridge can relay between. Package names verified against Google Play listings (see docs/PROTOCOL.md). */
enum class Target(val packageName: String, val label: String) {
    CHATGPT("com.openai.chatgpt", "ChatGPT"),
    GROK("ai.x.grok", "Grok");
    fun other(): Target = if (this == CHATGPT) GROK else CHATGPT
}

/** Operation life cycle. SENT = handed to the target app; CONFIRMED = a reply carrying the ID came back. */
enum class OpState { INTENDED, SENT, CONFIRMED, FAILED, UNKNOWN }

@Serializable
data class Task(val id: String, val createdAt: Long, val title: String, val body: String)

@Serializable
data class Operation(
    val opId: String,
    val taskId: String,
    val seq: Int,
    val target: Target,
    val state: OpState,
    val contentHash: String,
    val composedText: String,
    val attempts: Int,
    val updatedAt: Long,
    val note: String = "",
)

@Serializable
data class Reply(val taskId: String, val seq: Int, val from: Target?, val text: String, val contentHash: String, val receivedAt: Long)

@Serializable
data class AuditEntry(val seqNo: Long = 0, val at: Long, val taskId: String?, val event: String, val detail: String)
