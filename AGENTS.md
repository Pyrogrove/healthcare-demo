# Working Instructions

- Scope is the local synthetic Hospital Flow Decision Lab only.
- Source of truth: `src/generate_synthetic_data.py`, `src/pipeline.py`, `app.py`, and `tests/test_pipeline.py`.
- Run: `python -m streamlit run app.py`. Test: `python -m pytest -q`.
- Use only synthetic, fictional, non-identifying data. Never add real patient, staff, or hospital data.
- Do not silently weaken tests, requirements, validation rules, or the Reported-vs-Reconciled reveal.
- Do not deploy, publish, initialise or change Git, commit, push, or alter registries without Chee's approval.
- Never commit or publish `GE material/`; it contains interview research artifacts, not application source.
- Keep the accountable-owner and time-bound-action pathway visible.
