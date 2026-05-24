# NeurForge — Product Direction (Post-Baseline)

> **When to read this:** Only after the rebranded baseline is stable and the
> user has explicitly asked you to start extending toward the platform direction.
> During baseline work, ignore this file.

> **What this is:** Direction, not specification. Use it to understand *why*
> a feature matters and *whether* a proposal compounds the platform — not as
> a checklist to implement.

---

## 1. Product positioning

NeurForge is an **Agent Development Platform for industrial / manufacturing
operations**. The thesis: most enterprises don't lack data or model capability
anymore — they lack the execution layer that turns site data, tools, and SOPs
into Agents that can actually run inside production workflows.

What NeurForge is **not**:

- Not a general-purpose chatbot or Copilot clone
- Not a from-scratch agent framework (built on youtu-agent / OpenAI Agents SDK conventions)
- Not a point-solution AI project — every feature should compound the platform

---

## 2. Three-layer architecture (target shape)

This is the long-term shape. Do not build it all upfront. Each layer matures
through real applications.

**L1 — Data Layer**
Integrate plant-floor data into Agent-usable knowledge:
SOPs, work orders, inspection records, quality logs, sensor / time-series data,
images, audio. The job is not just storage — it is making data *queryable,
traceable, comparable, and instructable* by Agents.

**L2 — Platform Layer (NeurForge Agent Runtime)**
Agent Builder, Tool Registry, Orchestration, Guardrails, Memory, Multi-Agent.
Built on top of the youtu-agent baseline. We extend, we don't replace.

**L3 — Application Layer**
Concrete Agents delivered to customers. Initial focus areas:
inspection, quality assistance, anomaly investigation, custom vision.

> Order of work: **L3 first, then extract patterns into L2, with L1 maturing alongside.**
> Do not build platform abstractions before there are at least two real
> applications that need them.

---

## 3. Hard product requirements

These are non-negotiable across all features once we move past baseline:

- **Traceability.** Every agent run must produce a reviewable tool trace and
  evidence path. This is a product requirement, not a nice-to-have. Industrial
  customers will not accept opaque agent decisions.
- **On-prem deployable.** No hard dependencies on cloud-only services unless
  gated behind a config flag. Data governance is a hard constraint for our
  target customers.
- **Safe execution.** When agents act on real systems, they need:
  permission checks, sandboxing, approval gates, timeout / retry / degradation,
  full execution logging.
- **Multimodal-ready.** Text, image, audio, time-series should flow through the
  same agent pipeline — not parallel one-off pipelines.

---

## 4. Compounding test

Before adding any non-trivial feature, ask:

> "Does this compound into the platform — meaning the next application benefits
> from it — or is it a one-off for a single customer?"

One-offs are fine when explicitly scoped as such. The danger is one-offs
disguised as platform features.

---

## 5. Multi-role agent direction (later phase)

The long-term direction is multi-agent collaboration with role specialization,
roughly:

- **Planner** — task decomposition, workflow selection
- **Inspector** — site data acquisition, evidence gathering
- **Analyst** — reasoning, case comparison, root cause
- **Reporter** — work orders, reports, notifications, summaries

Do not implement this speculatively. It emerges from real workflows that need it.

---

## 6. Memory / case accumulation (later phase)

The platform's long-term value comes from accumulating site experience —
faults, handling, outcomes, human corrections — into reusable case memory
with retained evidence paths. Each interaction should be capable of feeding
back into the system, but the mechanism only matters once we have applications
generating cases worth keeping.

---

## 7. Plugin Marketplace (differentiator)

The core competitive differentiator for enterprise pitch (Nvidia TW, Chunghwa Telecom,
Far EasTone, industrial clients):

> "NeurForge lets your partner ecosystem and internal departments publish Agent
> Tools to a shared marketplace. Every agent on the platform can discover,
> install, and use these tools — governed, versioned, and auditable."

**Prototype target:** Browse, install/uninstall, and upload custom tools via UI.  
**Production target:** Sandboxed execution (Docker), static code analysis, permission scopes.

This roadmap — from prototype to production-grade security — is itself a selling point
for enterprise pilots.
