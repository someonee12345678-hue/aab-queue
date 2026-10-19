package uk.aab.bridge

import android.app.Application
import uk.aab.bridge.core.Coordinator
import uk.aab.bridge.data.BridgeDb
import uk.aab.bridge.data.RoomRepository

class BridgeApp : Application() {
    lateinit var coordinator: Coordinator
    var recovered = false
    override fun onCreate() {
        super.onCreate()
        coordinator = Coordinator(RoomRepository(BridgeDb.open(this).dao()))
    }
}
