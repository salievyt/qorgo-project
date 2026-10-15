package kg.qorgo.qorgo

import android.content.Intent
import android.service.quicksettings.TileService

/** System Quick Settings entry. The system controls whether it is visible on lock screen. */
class SosTileService : TileService() {
    override fun onClick() {
        super.onClick()
        val intent = Intent(this, MainActivity::class.java).apply {
            action = MainActivity.SOS_ACTION
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
        }
        startActivityAndCollapse(intent)
    }
}
