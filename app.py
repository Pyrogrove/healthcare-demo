from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.generate_synthetic_data import AS_OF, generate_events
from src.pipeline import build_actions, planning_scenario, reconcile, unit_summary, validate_events

st.set_page_config(page_title="Hospital Flow Decision Lab", page_icon="◆", layout="wide")
st.markdown("""<style>
:root{--ink:#14212b;--muted:#5f6c76;--teal:#007f7b;--blue:#1d4e89;--orange:#d97706;--red:#b42318;--line:#dce3e8;--wash:#f5f8fa}
.block-container{padding-top:1.25rem;max-width:1450px}.stApp{color:var(--ink)}
.eyebrow{font-size:.76rem;letter-spacing:.12em;text-transform:uppercase;color:var(--teal);font-weight:750}
.boundary{background:#fff7e6;border:1px solid #f3d19c;padding:10px 14px;border-radius:7px;font-size:.86rem}
.decision{background:#102f47;color:white;padding:22px 26px;border-radius:12px;margin:14px 0 18px;border-left:7px solid #23b5aa}
.decision h2{font-size:1.55rem;margin:0 0 8px}.decision p{margin:0;color:#e4edf3;font-size:1.02rem}
.fact-card{border:1px solid var(--line);border-radius:10px;padding:16px 18px;min-height:142px;background:white}
.fact-card .label{font-size:.75rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-weight:700}
.fact-card .value{font-size:1.65rem;font-weight:760;margin:5px 0}.fact-card .copy{font-size:.9rem;color:#40515d}
.callout{background:#edf7f6;border-left:5px solid var(--teal);padding:14px 18px;border-radius:7px;margin:10px 0}
.method{background:var(--wash);border:1px solid var(--line);padding:14px 16px;border-radius:9px;min-height:118px}
.path{display:flex;gap:8px;align-items:stretch;margin:12px 0;flex-wrap:wrap}.path div{flex:1;min-width:150px;padding:12px;border:1px solid var(--line);border-radius:8px;background:white}.path b{display:block;color:var(--blue);margin-bottom:4px}.arrow{display:flex!important;align-items:center;justify-content:center;flex:0!important;min-width:20px!important;border:0!important;background:transparent!important;font-size:1.3rem}
div[data-testid="stMetric"]{background:white;border:1px solid var(--line);padding:12px 14px;border-radius:9px}
</style>""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    events = generate_events()
    latest, metrics = reconcile(events)
    return events, latest, metrics, build_actions(events), unit_summary(events)


events, latest, metrics, actions, units = load_data()
st.markdown('<div class="eyebrow">Problem-back analytics · interview demonstration</div>', unsafe_allow_html=True)
st.title("Hospital Flow Decision Lab")
st.caption("Northstar General Hospital · synthetic operational snapshot · 19 Aug 2026, 10:00")
st.markdown('<div class="boundary"><b>Synthetic demonstration.</b> No real patient, hospital, staff, or GE HealthCare data. Not a GE product, clinical tool, deployment, or production forecast.</div>', unsafe_allow_html=True)

st.markdown(f'''<div class="decision"><h2>The hospital has a real flow problem—but the reported census overstates it.</h2>
<p>Reported occupancy is <b>{metrics['reported_occupancy_pct']:.1f}%</b>. Reconciliation removes <b>{metrics['phantom_occupancy']} stale bed states</b>, revealing true occupancy of <b>{metrics['reconciled_occupancy_pct']:.1f}%</b>. That correction creates decision room; it does not eliminate {metrics['ed_boarders_over_4h']} long-wait boarders.</p></div>''', unsafe_allow_html=True)

tabs = st.tabs(["EXECUTIVE BRIEF", "FLOW DIAGNOSIS", "DAILY OPERATING SYSTEM", "EVIDENCE & METHOD"])

with tabs[0]:
    st.subheader("What leaders need to decide now")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="fact-card"><div class="label">Fact</div><div class="value">{metrics["reported_occupied"]} → {metrics["reconciled_occupied"]} beds</div><div class="copy">Late discharge events leave {metrics["phantom_occupancy"]} clean, physically available beds reported as occupied.</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="fact-card"><div class="label">Operational truth</div><div class="value">{metrics["ed_boarders_over_4h"]} boarders &gt;4h</div><div class="copy">After the data correction, genuine congestion remains. The constraint is not explained by bad data alone.</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="fact-card"><div class="label">Decision</div><div class="value">Two-track response</div><div class="copy">Release trusted capacity within one hour and run a tiered flow huddle against the {metrics["discharge_ready"]} discharge-ready cohort.</div></div>', unsafe_allow_html=True)
    left, right = st.columns([1.05, 1], gap="large")
    with left:
        st.markdown("#### Capacity reconciliation")
        waterfall = go.Figure(go.Waterfall(
            orientation="v", measure=["absolute", "relative", "total"],
            x=["Reported occupied", "Remove phantom states", "Reconciled occupied"],
            y=[metrics["reported_occupied"], -metrics["phantom_occupancy"], metrics["reconciled_occupied"]],
            text=[str(metrics["reported_occupied"]), f"-{metrics['phantom_occupancy']}", str(metrics["reconciled_occupied"])],
            connector={"line": {"color": "#9aa8b2"}}, decreasing={"marker": {"color": "#23a39b"}},
            increasing={"marker": {"color": "#d97706"}}, totals={"marker": {"color": "#1d4e89"}},
        ))
        waterfall.update_layout(height=360, margin=dict(l=20, r=20, t=15, b=20), yaxis_title="Beds", showlegend=False)
        st.plotly_chart(waterfall, width="stretch")
    with right:
        st.markdown("#### Executive recommendation")
        st.markdown(f"""
1. **Stabilize the fact base by 11:00.** Bed Management confirms and closes the {metrics['phantom_occupancy']} stale encounters; Interface Support traces the late `ADT^A03` pathway.
2. **Use the corrected census in the next flow huddle.** Hospital Operations prioritizes units by boarder pressure, clean capacity, and discharge-ready opportunity.
3. **Measure the intervention, not the screen.** Track census agreement, boarders over four hours, action completion by deadline, and time from physical discharge to system closure.
""")
        st.markdown('<div class="callout"><b>Decision request:</b> approve the one-hour reconciliation sprint and require owners to report outcomes—not activity—at the next tiered huddle.</div>', unsafe_allow_html=True)
    st.caption("This conclusion is generated from deterministic synthetic evidence; no external outcome claim is applied to this fictional scenario.")

with tabs[1]:
    st.subheader("Separate the signal, locate the constraint, test the intervention")
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Physical capacity", metrics["bed_capacity"], help="Six fictional units × 40 beds.")
    k2.metric("Reported occupancy", f"{metrics['reported_occupancy_pct']:.1f}%", help=f"{metrics['reported_occupied']} of {metrics['bed_capacity']} beds")
    k3.metric("Reconciled occupancy", f"{metrics['reconciled_occupancy_pct']:.1f}%", help=f"{metrics['reconciled_occupied']} of {metrics['bed_capacity']} beds")
    k4.metric("Clean available", metrics["clean_available"])
    k5.metric("Dirty available", metrics["dirty_available"])

    left, right = st.columns([1.15, .85], gap="large")
    with left:
        st.markdown("#### Unit pressure map")
        plot_units = units.copy()
        plot_units["Reconciled occupancy %"] = plot_units["Reconciled"] / plot_units["Capacity"] * 100
        fig = px.scatter(plot_units, x="Reconciled occupancy %", y="ED_boarders", size="Discharge_ready",
                         color="Phantom", text="unit", hover_data=["Reported", "Reconciled", "Clean_available"],
                         color_continuous_scale=["#d7efed", "#007f7b"], size_max=34)
        fig.update_traces(textposition="top center")
        fig.add_vline(x=90, line_dash="dash", line_color="#9aa8b2")
        fig.update_layout(height=410, margin=dict(l=10, r=10, t=20, b=20), coloraxis_colorbar_title="Phantom")
        st.plotly_chart(fig, width="stretch")
    with right:
        st.markdown("#### Bottleneck decomposition")
        factors = pd.DataFrame({"Factor": ["ED boarders >4h", "Discharge-ready cohort", "Phantom occupancy", "Dirty empty beds"],
                                "Count": [metrics["ed_boarders_over_4h"], metrics["discharge_ready"], metrics["phantom_occupancy"], metrics["dirty_available"]],
                                "Type": ["Demand pressure", "Flow opportunity", "Data distortion", "Turnaround constraint"]})
        bar = px.bar(factors.sort_values("Count"), x="Count", y="Factor", orientation="h", color="Type",
                     color_discrete_map={"Demand pressure":"#b42318", "Flow opportunity":"#1d4e89", "Data distortion":"#007f7b", "Turnaround constraint":"#d97706"}, text="Count")
        bar.update_layout(height=410, margin=dict(l=10, r=10, t=20, b=20), legend_title="")
        st.plotly_chart(bar, width="stretch")

    st.markdown("#### Near-term planning scenario")
    horizon = st.slider("Planning horizon (hours)", 4, 12, 8, help="Changes the arithmetic horizon; this is not a trained forecast.")
    scenario = planning_scenario(events, horizon)
    line = px.line(scenario, x="Hour", y="Occupied beds", color="Scenario", markers=True,
                   color_discrete_map={"Current practice":"#b42318", "Owned actions completed":"#007f7b"})
    line.add_hline(y=228, line_dash="dash", annotation_text="95% capacity threshold", line_color="#d97706")
    line.update_layout(height=360, margin=dict(l=20, r=20, t=20, b=20), legend_title="")
    st.plotly_chart(line, width="stretch")
    end = scenario[scenario["Hour"].eq(horizon)].set_index("Scenario")["Occupied beds"]
    st.markdown(f'<div class="callout"><b>Scenario result at +{horizon}h:</b> current-practice arithmetic reaches {int(end["Current practice"])} occupied beds; completing owned discharge actions yields {int(end["Owned actions completed"])}. Assumptions: 4.5 arrivals/hour, 2.5 routine releases/hour, and up to 1.5 additional releases/hour from the ready cohort.</div>', unsafe_allow_html=True)
    st.dataframe(units, width="stretch", hide_index=True)

with tabs[2]:
    st.subheader("Turn the analysis into the hospital's daily operating rhythm")
    st.markdown('''<div class="path"><div><b>Unit round</b>Confirm readiness and barriers</div><div class="arrow">→</div><div><b>Service queue</b>Remove data and support delays</div><div class="arrow">→</div><div><b>Tiered huddle</b>Deconflict demand and capacity</div><div class="arrow">→</div><div><b>Central command</b>Resolve exceptions and assure closure</div></div>''', unsafe_allow_html=True)
    f1, f2, f3 = st.columns([1, 1, 2])
    tier_options = list(actions["Huddle tier"].unique())
    severity_options = ["Critical", "High", "Medium"]
    selected_tiers = f1.multiselect("Huddle tier", tier_options, default=tier_options)
    selected_severity = f2.multiselect("Severity", severity_options, default=severity_options)
    unit_choice = f3.selectbox("Focus unit", ["All units"] + list(units["unit"]))
    queue = actions[actions["Huddle tier"].isin(selected_tiers) & actions["Severity"].isin(selected_severity)]
    if unit_choice != "All units":
        queue = queue[queue["Affected unit"].isin([unit_choice, "UNMAPPED-X"])]
    st.dataframe(queue, width="stretch", hide_index=True, height=460,
                 column_config={"Escalation deadline": st.column_config.DatetimeColumn(format="DD MMM, HH:mm")})
    a1, a2, a3, a4 = st.columns(4)
    a1.markdown('<div class="method"><b>10:00 · Unit round</b><br>Validate discharge-ready cohort and name unresolved barriers.</div>', unsafe_allow_html=True)
    a2.markdown('<div class="method"><b>10:30 · Tiered huddle</b><br>Use corrected capacity and pressure ranking to assign placements.</div>', unsafe_allow_html=True)
    a3.markdown('<div class="method"><b>11:00 · Central review</b><br>Confirm stale encounters closed and overdue actions escalated.</div>', unsafe_allow_html=True)
    a4.markdown('<div class="method"><b>14:00 · Measure</b><br>Compare boarders, census agreement, and action closure to baseline.</div>', unsafe_allow_html=True)
    st.caption("Accountability is explicit: every row contains evidence, one accountable role, a next action, a deadline, and a success measure.")

with tabs[3]:
    st.subheader("Evidence chain and consulting method")
    st.markdown('''<div class="path"><div><b>1 · Source events</b>5,000 fixed-seed ADT-like records</div><div class="arrow">→</div><div><b>2 · Validation</b>Freshness, ACK, duplicate, mapping, sequence</div><div class="arrow">→</div><div><b>3 · Reconciliation</b>System census vs physical bed state</div><div class="arrow">→</div><div><b>4 · Operational analysis</b>Pressure, cohorts, scenario arithmetic</div><div class="arrow">→</div><div><b>5 · Change control</b>Owner, deadline, success measure</div></div>''', unsafe_allow_html=True)
    trust = st.columns(6)
    for col, label, key in zip(trust, ["Freshness min", "Missing ACK", "Duplicates", "Late discharges", "Unmapped", "Sequence errors"],
                               ["feed_freshness_minutes", "missing_ack", "duplicates", "late_discharges", "unmapped_units", "timestamp_violations"]):
        col.metric(label, metrics[key])
    rules = pd.DataFrame([
        ["Missing acknowledgement", "Acknowledgement timestamp is absent", "Interface Support"],
        ["Duplicate", "Encounter, timestamp, message type, unit and bed repeat", "Interface Support"],
        ["Late discharge", "ADT^A03 is marked late in the controlled scenario", "Interface Support"],
        ["Unmapped unit", "Unit code is outside the fictional master list", "Data Steward"],
        ["Sequence violation", "Non-admission event precedes admission", "Data Steward"],
        ["Phantom occupancy", "Latest state is system-occupied and physically available", "Bed Management"],
    ], columns=["Rule", "Deterministic test", "Control owner"])
    st.dataframe(rules, width="stretch", hide_index=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown('<div class="method"><b>Problem statement</b><br>Is apparent capacity pressure physical, operational, or a data artifact?</div>', unsafe_allow_html=True)
    m2.markdown('<div class="method"><b>Analytical answer</b><br>It is both: 18 false occupied states and persistent boarding after correction.</div>', unsafe_allow_html=True)
    m3.markdown('<div class="method"><b>Intervention</b><br>Reconcile records, prioritize ready cohorts, and operate a tiered escalation rhythm.</div>', unsafe_allow_html=True)
    m4.markdown('<div class="method"><b>Evaluation</b><br>Test census agreement, action closure, and boarder reduction against baseline.</div>', unsafe_allow_html=True)
    with st.expander("Assumptions, boundaries, and interview relevance", expanded=True):
        st.markdown("""
- **Synthetic boundary:** no names, MRNs, diagnoses, clinical results, notes, or real organizations are generated. `ADT^A01`, `ADT^A02`, and `ADT^A03` are illustrative labels, not full messages or a conformance claim.
- **Planning boundary:** the near-term curve is transparent arithmetic for discussion, not regression, simulation validation, machine learning, or a production forecast.
- **Operational assumptions:** physical bed state is the comparison signal; each unit has 40 fictional beds; readiness is a scenario flag, not a clinical discharge decision.
- **What the demonstration proves:** structured problem framing, data validation, flow analysis, executive communication, deterministic operational rules, and change measurement.
- **What it does not prove:** clinical validity, production integration, predictive accuracy, cybersecurity, real-time performance, or outcomes in a real hospital.
""")
