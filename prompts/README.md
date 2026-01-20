# Prompts / Guardrails (Delhi Electricity Law Bot)

This folder documents the instruction layer used in the GPT.

The goal is **compliance-grade behavior**:
- Delhi-only scope
- citation-first answers
- refusal when clause not found
- structured procedural guidance (DISCOM → CGRF → Ombudsman)
- safe handling for theft/raid/FIR cases

## Files to add here

### 1) system_instructions.md
Paste the full “Instructions” you set in GPT Builder (the final version with:
- SOURCE DISCIPLINE
- Mandatory citation format
- Output structure
- High-risk rules
- Refusal rules
)

### 2) test_cases.md
A small evaluation suite (10–25 prompts) with pass criteria:
- Every legal claim has citation
- Refuses when missing clause
- Correct forum routing
- Theft/raid → procedure only, no strategy

### 3) release_notes.md (optional)
Track changes to instructions by date:
- what changed
- why changed
- what test it fixed

## Why this matters
In regulated domains, the “prompt layer” is effectively a **policy + safety spec**.
This repo treats it like production documentation, not hidden magic.
