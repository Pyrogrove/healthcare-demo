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
- unit pressure and bottleneck analysis
- a transparent Holt census baseline, small OLS association example, and exploratory permutation test
- deterministic what-if capacity arithmetic and an action queue with owners and deadlines

## Architecture and setup

Python + Streamlit UI, pandas/NumPy pipeline, Plotly charts, standard-library SQLite, and pytest tests. SQLite is in-memory for demonstration; there is no external API, persistent database, authentication, or production integration.

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Stop with `Ctrl+C`; restart with the same Streamlit command. The app defaults to `http://localhost:8501`.

## Deployment status

The canonical source repository is [Pyrogrove/healthcare-demo](https://github.com/Pyrogrove/healthcare-demo). The enhanced milestone is committed on `main` and connected to the public [Streamlit Community Cloud demonstration](https://pyrogrove-healthcare-demo.streamlit.app/). After the push, the public endpoint returned HTTP 200; browser-level confirmation that all six enhanced sections are rendered remains unverified.

The local `GE material/` directory contains interview research artifacts and is explicitly excluded from version control and publication.

## Five-minute interview path

1. **Current State:** lead with 234 reported occupied beds versus 216 reconciled, then distinguish data distortion from persistent boarding.
2. **Data & ETL:** show raw → validate → transform → curate, one defect-handling example, one simplified integration mapping, and one SQL query.
3. **Forecast & Statistics:** explain the transparent seven-day baseline, low-powered exploratory regression, and what the permutation-test p-value does not prove.
4. **What-if & Action:** change one assumption, interpret the result as deterministic arithmetic, and close on owner, deadline, success measure, and human decision.

See `INTERVIEW_DEMO_GUIDE.md` for exact wording, likely questions, and production limitations.

## Verification

On 2026-08-20, 17 tests passed, Python compilation completed, installed-package consistency passed, the exact Streamlit command started the application, and Streamlit's app test runner rendered all six tabs and interactive controls with no application exception. The intended change set passed credential, ignored-file, generated-junk, size, and diff checks before commit. GitHub `main` and the public Streamlit endpoint were reachable after push. Direct browser confirmation of the deployed six-section interface remains unverified because the browser-control connection was unavailable. No lint or static type-check configuration exists. See `PROJECT.md` for the state boundary.

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
