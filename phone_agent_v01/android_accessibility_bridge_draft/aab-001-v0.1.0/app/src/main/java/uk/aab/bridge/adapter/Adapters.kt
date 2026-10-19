package uk.aab.bridge.adapter

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import uk.aab.bridge.core.Dispatch
import uk.aab.bridge.core.Target
import uk.aab.bridge.core.TargetAdapter

/** Hands text to the target app with a standard ACTION_SEND intent. The owner still presses Send inside that app. */
class ShareIntentAdapter(private val ctx: Context) : TargetAdapter {
    override val name = "ShareIntent"
    fun intentFor(target: Target, text: String) = Intent(Intent.ACTION_SEND).apply {
        type = "text/plain"; putExtra(Intent.EXTRA_TEXT, text); setPackage(target.packageName)
        addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    }
    override fun isAvailable(target: Target): Boolean =
        ctx.packageManager.queryIntentActivities(intentFor(target, "x"), PackageManager.MATCH_DEFAULT_ONLY).isNotEmpty()
    override fun deliver(target: Target, text: String): Dispatch {
        if (!isAvailable(target)) return Dispatch.Unavailable("${target.label} (${target.packageName}) not installed or does not accept shared text")
        return try { ctx.startActivity(intentFor(target, text)); Dispatch.HandedOver }
        catch (e: Exception) { Dispatch.Error(e.javaClass.simpleName) }
    }
}

/** Fallback: copies the composed text and opens the target app; the owner long-presses and pastes. */
class ClipboardAdapter(private val ctx: Context) : TargetAdapter {
    override val name = "Clipboard"
    override fun isAvailable(target: Target) = true
    override fun deliver(target: Target, text: String): Dispatch = try {
        (ctx.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager).setPrimaryClip(ClipData.newPlainText("AAB message", text))
        ctx.packageManager.getLaunchIntentForPackage(target.packageName)?.let { ctx.startActivity(it.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)) }
        Dispatch.HandedOver
    } catch (e: Exception) { Dispatch.Error(e.javaClass.simpleName) }
}
