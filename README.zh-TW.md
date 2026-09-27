# mtouyang-skills

mtouyang 的 Claude Code skill，打包成一個 plugin，放在 Claude Code 的 plugin marketplace 上。

[English](README.md)

## Skill 一覽

| Skill | 做什麼 | 叫用 |
|---|---|---|
| [docs-for-humans](#docs-for-humans) | 把手冊、SOP、runbook 改寫成人真的照得下去的形狀。支援英文與繁中。 | `/mtouyang-skills:docs-for-humans` |

## 安裝

需要 [Claude Code](https://code.claude.com)。skill 用 `${CLAUDE_SKILL_DIR}` 找自己的腳本，所以不支援 claude.ai 與 API。

### 裝成 plugin（建議）

在 Claude Code 對話裡：

```text
/plugin marketplace add mtouyang/claude-skills
/plugin install mtouyang-skills@mtouyang
```

這樣會裝上 plugin 裡的每一支 skill。同一個 plugin 的 skill 只能一起啟用或停用。

### 只要一支：直接複製資料夾

```bash
git clone https://github.com/mtouyang/claude-skills.git
cp -r claude-skills/skills/docs-for-humans ~/.claude/skills/
```

### 更新

第三方 marketplace 預設不自動更新。要拿新版：

```text
/plugin marketplace update mtouyang
```

再到 `/plugin` 的 **Installed** 分頁更新，或在 shell 執行 `claude plugin update mtouyang-skills@mtouyang`。也可以在 **Marketplaces** 分頁替這個 marketplace 打開自動更新。

## docs-for-humans

把手冊、SOP、runbook 改寫成人真的照得下去的形狀。

技術文件難讀，通常不是因為寫得不夠詳細，而是因為「你現在要做什麼」和「為什麼是這樣」黏在同一句裡。這支 skill 把兩者拆開，而不是把任何一邊刪掉：

1. 開頭給分流表：你的來意 → 去哪一節 → 要多久。
2. 每一段先給完整指令串：一段可以整段複製的 code block，註解寫要看到什麼。
3. 粗體限額：只留原文的四分之一以下，每一個都要答得出「不照做會壞掉什麼」。
4. 設計理由集中到附錄：不影響讀者下一個動作的理由，搬到編號附錄（C1、C2…），原地留一行回指。
5. 破折號插入句拆成獨立句子。
6. 標點一律全形（只限中文），用腳本修、用腳本驗。

每次改寫的最後都附一段「這份動了什麼」，裡面的數字由腳本算，不是估的。

### 看範例

同一份虛構的手冊，改寫前與改寫後：

| | 改寫前 | 改寫後 |
|---|---|---|
| English | [before.md](examples/docs-for-humans/en/before.md) | [after.md](examples/docs-for-humans/en/after.md) |
| 繁體中文 | [before.md](examples/docs-for-humans/zh-TW/before.md) | [after.md](examples/docs-for-humans/zh-TW/after.md) |

兩份的粗體都是 23 → 2。文件會變長，不會變短：中文版 17 → 76 行。換到的是照做的人只需要讀前三分之一。

### 使用

直接用白話講，例如「這份 SOP 看不懂，幫我改寫」。Claude 會依 skill 的描述自動叫用。也可以直接打 `/mtouyang-skills:docs-for-humans`。

skill 會在原文旁邊寫一份樣稿，末尾附「這份動了什麼」。你接受之後，再叫 Claude 轉正。

### 支援的語言

| 語言 | 套用規則 | 額外檢查 |
|---|---|---|
| English | 一到五 | 無 |
| 繁體中文（zh-TW） | 一到六 | `check_punct.py` |

其他語言只套規則一到四。歡迎發 PR 加簡體中文（zh-CN）模組：引號與用字跟繁中不同，需要日常寫簡中的人來維護。

### 腳本

全部只用 Python 標準函式庫（3.9 以上）。檢查不過時結束碼為 1。

| 腳本 | 做什麼 |
|---|---|
| `doc_stats.py [--baseline 原文] 檔案…` | 行數、粗體數、失效的相對連結；加 `--baseline` 時，粗體超過原文四分之一就失敗 |
| `fix_punct.py 檔案…` | 繁中：把緊鄰中文字的半形標點就地改成全形。不動程式碼、URL、連結目標與時間 |
| `check_punct.py 檔案…` | 繁中：列出緊鄰中文字的半形標點 |

## 開發與發版

開發、測試與發版流程見 [README.md](README.md) 的 Develop 一節。

## 授權

[MIT](LICENSE)
