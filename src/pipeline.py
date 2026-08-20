"""Validation, reconciliation, operational analysis, and deterministic actions."""

from __future__ import annotations

import sqlite3

import numpy as np
import pandas as pd

from .generate_synthetic_data import AS_OF, UNIT_CAPACITY, UNITS

DUPLICATE_KEY = ["encounter_id", "event_timestamp", "message_type", "unit", "bed"]


def validate_events(events: pd.DataFrame) -> pd.DataFrame:
    df = events.copy()
    df["is_duplicate"] = df.duplicated(DUPLICATE_KEY, keep="first")
    df["is_missing_ack"] = df["ack_timestamp"].isna()
    df["is_late_discharge"] = df["event_type"].eq("discharge") & df["interface_status"].eq("Late")
    df["is_unmapped_unit"] = ~df["unit"].isin(UNITS)
    admission = df[df["event_type"].eq("admission")].groupby("encounter_id")["event_timestamp"].min()
    df["admission_timestamp"] = df["encounter_id"].map(admission)
    df["is_timestamp_violation"] = df["event_type"].ne("admission") & (df["event_timestamp"] < df["admission_timestamp"])
    return df


def _latest_encounters(events: pd.DataFrame) -> pd.DataFrame:
    checked = validate_events(events)
    canonical = checked[~checked["is_duplicate"]].sort_values(["encounter_id", "event_timestamp", "event_id"])
    latest = canonical.groupby("encounter_id", as_index=False).tail(1).copy()
    latest["reported_occupied"] = latest["system_bed_status"].eq("occupied")
    latest["reconciled_occupied"] = latest["physical_bed_status"].eq("occupied")
    latest["phantom_occupancy"] = latest["reported_occupied"] & ~latest["reconciled_occupied"]
    return latest


def bed_inventory(events: pd.DataFrame) -> pd.DataFrame:
    latest = _latest_encounters(events)
    reported = set(latest.loc[latest["reported_occupied"], "bed"])
    physical = set(latest.loc[latest["reconciled_occupied"], "bed"])
    phantom = set(latest.loc[latest["phantom_occupancy"], "bed"])
    rows = []
    for unit in UNITS:
        for number in range(1, UNIT_CAPACITY + 1):
            bed = f"{unit}-{number:02d}"
            available = bed not in physical
            rows.append({"unit": unit, "bed": bed, "reported_occupied": bed in reported,
                         "reconciled_occupied": bed in physical, "phantom_occupancy": bed in phantom,
                         "cleaning_status": "dirty" if available and number == UNIT_CAPACITY else ("clean" if available else "not-applicable")})
    return pd.DataFrame(rows)


def reconcile(events: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    checked = validate_events(events)
    latest = _latest_encounters(events)
    inventory = bed_inventory(events)
    metrics = {
        "event_count": len(events), "bed_capacity": len(inventory),
        "reported_occupied": int(inventory["reported_occupied"].sum()),
        "reconciled_occupied": int(inventory["reconciled_occupied"].sum()),
        "phantom_occupancy": int(inventory["phantom_occupancy"].sum()),
        "reported_occupancy_pct": float(inventory["reported_occupied"].mean() * 100),
        "reconciled_occupancy_pct": float(inventory["reconciled_occupied"].mean() * 100),
        "ed_boarders_over_4h": int((latest["reconciled_occupied"] & latest["ed_boarding_duration_hours"].gt(4)).sum()),
        "clean_available": int((~inventory["reconciled_occupied"] & inventory["cleaning_status"].eq("clean")).sum()),
        "dirty_available": int((~inventory["reconciled_occupied"] & inventory["cleaning_status"].eq("dirty")).sum()),
        "discharge_ready": int((latest["reconciled_occupied"] & latest["discharge_readiness_status"].eq("ready")).sum()),
        "missing_ack": int(checked["is_missing_ack"].sum()), "duplicates": int(checked["is_duplicate"].sum()),
        "late_discharges": int(checked["is_late_discharge"].sum()), "unmapped_units": int(checked["is_unmapped_unit"].sum()),
        "timestamp_violations": int(checked["is_timestamp_violation"].sum()),
        "feed_freshness_minutes": int((AS_OF - checked["event_timestamp"].max()).total_seconds() // 60),
    }
    return latest, metrics


def unit_summary(events: pd.DataFrame) -> pd.DataFrame:
    latest = _latest_encounters(events)
    inventory = bed_inventory(events)
    bed_counts = inventory.groupby("unit", as_index=False).agg(
        Capacity=("bed", "count"), Reported=("reported_occupied", "sum"), Reconciled=("reconciled_occupied", "sum"),
        Phantom=("phantom_occupancy", "sum"), Clean_available=("cleaning_status", lambda x: int((x == "clean").sum())),
        Dirty_available=("cleaning_status", lambda x: int((x == "dirty").sum())),
    )
    active = latest[latest["reconciled_occupied"]].groupby("unit", as_index=False).agg(
        ED_boarders=("ed_boarding_duration_hours", lambda x: int((x > 4).sum())),
        Discharge_ready=("discharge_readiness_status", lambda x: int((x == "ready").sum())),
    )
    result = bed_counts.merge(active, on="unit", how="left").fillna(0)
    result["Pressure"] = result["ED_boarders"] + result["Reported"] - result["Clean_available"] - result["Discharge_ready"]
    return result.sort_values("Pressure", ascending=False).reset_index(drop=True)


def planning_scenario(events: pd.DataFrame, hours: int = 8) -> pd.DataFrame:
    """Transparent planning arithmetic; deliberately not a predictive model."""
    _, metrics = reconcile(events)
    rows = []
    for hour in range(hours + 1):
        arrivals = round(4.5 * hour)
        routine_releases = round(2.5 * hour)
        accelerated = min(metrics["discharge_ready"], round(1.5 * hour))
        no_intervention = min(metrics["bed_capacity"], metrics["reconciled_occupied"] + arrivals - routine_releases)
        action_case = max(0, no_intervention - accelerated)
        rows.extend([{"Hour": hour, "Scenario": "Current practice", "Occupied beds": no_intervention},
                     {"Hour": hour, "Scenario": "Owned actions completed", "Occupied beds": action_case}])
    return pd.DataFrame(rows)


def build_actions(events: pd.DataFrame) -> pd.DataFrame:
    checked = validate_events(events)
    latest, metrics = reconcile(events)
    actions: list[dict] = []
    def add(tier, issue, unit, impact, severity, evidence, owner, action, hours, measure):
        actions.append({"Huddle tier": tier, "Issue": issue, "Affected unit": unit, "Operational impact": impact,
                        "Severity": severity, "Supporting evidence": evidence, "Accountable owner": owner,
                        "Next action": action, "Escalation deadline": AS_OF + pd.Timedelta(hours=hours), "Success measure": measure})
    for unit, count in latest[latest["phantom_occupancy"]].groupby("unit").size().items():
        add("Central command", "Phantom occupancy", unit, "Usable capacity is hidden", "Critical",
            f"{count} clean beds are physically available but system-occupied", "Bed Management",
            "Confirm physical state, close stale encounters, release beds", 1, "System and physical census agree")
    for unit, count in checked[checked["is_missing_ack"]].groupby("unit").size().items():
        add("Service queue", "Missing acknowledgements", unit, "Event delivery is unconfirmed", "High",
            f"{count} events have no acknowledgement", "Interface Support", "Trace, replay, and confirm acknowledgements", 2,
            "Zero unacknowledged events in affected batch")
    if metrics["unmapped_units"]:
        add("Service queue", "Unmapped unit code", "UNMAPPED-X", "Events cannot route reliably", "High",
            f"{metrics['unmapped_units']} events use an unmapped code", "Data Steward", "Map code and reprocess batch", 4,
            "All events assigned to an approved unit")
    for unit, count in latest[latest["reconciled_occupied"] & latest["ed_boarding_duration_hours"].gt(4)].groupby("unit").size().items():
        add("Tiered huddle", "ED boarding over four hours", unit, "Access and flow are delayed", "High",
            f"{count} current bed requests exceed four hours", "Hospital Operations", "Assign placement plan and remove top barrier", 1,
            "Boarders over four hours decrease by next huddle")
    for unit, count in latest[latest["reconciled_occupied"] & latest["discharge_readiness_status"].eq("ready")].groupby("unit").size().items():
        add("Unit round", "Discharge-ready cohort", unit, "Capacity release awaits coordinated follow-up", "Medium",
            f"{count} occupied encounters meet scenario readiness rule", "Nursing Unit", "Confirm plan and escalate unresolved barrier", 3,
            "Ready cohort disposition confirmed")
    return pd.DataFrame(actions).sort_values(["Escalation deadline", "Severity"]).reset_index(drop=True)


def build_curated_encounters(events: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Validate, transform, and curate event rows into one analytic encounter row.

    Duplicate, invalid-sequence, and unmapped rows are quarantined. Late-arriving
    discharge records are retained with an explicit audit flag because their
    clinical event time remains useful after arrival.
    """
    checked = validate_events(events)
    accepted = checked[
        ~checked["is_duplicate"]
        & ~checked["is_timestamp_violation"]
        & ~checked["is_unmapped_unit"]
    ].copy()
    accepted = accepted.sort_values(["encounter_id", "event_timestamp", "event_id"])

    current = _latest_encounters(events)
    current = current[current["unit"].isin(UNITS)]
    occupied_by_unit = current.groupby("unit")["reconciled_occupied"].sum().to_dict()
    recent_admissions = accepted[
        accepted["event_type"].eq("admission")
        & accepted["event_timestamp"].ge(AS_OF - pd.Timedelta(hours=24))
    ].groupby("unit")["encounter_id"].nunique().to_dict()

    rows: list[dict] = []
    for encounter_id, group in accepted.groupby("encounter_id", sort=True):
        admissions = group[group["event_type"].eq("admission")]
        if admissions.empty:
            continue
        admission_time = admissions["event_timestamp"].min()
        transfers = group[group["event_type"].eq("transfer")]
        discharges = group[group["event_type"].eq("discharge")]
        latest = group.iloc[-1]
        unit = str(latest["unit"])
        number = int(encounter_id.split("-")[-1])
        decision_time = admission_time + pd.Timedelta(minutes=25 + number % 31)
        request_time = decision_time + pd.Timedelta(minutes=10 + number % 16)
        transfer_time = transfers["event_timestamp"].min() if not transfers.empty else pd.NaT
        board_hours = float(latest["ed_boarding_duration_hours"])
        assigned_time = request_time + pd.Timedelta(hours=board_hours)
        actual_discharge = discharges["event_timestamp"].max() if not discharges.empty else pd.NaT
        acuity = ["low", "moderate", "high"][number % 3]
        rows.append({
            "patient_id": f"PAT-SYN-{number:05d}",
            "encounter_id": encounter_id,
            "unit": unit,
            "admission_time": admission_time,
            "decision_to_admit_time": decision_time,
            "bed_request_time": request_time,
            "bed_assigned_time": assigned_time,
            "transfer_time": transfer_time,
            "expected_discharge_time": admission_time + pd.Timedelta(hours=48 + number % 25),
            "actual_discharge_time": actual_discharge,
            "bed_status": "occupied" if bool(latest["physical_bed_status"] == "occupied") else "available",
            "staffed_beds": UNIT_CAPACITY,
            "occupancy": float(occupied_by_unit.get(unit, 0) / UNIT_CAPACITY),
            "patient_acuity": acuity,
            "boarding_hours": board_hours,
            "admission_volume_24h": int(recent_admissions.get(unit, 0)),
            "discharge_before_noon": bool(pd.notna(actual_discharge) and actual_discharge.hour < 12),
            "decision_to_bed_minutes": float((assigned_time - decision_time).total_seconds() / 60),
            "late_arriving_record": bool(group["is_late_discharge"].any()),
            "missing_acknowledgement": bool(group["is_missing_ack"].any()),
            "source_record_count": int(len(group)),
        })
    curated = pd.DataFrame(rows).sort_values("encounter_id").reset_index(drop=True)
    audit = {
        "raw_rows": int(len(events)),
        "validated_rows": int(len(checked)),
        "duplicate_rows_quarantined": int(checked["is_duplicate"].sum()),
        "invalid_sequence_rows_quarantined": int(checked["is_timestamp_violation"].sum()),
        "unmapped_rows_quarantined": int(checked["is_unmapped_unit"].sum()),
        "accepted_event_rows": int(len(accepted)),
        "curated_encounters": int(len(curated)),
        "late_rows_retained_with_flag": int(checked["is_late_discharge"].sum()),
        "missing_ack_rows_flagged": int(checked["is_missing_ack"].sum()),
    }
    return curated, audit


def map_fhir_encounter(payload: dict) -> dict:
    """Map a tiny synthetic FHIR-style Encounter payload to the canonical schema."""
    period = payload.get("period", {})
    location = (payload.get("location") or [{}])[0].get("location", {})
    return {
        "patient_id": payload.get("subject", {}).get("reference", "").replace("Patient/", ""),
        "encounter_id": payload.get("id"),
        "unit": location.get("display"),
        "admission_time": period.get("start"),
        "actual_discharge_time": period.get("end"),
        "bed_status": "available" if payload.get("status") == "finished" else "occupied",
        "source_format": "FHIR-style REST/JSON",
    }


def map_adt_like(message: str) -> dict:
    """Map a deliberately simplified pipe-delimited ADT-like event."""
    fields = dict(part.split("=", 1) for part in message.split("|") if "=" in part)
    return {
        "patient_id": fields.get("PID"),
        "encounter_id": fields.get("ENC"),
        "unit": fields.get("UNIT"),
        "admission_time": fields.get("TIME"),
        "bed_status": "occupied" if fields.get("EVENT") in {"A01", "A02"} else "available",
        "source_format": "ADT-like",
    }


def sql_examples(curated: pd.DataFrame) -> list[dict]:
    """Run four visible, read-only SQLite examples over the curated table."""
    sql_ready = curated.copy()
    for column in sql_ready.select_dtypes(include=["datetime64[ns]"]).columns:
        sql_ready[column] = sql_ready[column].astype("string")
    queries = [
        ("Average decision-to-bed minutes by unit", """
            SELECT unit, ROUND(AVG(decision_to_bed_minutes), 1) AS avg_minutes
            FROM encounters GROUP BY unit ORDER BY avg_minutes DESC
        """),
        ("Current occupancy by unit", """
            SELECT unit, staffed_beds,
                   SUM(CASE WHEN bed_status = 'occupied' THEN 1 ELSE 0 END) AS occupied,
                   ROUND(100.0 * SUM(CASE WHEN bed_status = 'occupied' THEN 1 ELSE 0 END) / staffed_beds, 1) AS occupancy_pct
            FROM encounters GROUP BY unit, staffed_beds ORDER BY occupancy_pct DESC
        """),
        ("Discharge-before-noon percentage", """
            SELECT unit, COUNT(*) AS completed_discharges,
                   ROUND(100.0 * AVG(CASE WHEN discharge_before_noon = 1 THEN 1.0 ELSE 0.0 END), 1) AS before_noon_pct
            FROM encounters WHERE actual_discharge_time IS NOT NULL
            GROUP BY unit ORDER BY before_noon_pct DESC
        """),
        ("Current boarding over four hours", """
            SELECT unit, COUNT(*) AS boarders_over_4h
            FROM encounters WHERE bed_status = 'occupied' AND boarding_hours > 4
            GROUP BY unit ORDER BY boarders_over_4h DESC
        """),
    ]
    results: list[dict] = []
    with sqlite3.connect(":memory:") as connection:
        sql_ready.to_sql("encounters", connection, index=False)
        for title, query in queries:
            results.append({"title": title, "query": query.strip(), "result": pd.read_sql_query(query, connection)})
    return results


def census_forecast(events: pd.DataFrame, horizon: int = 7, alpha: float = 0.35, beta: float = 0.15) -> pd.DataFrame:
    """Create synthetic history and a transparent Holt level/trend forecast."""
    _, metrics = reconcile(events)
    dates = pd.date_range(AS_OF.normalize() - pd.Timedelta(days=27), periods=28, freq="D")
    index = np.arange(28)
    actual = metrics["reconciled_occupied"] - 7 + 0.35 * index + 5 * np.sin(2 * np.pi * index / 7)
    actual = np.clip(np.rint(actual), 0, metrics["bed_capacity"]).astype(int)
    level = float(actual[0])
    trend = float(actual[1] - actual[0])
    fitted = [level]
    for value in actual[1:]:
        previous_level = level
        level = alpha * float(value) + (1 - alpha) * (level + trend)
        trend = beta * (level - previous_level) + (1 - beta) * trend
        fitted.append(level + trend)
    rows = [{"date": date, "series": "Historical actual", "census": int(value)} for date, value in zip(dates, actual)]
    rows.extend({"date": dates[-1] + pd.Timedelta(days=step), "series": "Baseline forecast",
                 "census": round(float(np.clip(level + step * trend, 0, metrics["bed_capacity"])), 1)}
                for step in range(1, horizon + 1))
    return pd.DataFrame(rows)


def regression_summary(curated: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Fit a small OLS illustration for current boarding time; not causal."""
    sample = curated[curated["bed_status"].eq("occupied")].copy()
    sample["acuity_score"] = sample["patient_acuity"].map({"low": 1, "moderate": 2, "high": 3})
    predictors = ["occupancy", "admission_volume_24h", "acuity_score"]
    raw_x = sample[predictors].astype(float).to_numpy()
    means = raw_x.mean(axis=0)
    scales = raw_x.std(axis=0)
    scales[scales == 0] = 1
    standardized = (raw_x - means) / scales
    design = np.column_stack([np.ones(len(sample)), standardized])
    y = sample["boarding_hours"].astype(float).to_numpy()
    coefficients, *_ = np.linalg.lstsq(design, y, rcond=None)
    predicted = design @ coefficients
    denominator = float(np.sum((y - y.mean()) ** 2))
    r_squared = 1 - float(np.sum((y - predicted) ** 2)) / denominator if denominator else 0.0
    table = pd.DataFrame({
        "Predictor (one standard-deviation increase)": ["Unit occupancy", "Recent admission volume", "Patient acuity"],
        "Estimated boarding-hour change": np.round(coefficients[1:], 2),
    })
    return table, {"sample_size": int(len(sample)), "intercept_hours": round(float(coefficients[0]), 2),
                   "r_squared": round(r_squared, 3)}


def boarding_hypothesis_test(curated: pd.DataFrame, permutations: int = 2000) -> dict:
    """Deterministic two-sided permutation test for high versus lower occupancy."""
    sample = curated[curated["bed_status"].eq("occupied")].copy()
    threshold = float(sample["occupancy"].median())
    high = sample.loc[sample["occupancy"].gt(threshold), "boarding_hours"].to_numpy(float)
    lower = sample.loc[sample["occupancy"].le(threshold), "boarding_hours"].to_numpy(float)
    observed = float(high.mean() - lower.mean())
    combined = np.concatenate([high, lower])
    rng = np.random.default_rng(20260819)
    extreme = 0
    for _ in range(permutations):
        shuffled = rng.permutation(combined)
        difference = float(shuffled[:len(high)].mean() - shuffled[len(high):].mean())
        extreme += abs(difference) >= abs(observed)
    return {
        "threshold_pct": round(threshold * 100, 1),
        "high_mean": round(float(high.mean()), 2),
        "lower_mean": round(float(lower.mean()), 2),
        "test_statistic": round(observed, 2),
        "p_value": round((extreme + 1) / (permutations + 1), 4),
        "high_n": int(len(high)),
        "lower_n": int(len(lower)),
    }


def capacity_what_if(events: pd.DataFrame, projected_admissions: int, expected_discharges: int,
                     discharge_timing_improvement: int = 0) -> dict:
    """Deterministic one-horizon capacity arithmetic for an operational discussion."""
    _, metrics = reconcile(events)
    accelerated = min(metrics["discharge_ready"], int(round(expected_discharges * discharge_timing_improvement / 100)))
    baseline = metrics["reconciled_occupied"] + projected_admissions - expected_discharges
    scenario = baseline - accelerated
    return {
        "staffed_beds": metrics["bed_capacity"],
        "starting_occupied": metrics["reconciled_occupied"],
        "baseline_occupied": max(0, baseline),
        "scenario_occupied": max(0, scenario),
        "accelerated_discharges": accelerated,
        "baseline_pressure": max(0, baseline - metrics["bed_capacity"]),
        "scenario_pressure": max(0, scenario - metrics["bed_capacity"]),
    }
