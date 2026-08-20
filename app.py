from __future__ import annotations

import importlib
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.generate_synthetic_data import AS_OF, generate_events
from src import pipeline as _pipeline

# Streamlit Cloud may rerun app.py in an existing interpreter after a deploy.
# If app.py and an already-imported pipeline module come from different
# revisions, refresh the module once before binding the public functions.
_PIPELINE_FUNCTIONS = (
    "boarding_hypothesis_test", "build_actions", "build_curated_encounters",
    "capacity_what_if", "census_forecast", "map_adt_like",
    "map_fhir_encounter", "reconcile", "regression_holdout_evaluation",
    "regression_ready_dataset", "regression_summary", "sql_examples",
    "unit_summary",
)
if any(not hasattr(_pipeline, name) for name in _PIPELINE_FUNCTIONS):
    importlib.invalidate_caches()
    _pipeline = importlib.reload(_pipeline)

(
    boarding_hypothesis_test, build_actions, build_curated_encounters,
    capacity_what_if, census_forecast, map_adt_like, map_fhir_encounter,
    reconcile, regression_holdout_evaluation, regression_ready_dataset,
    regression_summary, sql_examples, unit_summary,
) = (getattr(_pipeline, name) for name in _PIPELINE_FUNCTIONS)

st.set_page_config(page_title="Hospital Flow Decision Lab", page_icon="◆", layout="wide")
st.markdown("""<style>
:root{--ink:#14212b;--teal:#007f7b;--blue:#1d4e89;--line:#dce3e8;--wash:#f5f8fa}
.block-container{padding-top:1.2rem;max-width:1450px}.stApp{color:var(--ink)}
.eyebrow{font-size:.76rem;letter-spacing:.12em;text-transform:uppercase;color:var(--teal);font-weight:750}
.boundary{background:#fff7e6;border:1px solid #f3d19c;padding:10px 14px;border-radius:7px;font-size:.86rem}
.decision{background:#102f47;color:white;padding:20px 24px;border-radius:12px;margin:14px 0 18px;border-left:7px solid #23b5aa}
.decision h2{font-size:1.45rem;margin:0 0 8px}.decision p{margin:0;color:#e4edf3;font-size:1rem}
.callout{background:#edf7f6;border-left:5px solid var(--teal);padding:14px 18px;border-radius:7px;margin:10px 0}
.method{background:var(--wash);border:1px solid var(--line);padding:14px 16px;border-radius:9px;min-height:112px}
.path{display:flex;gap:7px;align-items:stretch;margin:12px 0;flex-wrap:wrap}.path div{flex:1;min-width:130px;padding:11px;border:1px solid var(--line);border-radius:8px;background:white}.path b{display:block;color:var(--blue);margin-bottom:4px}.arrow{display:flex!important;align-items:center;justify-content:center;flex:0!important;min-width:18px!important;border:0!important;background:transparent!important}
div[data-testid="stMetric"]{background:white;border:1px solid var(--line);padding:12px 14px;border-radius:9px}
</style>""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    events = generate_events()
    latest, metrics = reconcile(events)
    curated, audit = build_curated_encounters(events)
    return events, latest, metrics, curated, audit, unit_summary(events), build_actions(events)


events, latest, metrics, curated, audit, units, actions = load_data()
regression_data = regression_ready_dataset(curated)
r_script_path = Path(__file__).parent / "analysis" / "hospital_flow_regression.R"
r_script_text = r_script_path.read_text(encoding="utf-8")

st.markdown('<div class="eyebrow">Synthetic data → operational decision · interview demonstration</div>', unsafe_allow_html=True)
st.title("Hospital Flow Decision Lab")
st.caption(f"Northstar General Hospital · fictional operational snapshot · {AS_OF:%d %b %Y, %H:%M}")
st.markdown('<div class="boundary"><b>Boundary:</b> synthetic, non-identifying data only. Educational prototype—not a GE HealthCare product, clinical tool, validated digital twin, production integration, or production forecast.</div>', unsafe_allow_html=True)
st.markdown(f'''<div class="decision"><h2>Reported capacity pressure contains both a data defect and a real flow constraint.</h2><p>Reconciliation changes occupied beds from <b>{metrics['reported_occupied']}</b> to <b>{metrics['reconciled_occupied']}</b>, releasing <b>{metrics['phantom_occupancy']} false occupied states</b>. Human operators still need to act on <b>{metrics['ed_boarders_over_4h']} boarders over four hours</b> and the <b>{metrics['discharge_ready']} discharge-ready cohort</b>.</p></div>''', unsafe_allow_html=True)

tabs = st.tabs(["1 · CURRENT STATE", "2 · DATA & ETL", "3 · BOTTLENECKS", "4 · FORECAST & STATISTICS", "5 · WHAT-IF & ACTION", "6 · ROLE MAP"])

with tabs[0]:
    st.subheader("Current Operational State")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Staffed beds", metrics["bed_capacity"])
    c2.metric("Reported occupancy", f'{metrics["reported_occupancy_pct"]:.1f}%')
    c3.metric("Reconciled occupancy", f'{metrics["reconciled_occupancy_pct"]:.1f}%', delta=f'-{metrics["phantom_occupancy"]} false occupied')
    c4.metric("Boarders >4h", metrics["ed_boarders_over_4h"])
    left, right = st.columns([1.05, 1], gap="large")
    with left:
        chart = go.Figure(go.Waterfall(
            measure=["absolute", "relative", "total"],
            x=["Reported occupied", "Remove phantom states", "Reconciled occupied"],
            y=[metrics["reported_occupied"], -metrics["phantom_occupancy"], metrics["reconciled_occupied"]],
            text=[str(metrics["reported_occupied"]), f'-{metrics["phantom_occupancy"]}', str(metrics["reconciled_occupied"])],
            decreasing={"marker": {"color": "#23a39b"}}, totals={"marker": {"color": "#1d4e89"}},
        ))
        chart.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20), yaxis_title="Beds", showlegend=False)
        st.plotly_chart(chart, width="stretch")
    with right:
        st.markdown("#### Recommended Operational Attention")
        st.markdown(f"""
1. **By 11:00 — Bed Management:** close the {metrics['phantom_occupancy']} verified stale encounters.
2. **Next huddle — Hospital Operations:** assign a placement plan for boarders over four hours.
3. **By 14:00 — Nursing Units:** resolve or escalate barriers for {metrics['discharge_ready']} discharge-ready encounters.
4. **Measure:** census agreement, long-wait boarders, and action closure by deadline.
""")
        st.markdown('<div class="callout"><b>Human decision:</b> leaders choose priorities and approve action. The analysis supplies evidence; it does not make clinical discharge or placement decisions.</div>', unsafe_allow_html=True)

with tabs[1]:
    st.subheader("Data Quality, ETL, Integration, and SQL")
    st.markdown('''<div class="path"><div><b>Raw</b>5,000 ADT-like events</div><div class="arrow">→</div><div><b>Validate</b>Rules and quarantine</div><div class="arrow">→</div><div><b>Transform</b>Canonical fields</div><div class="arrow">→</div><div><b>Curate</b>One row per encounter</div><div class="arrow">→</div><div><b>Analyze</b>SQL and KPIs</div></div>''', unsafe_allow_html=True)
    stages = pd.DataFrame([
        ["Raw", audit["raw_rows"], "Retain source record and event time"],
        ["Validated", audit["validated_rows"], "Flag every deterministic rule"],
        ["Accepted events", audit["accepted_event_rows"], "Quarantine invalid rows"],
        ["Curated encounters", audit["curated_encounters"], "Aggregate to canonical encounter grain"],
    ], columns=["Stage", "Rows", "Handling"])
    st.dataframe(stages, width="stretch", hide_index=True)
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Duplicates quarantined", audit["duplicate_rows_quarantined"])
    q2.metric("Invalid sequence", audit["invalid_sequence_rows_quarantined"])
    q3.metric("Unmapped rows", audit["unmapped_rows_quarantined"])
    q4.metric("Late rows retained + flagged", audit["late_rows_retained_with_flag"])
    handling = pd.DataFrame([
        ["Missing acknowledgement", audit["missing_ack_rows_flagged"], "Retain with flag; investigate delivery/replay"],
        ["Duplicate event", audit["duplicate_rows_quarantined"], "Keep first deterministic key; quarantine repeats"],
        ["Invalid timestamp sequence", audit["invalid_sequence_rows_quarantined"], "Quarantine; preserve audit evidence"],
        ["Late-arriving discharge", audit["late_rows_retained_with_flag"], "Use event time; retain late-arrival flag"],
        ["Unmapped unit", audit["unmapped_rows_quarantined"], "Quarantine until reference mapping is fixed"],
    ], columns=["Data issue", "Rows", "Treatment"])
    st.dataframe(handling, width="stretch", hide_index=True)
    with st.expander("View curated analytic dataset preview"):
        shown = ["patient_id", "encounter_id", "unit", "admission_time", "decision_to_admit_time", "bed_request_time", "bed_assigned_time", "transfer_time", "expected_discharge_time", "actual_discharge_time", "bed_status", "staffed_beds", "occupancy", "patient_acuity"]
        st.dataframe(curated[shown].head(25), width="stretch", hide_index=True)
        st.caption(f"Preview only: 25 of {len(curated):,} curated encounters and 14 selected fields.")
    d1, d2 = st.columns(2)
    d1.download_button(
        "Download full curated dataset",
        curated.to_csv(index=False, date_format="%Y-%m-%d %H:%M:%S").encode("utf-8"),
        file_name="hospital_flow_curated.csv",
        mime="text/csv",
        help=f"All {len(curated):,} encounters and {len(curated.columns)} fields used across the demonstration.",
        width="stretch",
    )
    d2.download_button(
        "Download regression-ready dataset",
        regression_data.to_csv(index=False, date_format="%Y-%m-%d %H:%M:%S").encode("utf-8"),
        file_name="hospital_flow_regression_ready.csv",
        mime="text/csv",
        help=f"The {len(regression_data)} current occupied encounters and explicit predictors used by the regression examples.",
        width="stretch",
    )
    with st.expander("Dataset grain and compact codebook"):
        st.markdown(f"""
- **Raw grain:** one source event; {audit['raw_rows']:,} rows before validation.
- **Curated grain:** one encounter; {len(curated):,} rows after quarantine and transformation.
- **Regression grain:** one currently occupied encounter; {len(regression_data)} rows.
- **Outcome:** `boarding_hours` — synthetic boarding duration in hours.
- **Predictors:** `occupancy` — current unit-level snapshot ratio; `admission_volume_24h` — recent valid admissions by unit; `acuity_score` — low=1, moderate=2, high=3.
- **Important limitation:** the occupancy value is a snapshot, not historical occupancy reconstructed at each encounter timestamp.
""")

    st.markdown("#### Simplified synthetic healthcare integration")
    i1, i2 = st.columns(2)
    fhir_example = {"resourceType": "Encounter", "id": "ENC-DEMO-01", "status": "in-progress", "subject": {"reference": "Patient/PAT-SYN-DEMO"}, "period": {"start": "2026-08-19T08:15:00"}, "location": [{"location": {"display": "North-1"}}]}
    adt_example = "EVENT=A01|PID=PAT-SYN-DEMO|ENC=ENC-DEMO-02|UNIT=South-1|TIME=2026-08-19T08:20:00"
    with i1:
        st.caption("FHIR-style Encounter through a REST/JSON endpoint")
        st.code(json.dumps(fhir_example, indent=2), language="json")
        st.json(map_fhir_encounter(fhir_example))
    with i2:
        st.caption("ADT-like event—not a complete HL7 v2 message")
        st.code(adt_example)
        st.json(map_adt_like(adt_example))
    st.caption("Production interfaces require profiles, identity and terminology controls, acknowledgements, replay, security, observability, and source-specific testing.")

    st.markdown("#### Visible SQL analysis (SQLite in memory)")
    outputs = sql_examples(curated)
    choice = st.selectbox("Choose a query", [item["title"] for item in outputs])
    selected = next(item for item in outputs if item["title"] == choice)
    st.code(selected["query"], language="sql")
    st.dataframe(selected["result"], width="stretch", hide_index=True)

with tabs[2]:
    st.subheader("Patient Flow Bottlenecks")
    p1, p2, p3 = st.columns(3)
    p1.metric("Boarders >4h", metrics["ed_boarders_over_4h"])
    p2.metric("Discharge-ready", metrics["discharge_ready"], help="Scenario flag only; not a clinical decision")
    p3.metric("Dirty available beds", metrics["dirty_available"])
    plot_units = units.copy()
    plot_units["Reconciled occupancy %"] = plot_units["Reconciled"] / plot_units["Capacity"] * 100
    pressure = px.scatter(plot_units, x="Reconciled occupancy %", y="ED_boarders", size="Discharge_ready", color="Phantom", text="unit", hover_data=["Reported", "Reconciled", "Clean_available"], color_continuous_scale=["#d7efed", "#007f7b"], size_max=34)
    pressure.update_traces(textposition="top center")
    pressure.add_vline(x=90, line_dash="dash", line_color="#9aa8b2")
    pressure.update_layout(height=410, margin=dict(l=10, r=10, t=20, b=20), coloraxis_colorbar_title="Phantom")
    st.plotly_chart(pressure, width="stretch")
    st.dataframe(units, width="stretch", hide_index=True)
    st.caption("Descriptive prioritization only; this view does not prescribe a bed assignment.")

with tabs[3]:
    st.subheader("Forecast, Regression, and Exploratory Hypothesis Test")
    forecast = census_forecast(events, horizon=7)
    forecast_chart = px.line(forecast, x="date", y="census", color="series", markers=True, color_discrete_map={"Historical actual": "#1d4e89", "Baseline forecast": "#d97706"})
    forecast_chart.add_hline(y=228, line_dash="dash", annotation_text="95% staffed capacity", line_color="#b42318")
    forecast_chart.update_layout(height=360, margin=dict(l=20, r=20, t=15, b=20), legend_title="")
    st.plotly_chart(forecast_chart, width="stretch")
    st.caption("Seven-day transparent Holt level-and-trend baseline (α=0.35, β=0.15) over 28 synthetic observations—not GE methodology or a production forecast.")
    r1, r2 = st.columns(2, gap="large")
    regression, regression_meta = regression_summary(curated)
    with r1:
        st.markdown("#### Small OLS regression illustration")
        st.dataframe(regression, width="stretch", hide_index=True)
        st.write(f'Current encounters: **{regression_meta["sample_size"]}** · R²: **{regression_meta["r_squared"]:.3f}**')
        st.caption("Coefficients show association per one-standard-deviation increase, holding displayed variables constant. Low R² means little variation is explained; association is not causation.")
        predictions, holdout = regression_holdout_evaluation(curated)
        st.markdown("##### Time-ordered holdout check")
        m1, m2, m3 = st.columns(3)
        m1.metric("Test model MAE", f'{holdout["model_mae"]:.2f}h')
        m2.metric("Mean baseline MAE", f'{holdout["baseline_mae"]:.2f}h')
        m3.metric("Test R²", f'{holdout["test_r_squared"]:.3f}')
        verdict = "The model beats the simple baseline." if holdout["beats_baseline"] else "The model does not beat the simple baseline."
        st.caption(f'{holdout["split_rule"]}: {holdout["training_rows"]} train and {holdout["test_rows"]} test rows. {verdict} This is an honest stop/revise signal, not a model to operationalize.')
    test = boarding_hypothesis_test(curated)
    with r2:
        st.markdown("#### Exploratory permutation test")
        h1, h2, h3 = st.columns(3)
        h1.metric("High occupancy", f'{test["high_mean"]:.2f}h')
        h2.metric("Lower occupancy", f'{test["lower_mean"]:.2f}h')
        h3.metric("p-value", f'{test["p_value"]:.4f}')
        st.write(f'Mean-difference statistic: **{test["test_statistic"]:+.2f}h**. High occupancy >{test["threshold_pct"]:.1f}% (n={test["high_n"]}); lower n={test["lower_n"]}.')
        conclusion = "The result is below 0.05 under this synthetic permutation test." if test["p_value"] < 0.05 else "The result is not below 0.05; no reliable group difference is established."
        st.caption(conclusion + " A p-value does not prove causation or measure operational importance.")
    st.info("Production forecasting requires temporal holdouts, baseline comparisons, error by horizon/unit, bias and drift monitoring, recalibration, and hospital-specific review.")
    with st.expander("R companion: the same regression workflow in base R", expanded=True):
        st.markdown("""
**Purpose:** demonstrate fundamental R workflow literacy and portability of the analytic question.

**Execution boundary:** the deployed Streamlit app executes the Python model. It displays and downloads this base-R companion, but does not execute R; no R runtime is installed in the hosting environment.

Workflow: `read.csv()` → validate required fields → filter with `subset()` → create features → time-order the data → fit `lm()` → score with `predict()` → compare MAE with a mean baseline.
""")
        st.code(r_script_text, language="r")
        st.download_button("Download base-R companion script", r_script_text.encode("utf-8"),
                           file_name="hospital_flow_regression.R", mime="text/plain")
        st.caption("Interview wording: Python is the implemented runtime; this script demonstrates an equivalent, reviewable R workflow—not professional R experience or a production model.")

with tabs[4]:
    st.subheader("Deterministic What-if Scenario and Owned Action")
    s1, s2 = st.columns(2)
    projected_admissions = s1.slider("Projected admissions in next 8 hours", 10, 50, 30)
    timing_improvement = s2.slider("Expected discharge timing improvement", 0, 50, 25, step=5)
    expected_discharges = 24
    scenario = capacity_what_if(events, projected_admissions, expected_discharges, timing_improvement)
    st.caption(f"Fixed assumption: {expected_discharges} expected discharges. Improvement releases {scenario['accelerated_discharges']} additional beds within the horizon.")
    w1, w2, w3, w4 = st.columns(4)
    w1.metric("Starting occupied", scenario["starting_occupied"])
    w2.metric("Current-practice result", scenario["baseline_occupied"])
    w3.metric("Improved-timing result", scenario["scenario_occupied"], delta=f'-{scenario["accelerated_discharges"]} beds')
    w4.metric("Scenario occupancy", f'{100 * scenario["scenario_occupied"] / scenario["staffed_beds"]:.1f}%')
    scenario_frame = pd.DataFrame({"Scenario": ["Current practice", "Improved discharge timing"], "Occupied beds": [scenario["baseline_occupied"], scenario["scenario_occupied"]]})
    scenario_chart = px.bar(scenario_frame, x="Scenario", y="Occupied beds", color="Scenario", text="Occupied beds", color_discrete_map={"Current practice": "#b42318", "Improved discharge timing": "#007f7b"})
    scenario_chart.add_hline(y=scenario["staffed_beds"], line_dash="dash", annotation_text="Staffed beds")
    scenario_chart.update_layout(height=330, showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(scenario_chart, width="stretch")
    st.markdown('<div class="callout"><b>Interpretation:</b> one-horizon arithmetic, not a validated digital twin. Operators can challenge assumptions before deciding what is feasible.</div>', unsafe_allow_html=True)
    st.markdown("#### Accountable operational queue")
    st.dataframe(actions.head(18), width="stretch", hide_index=True, height=420, column_config={"Escalation deadline": st.column_config.DatetimeColumn(format="DD MMM, HH:mm")})

with tabs[5]:
    st.subheader("How this maps to the Senior Analytics Consultant role")
    role_map = pd.DataFrame([
        ["Healthcare workflow", "ADT events, beds, boarding, discharge readiness, huddles", "Translate workflow into measurable states"],
        ["Data collection", "Synthetic event feed and REST/JSON example", "Identify source, grain, timing, ownership"],
        ["Validation", "ACK, duplicate, sequence, late, and mapping rules", "Establish trust before analysis"],
        ["ETL", "Raw → validate → transform → curated", "Create a traceable analytic table"],
        ["SQL", "Four visible SQLite queries", "Answer reproducible questions"],
        ["Analytics", "KPIs, OLS association, permutation test", "Describe and test focused patterns"],
        ["Forecasting", "Seven-day Holt baseline", "Anticipate pressure with explicit limits"],
        ["Simulation", "Eight-hour deterministic arithmetic", "Explore assumptions separately from prediction"],
        ["Visualization", "Reconciliation, pressure, forecast, scenario", "Put decisions ahead of chart volume"],
        ["Integration", "Simplified ADT-like and FHIR-style mappings", "Normalize messages to a canonical model"],
        ["Recommendation", "Owner, action, deadline, success measure", "Move from insight to human action"],
    ], columns=["Role area", "Visible evidence", "Consulting purpose"])
    st.dataframe(role_map, width="stretch", hide_index=True)
    st.markdown("#### Defensible closing statement")
    st.markdown('''<div class="method"><b>What I would say:</b><br>“This prototype shows how I structure a hospital-flow question: establish trustworthy data, normalize it to an analytic model, use explainable methods to separate data distortion from operational pressure, then give accountable operators evidence and transparent scenarios. I would not present these synthetic results as clinically validated or production-ready.”</div>''', unsafe_allow_html=True)
    st.markdown("See `INTERVIEW_DEMO_GUIDE.md` for the five-minute path, interview answers, and limitations.")
