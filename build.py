#!/usr/bin/env python3
"""
癌症藥物治療網站轉換腳本
=======================
將 Word (.docx) 轉換成 index.html

使用方法：
    python build.py 癌症藥物與健保.docx

依賴套件（第一次執行需安裝）：
    pip install beautifulsoup4 lxml
    sudo apt-get install pandoc   # Linux/GitHub Actions
    brew install pandoc           # Mac

所有修正規則已封裝在此腳本中：
  1. 表頭文字強制白色（覆蓋 strong/em 繼承的藍色）
  2. 刪除表格後重複出現的純文字段落（pandoc 產生的 fallback 文字）
  3. 第一欄藥名（藍色粗體）與比較方式（灰色斜體）分成兩行並用虛線分隔
"""

import sys
import os
import re
import copy
import json
import subprocess
import tempfile

# ──────────────────────────────────────────────
# 0. 參數處理
# ──────────────────────────────────────────────
if len(sys.argv) < 2:
    print("用法：python build.py <word_file.docx>")
    sys.exit(1)

DOCX_PATH = sys.argv[1]
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(DOCX_PATH)), "index.html")

print(f"✦ 輸入檔案：{DOCX_PATH}")
print(f"✦ 輸出網站：{OUTPUT_PATH}")

# ──────────────────────────────────────────────
# 1. 用 pandoc 將 docx 轉為 HTML
# ──────────────────────────────────────────────
try:
    from bs4 import BeautifulSoup
except ImportError:
    print("請先安裝依賴：pip install beautifulsoup4 lxml")
    sys.exit(1)

with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
    tmp_html = tmp.name

result = subprocess.run(
    ["pandoc", DOCX_PATH, "-o", tmp_html],
    capture_output=True, text=True
)
if result.returncode != 0:
    print("pandoc 轉換失敗：", result.stderr)
    sys.exit(1)

with open(tmp_html, "r", encoding="utf-8") as f:
    raw_html = f.read()
os.unlink(tmp_html)

soup = BeautifulSoup(raw_html, "lxml")
body = soup.body

# ──────────────────────────────────────────────
# 2. 切割為各癌別 section
# ──────────────────────────────────────────────
sections = []
current_title = None
current_elems = []

for elem in body.find_all(["p", "table"]):
    txt = elem.get_text().strip()
    if re.match(r"^[一二三四五六七八九]、.+", txt):
        if current_title:
            sections.append({"title": current_title, "elems": current_elems[:]})
        current_title = txt
        current_elems = []
    elif current_title:
        current_elems.append(elem)

if current_title:
    sections.append({"title": current_title, "elems": current_elems[:]})

print(f"✦ 找到 {len(sections)} 個癌別分類")

# ──────────────────────────────────────────────
# 3. 設定：圖示 & 顏色（依序對應癌別）
#    如新增癌別，請在此兩個 list 末尾增加項目
# ──────────────────────────────────────────────
ICONS  = ["🫁", "🎀", "🫀", "🫃", "🔬", "🦷", "♀️"]
COLORS = ["#2563eb", "#db2777", "#16a34a", "#9333ea", "#ea580c", "#0891b2", "#be185d"]

# ──────────────────────────────────────────────
# 4. 處理每個 section：
#    修正 A：刪除表格後重複純文字
#    修正 B：第一欄分行標記
# ──────────────────────────────────────────────
def process_section(elems):
    out = ""
    last_was_table = False

    for elem in elems:
        txt = elem.get_text().strip()

        if elem.name == "table":
            # ── 修正 B：標記表頭 row 及第一欄段落 ──
            t = copy.copy(elem)
            t["class"] = ["data-table"]
            for ri, row in enumerate(t.find_all("tr")):
                cells = row.find_all("td")
                if ri == 0:
                    row["class"] = ["header-row"]
                    continue
                if cells:
                    for p in cells[0].find_all("p"):
                        if p.find("strong"):
                            p["class"] = ["drug-name"]
                        elif p.find("em"):
                            p["class"] = ["drug-compare"]
            out += str(t)
            last_was_table = True

        elif elem.name == "p":
            # 子標題：嚴格比對「數字.數字 」開頭
            is_sub = bool(re.match(r"^\d+\.\d+\s", txt))

            if last_was_table:
                # ── 修正 A：表格後只保留子標題，其餘略過 ──
                if is_sub:
                    out += f'<p class="sub-section-header"><strong>{txt}</strong></p>'
                    last_was_table = False
                # else: 重複文字 → 略過
            else:
                if is_sub:
                    out += f'<p class="sub-section-header"><strong>{txt}</strong></p>'
                else:
                    out += str(elem)

    return out

sections_data = []
for i, s in enumerate(sections):
    sections_data.append({
        "title":   s["title"],
        "icon":    ICONS[i]  if i < len(ICONS)  else "💊",
        "color":   COLORS[i] if i < len(COLORS) else "#2563eb",
        "content": process_section(s["elems"]),
    })

# ──────────────────────────────────────────────
# 5. 組裝 HTML
# ──────────────────────────────────────────────
def make_tabs(sections_data):
    html = ""
    for i, s in enumerate(sections_data):
        active = "active" if i == 0 else ""
        m = re.match(r"[一二三四五六七八九]、(.+?)（(.+?)）", s["title"])
        if m:
            label = f'{m.group(1)}<br><span class="en-name">{m.group(2)}</span>'
        else:
            label = s["title"]
        html += (
            f'    <button class="tab-btn {active}" onclick="showTab({i})" '
            f'id="tab-{i}" style="--tab-color:{s["color"]}">\n'
            f'        <span class="tab-icon">{s["icon"]}</span>\n'
            f'        <span class="tab-label">{label}</span>\n'
            f'    </button>\n'
        )
    return html

def make_panels(sections_data):
    html = ""
    for i, s in enumerate(sections_data):
        display = "block" if i == 0 else "none"
        html += (
            f'    <div class="tab-panel" id="panel-{i}" style="display:{display}">\n'
            f'        <h2 class="section-title" style="color:{s["color"]}">'
            f'{s["icon"]} {s["title"]}</h2>\n'
            f'        {s["content"]}\n'
            f'    </div>\n'
        )
    return html

CSS = """
    :root {
        --primary: #1e3a5f;
        --bg: #f4f7fb;
        --white: #ffffff;
        --border: #dde3ed;
        --text: #1a202c;
        --muted: #5a6a7a;
        --shadow: 0 1px 4px rgba(0,0,0,0.08);
        --shadow-md: 0 4px 16px rgba(0,0,0,0.10);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'PingFang TC',
                     'Microsoft JhengHei', 'Noto Sans TC', sans-serif;
        background: var(--bg);
        color: var(--text);
        font-size: 14px;
        line-height: 1.6;
    }
    /* ── Header ── */
    .site-header {
        background: linear-gradient(135deg, #1a2f50 0%, #2563eb 100%);
        color: white;
        padding: 22px 28px 16px;
        position: sticky; top: 0; z-index: 100;
        box-shadow: 0 2px 10px rgba(0,0,0,0.25);
    }
    .site-header h1 { font-size: 1.25rem; font-weight: 700; margin-bottom: 3px; }
    .site-header .subtitle { font-size: 0.75rem; opacity: 0.82; }
    .search-wrap { margin-top: 10px; }
    .search-input {
        width: 100%; max-width: 380px;
        padding: 7px 12px 7px 34px;
        border-radius: 8px; border: none;
        background: rgba(255,255,255,0.15);
        color: white; font-size: 0.82rem; outline: none;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' fill='white' viewBox='0 0 16 16'%3E%3Cpath d='M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.099zm-5.242 1.656a5.5 5.5 0 1 1 0-11 5.5 5.5 0 0 1 0 11z'/%3E%3C/svg%3E");
        background-repeat: no-repeat; background-position: 10px center;
    }
    .search-input::placeholder { color: rgba(255,255,255,0.65); }
    .search-input:focus { background-color: rgba(255,255,255,0.22); }
    /* ── Tabs ── */
    .tab-nav {
        display: flex; overflow-x: auto;
        background: var(--white); border-bottom: 2px solid var(--border);
        padding: 0 12px; gap: 2px; scrollbar-width: none;
    }
    .tab-nav::-webkit-scrollbar { display: none; }
    .tab-btn {
        display: flex; flex-direction: column; align-items: center; gap: 2px;
        padding: 11px 14px 9px; border: none; background: none; cursor: pointer;
        color: var(--muted); font-size: 0.78rem; font-family: inherit;
        border-bottom: 3px solid transparent; margin-bottom: -2px;
        transition: all 0.18s; min-width: 82px; white-space: nowrap;
    }
    .tab-btn:hover { color: var(--tab-color); background: #f8fafc; }
    .tab-btn.active { color: var(--tab-color); border-bottom-color: var(--tab-color); font-weight: 700; }
    .tab-icon { font-size: 1.25rem; line-height: 1; }
    .tab-label { text-align: center; line-height: 1.3; }
    .en-name { font-size: 0.67rem; display: block; opacity: 0.75; }
    /* ── Main ── */
    .main-content { max-width: 1440px; margin: 0 auto; padding: 20px 18px; }
    .tab-panel { animation: fadeIn 0.18s ease; }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    .section-title {
        font-size: 1.15rem; font-weight: 700;
        margin-bottom: 16px; padding-bottom: 9px;
        border-bottom: 2.5px solid currentColor;
    }
    /* ── Legend ── */
    .legend {
        display: flex; gap: 14px; flex-wrap: wrap;
        margin-bottom: 16px; padding: 10px 14px;
        background: var(--white); border-radius: 8px;
        box-shadow: var(--shadow); font-size: 0.78rem; align-items: center;
    }
    .legend-item { display: flex; align-items: center; gap: 5px; }
    .legend-dot { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }
    .legend-hint { margin-left: auto; color: var(--muted); font-size: 0.72rem; }
    /* ── Sub-section header ── */
    .sub-section-header {
        font-size: 0.92rem; font-weight: 700;
        margin: 22px 0 10px;
        padding: 7px 13px;
        background: #eef3fb;
        border-left: 4px solid #2563eb;
        border-radius: 0 6px 6px 0;
        color: #1a2f50;
    }
    /* ── Table ── */
    .data-table {
        width: 100%; border-collapse: collapse;
        margin-bottom: 20px;
        background: var(--white);
        border-radius: 10px; overflow: hidden;
        box-shadow: var(--shadow-md);
        font-size: 0.83rem;
    }
    /* 修正 A：表頭強制白色（包含 strong/em 繼承問題） */
    .data-table tr.header-row td {
        background: #1e3a5f !important;
        color: #ffffff !important;
        font-weight: 700;
        text-align: center;
        padding: 9px 11px;
        border: 1px solid #2a4a70;
        font-size: 0.8rem;
    }
    .data-table tr.header-row td strong,
    .data-table tr.header-row td em,
    .data-table tr.header-row td * { color: #ffffff !important; }
    /* Data rows */
    .data-table tr.odd:not(.header-row) { background: var(--white); }
    .data-table tr.even { background: #f6f9fd; }
    .data-table tr:not(.header-row):hover { background: #eff5ff; }
    .data-table td {
        padding: 9px 11px;
        border: 1px solid #e4eaf2;
        vertical-align: top;
    }
    .data-table tr:not(.header-row) td:first-child { background: #f0f4f9; min-width: 140px; }
    /* 修正 B：第一欄分行 */
    .drug-name { margin-bottom: 5px !important; }
    .drug-name strong { color: #1e3a5f; font-size: 0.86rem; display: block; line-height: 1.4; }
    .drug-compare { margin-top: 0 !important; padding-top: 4px; border-top: 1px dashed #c5d0de; }
    .drug-compare em { color: #5a6a7a; font-size: 0.78rem; font-style: italic; }
    /* Results & NHI columns */
    .data-table tr:not(.header-row) td:nth-child(5) { font-size: 0.8rem; line-height: 1.65; }
    .data-table tr:not(.header-row) td:nth-child(5) strong { color: #1e3a5f; }
    .data-table tr:not(.header-row) td:last-child {
        text-align: center; font-weight: 600; min-width: 95px; font-size: 0.8rem;
    }
    /* ── Back to top ── */
    .back-top {
        position: fixed; bottom: 22px; right: 22px;
        width: 38px; height: 38px;
        background: #1e3a5f; color: white;
        border: none; border-radius: 50%; font-size: 1.1rem; cursor: pointer;
        box-shadow: var(--shadow-md);
        display: none; align-items: center; justify-content: center;
        transition: background 0.2s;
    }
    .back-top.visible { display: flex; }
    .back-top:hover { background: #2563eb; }
    /* ── Footer ── */
    .site-footer {
        text-align: center; padding: 18px;
        color: var(--muted); font-size: 0.73rem;
        border-top: 1px solid var(--border); margin-top: 28px;
    }
    /* ── Responsive ── */
    @media (max-width: 768px) {
        .site-header { padding: 14px 14px 12px; }
        .site-header h1 { font-size: 1rem; }
        .main-content { padding: 14px 10px; }
        .tab-btn { min-width: 68px; padding: 9px 8px 7px; font-size: 0.7rem; }
        .data-table { font-size: 0.74rem; }
        .data-table td { padding: 6px 7px; }
        .drug-name strong { font-size: 0.76rem; }
    }
    @media print {
        .site-header, .tab-nav, .back-top { display: none !important; }
        .tab-panel { display: block !important; }
    }
"""

JS = """
    function showTab(idx) {
        document.querySelectorAll('.tab-panel').forEach((p,i) => {
            p.style.display = i === idx ? 'block' : 'none';
        });
        document.querySelectorAll('.tab-btn').forEach((b,i) => {
            b.classList.toggle('active', i === idx);
        });
        window.scrollTo({top: 0, behavior: 'smooth'});
    }
    function colorNHI() {
        document.querySelectorAll('.data-table').forEach(table => {
            table.querySelectorAll('tr:not(.header-row)').forEach(row => {
                const cells = row.querySelectorAll('td');
                if (!cells.length) return;
                const cell = cells[cells.length - 1];
                const t = cell.textContent;
                if      (t.includes('已給付'))                       cell.style.color = '#16a34a';
                else if (t.includes('未上市') || t.includes('未給付')) cell.style.color = '#dc2626';
                else if (t.includes('已核准'))                        cell.style.color = '#2563eb';
                else if (t.includes('申請') || t.includes('部分'))    cell.style.color = '#d97706';
            });
        });
    }
    function doSearch(q) {
        q = q.trim().toLowerCase();
        let anyActive = false;
        document.querySelectorAll('.tab-panel').forEach((p, i) => {
            const match = !q || p.textContent.toLowerCase().includes(q);
            p.style.display = match ? 'block' : 'none';
            document.getElementById('tab-' + i).classList.toggle('active', match);
            if (match && !anyActive) anyActive = true;
        });
        if (!anyActive) showTab(0);
    }
    window.addEventListener('scroll', () => {
        document.getElementById('backTop').classList.toggle('visible', window.scrollY > 280);
    });
    document.addEventListener('DOMContentLoaded', colorNHI);
"""

FINAL_HTML = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>癌症藥物治療新進展：臨床試驗彙整對照表</title>
    <style>{CSS}</style>
</head>
<body>

<header class="site-header">
    <h1>💊 癌症藥物治療新進展：臨床試驗彙整對照表</h1>
    <div class="subtitle">依癌別分類 ｜ 試驗組 vs. 對照組 ｜ 主要療效數據 ｜ 台灣健保給付狀態 ｜ 資料截至 2026 年 3 月</div>
    <div class="search-wrap">
        <input type="text" class="search-input" id="searchInput"
               placeholder="搜尋藥物、試驗名稱…" oninput="doSearch(this.value)">
    </div>
</header>

<nav class="tab-nav">
{make_tabs(sections_data)}</nav>

<main class="main-content">
    <div class="legend">
        <div class="legend-item"><div class="legend-dot" style="background:#16a34a"></div><span>已給付</span></div>
        <div class="legend-item"><div class="legend-dot" style="background:#dc2626"></div><span>未給付 / 未上市</span></div>
        <div class="legend-item"><div class="legend-dot" style="background:#d97706"></div><span>審查中 / 部分給付</span></div>
        <div class="legend-item"><div class="legend-dot" style="background:#2563eb"></div><span>已核准（健保申請中）</span></div>
        <div class="legend-hint">← 左右滑動切換癌別</div>
    </div>
{make_panels(sections_data)}</main>

<button class="back-top" id="backTop" title="回到頂部"
        onclick="window.scrollTo({{top:0,behavior:'smooth'}})">↑</button>

<footer class="site-footer">
    資料截至 2026 年 3 月 ｜ 本表僅供臨床參考，實際給付狀態請以衛福部健保署公告為準
</footer>

<script>{JS}</script>
</body>
</html>"""

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(FINAL_HTML)

print(f"\n✅ 完成！已輸出：{OUTPUT_PATH}  ({len(FINAL_HTML):,} bytes)")
print("   → 上傳 index.html 到 GitHub 後，Vercel 自動部署（約 30 秒）")
