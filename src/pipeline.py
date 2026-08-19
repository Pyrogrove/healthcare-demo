"""Validation, reconciliation, operational analysis, and deterministic actions."""

from __future__ import annotations

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
