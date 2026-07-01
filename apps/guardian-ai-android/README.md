# Guardian Ai (Android)

**Developed by Suckbob | Guardian Ai**

Monster AI 行動客戶端 · **Cloudflare Tunnel HTTPS** 連線家中 Monster AI · Guardian 雲端 E2E 同步。

## 專案結構

```
apps/guardian-ai-android/
├── app/src/main/java/ai/guardian/app/
│   ├── GuardianAiApp.kt             # Application 入口
│   ├── network/
│   │   ├── ConnectionManager.kt     # Tunnel 連線、重試、離線快取
│   │   ├── TunnelConnection.kt      # URL 驗證（僅 HTTPS trycloudflare）
│   │   ├── HomeMonsterClient.kt     # OkHttp API 客戶端
│   │   ├── MonsterApiService.kt     # Retrofit 介面
│   │   └── RetryInterceptor.kt      # 指數退避重試
│   ├── guardian/                    # E2E 雲端同步（與 Web /guardian-sync 互通）
│   ├── sync/
│   │   ├── SyncScheduler.kt         # WorkManager 排程
│   │   └── ConnectionHealthWorker.kt # 30min 健康探測
│   ├── security/                    # 憑證與 Training Vault 金鑰
│   ├── billing/                     # 7 日試用 + 一次性付費
│   └── ui/screens/
│       ├── HomeScreen.kt            # Tunnel URL + 連線狀態
│       ├── GuardianSyncScreen.kt    # 雲端同步
│       ├── PaywallScreen.kt
│       └── PrivacyScreen.kt
├── docs/TUNNEL_SETUP.md
├── PRIVACY_POLICY.md
└── build.gradle.kts
```

## 快速開始

### 電腦

```bat
python main.py
run-tunnel.bat
```

### 手機

1. 安裝 APK
2. 貼上 `https://xxx.trycloudflare.com`
3. 測試連線 → 開啟 Guardian 雲端同步

詳見 [docs/TUNNEL_SETUP.md](docs/TUNNEL_SETUP.md)

## 連線原則

| 允許 | 禁止 |
|------|------|
| `https://*.trycloudflare.com` | Tailscale / `100.x.x.x` |
| Named Tunnel 自訂網域 | 手動輸入 LAN IP |

## 建置 APK

```bat
cd apps\guardian-ai-android
gradlew.bat assembleRelease
```

## 與 Call Guard 的差異

本專案已移除 Call Guard 專屬功能：

- 來電過濾 / Call Screening
- 威脅庫同步
- 防盜模式 / 位置追蹤
- VPN 鎖網

保留：Tunnel 連線、Guardian E2E 同步、付費試用、資安告知。