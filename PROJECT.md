---
project_name: Hospital Flow Decision Lab
repository: https://github.com/Pyrogrove/healthcare-demo
project_type: Streamlit interview demonstration
lifecycle: candidate-retained-milestone
stack: Python 3.14, Streamlit, pandas, Plotly, pytest
tags: synthetic-healthcare, hospital-flow, analytics-consulting, daily-operating-system
deployment: streamlit-community-cloud
deployment_url: https://pyrogrove-healthcare-demo.streamlit.app/
last_verified: 2026-08-19
---

# Purpose
Demonstrate a problem-back analytics consulting pathway from trusted data to an owned intervention and measurable operational outcome.

# Current State
Candidate retained milestone. The application is locally runnable at `http://localhost:8501`, committed to `https://github.com/Pyrogrove/healthcare-demo`, and publicly deployed at `https://pyrogrove-healthcare-demo.streamlit.app/`.

# Demonstrated Capabilities
Deterministic event generation, plausible bed inventory, controlled defect detection, occupancy reconciliation, unit pressure analysis, bottleneck decomposition, transparent scenario arithmetic, and tiered accountable actions.

# Verification
On 2026-08-19: 11 tests passed; Python compilation and installed-package consistency passed; the exact README run command started the app; all four workflows, controls, charts, central reveal, and local browser/HTTP paths were checked. Secret, sensitive-data, generated-junk, and large-file checks were performed on the intended source set. Lint and static type checking are UNVERIFIED because the project has no configured tools. GitHub commit `e290889` on `main` was verified, with `GE material/` excluded. The Streamlit Community Cloud deployment loaded all four workflows without browser alerts or console errors. Headline reconciliation: 234 reported - 216 reconciled = 18 phantom beds across 5,000 events and 240 fictional beds.

# Known Limitations
No live data, full standards messages, trained prediction, validated simulation, clinical validation, production security model, or persistent storage.

# Next Action
Use the live deployment for the interview demonstration. Preserve the synthetic boundary and never commit or publish `GE material/`.

# Tool-native Instructions
Run `python -m pytest -q tests -p no:cacheprovider`, then `python -m streamlit run app.py`. Treat `GE material/` and `tmp/` as local-only artifacts.
