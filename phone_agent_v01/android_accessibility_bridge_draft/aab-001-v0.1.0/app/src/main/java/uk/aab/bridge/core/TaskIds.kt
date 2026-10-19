package uk.aab.bridge.core

import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone
import kotlin.random.Random

/** Task IDs: AAB-YYYYMMDD-HHMMSS-xxxx (UTC, 4 lower-case hex chars). */
object TaskIds {
    val PATTERN = Regex("""AAB-\d{8}-\d{6}-[0-9a-f]{4}""")

    fun generate(nowMillis: Long, random: Random = Random.Default, exists: (String) -> Boolean = { false }): String {
        val fmt = SimpleDateFormat("yyyyMMdd-HHmmss", Locale.UK).apply { timeZone = TimeZone.getTimeZone("UTC") }
        val stamp = fmt.format(Date(nowMillis))
        repeat(64) {
            val id = "AAB-$stamp-" + random.nextInt(0, 0x10000).toString(16).padStart(4, '0')
            if (!exists(id)) return id
        }
        error("Could not generate a unique task ID")
    }

    fun isValid(id: String) = PATTERN.matches(id)
    fun findIn(text: String): List<String> = PATTERN.findAll(text).map { it.value }.distinct().toList()
}
