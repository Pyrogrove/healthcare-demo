# Hospital Flow Decision Lab

A locally runnable, independent interview demonstration for fictional Northstar General Hospital. It shows a senior analytics consulting pathway: frame a high-value operational problem, validate the data, separate false capacity pressure from real congestion, recommend an intervention, and define how success will be measured.

It is not a GE HealthCare product, Command Center replica, clinical tool, hospital deployment, or proof of production interoperability or predictive modelling.

## What it demonstrates

- 5,000 deterministic synthetic ADT-like events generated in memory
- a plausible 240-bed inventory with controlled integration defects
- executive-level problem framing and a prominent Reported-vs-Reconciled decision
- unit pressure analysis and bottleneck decomposition
- transparent near-term planning arithmetic, explicitly not a trained forecast
- a tiered Daily Operating System with evidence, accountable owners, deadlines, and success measures

## Architecture and setup

Python + Streamlit UI, pandas pipeline, Plotly charts, and pytest tests. No database, external API, machine learning, authentication, or cloud configuration.

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Stop with `Ctrl+C`; restart with the same Streamlit command. The app defaults to `http://localhost:8501`.

## Deployment status

The canonical source repository is [Pyrogrove/healthcare-demo](https://github.com/Pyrogrove/healthcare-demo). There is not yet a hosted deployment. A public Streamlit runtime requires a separate Streamlit Community Cloud deployment connected to the repository. `app.py` is the intended entrypoint and `requirements.txt` is at the repository root; cloud compatibility and the final `streamlit.app` URL remain unverified until deployment completes.

The local `GE material/` directory contains interview research artifacts and is explicitly excluded from version control and publication.

## Two-minute interview path

1. **Executive Brief:** state the conclusion first—97.5% reported occupancy becomes 90.0% after removing 18 phantom states, but 92 long-wait boarders prove real congestion remains.
2. **Flow Diagnosis:** show which units carry pressure, decompose the bottlenecks, then test the owned-action scenario without claiming a forecast.
3. **Daily Operating System:** move from a unit round to service queues, tiered huddle, central escalation, and outcome measurement.
4. **Evidence & Method:** trace every conclusion back through validation and reconciliation rules; close on assumptions and what the prototype does not prove.

## Verification

On 2026-08-19, 11 tests passed, Python compilation completed, installed-package consistency passed, the exact Streamlit command started the application, and the local HTTP/browser workflow was checked. No lint or static type-check configuration exists, so those checks are unverified rather than claimed. See `PROJECT.md` for retained evidence.

## Data and privacy boundary

All records are fixed-seed and fictional. No names, MRNs, addresses, diagnoses, clinical results, or notes are generated. Event labels are illustrative; no HL7/FHIR/DICOM conformance or connectivity is claimed.

## Known limitations

Physical status is assumed trustworthy; the as-of time and planning rates are fixed; readiness is a non-clinical scenario flag. There is no production security, live integration, workflow write-back, trained prediction, validated simulation, or clinical validation.

## Conceptual inputs

The design was informed by the locally supplied GE HealthCare Command Center Executive Brief and Senior Analytics Consultant job description. Their concepts—problem-back design, Daily Operating Systems, tiered huddles, real-time data quality, actionable worklists, escalation, and measurement—were adapted into an original synthetic demonstration. No source interface, image, logo, proprietary data, or outcome claim is reproduced.

Public conceptual links:

- [GE HealthCare Command Center](https://www.gehealthcare.com/en-us/products/software/command-center)
- [GE HealthCare Research: census forecast and staffing](https://research.gehealthcare.com/across-the-enterprise/the-science-behind-ge-healthcares-command-center-census-forecast-and-staffing-helping-hospitals-predict-resource-needs-with-astonishing-accuracy-jb33676xx/)
- [HL7 FHIR R4B Encounter](https://hl7.org/fhir/R4B/encounter.html)
- [DICOM Standard](https://www.dicomstandard.org/)
