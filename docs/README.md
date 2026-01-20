# Architecture: Delhi Electricity Regulatory AI (DERC Bot)

This folder documents the architectural design of the Delhi Electricity Law Bot.

The system is designed to provide **procedural, citation-backed regulatory guidance**
strictly based on official Delhi electricity regulations and the Electricity Act, 2003.

---

## 1. System Overview

The system is composed of four layers:

1. Source Layer (regulatory truth)
2. Preparation Layer (offline processing)
3. Knowledge Layer (controlled ingestion)
4. Reasoning Layer (rule-bound GPT)

Each layer is intentionally isolated to prevent hallucination, inconsistent citation,
and cross-document contamination.

---

## 2. Source Layer (Regulatory Truth)

The system is built only on **official regulatory documents**, including:

### Core Acts & Policies (PDF form)
These are uploaded as PDFs because they are **stable, structured, and rarely change**:

- Electricity Act, 2003
- National Electricity Policy
- Delhi Electricity Reform Act
- Tariff Policy
- Budget Rules / Organisational Orders

These documents provide **statutory backbone** and legal authority.

---

### Operational & Case-Based Documents (TXT form)

High-volume, frequently referenced, and case-specific documents are converted to TXT
to ensure reliable retrieval and precise citation:

- DERC Supply Code orders
- DERC Supply Code clarifications
- Section 142 final orders
- Non-142 final orders
- General orders
- Consumer grievance related orders
- Committee decisions and outcomes
- Circulars and procedural directions

These documents form the **practical decision-making layer** of the system.

---

## 3. Preparation Layer (Offline Processing)

All documents are processed **outside the GPT** using Python:

- PDFs scraped from DERC website
- Deduplicated using hash-based comparison
- Converted to TXT for retrieval reliability
- Split into logical chunks to avoid token limits
- Versioned and stored for auditability

This ensures the model never sees:
- duplicate orders
- scanned/OCR noise
- inconsistent formatting

---

## 4. Knowledge Layer (Controlled Ingestion)

Only **cleaned, deduplicated TXT files** and **core statutory PDFs** are uploaded to GPT Knowledge.

Design rule:
- PDFs = statutory authority
- TXT = operational reality

If an answer cannot be supported by either,
the assistant must explicitly refuse.

This guarantees citation discipline.

---

## 5. Reasoning Layer (Rule-Bound GPT)

The GPT is configured with strict system rules:

- Delhi electricity law only
- Citation required for every legal claim
- No inference beyond uploaded sources
- Mandatory procedural steps
- Mandatory forum hierarchy:
  CGRF → Ombudsman → statutory appeal
- Safe handling of criminal / theft cases
- Refusal outside scope

This converts a general LLM into a **regulatory-grade assistant**.

---

## 6. Failure-Safe Design

The system fails safely by design:

| Scenario | Behavior |
|--------|---------|
| Clause not found | Refuse |
| Outside Delhi law | Refuse |
| Theft / FIR | Rights + procedure only |
| Missing document | Ask for upload |
| Ambiguous facts | Ask for clarification |

---

## 7. Why This Architecture Matters

Most legal bots fail because they:
- mix sources
- hallucinate clauses
- infer instead of citing
- answer outside jurisdiction

This system avoids all four by design.

It is built for:
- auditability
- reproducibility
- regulatory safety
- production deployment

---

## 8. Design Philosophy

> “Correct refusal is better than incorrect confidence.”

---

## 9. What This Demonstrates

- Regulatory AI architecture
- Data governance
- Source discipline
- Prompt constraint engineering
- Legal process modeling
- Rapid system design (built in 24 hours)
---

## Diagram

```text
DERC Website
   ↓
Scraper (PDF)
   ↓
Dedupe
   ↓
Text conversion
   ↓
Chunked corpus
   ↓
GPT Knowledge
   ↓
Instruction Guardrails
   ↓
Citation-first Answers

