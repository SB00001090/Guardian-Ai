package ai.guardian.app.ui.screens

import ai.guardian.app.ui.theme.NeonCyan
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun PrivacyScreen() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
    ) {
        Text("透明資安告知", style = MaterialTheme.typography.headlineSmall, color = NeonCyan)
        Spacer(Modifier.height(12.dp))
        Text(
            """
            您的資安數據（偏好設定、同步 bundle、日誌）僅儲存在本機加密空間，並可透過您授權的安全通道同步至您自己的 Monster AI 實例。

            · 不會上傳至第三方 Monster AI 查詢或訓練數據
            · 開發者 Suckbob 僅在獲得您明確同意後，透過 Monster AI 協助處理您主動提交的問題，用於優化本機模型與服務規則
            · 無第三方雲端存儲 · 無廣告追蹤或轉販
            · 無來電過濾、無位置追蹤、無 SIM 監控

            Developed by Suckbob | Guardian Ai
            """.trimIndent(),
            style = MaterialTheme.typography.bodyMedium,
        )
    }
}