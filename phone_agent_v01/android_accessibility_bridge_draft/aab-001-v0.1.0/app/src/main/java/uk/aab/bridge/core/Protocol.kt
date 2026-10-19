package uk.aab.bridge.core

import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import java.security.MessageDigest

@Serializable
data class Header(val v: Int = 1, val task: String, val seq: Int, val from: String, val to: String, val hash: String)

data class Parsed(val header: Header?, val taskIds: List<String>, val replySeq: Int?, val body: String)

/** Structured message protocol. See docs/PROTOCOL.md. */
object Protocol {
    const val OPEN = "[AAB-HEADER]"
    const val CLOSE = "[/AAB-HEADER]"
    const val INSTRUCTION = "Please start your reply with this exact line: "
    private val json = Json { ignoreUnknownKeys = true; encodeDefaults = true }
    private val replyTag = Regex("""\[AAB-REPLY task=(AAB-\d{8}-\d{6}-[0-9a-f]{4}) seq=(\d+)]""")

    fun sha256(text: String): String =
        MessageDigest.getInstance("SHA-256").digest(normalise(text).toByteArray(Charsets.UTF_8)).joinToString("") { "%02x".format(it) }

    /** Whitespace normalisation so trivial copy/paste differences do not defeat duplicate detection. */
    fun normalise(text: String) = text.replace("\r\n", "\n").trim().replace(Regex("[ \t]+\n"), "\n")

    fun compose(taskId: String, seq: Int, from: String, to: Target, body: String): String {
        require(TaskIds.isValid(taskId)) { "Invalid task ID: $taskId" }
        val h = Header(task = taskId, seq = seq, from = from, to = to.name, hash = sha256(body))
        return buildString {
            append(OPEN).append('\n').append(json.encodeToString(h)).append('\n').append(CLOSE).append("\n\n")
            append(normalise(body)).append("\n\n")
            append(INSTRUCTION).append("[AAB-REPLY task=$taskId seq=$seq]")
        }
    }

    fun parse(text: String): Parsed {
        val t = text.replace("\r\n", "\n")
        var header: Header? = null
        var body = t
        val s = t.indexOf(OPEN); val e = t.indexOf(CLOSE)
        if (s >= 0 && e > s) {
            header = runCatching { json.decodeFromString<Header>(t.substring(s + OPEN.length, e).trim()) }.getOrNull()
            body = (t.substring(0, s) + t.substring(e + CLOSE.length))
        }
        val tag = replyTag.find(t)
        if (tag != null) body = body.replace(INSTRUCTION + tag.value, "").replace(tag.value, "")
        return Parsed(header, TaskIds.findIn(t), tag?.groupValues?.get(2)?.toIntOrNull(), normalise(body))
    }
}
