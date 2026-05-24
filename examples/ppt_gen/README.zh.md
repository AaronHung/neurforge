# PowerPoint 模板示例

## 環境依賴

**安裝方式：**

```bash
# 專案根目錄
cd youtu-agent

# 安裝 PPT 生成所需依賴
uv sync --extra ppt-gen
```

## 快速開始

1. 下載[模板檔案](https://cdn.jsdelivr.net/gh/TencentCloudADP-DevRel/picgo-images@main/assets/templates.zip)到 `examples/ppt_gen/templates` 目錄。
2. 準備需要轉成 PPT 的參考資料（純文本、Markdown 或網頁）。例如下載 [諾貝爾獎介紹網頁](https://www.nobelprize.org/prizes/physics/2025/popular-information/)。

```bash
# 進入示例目錄
cd examples/ppt_gen

# 下載示例網頁
wget https://www.nobelprize.org/prizes/physics/2025/popular-information/ -O webpage.html
```

執行 PPT 生成指令碼：

```python
python main.py \
  --file webpage.html \
  --template_path templates \
  --yaml_path yaml_example2.yaml \
  --pages 8 \
  --disable_tooluse \
  --extra_prompt "確保PPT語言是中文" \
  --template_name 11
```

指令碼會生成同名的 `json` 與 `pptx` 檔案。透過 `--yaml_path` 可以切換不同的模板配置。

## YAML 驅動的模板配置

> 詳見 [YAML 配置指南](YAML_CONFIG_GUIDE.zh.md)。

套模板流程由 YAML 配置驅動（參見 `yaml_example.yaml`），配置檔案主要有兩部分：

1. **type_map**：將每類幻燈片的 `type`（如 `title`, `items_page_4`）對映到模板 PPT 中的幻燈片索引，渲染器據此複製對應母板。
2. **頁面定義塊**：每個 `<name>_page` 描述該類幻燈片的全部欄位，欄位會宣告 `type`、長度限制以及會被注入到 JSON Schema 的提示。

支援的欄位型別包括 `str`、`int`、`content`（富文本/圖片/表格容器）、`content_list`、`item_list`、`str_list` 與 `image`。當 Agent 輸出內容後，`fill_template_with_yaml_config` 會讀取 YAML、根據 `type_map` 找到目標幻燈片、複製模板，並按照欄位型別渲染。自定義模板步驟：

1. 複製 `yaml_example.yaml`，調整 `type_map` 使其與 PPT 模板的幻燈片順序一致。
2. 更新或新增頁面塊，確保所有期望生成的 slide 型別都擁有正確的欄位定義。
3. 執行指令碼時使用 `--yaml_path <your_config.yaml>`，即可載入新的 schema 並與模板貼合。

### 如何標註新的 PPT 模板

- 在 PowerPoint 的「選擇窗格」（Selection Pane）中重新命名形狀，確保名稱與 YAML 欄位完全一致（例如：`title`、`subtitle`、`item_title1`、`item_content1`、`label1`、`content1`）。
- 同一頁不可出現重複的名稱。每個形狀名稱必須唯一，以便渲染器能準確定位並替換。
- 可參考 `examples/ppt_gen/templates` 中的現有模板，以及 `yaml_example.yaml` 的欄位定義進行命名。