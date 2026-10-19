package uk.aab.bridge.core

import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Test
import kotlin.random.Random

/** JVM unit tests. These exercise logic only; they are NOT device tests and use a fake adapter. */
class FakeAdapter(var result: Dispatch = Dispatch.HandedOver) : TargetAdapter {
    override val name = "FakeForUnitTest"
    val delivered = mutableListOf<String>()
    override fun isAvailable(target: Target) = true
    override fun deliver(target: Target, text: String): Dispatch { delivered += text; return result }
}

class TaskIdTests {
    @Test fun formatMatches() {
        val id = TaskIds.generate(1_760_000_000_000L, Random(1))
        assertTrue(id, TaskIds.isValid(id)); assertTrue(id.startsWith("AAB-20251009-"))
    }
    @Test fun avoidsExistingIds() {
        val first = TaskIds.generate(0L, Random(7))
        val second = TaskIds.generate(0L, Random(7)) { it == first }
        assertNotEquals(first, second)
    }
    @Test fun manyIdsUnique() {
        val seen = mutableSetOf<String>()
        repeat(2000) { seen += TaskIds.generate(0L) { it in seen } }
        assertEquals(2000, seen.size)
    }
    @Test fun findsIdInText() { assertEquals(listOf("AAB-20261015-120000-ab12"), TaskIds.findIn("x AAB-20261015-120000-ab12 y AAB-20261015-120000-ab12")) }
    @Test fun rejectsBadIds() { assertFalse(TaskIds.isValid("AAB-2026-1-zz")) }
}

class ProtocolTests {
    private val id = "AAB-20261015-120000-ab12"
    @Test fun roundTrip() {
        val txt = Protocol.compose(id, 2, "OWNER", Target.GROK, "Synthetic test: say hello")
        val p = Protocol.parse(txt)
        assertEquals(id, p.header!!.task); assertEquals(2, p.header!!.seq); assertEquals("GROK", p.header!!.to)
        assertEquals(Protocol.sha256("Synthetic test: say hello"), p.header!!.hash)
        assertEquals(2, p.replySeq)
        assertEquals("Synthetic test: say hello", p.body)
    }
    @Test fun parsesReplyTagOnly() {
        val p = Protocol.parse("[AAB-REPLY task=$id seq=1]\nHello from the synthetic test.")
        assertNull(p.header); assertEquals(listOf(id), p.taskIds); assertEquals(1, p.replySeq)
        assertEquals("Hello from the synthetic test.", p.body)
    }
    @Test fun plainTextHasNoId() { assertTrue(Protocol.parse("just a reply").taskIds.isEmpty()) }
    @Test fun corruptHeaderTolerated() { assertNull(Protocol.parse("[AAB-HEADER]\n{not json\n[/AAB-HEADER]\nhi").header) }
    @Test fun hashIgnoresTrivialWhitespace() { assertEquals(Protocol.sha256("a\r\nb  \n"), Protocol.sha256("a\nb")) }
    @Test(expected = IllegalArgumentException::class) fun composeRejectsBadId() { Protocol.compose("bad", 1, "X", Target.GROK, "b") }
}

class StateMachineTests {
    @Test fun legalTransitions() {
        assertTrue(StateMachine.canMove(OpState.INTENDED, OpState.SENT))
        assertTrue(StateMachine.canMove(OpState.SENT, OpState.CONFIRMED))
        assertTrue(StateMachine.canMove(OpState.SENT, OpState.UNKNOWN))
        assertTrue(StateMachine.canMove(OpState.FAILED, OpState.INTENDED))
    }
    @Test fun illegalTransitions() {
        assertFalse(StateMachine.canMove(OpState.CONFIRMED, OpState.SENT))
        assertFalse(StateMachine.canMove(OpState.INTENDED, OpState.CONFIRMED))
        assertFalse(StateMachine.canMove(OpState.FAILED, OpState.CONFIRMED))
    }
}

class CoordinatorTests {
    private fun setup(): Pair<Coordinator, InMemoryRepository> { val r = InMemoryRepository(); var t = 1_000L; return Coordinator(r) { t++ } to r }

    @Test fun happyPathOneTapRelay() = runTest {
        val (c, r) = setup(); val a = FakeAdapter()
        val task = c.createTask("t", "Synthetic: what is 2+2?")
        val op = (c.prepareSend(task.id, Target.CHATGPT, task.body) as SendResult.Ready).op
        assertEquals(OpState.INTENDED, r.op(op.opId)!!.state)
        assertEquals(OpState.SENT, c.dispatch(op.opId, a).state)
        val res = c.receiveReply("[AAB-REPLY task=${task.id} seq=1]\n4")
        assertTrue(res is ReplyResult.Confirmed)
        assertEquals(OpState.CONFIRMED, r.op(op.opId)!!.state)
        val fwd = c.prepareForward(task.id) as SendResult.Ready
        assertEquals(Target.GROK, fwd.op.target); assertEquals(2, fwd.op.seq)
        assertTrue(fwd.op.composedText.contains("\"from\":\"CHATGPT\""))
    }
    @Test fun duplicateSendBlocked() = runTest {
        val (c, _) = setup(); val task = c.createTask("t", "same")
        val op = (c.prepareSend(task.id, Target.GROK, "same") as SendResult.Ready).op
        c.dispatch(op.opId, FakeAdapter())
        assertTrue(c.prepareSend(task.id, Target.GROK, "same ") is SendResult.Rejected)
    }
    @Test fun duplicateReplyIgnored() = runTest {
        val (c, r) = setup(); val task = c.createTask("t", "x")
        c.dispatch((c.prepareSend(task.id, Target.GROK, "x") as SendResult.Ready).op.opId, FakeAdapter())
        val txt = "reply ${task.id}"
        assertTrue(c.receiveReply(txt) is ReplyResult.Confirmed)
        assertTrue(c.receiveReply(txt) is ReplyResult.Duplicate)
        assertEquals(1, r.replies(task.id).size)
    }
    @Test fun replyWithoutIdNeedsOneTapPick() = runTest {
        val (c, r) = setup(); val task = c.createTask("t", "x")
        val op = (c.prepareSend(task.id, Target.GROK, "x") as SendResult.Ready).op; c.dispatch(op.opId, FakeAdapter())
        val res = c.receiveReply("plain reply")
        assertEquals(listOf(task.id), (res as ReplyResult.NeedsPick).pendingTaskIds)
        assertTrue(c.receiveReply("plain reply", task.id) is ReplyResult.Confirmed)
        assertEquals(OpState.CONFIRMED, r.op(op.opId)!!.state)
    }
    @Test fun stopHaltsRelayAndPersists() = runTest {
        val (c, r) = setup(); val task = c.createTask("t", "x"); c.stop()
        assertTrue(c.prepareSend(task.id, Target.GROK, "x") is SendResult.Rejected)
        assertTrue(Coordinator(r).isStopped())   // survives a new coordinator (process restart)
        c.resume(); assertTrue(c.prepareSend(task.id, Target.GROK, "x") is SendResult.Ready)
    }
    @Test fun boundedRetries() = runTest {
        val (c, r) = setup(); val a = FakeAdapter(Dispatch.Error("synthetic"))
        val task = c.createTask("t", "x")
        var op = (c.prepareSend(task.id, Target.GROK, "x") as SendResult.Ready).op
        repeat(StateMachine.MAX_ATTEMPTS) { i ->
            op = c.dispatch(op.opId, a); assertEquals(OpState.FAILED, op.state)
            val rr = c.retry(op.opId)
            if (i < StateMachine.MAX_ATTEMPTS - 1) { assertTrue(rr is SendResult.Ready); op = (rr as SendResult.Ready).op } else assertTrue(rr is SendResult.Rejected)
        }
        assertEquals(StateMachine.MAX_ATTEMPTS, a.delivered.size)
        assertEquals(StateMachine.MAX_ATTEMPTS, r.op(op.opId)!!.attempts)
    }
    @Test fun recoveryMarksInterruptedSendsUnknownNotResent() = runTest {
        val (c, r) = setup(); val task = c.createTask("t", "x")
        val op = (c.prepareSend(task.id, Target.CHATGPT, "x") as SendResult.Ready).op
        // simulate process death before dispatch: build a fresh coordinator on the same store
        val c2 = Coordinator(r); val a = FakeAdapter()
        assertEquals(1, c2.recover())
        assertEquals(OpState.UNKNOWN, r.op(op.opId)!!.state); assertTrue(a.delivered.isEmpty())
        // a reply for it can still confirm
        assertTrue(c2.receiveReply("ok ${task.id}") is ReplyResult.Confirmed)
        assertEquals(OpState.CONFIRMED, r.op(op.opId)!!.state)
    }
    @Test fun auditIsAppendOnlyAndOrdered() = runTest {
        val (c, r) = setup(); val task = c.createTask("t", "x")
        c.dispatch((c.prepareSend(task.id, Target.GROK, "x") as SendResult.Ready).op.opId, FakeAdapter())
        val a = r.audit(); assertEquals(listOf("TASK_CREATED", "INTENDED", "SENT"), a.map { it.event })
        assertEquals((1L..a.size).toList(), a.map { it.seqNo })
        assertTrue(c.exportJson().contains("\"audit\""))
    }
}
