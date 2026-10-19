package uk.aab.bridge.core

object StateMachine {
    const val MAX_ATTEMPTS = 3
    private val allowed = mapOf(
        OpState.INTENDED to setOf(OpState.SENT, OpState.FAILED, OpState.UNKNOWN),
        OpState.SENT to setOf(OpState.CONFIRMED, OpState.FAILED, OpState.UNKNOWN),
        OpState.UNKNOWN to setOf(OpState.CONFIRMED, OpState.FAILED, OpState.INTENDED),
        OpState.FAILED to setOf(OpState.INTENDED),
        OpState.CONFIRMED to emptySet(),
    )
    fun canMove(from: OpState, to: OpState) = to in (allowed[from] ?: emptySet())
    fun canRetry(op: Operation) = (op.state == OpState.FAILED || op.state == OpState.UNKNOWN) && op.attempts < MAX_ATTEMPTS
    fun isPending(s: OpState) = s == OpState.INTENDED || s == OpState.SENT || s == OpState.UNKNOWN
}
