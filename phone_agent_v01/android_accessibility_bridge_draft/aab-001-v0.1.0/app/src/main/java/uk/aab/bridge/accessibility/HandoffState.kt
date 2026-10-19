package uk.aab.bridge.accessibility

/** Process-local handoff state. Message text is not written to disk or logs. */
object HandoffState {
    @Volatile var pendingText: String? = null
    @Volatile var status: String = "Accessibility bridge is inactive until enabled in Android Settings."
    @Volatile var onStatusChanged: ((String) -> Unit)? = null

    fun updateStatus(value: String) {
        status = value
        onStatusChanged?.invoke(value)
    }
}
