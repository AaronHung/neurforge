# <img src="docs/assets/logo-square.png" alt="NeurForge Logo" height="32px"> NeurForge

**考える工場を鍛造する**

> エージェントプラットフォーム × エンタープライズデータフライホイール × 産業アプリ

<p align="center">
| <a href="README.md"><b>English</b></a>
| <a href="README_ZHTW.md"><b>繁體中文</b></a>
| <a href="https://github.com/AaronHung/neurforge"><b>GitHub</b></a>
|
</p>

---

NeurForge は**スマートマニュファクチャリングのために構築されたエージェント開発プラットフォーム**です。チャットボットではありません。工場のデータ、SOP、現場経験を、使えば使うほど賢くなるエージェントシステムへと鍛造するプラットフォームです。

[OpenAI Agents SDK](https://github.com/openai/openai-agents-python) を基盤とし、製造現場専用のハーネス、メモリ、マルチエージェント協調、データフライホイールを重ねることで、エージェントをデモから実運用レベルへと引き上げます。

---

## 課題

工場現場における3つの構造的ペインポイント：

| # | 課題 | 影響 |
|---|------|------|
| 1 | **熟練技術者の経験が残らない** — 欠陥判定・異音検知・故障兆候の多くはベテランの直感と口頭伝承に依存。退職・異動とともに知識が消える。 | 新人育成期間が長く、品質にばらつき |
| 2 | **データがシステムをまたいで散在する** — PdM・MES・SCADA・巡回点検票・作業指示書・品質記録がそれぞれ別のシステムに存在。横断的な問いに自動回答できない。 | オペレーターが5〜6画面を開いて全体像を把握 |
| 3 | **AIプロジェクトは導入後に固まる** — ライン変更・機種変更・欠陥種類の変化のたびに再ラベリング・再学習・再デプロイが必要。コストが高く、製品イテレーションに追いつかない。 | AI投資が複利的に積み上がらない |

**結果：** AIへの投資は増えても、現場への定着は不安定。知識は毎年失われ、優良ラインの経験を複製することが難しくなる。

---

## 三層プロダクトアーキテクチャ

```
L3 · アプリ層    工場巡回点検 Agent · 品質検査 Agent · 異常調査ワークベンチ · PdM
                 ──────────────────────────────────────────────────────────────
L2 · プラットフォーム層
                 Agent Builder · Tool Registry & Synthesis
                 Orchestration / Guardrails · Memory / Multi-Agent
                 ──────────────────────────────────────────────────────────────
L1 · データ層    エンタープライズデータフライホイール
                 (SOP · 作業指示書 · 点検結果 · SCADA/MES · センサー信号 · 画像)
```

OpenAI Agents SDK の上に、NeurForge は製造現場向けのデータ接続・プロセス編成・メモリ蓄積・多役割協調を重ね、簡単には模倣できない垂直特化能力を形成します。

---

## プラットフォームのコア機能

| 機能 | 説明 |
|------|------|
| **Tool Registry & ツール合成** | ツールを一度定義すれば複数のエージェントで再利用。説明からツールコードを自動合成。 |
| **オーケストレーション & ガードレール** | 人間の承認ステップ・タイムアウト・リトライ・フォールバック保護を備えたマルチステップワークフロー。 |
| **メモリ & ケース蓄積** | 現場ケース・専門家の修正・SOP実行結果が企業専用メモリとして蓄積され、次回のエージェントが参照・再利用。 |
| **マルチエージェント協調** | Planner → Inspector → Analyst → Reporter の役割分担で複雑タスクを処理。 |
| **マルチモーダル理解** | テキスト・画像（欠陥写真・熱画像・CCTV）・音声（異音）・時系列データを同一のエージェントパイプラインで処理。 |
| **エビデンスパス** | すべてのエージェント結論にツールトレースと証拠チェーンを保持。監査・追跡可能。 |
| **システム接続** | MES・SCADA・PLC・文書ストア・作業指示システム・ビジョンパイプラインに接続。 |

---

## 産業向けエージェントアプリ

### App 01 — 工場巡回点検エージェント
- マルチモーダル点検：画像・計器読み取り・音声メモ
- 異常から作業指示書と推奨対応を自動生成
- 点検結果がケースライブラリにフィードバック — 精度が継続改善
- **目標効果：** 1シフトの点検時間 2時間 → 25分

### App 02 — 品質検査エージェント
- 原材料・工程・完成品にまたがる一気通貫トレーサビリティ
- 類似ケースと過去の処置記録を比較参照
- 作業指示書・SOP・品質文書を連携し初期判断を高速化
- **目標効果：** 品質事象の初期判断：日単位 → 時間単位

### App 03 — カスタムビジョンエージェント（共同開発）
- 顧客指定の画像・欠陥ナレッジ・現場ケースを取り込み
- 単一ステーション / 単一欠陥種類からスピーディに反復
- 表面欠陥・組み立て異常・外観検査へ拡張可能

---

## データフライホイール

使えば使うほど、システムはあなたの工場をよく理解します：

```
1. 現場データを接続     →  文書・設備・写真・作業指示書
2. 知識として整備       →  故障知識グラフ・ケースライブラリ・実行可能SOP
3. 判断を支援           →  ケースに裏付けられた説明可能な提案と証拠
4. ワークフローを実行   →  派遣・報告・追跡・エスカレーション
5. 人間のフィードバック →  オペレーターが確認・補完・修正
6. 企業メモリとして蓄積 →  ケースと経験を次の案件で再利用
      └──────────────────────────────────────────┘
                  フライホイールが加速する →
```

**3つのコア価値：** より速い対応 · 情報漏れの削減 · 組織に留まる知識。

---

## クイックスタート

> Python 3.12+ と [uv](https://github.com/astral-sh/uv) が必要です。

```bash
git clone https://github.com/AaronHung/neurforge.git
cd neurforge
uv sync
cp .env.example .env
# .env を編集：NEURFORGE_LLM_API_KEY および関連設定を入力
```

基本的な対話の実行（ツールなし）：

```bash
python scripts/cli_chat.py --config simple/base
```

Web検索付きの対話：

```bash
# .env に SERPER_API_KEY と JINA_API_KEY を設定する必要があります
python scripts/cli_chat.py --config simple/base_search
```

Web UIの起動：

```bash
python examples/svg_generator/main_web.py
# http://127.0.0.1:8848 を開く
```

`.env` LLM設定の例：

```bash
NEURFORGE_LLM_TYPE=chat.completions
NEURFORGE_LLM_MODEL=deepseek-chat
NEURFORGE_LLM_BASE_URL=https://api.deepseek.com/v1
NEURFORGE_LLM_API_KEY=your-api-key
```

---

## 謝辞

NeurForge は Tencent Youtu Lab の [youtu-agent](https://github.com/TencentCloudADP/youtu-agent)（MITライセンス）をフォークし、製造現場専用の機能を追加したものです。upstream への完全な帰属表示を維持しています。

また、以下のプロジェクトを使用しています：
- [openai-agents](https://github.com/openai/openai-agents-python)
- [mkdocs-material](https://github.com/squidfunk/mkdocs-material)
- [model-context-protocol](https://github.com/modelcontextprotocol/python-sdk)

---

*NeurForge · スマートマニュファクチャリングのためのエージェント開発プラットフォーム*
