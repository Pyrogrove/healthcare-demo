# Interview Demo Guide

This guide supports a synthetic interview demonstration for a Senior Analytics Consultant / hospital command-center conversation. The demo uses fictional, deterministic data. It is not a GE HealthCare product, a clinical tool, a production integration, or evidence of real-world outcomes.

## Five-minute demonstration

1. **0:00–0:45 — Frame the decision.** On **Current State**, show 234 reported occupied beds versus 216 reconciled. Say that trusted data creates decision room but does not remove the real flow constraint: 92 boarders over four hours.
2. **0:45–1:45 — Establish the evidence chain.** On **Data & ETL**, walk through raw → validate → transform → curate. Point to missing acknowledgements, duplicates, invalid sequences, unmapped units, and late-arriving discharges. Explain quarantine versus retain-with-flag.
3. **1:45–2:25 — Show integration and SQL.** Open one FHIR-style REST/JSON mapping and the ADT-like mapping. State clearly that neither is a conformant server or full message. Select the occupancy SQL query and show that the result comes from the curated encounter table.
4. **2:25–3:40 — Explain the analytics.** On **Forecast & Statistics**, describe the seven-day Holt baseline, the small OLS association example, and the permutation test. Emphasize transparent assumptions, low explanatory power, exploratory interpretation, and no causal claim.
5. **3:40–5:00 — Move to action.** On **What-if & Action**, change projected admissions or discharge timing. Explain that forecast estimates a likely future while simulation asks what happens under chosen assumptions. End on the accountable queue: owner, next action, deadline, and success measure remain human-controlled.

## Technical areas

### Healthcare workflow

1. **What the demo does:** represents admissions, transfers, discharges, bed states, boarding, readiness, and escalation work.
2. **Technique:** deterministic ADT-like event lifecycles reconciled to physical bed state.
3. **Why useful:** connects technical records to capacity and patient-flow decisions.
4. **Limitations:** readiness and physical state are fictional scenario flags, not clinical facts.
5. **Production requirement:** workflow discovery with local clinical, operational, interface, privacy, and governance stakeholders.

### Data collection

1. **What the demo does:** ingests 5,000 fixed-seed synthetic events at event grain.
2. **Technique:** an in-memory pandas source table with event IDs, timestamps, interface status, location, and bed state.
3. **Why useful:** preserves source grain before aggregation and makes provenance discussable.
4. **Limitations:** no live feed, source latency distribution, authentication, or failure recovery.
5. **Production requirement:** secure connectors, source contracts, observability, replay, service-level expectations, and data ownership.

### Validation

1. **What the demo does:** detects missing acknowledgements, deterministic duplicates, invalid timestamp sequences, late discharge records, and unmapped units.
2. **Technique:** explicit Boolean rules and a documented duplicate key.
3. **Why useful:** prevents a visually convincing dashboard from hiding an untrustworthy fact base.
4. **Limitations:** rules cover only the controlled synthetic defects.
5. **Production requirement:** source-specific quality thresholds, reference-data stewardship, alerting, reconciliation, audit history, and exception workflows.

### ETL and transformation

1. **What the demo does:** moves raw events through validation and quarantine to a one-row-per-encounter curated table.
2. **Technique:** deterministic filtering, timestamp derivation, canonical naming, and encounter aggregation.
3. **Why useful:** separates source-message shape from the analytic model used by SQL and statistics.
4. **Limitations:** in-memory batch processing only; no incremental state, orchestration, or persistent lineage store.
5. **Production requirement:** idempotent jobs, checkpoints, late-data windows, schema evolution, lineage, access controls, and monitored recovery.

### Healthcare integration

1. **What the demo does:** maps one ADT-like pipe-delimited event and one FHIR-style Encounter REST/JSON payload into common fields.
2. **Technique:** small educational adapter functions.
3. **Why useful:** demonstrates the boundary between transport/source formats and the canonical patient-flow model.
4. **Limitations:** not complete HL7 v2, not a FHIR server, and not a conformance claim.
5. **Production requirement:** implementation guides, profiles, terminology, patient/encounter identity, acknowledgements, security, versioning, replay, and end-to-end conformance testing.

### SQL analysis

1. **What the demo does:** runs four visible queries for decision-to-bed time, occupancy, discharge before noon, and long boarding.
2. **Technique:** read-only SQLite over the curated encounter table.
3. **Why useful:** makes operational definitions reproducible and inspectable.
4. **Limitations:** small in-memory database with no indexing, concurrency, or governed semantic layer.
5. **Production requirement:** governed definitions, tested transformations, workload design, row-level security, performance engineering, and reconciliation to authoritative sources.

### Time-series forecasting

1. **What the demo does:** forecasts seven synthetic daily census values from 28 synthetic historical observations.
2. **Technique:** transparent Holt level-and-trend exponential smoothing with fixed alpha and beta.
3. **Why useful:** provides a simple baseline for discussing near-term capacity risk.
4. **Limitations:** generated history, short horizon, no intervals, no holidays or operational drivers, and no out-of-sample validation.
5. **Production requirement:** temporal holdouts, naive-baseline comparison, error by horizon and unit, prediction intervals, bias/drift monitoring, recalibration, and hospital-specific modelling.

### Regression and statistics

1. **What the demo does:** estimates the association of unit occupancy, recent admission volume, and acuity with boarding hours for current encounters.
2. **Technique:** ordinary least squares with standardized predictors and an intercept.
3. **Why useful:** demonstrates multivariable association and honest interpretation of a low R-squared.
4. **Limitations:** synthetic cross-sectional sample, omitted variables, clustered observations, and no causal design.
5. **Production requirement:** clinically and operationally justified features, diagnostics, uncertainty estimates, temporal validation, missing-data strategy, subgroup review, and causal methods if a causal question is asked.

### Hypothesis testing

1. **What the demo does:** compares mean boarding hours between higher- and lower-occupancy groups.
2. **Technique:** deterministic two-sided permutation test with the observed mean difference as the statistic.
3. **Why useful:** asks whether the displayed difference would be unusual if group labels were exchangeable.
4. **Limitations:** exploratory threshold, synthetic data, no adjustment for confounding or multiple comparisons.
5. **Production requirement:** pre-specified question, appropriate design and assumptions, confidence intervals, effect-size interpretation, power analysis, and operational context.

### What-if simulation

1. **What the demo does:** varies projected admissions and discharge-timing improvement over an eight-hour horizon.
2. **Technique:** deterministic capacity arithmetic from starting occupancy, admissions, expected discharges, and accelerated releases.
3. **Why useful:** exposes assumptions and separates a chosen intervention scenario from a prediction.
4. **Limitations:** no queues, length-of-stay distributions, uncertainty, unit constraints, staffing interactions, or validation.
5. **Production requirement:** calibrated distributions, pathway logic, resource constraints, sensitivity analysis, historical back-testing, expert validation, and controlled operational evaluation.

### Visualization and operational recommendation

1. **What the demo does:** presents reconciliation, unit pressure, forecast, scenario output, and an owned action queue.
2. **Technique:** a small set of Plotly charts and explicit owner/action/deadline/success-measure rules.
3. **Why useful:** keeps the decision and accountability pathway visible.
4. **Limitations:** accessibility, usability, alert burden, and real operating cadence have not been studied.
5. **Production requirement:** user research, role-based access, accessibility testing, workflow integration, alert governance, outcome measurement, and change management.

## Questions an interviewer may ask

### What is ETL?

Extract gets data from its source, transform validates and reshapes it into consistent definitions, and load makes the result available to a target such as an analytic table. In this demo the stages are in memory, but the separation is visible.

### How did you validate the data?

I used explicit rules for acknowledgement presence, a defined duplicate key, valid event ordering, approved unit mapping, and late-arrival status. Invalid or unmapped rows are quarantined; late records are retained with an audit flag when their event time remains useful.

### Why use SQL?

SQL makes metric definitions inspectable, repeatable, and portable across many analytic platforms. It is well suited to grouped operational questions over a curated table.

### What is the difference between forecasting and simulation?

A forecast estimates what is likely to happen from historical patterns. A simulation or what-if model estimates consequences under assumptions chosen by the analyst or operator. Here the Holt baseline is a forecast; the adjustable eight-hour capacity arithmetic is a what-if scenario.

### How would you validate a time-series model?

Use time-ordered holdouts or rolling-origin evaluation, compare against naive baselines, assess error by horizon and operational segment, inspect bias and prediction-interval coverage, and monitor drift after deployment. Never randomly mix future observations into training data.

### What does a p-value tell you?

Under the stated null model and assumptions, it is the probability of obtaining a statistic at least as extreme as the observed one.

### What does a p-value not tell you?

It does not give the probability that the hypothesis is true, prove causation, measure effect importance, validate data quality, or replace operational judgment.

### What is regression used for?

Regression estimates how an outcome varies with one or more predictors while holding the other included predictors constant. It can support description, prediction, or carefully designed causal analysis, but this demo uses it only for exploratory association.

### How would HL7 or FHIR data enter this pipeline?

An interface receives and authenticates a message or API request, validates its structure and identifiers, records transport and event time, maps source fields and terminology to a canonical schema, and sends failures to a monitored exception path. The two adapters here show only the mapping concept.

### How would you handle duplicate or late records?

Use a stable source identifier or deterministic business key for idempotency. Quarantine duplicates with lineage. For late records, preserve both event time and arrival time, recompute affected windows, and monitor lateness against the agreed service level.

### What happens when a source feed stops?

Freshness monitoring should alert the accountable support team, mark downstream data as stale, stop misleading automated decisions, preserve the last known state with a visible timestamp, investigate the interface, and replay safely after recovery.

### What if the forecast is wrong?

Show uncertainty, compare actuals with forecasts, monitor bias and error by horizon, keep fallback operating thresholds, recalibrate when needed, and ensure the human team can override the forecast using current operational evidence.

### How would this scale beyond the prototype?

Replace in-memory generation and SQLite with governed event ingestion, durable storage, tested incremental transformations, a canonical semantic layer, monitored model services, role-based applications, auditability, and formal release and support processes.

### What should remain a human decision?

Clinical readiness, patient placement, staffing trade-offs, escalation priority, resource allocation, and whether to act on a forecast must remain with accountable professionals. Analytics should make evidence, assumptions, uncertainty, ownership, and outcomes visible.

## What not to over-demonstrate

- Do not spend time explaining the OLS matrix calculation unless asked; focus on interpretation and limitations.
- Do not claim the p-value validates the operational hypothesis or proves high occupancy causes boarding.
- Do not describe the adapters as a working HL7/FHIR integration.
- Do not call the what-if arithmetic a digital twin or the census baseline a production model.
- Do not improvise claims about real hospitals, GE HealthCare methods, clinical outcomes, or deployment scalability.
