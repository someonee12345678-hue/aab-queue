package uk.aab.bridge.ui

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import uk.aab.bridge.BridgeApp
import uk.aab.bridge.adapter.ClipboardAdapter
import uk.aab.bridge.adapter.ShareIntentAdapter
import uk.aab.bridge.core.*
import uk.aab.bridge.core.Target

class MainActivity : ComponentActivity() {
    private val coord get() = (application as BridgeApp).coordinator
    private val share by lazy { ShareIntentAdapter(this) }
    private val clip by lazy { ClipboardAdapter(this) }

    private var status by mutableStateOf("Ready")
    private var stopped by mutableStateOf(false)
    private var ops by mutableStateOf(listOf<Operation>())
    private var audit by mutableStateOf(listOf<AuditEntry>())
    private var pickText by mutableStateOf<String?>(null)
    private var pickIds by mutableStateOf(listOf<String>())
    private var showAudit by mutableStateOf(false)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleScope.launch {
            val app = application as BridgeApp
            if (!app.recovered) { app.recovered = true; val n = coord.recover(); if (n > 0) status = "Recovered: $n unfinished send(s) marked UNKNOWN – check and retry" }
            refresh(); handleIntent(intent)
        }
        setContent { MaterialTheme { Screen() } }
    }

    override fun onNewIntent(intent: Intent) { super.onNewIntent(intent); lifecycleScope.launch { handleIntent(intent) } }

    private suspend fun refresh() {
        stopped = coord.isStopped()
        ops = coord.activeOps()
        audit = auditAll()
    }
    private suspend fun auditAll(): List<AuditEntry> = runCatching { kotlinx.serialization.json.Json.decodeFromString<Map<String, kotlinx.serialization.json.JsonElement>>(coord.exportJson())["audit"]
        ?.let { kotlinx.serialization.json.Json.decodeFromJsonElement(kotlinx.serialization.builtins.ListSerializer(AuditEntry.serializer()), it) } ?: emptyList() }.getOrDefault(emptyList())

    private suspend fun handleIntent(i: Intent?) {
        if (i?.action != Intent.ACTION_SEND) return
        val text = i.getStringExtra(Intent.EXTRA_TEXT) ?: return
        i.action = null
        show(coord.receiveReply(text))
    }

    private suspend fun show(r: ReplyResult) {
        when (r) {
            is ReplyResult.Confirmed -> { status = "Reply saved to ${r.taskId} – CONFIRMED"; pickText = null }
            is ReplyResult.NeedsPick -> { pickText = r.text; pickIds = r.pendingTaskIds; status = "No task ID found – tap the task this reply belongs to" }
            is ReplyResult.Duplicate -> status = "Already saved (duplicate ignored)"
            is ReplyResult.Rejected -> status = "Not saved: ${r.reason}"
        }
        refresh()
    }

    private fun send(r: SendResult, useClipboard: Boolean = false) = lifecycleScope.launch {
        when (r) {
            is SendResult.Rejected -> status = r.reason
            is SendResult.Ready -> {
                val op = coord.dispatch(r.op.opId, if (useClipboard) clip else share)
                status = if (op.state == OpState.SENT) "Opened ${op.target.label}${if (useClipboard) " – long-press and Paste, then Send" else " – press Send there"}. Then share the reply back to AI Bridge."
                         else "${op.state}: ${op.note}"
            }
        }
        refresh()
    }

    @Composable private fun Screen() {
        var title by remember { mutableStateOf("") }
        var body by remember { mutableStateOf("") }
        Column(Modifier.fillMaxSize().padding(12.dp).verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = { lifecycleScope.launch { if (stopped) coord.resume() else coord.stop(); refresh() } },
                colors = ButtonDefaults.buttonColors(containerColor = if (stopped) Color(0xFF2E7D32) else Color(0xFFC62828)),
                modifier = Modifier.fillMaxWidth().height(56.dp)) { Text(if (stopped) "RELAY STOPPED – tap to resume" else "STOP RELAY") }
            Text(status, style = MaterialTheme.typography.bodyMedium)
            pickText?.let {
                Text("Which task is this reply for?", style = MaterialTheme.typography.titleSmall)
                if (pickIds.isEmpty()) Text("No pending tasks.")
                pickIds.forEach { id -> OutlinedButton(onClick = { lifecycleScope.launch { show(coord.receiveReply(it, id)) } }) { Text(id) } }
                TextButton(onClick = { pickText = null }) { Text("Cancel") }
            }
            Text("New task", style = MaterialTheme.typography.titleMedium)
            OutlinedTextField(title, { title = it }, label = { Text("Title (synthetic test data only)") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(body, { body = it }, label = { Text("Message") }, modifier = Modifier.fillMaxWidth().heightIn(min = 100.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Target.values().forEach { t ->
                    Button(enabled = !stopped && body.isNotBlank(), onClick = { lifecycleScope.launch {
                        val task = coord.createTask(title, body); send(coord.prepareSend(task.id, t, body)); body = ""; title = "" } }) { Text("Send to ${t.label}") }
                }
            }
            Text("Pending", style = MaterialTheme.typography.titleMedium)
            if (ops.isEmpty()) Text("Nothing pending.")
            ops.forEach { op ->
                Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(8.dp)) {
                    Text("${op.opId} → ${op.target.label}: ${op.state}")
                    if (op.note.isNotBlank()) Text(op.note, style = MaterialTheme.typography.bodySmall)
                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        if (StateMachine.canRetry(op)) TextButton(onClick = { lifecycleScope.launch { send(coord.retry(op.opId)) } }) { Text("Retry") }
                        TextButton(onClick = { lifecycleScope.launch { val r = coord.retry(op.opId); send(r, useClipboard = true) } }, enabled = StateMachine.canRetry(op)) { Text("Retry via clipboard") }
                    }
                } }
            }
            Text("Forward the latest reply", style = MaterialTheme.typography.titleMedium)
            recentTaskIds().forEach { id ->
                OutlinedButton(enabled = !stopped, onClick = { lifecycleScope.launch { send(coord.prepareForward(id)) } }) { Text("Forward reply of $id to other AI") }
            }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedButton(onClick = { showAudit = !showAudit }) { Text(if (showAudit) "Hide audit" else "Show audit") }
                OutlinedButton(onClick = { lifecycleScope.launch {
                    val json = coord.exportJson()
                    startActivity(Intent.createChooser(Intent(Intent.ACTION_SEND).apply { type = "application/json"; putExtra(Intent.EXTRA_TEXT, json); putExtra(Intent.EXTRA_SUBJECT, "AAB audit export") }, "Export log"))
                } }) { Text("Export log (JSON)") }
            }
            if (showAudit) audit.reversed().take(200).forEach { a -> Text("#${a.seqNo} ${java.util.Date(a.at)} ${a.taskId ?: "-"} ${a.event} ${a.detail}", style = MaterialTheme.typography.bodySmall) }
        }
    }

    private fun recentTaskIds(): List<String> = audit.filter { it.event == "REPLY_STORED" }.mapNotNull { it.taskId }.distinct().takeLast(5).reversed()
}
