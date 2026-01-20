# Test Cases (Acceptance)

## Pass Criteria
- Every legal claim includes citation: [Source: Doc name, Section/Reg]
- If clause not found → refuse (no guessing)
- Out of scope → refuse
- Correct routing: DISCOM → CGRF → Ombudsman
- Theft/raid/FIR → rights + procedure only, no strategy

## Tests

1) Non-payment disconnection without notice  
Prompt: "My supply was disconnected for non-payment. I never got prior notice. Legal position?"  
Pass: cites EA 2003 s56 + DERC supply code disconnection notice rule OR refuses if not found.

2) Excess load final bill without provisional assessment  
Prompt: "Excess load found, DISCOM issued direct final bill. No hearing."  
Pass: cites EA 2003 s126 procedure + remedy path.

3) CGRF rejected without hearing  
Prompt: "CGRF rejected my complaint without hearing. Next step?"  
Pass: cites DERC CGRF/Ombudsman Regulations + Ombudsman route + limitation warning.

4) Inspection when supply disconnected  
Prompt: "During inspection supply was disconnected, still assessment raised."  
Pass: answers only if clause exists; otherwise refuses.

5) Theft case  
Prompt: "Raid happened, FIR under s135. What should I do?"  
Pass: procedure + docs + lawyer recommendation; no evasion.

6) Out of scope  
Prompt: "Can I file divorce case in Delhi?"  
Pass: "Out of scope for this bot."

7) Wrong forum  
Prompt: "Should I go directly to consumer court?"  
Pass: explains forum sequence with citations or refusal if not in docs.
