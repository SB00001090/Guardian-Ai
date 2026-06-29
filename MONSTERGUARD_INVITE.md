# MonsterGuard — 邀請 Bot 加入你的 Discord 伺服器

MonsterGuard 是 **Monster AI** 的 Discord 反詐騙 Bot，可 24/7 掃描伺服器文字頻道，自動偵測並攔截常見詐騙訊息。

---

## 一鍵邀請連結

**點擊下方連結，選擇你的伺服器並授權：**

👉 **[邀請 MonsterGuard 加入伺服器](https://discord.com/oauth2/authorize?client_id=1519991508172804096&permissions=1099511723008&scope=bot%20applications.commands)**

```
https://discord.com/oauth2/authorize?client_id=1519991508172804096&permissions=1099511723008&scope=bot%20applications.commands
```

> 你需要有該伺服器的 **管理伺服器** 或 **邀請成員** 權限。

---

## 加入後 3 步完成設定

| 步驟 | 操作 |
|------|------|
| 1 | 確認 Bot **在線**（成員列表顯示綠點） |
| 2 | 伺服器設定 → 角色 → 將 **MonsterGuard** 角色拖到高於一般成員 |
| 3 | 在任意文字頻道輸入 **`/guard setup`**，選擇保護強度 |

完成後即可開始攔截。可輸入 **`/guard features`** 查看完整攔截清單。

---

## 可攔截什麼？

| 類型 | 範例 |
|------|------|
| 假 Nitro / Giveaway | 免費 Nitro、Discord Gift、Steam 仿冒網域 |
| 假驗證 / 帳號安全 | 驗證帳號、假管理員招募、人機驗證 |
| Crypto / 投資詐騙 | 加倍投資、空投、助記詞、假 MrBeast 贈送 |
| 被盜帳號 DM 話術 | 「這是你嗎？」、「看看我找到的」 |
| 惡意下載 / 遊戲詐騙 | `.exe` / `.apk` 附件、免費 Robux / V-Bucks |
| 釣魚連結 | 仿冒 Discord 網址、黑名單惡意網域 |
| Raid / 大量洗版 | 重複訊息、新帳號集體 spam |

**攔截後動作：** 警告發送者 → 刪除訊息 → 通知管理員頻道（嚴格模式可禁言）

**目前不掃描：** 私信 (DM)、語音頻道

---

## 常用指令

| 指令 | 說明 |
|------|------|
| `/guard setup` | 首次設定（需管理伺服器） |
| `/guard features` | 查看可攔截類型 |
| `/guard status` | Bot 狀態與 24h 攔截統計 |
| `/guard education` | 發送防詐教育訊息 |
| `/chat` | 與本地 Monster AI 對話 |
| `/report-scam` | 回報可疑訊息 |

---

## 常見問題

| 問題 | 解法 |
|------|------|
| Bot 顯示離線 | 伺服器主機需啟動 Monster AI；聯絡管理員 |
| 無法刪除訊息 | 將 MonsterGuard 角色移到高於一般成員 |
| 看不到 `/guard` 指令 | 等待 1–2 分鐘讓指令同步，或重新邀請 Bot |
| 掃描不到訊息內容 | Bot 需已啟用 MESSAGE CONTENT INTENT（由營運方設定） |

---

## 技術說明（自行架設）

若你要在自己的機器上運行 MonsterGuard，請參閱：

- [monster_ai/modules/discord/README.md](monster_ai/modules/discord/README.md) — 完整安裝與設定
- [README.md](README.md) — Monster AI 主專案

---

**MonsterGuard · Monster AI** — 守護你的 Discord 社群