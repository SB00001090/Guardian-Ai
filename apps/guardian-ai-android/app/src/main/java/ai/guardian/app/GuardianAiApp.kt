package ai.guardian.app

import ai.guardian.app.network.HomeMonsterClient
import android.app.Application
import java.io.PrintWriter
import java.io.StringWriter

class GuardianAiApp : Application() {
    lateinit var homeClient: HomeMonsterClient

    override fun onCreate() {
        super.onCreate()
        installCrashLogger()
        homeClient = HomeMonsterClient(this)
    }

    private fun installCrashLogger() {
        val previous = Thread.getDefaultUncaughtExceptionHandler()
        Thread.setDefaultUncaughtExceptionHandler { thread, error ->
            try {
                val sw = StringWriter()
                error.printStackTrace(PrintWriter(sw))
                openFileOutput("last_crash.txt", MODE_PRIVATE).use {
                    it.write("${System.currentTimeMillis()}\n${sw}".toByteArray())
                }
            } catch (_: Exception) {
            }
            previous?.uncaughtException(thread, error)
        }
    }
}