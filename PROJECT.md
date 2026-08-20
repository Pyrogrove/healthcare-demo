---
project_name: Hospital Flow Decision Lab
repository: https://github.com/Pyrogrove/healthcare-demo
project_type: Streamlit interview demonstration
lifecycle: candidate-retained-milestone
stack: Python 3.14, Streamlit, pandas, NumPy, Plotly, SQLite, pytest
tags: synthetic-healthcare, hospital-flow, ETL, SQL, forecasting, simulation
deployment: streamlit-community-cloud
deployment_url: https://pyrogrove-healthcare-demo.streamlit.app/
last_verified: 2026-08-20
---

# Purpose
Demonstrate a problem-back analytics consulting pathway from trusted data to an owned intervention and measurable operational outcome.

# Current State
The enhanced six-section working copy is locally runnable at `http://localhost:8501`. It has not been committed, pushed, or deployed. The GitHub repository and `streamlit.app` URL still represent the previous retained milestone.

# Demonstrated Capabilities
Deterministic event generation; controlled defect detection and quarantine; raw-to-curated ETL; simplified ADT-like and FHIR-style mappings; visible SQLite analysis; occupancy reconciliation; bottleneck analysis; transparent census forecasting; exploratory OLS and permutation testing; deterministic capacity what-if arithmetic; and tiered accountable actions.

# Verification
On 2026-08-20: 17 tests passed; Python compilation and installed-package consistency passed; the exact README run command started the app; Streamlit's app test runner rendered all six sections, two sliders, and the SQL selector without an application exception. The intended eight-file change set passed diff, credential-pattern, ignored-secret-file, generated-junk, and file-size checks; no repository secret scanner is configured. Direct browser rendering of the enhanced local copy is UNVERIFIED because browser control was unavailable. Lint and static type checking remain UNVERIFIED because no tools are configured. The public deployment was not changed. Headline reconciliation remains 234 reported - 216 reconciled = 18 phantom beds across 5,000 events and 240 fictional beds.

# Known Limitations
No live data, conformant standards messages or server, trained production prediction, validated simulation, causal inference, clinical validation, uncertainty intervals, production security model, or persistent storage.

# Next Action
Chee reviews the local five-minute demo. Only after explicit approval should the retained-milestone gate, commit, push, or deployment run. Never commit or publish `GE material/`.

# Tool-native Instructions
Run `python -m pytest -q tests -p no:cacheprovider`, then `python -m streamlit run app.py`. Treat `GE material/` and `tmp/` as local-only artifacts.
