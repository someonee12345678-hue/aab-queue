package uk.aab.bridge.accessibility

import android.accessibilityservice.AccessibilityService
import android.content.Intent
import android.os.Bundle
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo

/**
 * Inactive-by-default draft service. Capture is owner-triggered using the Android
 * accessibility button. Staging only sets text in one uniquely exposed Termux
 * editable node; it never sends Enter or executes a command itself.
 */
class ChatTermuxAccessibilityService : AccessibilityService() {
    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event?.packageName?.toString() != TERMUX_PACKAGE) return
        val text = HandoffState.pendingText ?: return
        val root = rootInActiveWindow ?: return stopWith("Stopped: Termux input is not available.")
        if (root.packageName?.toString() != TERMUX_PACKAGE) return

        val editable = mutableListOf<AccessibilityNodeInfo>()
        collectEditable(root, editable, 0)
        if (editable.size != 1) {
            stopWith("Stopped: Termux did not expose exactly one editable input. Nothing staged.")
            return
        }

        val args = Bundle().apply {
            putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, text)
        }
        val staged = runCatching {
            editable.single().performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args)
        }.getOrDefault(false)
        editable.forEach { it.recycle() }
        HandoffState.pendingText = null
        HandoffState.updateStatus(
            if (staged) "Text staged in Termux. Review it; press Enter yourself."
            else "Stopped: Termux rejected text staging. Nothing executed."
        )
    }

    override fun onAccessibilityButtonClicked() {
        val root = rootInActiveWindow
        if (root == null || root.packageName?.toString() != CHATGPT_PACKAGE) {
            HandoffState.updateStatus("Stopped: open ChatGPT before pressing Capture.")
            return
        }
        val text = StringBuilder()
        collectVisibleText(root, text, 0)
        val captured = text.toString().trim().take(MAX_CAPTURE_CHARS)
        if (captured.isBlank()) {
            HandoffState.updateStatus("Nothing readable was exposed by ChatGPT's accessibility tree.")
            return
        }
        HandoffState.updateStatus("Captured visible text for review. Nothing has been staged.")
        startActivity(Intent(this, CapturePreviewActivity::class.java).apply {
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
            putExtra(CapturePreviewActivity.EXTRA_CAPTURE, captured)
        })
    }

    override fun onInterrupt() {
        HandoffState.pendingText = null
        HandoffState.updateStatus("Accessibility bridge interrupted; pending staging cleared.")
    }

    private fun collectVisibleText(node: AccessibilityNodeInfo, out: StringBuilder, depth: Int) {
        if (depth > MAX_DEPTH || out.length >= MAX_CAPTURE_CHARS) return
        if (node.isVisibleToUser) {
            val value = (node.text ?: node.contentDescription)?.toString()?.trim().orEmpty()
            if (value.isNotEmpty()) {
                if (out.isNotEmpty()) out.append('\n')
                out.append(value.take(MAX_CAPTURE_CHARS - out.length))
            }
        }
        for (index in 0 until node.childCount) {
            if (out.length >= MAX_CAPTURE_CHARS) break
            node.getChild(index)?.let { child ->
                collectVisibleText(child, out, depth + 1)
                child.recycle()
            }
        }
    }

    private fun collectEditable(node: AccessibilityNodeInfo, found: MutableList<AccessibilityNodeInfo>, depth: Int) {
        if (depth > MAX_DEPTH || found.size > 1) return
        if (node.isVisibleToUser && node.isEditable && node.isEnabled) found.add(AccessibilityNodeInfo.obtain(node))
        for (index in 0 until node.childCount) {
            if (found.size > 1) break
            node.getChild(index)?.let { child ->
                collectEditable(child, found, depth + 1)
                child.recycle()
            }
        }
    }

    private fun stopWith(message: String) {
        HandoffState.pendingText = null
        HandoffState.updateStatus(message)
    }

    companion object {
        private const val CHATGPT_PACKAGE = "com.openai.chatgpt"
        private const val TERMUX_PACKAGE = "com.termux"
        private const val MAX_CAPTURE_CHARS = 20_000
        private const val MAX_DEPTH = 32

        fun stageInTermux(context: android.content.Context, text: String): Boolean {
            if (text.isBlank() || text.length > MAX_CAPTURE_CHARS) {
                HandoffState.updateStatus("Stopped: empty or oversized text.")
                return false
            }
            val launch = context.packageManager.getLaunchIntentForPackage(TERMUX_PACKAGE)
            if (launch == null) {
                HandoffState.updateStatus("Stopped: Termux is not installed.")
                return false
            }
            HandoffState.pendingText = text
            HandoffState.updateStatus("Opening Termux to stage reviewed text; no command will be submitted.")
            return runCatching {
                launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                context.startActivity(launch)
                true
            }.getOrElse {
                HandoffState.pendingText = null
                HandoffState.updateStatus("Stopped: could not open Termux.")
                false
            }
        }
    }
}
