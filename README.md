# 癌症藥物治療新進展：臨床試驗彙整對照表

> 依癌別分類 ｜ 試驗組 vs. 對照組 ｜ 主要療效數據 ｜ 台灣健保給付狀態

---

## 🚀 如何部署到 Vercel（第一次設定）

### 步驟 1：建立 GitHub 帳號與儲存庫
1. 前往 [github.com](https://github.com) 登入或註冊帳號
2. 點擊右上角「＋」→「New repository」
3. 輸入名稱（例如：`cancer-drug-reference`），設為 **Public**
4. 點擊「Create repository」

### 步驟 2：上傳檔案到 GitHub
1. 在儲存庫頁面，點擊「Add file」→「Upload files」
2. 將以下檔案拖入：
   - `index.html`（主網站檔案）
   - `README.md`（此說明文件）
3. 點擊「Commit changes」確認上傳

### 步驟 3：連結 Vercel
1. 前往 [vercel.com](https://vercel.com) 登入（建議用 GitHub 帳號登入）
2. 點擊「Add New Project」
3. 選擇您剛建立的 GitHub 儲存庫
4. 設定：
   - Framework Preset：選「**Other**」
   - Root Directory：`.`（預設即可）
5. 點擊「Deploy」

部署完成後，Vercel 會給您一個網址（例如：`https://cancer-drug-reference.vercel.app`）

---

## 🔄 如何更新網站內容（日常使用）

> **每次只要更新 GitHub 上的 `index.html`，Vercel 就會在約 30 秒內自動重新部署，網站立即更新！**

### 方法 A：直接在 GitHub 網頁上編輯（最簡單）

1. 前往您的 GitHub 儲存庫
2. 點擊 `index.html` 檔案
3. 點擊右上角的「✏️ 鉛筆圖示」
4. 找到要修改的內容進行編輯
5. 滾到頁面底部，點擊「**Commit changes**」
6. 等待約 30 秒 → 網站自動更新！

### 方法 B：上傳新版 index.html（更新大量內容時）

當您更新了 Word 文件，請透過以下步驟重新產生網站：

1. 將新版 Word 文件（`.docx`）交給 AI 助理（Claude）
2. Claude 會自動將 Word 轉換成新版 `index.html`
3. 前往 GitHub 儲存庫 → 點擊 `index.html` → 點擊「...」→「Upload new version」
4. 上傳新版 `index.html`，點擊「Commit changes」
5. 等待約 30 秒 → 網站自動更新！

---

## 📁 檔案說明

| 檔案 | 說明 |
|------|------|
| `index.html` | **主網站檔案**，包含所有內容、樣式與功能 |
| `README.md` | 此說明文件（不影響網站） |

---

## 💡 常見問題

**Q：可以讓別人看到我的網站嗎？**
A：可以！直接把 Vercel 網址傳給對方即可，無需任何帳號即可瀏覽。

**Q：更新後多久生效？**
A：通常 30 秒以內，最慢 2 分鐘。

**Q：如何讓網址更好記？**
A：在 Vercel 的 Project Settings → Domains 可以自訂網址，或購買自訂網域。

**Q：這樣做是免費的嗎？**
A：是的！GitHub 公開儲存庫免費，Vercel 個人方案也是免費的，且沒有流量限制。
