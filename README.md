# Hospital Flow Decision Lab

A locally runnable, independent interview demonstration for fictional Northstar General Hospital. It shows a senior analytics consulting pathway: frame a high-value operational problem, validate the data, separate false capacity pressure from real congestion, recommend an intervention, and define how success will be measured.

It is not a GE HealthCare product, Command Center replica, clinical tool, hospital deployment, or proof of production interoperability or predictive modelling.

## What it demonstrates

- 5,000 deterministic synthetic ADT-like events generated in memory
- a plausible 240-bed inventory with controlled integration defects
- executive-level problem framing and a prominent Reported-vs-Reconciled decision
- raw → validation → transformation → curated encounter ETL with visible defect handling
- simplified synthetic ADT-like and FHIR-style REST/JSON mappings
- four visible SQLite queries over the curated analytic table
- downloadable full curated and regression-ready synthetic datasets
- unit pressure and bottleneck analysis
- a transparent Holt census baseline, small OLS association example, time-ordered holdout evaluation, and exploratory permutation test
- a downloadable base-R translation of the regression workflow, explicitly not executed by the hosted app
- deterministic what-if capacity arithmetic and an action queue with owners and deadlines

## Architecture and setup

Python + Streamlit UI, pandas/NumPy pipeline, Plotly charts, standard-library SQLite, pytest tests, and an educational base-R companion script. SQLite is in-memory and R is not executed by the hosted application; there is no external API, persistent database, authentication, or production integration.

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Stop with `Ctrl+C`; restart with the same Streamlit command. The app defaults to `http://localhost:8501`.

## Deployment status

The canonical source repository is [Pyrogrove/healthcare-demo](https://github.com/Pyrogrove/healthcare-demo), connected to the public [Streamlit Community Cloud demonstration](https://pyrogrove-healthcare-demo.streamlit.app/). The R-companion enhancement was pushed in commit `c873051`; the public endpoint returned HTTP 200 after the automatic rebuild. Direct browser confirmation of the rendered revision remains unverified.

The local `GE material/` directory contains interview research artifacts and is explicitly excluded from version control and publication.

## Five-minute interview path

1. **Current State:** lead with 234 reported occupied beds versus 216 reconciled, then distinguish data distortion from persistent boarding.
2. **Data & ETL:** show raw → validate → transform → curate, clarify that the table is a 25-row preview, then show the full and regression-ready downloads.
3. **Forecast & Statistics:** explain the seven-day baseline, exploratory regression, failed holdout comparison, permutation test, and equivalent base-R workflow.
4. **What-if & Action:** change one assumption, interpret the result as deterministic arithmetic, and close on owner, deadline, success measure, and human decision.

See `INTERVIEW_DEMO_GUIDE.md` for exact wording, likely questions, and production limitations.

## Verification

On 2026-08-20, 20 tests passed, including the full/regression dataset contracts, deterministic time-ordered holdout, and required base-R workflow tokens. Python compilation, installed-package consistency, Streamlit startup, and application rendering were also checked. R execution is unverified because neither the local nor hosted environment has an R runtime. Direct browser confirmation remains subject to the state recorded in `PROJECT.md`; no lint or static type-check configuration exists.

## Data and privacy boundary

All records are fixed-seed and fictional. No names, MRNs, addresses, diagnoses, clinical results, or notes are generated. Event labels are illustrative; no HL7/FHIR/DICOM conformance or connectivity is claimed.

## Known limitations

Physical status is assumed trustworthy; occupancy is a unit-level snapshot rather than historical occupancy at encounter time; the synthetic forecast history and planning rates are constructed; readiness is a non-clinical scenario flag. The regression fails to beat its mean baseline. There is no executed R environment, production security, live integration, workflow write-back, validated model, validated simulation, or clinical validation.

## Conceptual inputs

The design was informed by the locally supplied GE HealthCare Command Center Executive Brief and Senior Analytics Consultant job description. Their concepts—problem-back design, Daily Operating Systems, tiered huddles, real-time data quality, actionable worklists, escalation, and measurement—were adapted into an original synthetic demonstration. No source interface, image, logo, proprietary data, or outcome claim is reproduced.

Public conceptual links:

- [GE HealthCare Command Center](https://www.gehealthcare.com/en-us/products/software/command-center)
- [GE HealthCare Research: census forecast and staffing](https://research.gehealthcare.com/across-the-enterprise/the-science-behind-ge-healthcares-command-center-census-forecast-and-staffing-helping-hospitals-predict-resource-needs-with-astonishing-accuracy-jb33676xx/)
- [HL7 FHIR R4B Encounter](https://hl7.org/fhir/R4B/encounter.html)
- [DICOM Standard](https://www.dicomstandard.org/)
