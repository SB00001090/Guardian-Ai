# MonsterGuard — Discord 反詐騙 Bot

MonsterGuard 是 Monster AI 內建的 Discord 伺服器保護 Bot，24/7 掃描文字頻道訊息，自動偵測並攔截常見詐騙。

## 可攔截的內容

| 類型 | 說明 | 範例 |
|------|------|------|
| 假 Nitro / Giveaway | 免費 Nitro、假禮物連結 | `discord-gift`、`free nitro`、`steamcommunlty` |
| 假驗證 / 帳號安全 | 騙取帳號或身分 | `verify your account`、假管理員招募表單 |
| Crypto / 投資詐騙 | 虛擬貨幣與假贈送 | 加倍投資、空投、助記詞、MrBeast 假活動 |
| 被盜帳號 DM 模式 | 好友帳號被盜後的話術 | 「這是你嗎？」、「看看我找到的」 |
| 惡意下載 / 遊戲詐騙 | 惡意附件與假虛寶 | `.exe` / `.apk` 附件、免費 Robux / V-Bucks |
| 釣魚連結 | 仿冒與黑名單網域 | Discord 仿冒網址、同形異義字、可疑 TLD |
| Raid / 大量洗版 | 機器人或集體 spam | 重複訊息、短時間大量發文、新帳號洗版 |

**行為風險訊號：** 新帳號發連結、緊迫感 + 免費承諾話術等。

**攔截後動作：** 警告 → 刪除訊息 → 通知管理員頻道 → 可選 mute / 隔離。

**目前不掃描：** 私信 (DM)、語音頻道、Bot 自身訊息。

> 完整說明定義於 [`guard/capabilities.py`](guard/capabilities.py)，Bot 內使用 `/guard features` 查看。

## 邀請 Bot（給伺服器管理員）

若使用官方營運的 MonsterGuard，直接點擊邀請連結：

👉 **[邀請 MonsterGuard 加入伺服器](https://discord.com/oauth2/authorize?client_id=1519991508172804096&permissions=1099511723008&scope=bot%20applications.commands)**

完整用戶說明見專案根目錄 **[MONSTERGUARD_INVITE.md](../../../MONSTERGUARD_INVITE.md)**。

加入後在頻道執行 `/guard setup` 即可啟用保護。

---

## 快速開始（自行架設）

### 1. 建立 Discord Application

1. 前往 [Discord Developer Portal](https://discord.com/developers/applications)
2. 建立 Application → Bot → 複製 **Token**
3. 啟用 **Privileged Gateway Intents → MESSAGE CONTENT INTENT**
4. OAuth2 → URL Generator：勾選 `bot` + `applications.commands`，權限建議 `Manage Messages`、`Read Message History`

### 2. 設定 Token（勿上傳 GitHub）

```bat
copy discord.token.local.example discord.token.local
notepad discord.token.local
```

將 Bot Token 貼在第一行，儲存。`discord.token.local` 已在 `.gitignore` 中排除。

### 3. 啟用模組

`config.yaml`（或從 `config.example.yaml` 複製）：

```yaml
modules:
  discord:
    enabled: true
    token_env: "MONSTER_DISCORD_TOKEN"
    guard:
      enabled: true
      mode: embedded
      protection_level: standard
      chat_bridge_enabled: true
```

### 4. 啟動

```bat
scripts\start-monsterguard.bat
```

或：

```bat
python scripts\launch_monsterguard.py
```

### 5. 邀請 Bot 加入伺服器（自行架設時）

自行架設請用 Developer Portal → OAuth2 → URL Generator 產生邀請連結。  
官方 Bot 邀請連結見 [MONSTERGUARD_INVITE.md](../../../MONSTERGUARD_INVITE.md)。

#### 加入後必做

1. **確認 Bot 在線** — 成員列表中 MonsterGuard 顯示綠點（需先啟動 `start-monsterguard.bat`）
2. **調整角色順序** — 伺服器設定 → 角色 → 將 MonsterGuard 角色拖到**高於**一般成員，低於伺服主／管理員
3. **完成設定** — 在任意文字頻道輸入：

```
/guard setup
```

4. 可選：輸入 `/guard features` 查看攔截清單，`/guard status` 確認運作中

#### 常見問題

| 問題 | 解法 |
|------|------|
| 邀請連結無效 | 確認 Application ID 正確、SCOPES 含 `bot` |
| Bot 離線 | 啟動 Monster AI + 檢查 `discord.token.local` |
| 無法刪除訊息 | Bot 角色需高於發訊者；需 **Manage Messages** 權限 |
| `/guard` 指令看不到 | 等 1–2 分鐘讓 Slash 同步；重啟 Bot |
| 掃描不到訊息 | Developer Portal → Bot → 開啟 **MESSAGE CONTENT INTENT** |

## Slash 指令

| 指令 | 說明 |
|------|------|
| `/guard setup` | 設定精靈（需管理伺服器） |
| `/guard features` | 查看可攔截的詐騙類型 |
| `/guard status` | Bot 與 24h 攔截統計 |
| `/guard config` | 查看目前伺服器設定 |
| `/guard education` | 發送防詐教育訊息 |
| `/chat` | 與本地 Monster AI 對話（Chat Bridge） |
| `/report-scam` | 回報可疑訊息 |

## 保護強度

| 等級 | 攔截門檻 | 動作 |
|------|----------|------|
| 輕度 `light` | 90 | 僅警告 |
| 標準 `standard` | 80 | 刪除 + 警告（推薦） |
| 嚴格 `strict` | 70 | 刪除 + mute 10 分鐘 |

## 專案結構

```
monster_ai/modules/discord/
├── bot.py                 # Discord 服務入口
├── guard/
│   ├── bot.py             # MonsterGuard Bot
│   ├── capabilities.py    # 攔截能力說明（單一來源）
│   ├── pipeline.py        # 規則 → URL → 行為 → AI
│   ├── scorer.py          # 關鍵字規則評分
│   ├── url_scanner.py     # 黑名單與仿冒網域
│   ├── behavior.py        # 洗版 / Raid 偵測
│   ├── ai_analyzer.py     # Monster AI 語意分析
│   ├── actions.py         # 刪除 / 警告 / 通知
│   ├── data/
│   │   ├── rules/v2026.06.yaml
│   │   └── blacklists/domains.txt
│   └── cogs/              # Slash 指令
└── standalone/__main__.py   # 獨立執行 MonsterGuard
```

## 測試

```bat
pytest tests/test_guard_scorer.py tests/test_discord_self_heal.py -q
```

## 授權

MIT — 與 Monster AI 主專案相同。