# Demo Talk Track

## 20-second reveal

“The reported census says 234 of 240 beds are occupied—97.5%, apparently a physical-capacity crisis. Reconciliation shows 18 are stale system states, so true occupancy is 216, or 90%. That correction matters, but it does not explain away the 92 boarders waiting over four hours. The recommendation is therefore two-track: fix the fact base within one hour and run a tiered flow huddle against the real constraints.”

## Two-minute demonstration

1. **Lead with the executive conclusion.** Point to 234 reported, minus 18 phantom states, equals 216 reconciled. State the decision request: a one-hour reconciliation sprint plus an owned flow intervention.
2. **Diagnose, do not decorate.** In Flow Diagnosis, show which units combine high occupancy, long-wait boarders, and discharge-ready opportunity. Explain that false capacity pressure and genuine congestion coexist.
3. **Test the operational hypothesis.** Use the eight-hour planning scenario. Current-practice arithmetic reaches 232 occupied beds; completing owned actions yields 220. Say plainly that these are transparent assumptions, not a trained forecast.
4. **Show the operating mechanism.** In Daily Operating System, move through unit rounds, service queues, tiered huddle, and central escalation. Each action has evidence, one owner, a deadline, and a success measure.
5. **Close on consulting discipline.** “The screen is not the outcome. Value comes from a trusted fact base, a different action at a critical moment, and evidence that the intervention improved flow.”

## Likely technical questions

1. **Is this real HL7?** No. It uses plausible ADT event labels but does not construct messages or claim conformance.
2. **How is reproducibility assured?** A fixed seed, fixed as-of time, fixed 240-bed master, and automated tests produce the same scenario.
3. **How are duplicates found?** A deterministic composite key of encounter, timestamp, message type, unit, and bed.
4. **How is phantom occupancy defined?** A current bed is system-occupied while its physical state is available.
5. **Is the planning curve predictive modelling?** No. It is visible arithmetic using stated arrival and release rates. A production forecast would require local history, validation, error tracking, and governance.

## Likely stakeholder questions

1. **Should we trust the 18 beds immediately?** No. They form a prioritized confirmation worklist; Bed Management must verify and close each stale encounter.
2. **What changes operationally?** The next huddle uses reconciled capacity, prioritizes units by pressure and ready cohorts, and escalates missed deadlines.
3. **How do we know this worked?** Compare census agreement, time-to-close after physical discharge, boarders over four hours, and action completion with the pre-intervention baseline.

## What this prototype does not prove

It does not prove clinical validity, production readiness, predictive accuracy, validated simulation, real-time interoperability, standards conformance, deployment security, official affiliation, or outcomes in a real hospital.
