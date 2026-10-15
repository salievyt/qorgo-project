package kg.qorgo.qorgo

import android.content.Intent
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
}
