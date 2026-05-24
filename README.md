# <img src="docs/assets/logo-square.png" alt="NeurForge Logo" height="32px"> NeurForge

**Forging Factories That Think**

> Agent Platform × Data Flywheel × Industrial Apps

<p align="center">
| <a href="README_ZHTW.md"><b>繁體中文</b></a>
| <a href="README_JA.md"><b>日本語</b></a>
| <a href="https://github.com/AaronHung/neurforge"><b>GitHub</b></a>
|
</p>

---

NeurForge is an **Agent Development Platform built for smart manufacturing**. It is not a chatbot — it is a platform that turns your factory's data, SOPs, and field experience into Agents that get smarter with every use.

Built on top of the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python), NeurForge adds the manufacturing-specific harness, memory, multi-agent orchestration, and data flywheel needed to take Agents from demo to production.

---

## The Problem

Three structural pain points in every factory:

| # | Pain Point | Impact |
|---|-----------|--------|
| 1 | **Expert knowledge walks out the door** — fault diagnosis and anomaly judgment live in senior workers' heads. When they retire or rotate, the knowledge disappears. | Long new-hire ramp-up, quality variance |
| 2 | **Data is scattered across every system** — PdM, MES, SCADA, inspection sheets, work orders, and QC records live in separate silos. No system can answer cross-silo questions automatically. | Operators open 5–6 screens to piece together the picture |
| 3 | **AI projects freeze after delivery** — every new product line, machine type, or defect class requires re-labeling, re-training, and re-deployment. High cost, slow iteration. | AI investment doesn't compound |

**The result:** AI investment is high, but production-line rollout is fragile. Knowledge erodes year over year.

---

## Three-Layer Architecture

```
L3 · APPS          Factory Inspection Agent · Quality Check Agent · Anomaly Investigation · PdM
                   ─────────────────────────────────────────────────────────────────────────────
L2 · PLATFORM      Agent Builder · Tool Registry & Synthesis · Orchestration / Guardrails
                   Memory / Multi-Agent
                   ─────────────────────────────────────────────────────────────────────────────
L1 · DATA          Enterprise Data Flywheel
                   (SOP · Work Orders · Inspection · SCADA/MES · Sensor Signals · Images)
```

Built on the OpenAI Agents SDK, NeurForge layers manufacturing-specific harness, memory, multi-agent orchestration, and a data flywheel on top — forming vertical capabilities that are not easy to replicate.

---

## Platform Capabilities

| Capability | Description |
|-----------|-------------|
| **Tool Registry & Synthesis** | Define tools once; reuse across Agents. Auto-synthesize tool code from descriptions. |
| **Orchestration & Guardrails** | Multi-step workflow with human-in-the-loop approval, timeout, retry, and fallback protection. |
| **Memory & Case Accumulation** | Field cases, expert corrections, and SOP execution accumulate as enterprise memory — searchable by future Agents. |
| **Multi-Agent Collaboration** | Planner → Inspector → Analyst → Reporter role decomposition for complex tasks. |
| **Multimodal Understanding** | Text, images (defect photos, thermal, CCTV), audio (abnormal sound), and time-series data handled by the same Agent pipeline. |
| **Evidence Path** | Every Agent conclusion retains full tool trace and evidence chain — auditable and traceable. |
| **System Integration** | Connect MES, SCADA, PLC, document stores, work order systems, and vision pipelines. |

---

## Industrial Agent Apps

### App 01 — Factory Inspection Agent
- Multimodal inspection: images, meter readings, voice notes
- Auto-generate work orders and recommended actions from anomalies
- Inspection results feed back to the case library — accuracy improves over time
- **Target:** Single-shift inspection time 2 hr → 25 min

### App 02 — Quality Check Agent
- End-to-end traceability across raw material, process, and finished goods
- Compare similar cases and historical disposition records
- Connect work orders, SOPs, and quality documents to accelerate judgment
- **Target:** Quality event initial judgment: days → hours

### App 03 — Custom Vision Agent (co-development)
- Import customer-specific images, defect knowledge, and field cases
- Start from a single station / single defect type; iterate quickly
- Extendable to surface defects, assembly anomalies, appearance inspection

---

## Data Flywheel

The more you use NeurForge, the smarter it gets about your factory:

```
1. Connect field data      →  Documents, equipment, photos, work orders
2. Organize knowledge      →  Fault knowledge graph, case library, executable SOPs
3. Assist judgment         →  Case-backed, explainable suggestions with evidence
4. Execute workflow        →  Dispatch, report, track, escalate
5. Human feedback          →  Operators confirm, correct, and annotate
6. Accumulate memory       →  Cases and experience reused in the next incident
      └──────────────────────────────────────────────────────┘
                        Flywheel compounds →
```

**Value:** Faster response · Fewer information gaps · Knowledge that stays with the organization.

---

## Getting Started

> Requires Python 3.12+ and [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/AaronHung/neurforge.git
cd neurforge
uv sync
cp .env.example .env
# Edit .env: set NEURFORGE_LLM_API_KEY and related config
```

Run a minimal agent (no tools):

```bash
python scripts/cli_chat.py --config simple/base
```

Run with web search:

```bash
# Requires SERPER_API_KEY and JINA_API_KEY in .env
python scripts/cli_chat.py --config simple/base_search
```

Launch the Web UI:

```bash
python examples/svg_generator/main_web.py
# Open http://127.0.0.1:8848
```

Example `.env` LLM config:

```bash
NEURFORGE_LLM_TYPE=chat.completions
NEURFORGE_LLM_MODEL=deepseek-chat
NEURFORGE_LLM_BASE_URL=https://api.deepseek.com/v1
NEURFORGE_LLM_API_KEY=your-api-key
```

---

## Acknowledgements

NeurForge is a fork of [youtu-agent](https://github.com/TencentCloudADP/youtu-agent) by Tencent Youtu Lab, licensed under MIT. We extend it with manufacturing-specific capabilities while preserving full upstream attribution.

This project also builds upon:
- [openai-agents](https://github.com/openai/openai-agents-python)
- [mkdocs-material](https://github.com/squidfunk/mkdocs-material)
- [model-context-protocol](https://github.com/modelcontextprotocol/python-sdk)

---

*NeurForge · Agent Platform for Smart Manufacturing*
