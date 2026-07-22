# Piyo 交付物上傳 SOP

> 本 repo 是 Piyo 專案所有交付物的集中下載站（GitHub Pages）。
> 每次交付只需：放 ZIP + 改 manifest.json + push。**不要生成自定義 HTML。**

## 頁面地址

`https://henrywhuang.github.io/piyo-deliveries/`

## 交付步驟（agent 照做）

### 1. Clone（首次）或 pull（非首次）

```bash
# 首次
git clone git@github.com:henrywhuang/piyo-deliveries.git /tmp/piyo-deliveries

# 非首次
cd /tmp/piyo-deliveries && git pull origin main
```

### 2. 打包交付物

```bash
# task-slug 用小寫中線連接，如 pyo011-s3-review、age-calibration-v3
mkdir -p /tmp/piyo-deliveries/{task-slug}

# 打包（排除 .DS_Store）
cd {交付物來源目錄}
zip -r /tmp/piyo-deliveries/{task-slug}/{描述性檔名}.zip . -x '*.DS_Store'
```

**打包命名慣例**：`{BOOK_ID}_{STAGE}_{LOCALE}.zip`，如 `PYO-011_S3_zh-TW.zip`。
非書包交付用描述性名稱，如 `course_structure_spec.zip`。

### 3. 追加 manifest.json

用 Python（或 jq）追加一條記錄，**不要手寫整個 JSON**：

```bash
python3 -c "
import json, sys
with open('/tmp/piyo-deliveries/manifest.json', 'r') as f:
    data = json.load(f)
data.append({
    'id': '{task-slug}',
    'title': '{交付標題，中文}',
    'date': '$(date +%Y-%m-%d)',
    'description': '{一句話描述}',
    'files': ['{檔名}.zip'],
    'book': '{PYO-NNN 或空字串}',
    'stage': '{S3/S4A/S4B/… 或空字串}',
    'status': '{pending 或 frozen}',
    'round': '{R1/R2/greenlight/… 或空字串}'
})
with open('/tmp/piyo-deliveries/manifest.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
"
```

**manifest.json 欄位說明**：

| 欄位 | 類型 | 必填 | 說明 |
|---|---|---|---|
| `id` | string | 是 | 子目錄名（= task-slug） |
| `title` | string | 是 | 顯示標題 |
| `date` | string | 是 | ISO 日期 YYYY-MM-DD |
| `description` | string | 否 | 一句話描述 |
| `files` | string[] | 是 | ZIP 檔名列表（相對於 `{id}/`） |
| `book` | string | 是 | 書號，如 `PYO-013`；非書包交付填空字串 |
| `stage` | string | 是 | 站別，如 `S3`、`S4A`、`S4B`；無則空字串 |
| `status` | string | 是 | `pending`（待審/進行中）或 `frozen`（已凍結/已完結） |
| `round` | string | 是 | 輪次：`R1`、`R2`、`greenlight` 等；無則空字串 |

**status 判定規則**：
- `pending`：等待 Stacy 審核、尚未 Green Light、或需要後續修訂
- `frozen`：已 Green Light、已凍結定版、或為歸檔紀錄

### 4. Commit & Push

```bash
cd /tmp/piyo-deliveries
git add .
git commit -m "add {task-slug}"
git push origin main
```

### 5. 驗證

等 1-2 分鐘後開 `https://henrywhuang.github.io/piyo-deliveries/`，確認新卡片出現且 ZIP 可下載。

## 注意事項

- **不要生成 index.html**——已有通用模板，動態讀 manifest.json
- **不要刪除其他交付**——只追加，不覆蓋 manifest.json
- **ZIP 大小限制**：GitHub Pages 單檔 100MB、repo 總量建議 < 1GB
- **同一 task-slug 更新**：覆蓋 ZIP + 更新 manifest.json 中該條的 date，不要重複追加
- **repo 是 public**：GitHub Pages 免費版需 public repo
- **新 UI 結構**：index.html 按 status 分區（待審置頂、已凍結可收合）、按 book 分組、支援搜尋
