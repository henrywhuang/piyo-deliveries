# Piyo 交付物上傳 SOP

> 本 repo 是 Piyo 專案所有交付物的集中下載站（GitHub Pages）。
> 頁面地址：`https://henrywhuang.github.io/piyo-deliveries/`

## 自動上傳（推薦）

```bash
python3 scripts/deliver.py \
  --book PYO-017 --stage S4A --round R1 \
  --title "PYO-017 S4A en-US gate4 證據包" \
  --desc "三檔 draft + QA 二輪 + 回譯 33 頁" \
  --source /path/to/gate_package/ \
  --status pending
```

### 常用場景

```bash
# 首次送審（R1）
python3 scripts/deliver.py \
  --book PYO-005 --stage S3 --round R1 \
  --title "PYO-005 S3 繁中文案 — 關卡③審包" \
  --source /path/to/gate3/ --status pending

# 修訂輪次（R2, R3...）
python3 scripts/deliver.py \
  --book PYO-005 --stage S3 --round R2 \
  --title "PYO-005 S3 zh-TW R2（Stacy R1 修訂）" \
  --source /path/to/r2/ --status pending

# Green Light 凍結版（自動把同站舊 pending → frozen）
python3 scripts/deliver.py \
  --book PYO-005 --stage S3 --round GL \
  --title "PYO-005 S3 繁中文案 Green Light" \
  --source /path/to/gl/ --status frozen --freeze-prior

# 預覽不寫入
python3 scripts/deliver.py ... --dry-run
```

### 參數說明

| 參數 | 必填 | 說明 |
|---|---|---|
| `--book` | 是 | 書號，如 `PYO-017` |
| `--stage` | 是 | 環節：`S1` / `S2` / `S3` / `S4A` / `S4B` / `S5` / `S6` |
| `--round` | 是 | 輪次：`R1` / `R2` / `R3` / `GL`（Green Light） |
| `--title` | 是 | 顯示標題（中文） |
| `--desc` | 否 | 一句話描述 |
| `--source` | 是 | 交付物目錄或檔案（腳本自動 zip） |
| `--status` | 否 | `pending`（預設）或 `frozen` |
| `--freeze-prior` | 否 | 自動凍結同書同站的舊 pending 條目 |
| `--dry-run` | 否 | 預覽模式 |

## 分類規則

### 環節（Stage）

每本書依序經過以下環節，每個環節產出對應的 Gate 文檔：

| 環節 | 全名 | 產出 |
|---|---|---|
| S1 | 故事設計 | Gate 1 設計書 |
| S2 | 分鏡 | Gate 2 分鏡表 |
| S3 | 繁中文案 | Gate 3 zh-TW 文案 |
| S4A | 英文文案 | Gate 4 en-US 證據包 |
| S4B | 多語放量 | Gate 4B 七語收斂 |
| S5 | 資源拆解 | manifest + Bitable |
| S6 | 資源生成 | 繪本圖 / TTS / 動態 |

### 輪次（Round）

同一環節內的審修輪次：

| Round | 說明 |
|---|---|
| R1 | 首次提交（= Gate 審包） |
| R2, R3, ... | Stacy 回饋後的修訂版 |
| GL | Green Light 凍結版（最終定稿） |

### 狀態（Status）

| Status | 說明 |
|---|---|
| `pending` | 等待 Stacy 審核或需修訂 |
| `frozen` | 已 Green Light / 已凍結 |
| `deprecated` | 舊故事已廢棄（書號重新設計） |

## manifest.json 結構

```json
{
  "bookNames": {
    "PYO-001": "三隻小豬",
    "PYO-005": "黑夜裡的小燈"
  },
  "deliveries": [
    {
      "id": "pyo005-s3-r1",
      "title": "PYO-005 S3 繁中文案 — 關卡③審包",
      "date": "2026-07-29",
      "description": "...",
      "files": ["PYO-005_S3_R1.zip"],
      "book": "PYO-005",
      "stage": "S3",
      "status": "pending",
      "round": "R1"
    }
  ]
}
```

## 注意事項

- **不要手動編輯 index.html**——它動態讀 manifest.json
- **ZIP 大小限制**：GitHub Pages 單檔 100MB、repo 總量建議 < 1GB
- **repo 是 public**：GitHub Pages 免費版需 public repo
