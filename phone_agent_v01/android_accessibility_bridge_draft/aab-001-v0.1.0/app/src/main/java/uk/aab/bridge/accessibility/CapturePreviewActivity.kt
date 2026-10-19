package uk.aab.bridge.accessibility

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

/** Owner review screen. It does not persist captured content and has no Enter action. */
class CapturePreviewActivity : ComponentActivity() {
    private var capture by mutableStateOf("")
    private var status by mutableStateOf(HandoffState.status)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        capture = intent.getStringExtra(EXTRA_CAPTURE).orEmpty()
        HandoffState.onStatusChanged = { status = it }
        setContent {
            MaterialTheme {
                Column(
                    Modifier.fillMaxSize().padding(16.dp).verticalScroll(rememberScrollState()),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text("Review captured ChatGPT screen text", style = MaterialTheme.typography.titleLarge)
                    Text("The capture can include interface labels or incomplete text. Edit it before staging.")
                    OutlinedTextField(
                        value = capture,
                        onValueChange = { capture = it },
                        modifier = Modifier.fillMaxWidth(),
                        minLines = 8,
                        label = { Text("Captured text") }
                    )
                    Text(status)
                    Button(
                        enabled = capture.isNotBlank(),
                        onClick = { ChatTermuxAccessibilityService.stageInTermux(this@CapturePreviewActivity, capture) }
                    ) { Text("Stage in Termux (will not press Enter)") }
                    Button(onClick = {
                        HandoffState.pendingText = null
                        capture = ""
                        status = "Canceled. Captured text cleared."
                    }) { Text("Cancel and clear") }
                }
            }
        }
    }

    override fun onDestroy() {
        HandoffState.onStatusChanged = null
        super.onDestroy()
    }

    companion object {
        const val EXTRA_CAPTURE = "uk.aab.bridge.accessibility.CAPTURE"
    }
}
