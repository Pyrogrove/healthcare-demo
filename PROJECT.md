---
project_name: Hospital Flow Decision Lab
repository: https://github.com/Pyrogrove/healthcare-demo
project_type: Streamlit interview demonstration
lifecycle: candidate-retained-milestone
stack: Python 3.14, Streamlit, pandas, NumPy, Plotly, SQLite, pytest, base-R companion
tags: synthetic-healthcare, hospital-flow, ETL, SQL, forecasting, regression, R
deployment: streamlit-community-cloud
deployment_url: https://pyrogrove-healthcare-demo.streamlit.app/
last_verified: 2026-08-20
---

# Purpose
Demonstrate a problem-back analytics consulting pathway from trusted data to an owned intervention and measurable operational outcome.

# Current State
The R-companion six-section revision is locally verified, committed to GitHub `main`, and connected to the public Streamlit Community Cloud URL. The public endpoint returned HTTP 200 after the automatic rebuild; direct browser confirmation of the rendered revision remains unverified.

# Demonstrated Capabilities
Deterministic event generation; controlled defect detection and quarantine; raw-to-curated ETL; full and regression-ready downloads; simplified ADT-like and FHIR-style mappings; visible SQLite analysis; occupancy reconciliation; bottleneck analysis; transparent census forecasting; exploratory OLS, time-ordered holdout and permutation testing; educational base-R workflow translation; deterministic capacity arithmetic; and tiered accountable actions.

# Verification
On 2026-08-20: 20 tests passed, including deterministic holdout evaluation, export schemas, and base-R script structure. Python compilation, installed-package consistency, and Streamlit app rendering passed. The executed Python model uses 151 earlier training encounters and 65 later test encounters; its 1.97-hour MAE does not beat the 1.96-hour mean baseline and test R² is -0.024. R execution is UNVERIFIED because no R runtime is installed. Commit `c873051` was pushed to GitHub `main`, the remote head matched, and the public Streamlit endpoint returned HTTP 200 after rebuild. Direct browser confirmation is UNVERIFIED. Lint and static type checking remain UNVERIFIED because no tools are configured.

# Known Limitations
No live data, conformant standards server, executed R environment, validated prediction, validated simulation, causal inference, clinical validation, uncertainty intervals, production security model, or persistent storage. The regression fails its simple holdout-baseline comparison.

# Next Action
Use the public URL for a final human walkthrough and rehearse the documented five-minute storyline. Preserve the synthetic boundary and never commit or publish `GE material/`.

# Tool-native Instructions
Run `python -m pytest -q tests -p no:cacheprovider`, then `python -m streamlit run app.py`. Treat `GE material/` and `tmp/` as local-only artifacts.
