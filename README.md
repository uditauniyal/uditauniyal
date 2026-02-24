# Udita Uniyal

**B.Tech Information Technology** · Banasthali Vidyapith (2024-28) · GPA: 8.9/10.0

I build AI agents for domains where being wrong isn't an option: law, healthcare, finance.

My work sits at the intersection of **multi-agent orchestration** and **safe AI deployment** - designing systems with hallucination-constrained generation, citation-gated outputs, calibrated refusal mechanisms, and sentence-level audit traceability. Every agent I build knows when to answer and, more importantly, when *not* to.

---

## 🧠 What I Think About

Most LLM applications bolt a prompt onto an API and ship. The hard problems I care about are different:

- **Hallucination mitigation in high-stakes domains** - How do you guarantee every legal citation maps to a real statute? Every diagnostic claim traces to a medical reference?
- **Adaptive agent routing** - Why should a simple query and a complex one take the same path through your system? I build state machines that route based on what they discover, not fixed pipelines.
- **Calibrated refusal** - An agent that says "I don't know" with the right threshold is more valuable than one that always answers. I implement explicit abstention behavior when retrieval confidence falls below threshold.
- **Provenance and auditability** - If your system generates a recommendation, you should be able to trace every claim back through the retrieval → grounding → generation chain to its source.

---

## 🏗️ Systems I've Built

### [STRATIFY](https://github.com/uditauniyal/stratify) - SAR Authoring & Intelligent Alert Triage `Barclays HACK-O-HIRE 2026`
> *LangGraph · LangChain · ChromaDB · OpenAI GPT-4o-mini · FastAPI · Pydantic · Streamlit*

A LangGraph state-machine pipeline that transforms raw transaction monitoring alerts into audit-ready Suspicious Activity Reports. Designed a **3-layer triage cascade** (rule-based → behavioral anomaly scoring → LLM judge for borderline cases only) that eliminates 85-90% of false positives before a single narrative is written. Built a citation-constrained RAG engine over a FinCEN regulatory corpus with **11-check 5W+How validation** and sentence-level audit traceability. 100% classification accuracy across 5 synthetic scenarios. ~3,200 LOC, 15+ Pydantic schemas.

**Architecture:** 4-node state machine with conditional edge routing - the pipeline's behavior changes based on what it discovers about each alert.

```
TMS Alert → [Ingest & Enrich] → [Triage & Classify] → Conditional Router
                                                          ├── ~70-75% → FALSE_POSITIVE (auto-closed)
                                                          ├── ~15-20% → NEEDS_REVIEW (human queue)
                                                          └── ~10-15% → [RAG + Generate] → [Validate & Package] → SAR Output
```

---

### [Legal-MVP](https://github.com/uditauniyal/legal-mvp) - Agentic Legal Aid for the Indian Judiciary `Research · Paper in Preparation`
> *FastAPI · Qdrant · OpenAI Agents · RAG · Docker · fpdf2*

A **5-agent orchestration pipeline** (Intake → Router → Retrieval → Answer → Reporter) for Indian legal advisory, covering BNS, CrPC, and IPC statutes. The Router Agent implements a query complexity classifier (Layman vs. Paralegal) that selects divergent reasoning paths. Every legal claim must be grounded in a retrieved statute via Qdrant vector search with statute-aware re-ranking - and the system **explicitly declines when retrieval confidence falls below threshold**, providing a testbed for studying calibrated refusal in high-stakes domains.

The Reporter Agent generates structured PDF advisories with traceable citation chains: `claim → statute → provision → remedy`.

**📄 Paper:** *"Legal-MVP: A Multi-Agent Agentic Framework for Citation-Constrained Legal Advisory in the Indian Judiciary"* - in preparation (2026).

---

### [SwasthID](https://github.com/uditauniyal/SwasthID-pipelline2) - AI-Powered Medical Identity Platform `Microsoft Imagine Cup 2026`
> *Azure OpenAI (GPT-4o Vision) · FastAPI · Azure Web Apps · RAG · PDF Generation*

Multi-modal medical imaging pipeline processing ultrasound (PCOS) and X-ray (pneumonia, breast cancer) inputs through GPT-4o Vision with domain-adapted prompt templates. Cross-references outputs against medical reference datasets to produce **confidence-calibrated diagnostic scores** and radiologist-style PDF reports with severity classification (Normal/Mild/Moderate/Severe). Designed as a unified health identity layer aligned with India's ABHA infrastructure.

**🔗 Live:** [vitalscan-med-ai.azurewebsites.net](https://vitalscan-med-ai.azurewebsites.net)

---

### [ClauseAI](https://github.com/uditauniyal/ClauseAI) - Policy-Aware LLM Decision Engine for Insurance
> *LangChain · FAISS · OpenAI Embeddings · FastAPI · Multi-Agent RAG*

A **7-stage sequential pipeline** with typed inter-stage contracts (structured JSON handoffs) for insurance claim adjudication. Strict schema enforcement at stage boundaries drives **sub-2% hallucination** through citation-gated generation. Every output requires exact policy clause references, section identifiers, and coverage conditions, with per-decision confidence calibration enabling threshold-based routing to human reviewers.

---

### [NeerSetu Copilot](https://github.com/uditauniyal/neer-setu-copilot) - AI-Driven Groundwater Intelligence
> *LLM Tooling · SQL Analytics · RAG · SQLite/PostgreSQL*

Bilingual (English/Hindi) AI copilot for querying national water datasets (CGWB, state boards). Intent-conditioned routing dispatches to specialized backends: **text-to-SQL** for quantitative queries and **lightweight RAG** for contextual/policy questions, with a response synthesizer producing citation-aware outputs and interactive visualizations.

**🔗 Live:** [neer-setu-copilot.streamlit.app](https://neer-setu-copilot.streamlit.app)

---

## 🔧 Technical Stack

```
Orchestration       LangChain · LangGraph · LangSmith · OpenAI Agents SDK
LLMs & Vision       GPT-4o · GPT-4o-mini · GPT-4o Vision · Ollama (local)
Vector Databases    Qdrant · ChromaDB · FAISS
Retrieval           RAG · Semantic Search · Re-ranking · Embeddings · Text-to-SQL
Backend             FastAPI · Pydantic v2 · RESTful APIs · Streamlit
Cloud & DevOps      Microsoft Azure (Web Apps, OpenAI Service) · Docker · Git
Languages           Python · C++ · C · SQL · Bash
Safety & Eval       Hallucination Detection · Citation Verification · Provenance Tracking
                    Confidence Calibration · Ablation Studies · Error Taxonomy
```

---

## 🧪 Design Patterns Across My Work

Every project isn't just a one-off - they share architectural principles I've developed through iteration:

| Pattern | Where It Appears | Why It Matters |
|:---|:---|:---|
| **Citation-gated generation** | Legal-MVP, STRATIFY, ClauseAI | No claim leaves the system without a traceable source |
| **Calibrated refusal** | Legal-MVP, ClauseAI | Agents decline when confidence is below threshold rather than hallucinating |
| **Conditional routing** | STRATIFY, Legal-MVP, NeerSetu | Queries take different paths based on complexity/intent, not one-size-fits-all |
| **Typed state contracts** | STRATIFY (TypedDict), ClauseAI (JSON handoffs) | Strict inter-agent schemas prevent error propagation across pipeline stages |
| **Multi-layer triage** | STRATIFY (3-layer cascade) | Expensive LLM calls only for cases that need them - cost-accuracy tradeoff |
| **Sentence-level provenance** | STRATIFY (audit trail), Legal-MVP (citation chains) | Full traceability from output → evidence → source |

---

## 🌱 Outside the Code

- 📚 Behavioral psychology & decision science
- 🎾 Competitive tennis
- 🌍 Global politics & geopolitics
- 💃 Dance as structured creativity
- 🏃‍♀️ Long-distance running

---

## 📫 Let's Connect

[![Email](https://img.shields.io/badge/Email-udita.uniyal1630%40gmail.com-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:udita.uniyal1630@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-udita--uniyal-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://linkedin.com/in/udita-uniyal)
