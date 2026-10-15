package kg.qorgo.qorgo

import android.app.StatusBarManager
import android.content.ComponentName
import android.content.Intent
import android.graphics.drawable.Icon
import android.os.Build
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    companion object {
        const val SOS_ACTION = "kg.qorgo.qorgo.SOS"
        private const val CHANNEL = "qorgo/sos"
    }

    private var channel: MethodChannel? = null

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        channel = MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL)
        channel?.setMethodCallHandler { call, result ->
            if (call.method == "requestAddTile") {
                requestSosTile(result)
            } else {
                result.notImplemented()
            }
        }
        notifySosIntent(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        notifySosIntent(intent)
    }

    private fun notifySosIntent(intent: Intent?) {
        if (intent?.action == SOS_ACTION) channel?.invokeMethod("openSos", null)
    }

    private fun requestSosTile(result: MethodChannel.Result) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) {
            result.success("manual")
            return
        }

        getSystemService(StatusBarManager::class.java).requestAddTileService(
            ComponentName(this, SosTileService::class.java),
            "QORGO SOS",
            Icon.createWithResource(this, R.drawable.ic_sos_tile),
            mainExecutor,
        ) { status ->
            result.success(
                if (status == StatusBarManager.TILE_ADD_REQUEST_RESULT_TILE_ADDED) {
                    "added"
                } else {
                    "manual"
                },
            )
        }
    }
}
