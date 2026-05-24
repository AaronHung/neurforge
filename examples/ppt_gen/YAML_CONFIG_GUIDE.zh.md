# PPT YAML 配置指南

本檔案說明如何使用 YAML 描述 PPT 模板。

## YAML的合併

PPT模版的YAML配置主要有兩種：

1. [`yaml_example.yaml`](./yaml_example.yaml) 或者 [`yaml_example2.yaml`](./yaml_example2.yaml) 這類多個模版間共享的YAML配置。
2. 每個具體PPT專案獨有的YAML配置檔案，用於定義該PPT特有的頁面型別、覆蓋共享yaml的頁面型別、修改模版中的頁面順序（`type_map`）。和模版的pptx檔案放在同一個資料夾中。

## YAML 檔案結構

合併後的YAML主要包括兩部分：

1. **`type_map`**：按順序將每種幻燈片的 `type` 對映到參考 PPT 模板中的幻燈片索引（從 0 開始）。渲染器根據該索引複製相應母版。
2. **頁面定義塊**：每個 `<name>_page` 條目描述某類幻燈片的 schema，必須包含：
   - `description`：對頁面的文字說明，會用於檔案和 JSON Schema。
   - `type`：幻燈片型別，必須出現在 `type_map` 中。
   - 至少一個 **欄位定義**，用於描述每個佔位符希望接收的資料。

建議將 `type_map` 放在具體 PPT 模版的 YAML 配置檔案中。`type_map`只需要列出模版支援的頁面，對於沒有在其中列出的頁面，`gen_schema.py`指令碼會把它在最終的schema中去掉。

### 欄位定義可用的鍵

| 鍵名         | 說明 |
|--------------|------|
| `type`       | 欄位型別（見下方支援列表）。 |
| `description`| 可選提示，會被寫入 JSON Schema 供 LLM 參考。 |
| `min_len`    | 對字串或列表的最小長度約束（轉換為 `minLength` / `minItems`）。 |
| `max_len`    | 字串或列表的最大長度（轉換為 `maxLength` / `maxItems`）。 |
| `optional`   | 若設為 `true` 則欄位為可選；預設必填。 |

### 支援的欄位型別

| 欄位型別         | 含義 / 渲染行為 |
|------------------|----------------|
| `str` / `int`    | 直接寫入同名形狀，`int` 會被轉成字串。 |
| `content`        | 交由 `handle_content` 處理的富媒體欄位，使用下文列出的 `TextContent`/`ImageContent`/`TableContent` 結構。 |
| `content_list`   | `BaseContent` 陣列，與 `content` 相同的負載，每個條目對映到 `<欄位名>1`, `<欄位名>2` 等。 |
| `item_list`      | `Item` 物件陣列（標題 + 文本），使用 `handle_item` 渲染。 |
| `str_list`       | 短標籤列表（如 SWOT 字母），對映到 `label1`, `label2`... 等形狀。 |
| `image`          | `BasicImage`（僅包含 `image_url`），插入影像佔位符。 |

> ⚠️ **形狀命名**：PPT 模板中的形狀名稱需與 YAML 欄位一致，`fill_template_with_yaml_config` 才能定位並替換。

### 負載結構參考

這些型別會直接序列化為 [`ppt_template_model.py`](./ppt_template_model.py) 中的 Pydantic 模型：

1. **`content` / `content_list`** → `BaseContent` 聯合型別（由 `content_type` 決定具體模型）：
   - `TextContent`：`{"content_type": "text", "paragraph": [Paragraph] | str}`；`Paragraph` 包含 `{text, bullet, level}`。
   - `ImageContent`：`{"content_type": "image", "image_url": "https://...", "caption": "可選"}`。
   - `TableContent`：`{"content_type": "table", "header": [str], "rows": [[str]], "n_rows": int, "n_cols": int, "caption": "可選"}`。
2. **`item_list`** → `Item` 列表：`{"title": "2-4 個詞", "content": "≤10 個詞"}`，渲染時對映到 `item_title{n}` / `item_content{n}`。
3. **`image`** → `BasicImage`：`{"image_url": "https://..."}`，渲染器會下載圖片並替換佔位符。
4. **`str_list`** → 字串陣列，`min_len`/`max_len` 會寫入 JSON Schema，渲染器按順序填充 `label1`、`label2` 等形狀。
5. **`content_list`** 補充：每個條目與單獨的 `content` 欄位一致，請在 PPT 中使用 `<欄位名>1`、`<欄位名>2` 命名。

## YAML 如何轉成 JSON Schema

執行 [`main.py`](./main.py) 時，程式會讀取 `--yaml_path` 指向的 YAML，並呼叫 `build_schema` 將生成的 JSON Schema 注入 Agent 指令，無需手動處理 @examples/ppt_gen/main.py#39-84。

`gen_schema.build_schema` 在內部完成以下步驟：

1. 依據 `type_map` 得到允許的幻燈片型別集合。
2. 將每個頁面定義轉成 `oneOf` 項，其 `properties` 與欄位說明一致。
3. 把 `min_len` / `max_len` 對映到 JSON Schema 的 `minLength` / `maxLength` / `minItems` / `maxItems`。
4. 對 `content`、`item_list`、`image` 等複雜型別引用 `$defs`，確保驗證邏輯與渲染器保持一致。

> 如需除錯，可手動執行 `gen_schema.py` 匯出 schema，但正常流程會自動執行。

## 自定義頁面型別示例

假設需要新增“insight_grid_page”幻燈片展示三個核心指標：

1. **準備 PPT 模板**：複製現有幻燈片或重新設計，並在 Selection Pane 中將形狀命名為 `title`、`item_title1`、`item_content1` 等。
2. **擴充套件 `type_map`**：加入新型別對應的模板索引。

```yaml
type_map:
  - content: 0
  - title: 1
  - insight_grid: 13   # 新 slide 位於模板索引 13
```

3. **定義頁面塊**：

```yaml
insight_grid_page:
  description: 並排展示三個關鍵指標
  type: insight_grid
  title:
    type: str
    description: 6 個詞以內的標題
    max_len: 6
  items:
    type: item_list
    description: 每個元素包含指標名稱和簡短說明
    min_len: 3
    max_len: 3
  image:
    type: image
    optional: true
```

4. **執行 main.py**：攜帶 `--yaml_path <your_yaml>`，Agent 會輸出帶 `type: insight_grid` 的 slide，`fill_template_with_yaml_config` 會複製索引 13 的幻燈片並填充欄位。

注意，需要始終保持 YAML、JSON Schema 與 PPT 中的形狀命名一致。
