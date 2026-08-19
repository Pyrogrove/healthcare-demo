"""Deterministic, non-identifying synthetic hospital-flow event generation."""

from __future__ import annotations

import numpy as np
import pandas as pd

SEED = 20260819
AS_OF = pd.Timestamp("2026-08-19 10:00:00")
UNITS = ["North-1", "North-2", "South-1", "South-2", "East-1", "West-1"]
UNIT_CAPACITY = 40
CURRENT_OCCUPIED = dict(zip(UNITS, [38, 37, 36, 36, 35, 34]))
PHANTOM_BY_UNIT = dict(zip(UNITS, [2, 3, 3, 3, 3, 4]))


def _base_row(event_id: int, encounter_id: str, unit: str, bed: str, timestamp: pd.Timestamp,
              event_type: str, message_type: str, rng: np.random.Generator) -> dict:
    return {
        "event_id": f"EVT-{event_id:06d}", "encounter_id": encounter_id, "unit": unit, "bed": bed,
        "event_timestamp": timestamp, "event_type": event_type, "message_type": message_type,
        "interface_status": "Received", "ack_timestamp": timestamp + pd.Timedelta(minutes=int(rng.integers(1, 8))),
        "system_bed_status": "occupied", "physical_bed_status": "occupied", "cleaning_status": "not-applicable",
        "discharge_readiness_status": "not-ready", "ed_boarding_duration_hours": 0.0,
        "transfer_request_status": "none",
    }


def generate_events(seed: int = SEED, event_count: int = 5000) -> pd.DataFrame:
    """Return 5,000 plausible synthetic ADT-like events with controlled defects."""
    if event_count != 5000:
        raise ValueError("This controlled scenario is defined for exactly 5,000 events.")
    rng = np.random.default_rng(seed)
    rows: list[dict] = []
    beds = {unit: [f"{unit}-{number:02d}" for number in range(1, UNIT_CAPACITY + 1)] for unit in UNITS}

    # 1,300 completed encounters: 3 base events each plus 668 additional transfers = 4,568 events.
    cumulative_phantoms = []
    running = 0
    for unit in UNITS:
        running += PHANTOM_BY_UNIT[unit]
        cumulative_phantoms.append((running, unit))
    for number in range(1, 1301):
        enc_id = f"SYN-{number:05d}"
        phantom = number <= 18
        late_only = 19 <= number <= 28
        if phantom:
            unit = next(unit_name for threshold, unit_name in cumulative_phantoms if number <= threshold)
            prior = sum(PHANTOM_BY_UNIT[x] for x in UNITS[:UNITS.index(unit)])
            bed = beds[unit][CURRENT_OCCUPIED[unit] + number - prior - 1]
            admitted = AS_OF - pd.Timedelta(hours=int(rng.integers(36, 120)))
            discharged = AS_OF - pd.Timedelta(hours=int(rng.integers(1, 7)))
        else:
            unit = str(rng.choice(UNITS))
            bed = str(rng.choice(beds[unit]))
            admitted = AS_OF - pd.Timedelta(hours=int(rng.integers(72, 720)))
            discharged = min(AS_OF - pd.Timedelta(hours=12), admitted + pd.Timedelta(hours=int(rng.integers(18, 70))))
        transfer = admitted + pd.Timedelta(hours=6)
        lifecycle = [("admission", "ADT^A01", admitted), ("transfer", "ADT^A02", transfer)]
        if number <= 668:
            extra_time = transfer if number <= 18 else transfer + pd.Timedelta(hours=4)
            lifecycle.append(("transfer", "ADT^A02", extra_time))
        lifecycle.append(("discharge", "ADT^A03", discharged))
        for event_type, message_type, timestamp in lifecycle:
            row = _base_row(len(rows) + 1, enc_id, unit, bed, timestamp, event_type, message_type, rng)
            if event_type == "discharge":
                row.update({"system_bed_status": "occupied" if phantom else "available",
                            "physical_bed_status": "available", "cleaning_status": "clean"})
                if phantom or late_only:
                    row["interface_status"] = "Late"
            rows.append(row)

    # 216 current encounters occupy unique beds, producing 432 events.
    current_number = 1301
    for unit in UNITS:
        for bed in beds[unit][:CURRENT_OCCUPIED[unit]]:
            enc_id = f"SYN-{current_number:05d}"
            admitted = AS_OF - pd.Timedelta(hours=int(rng.integers(8, 120)))
            transfer = AS_OF - pd.Timedelta(minutes=int(rng.integers(5, 180)))
            readiness = "ready" if rng.random() < 0.28 else "not-ready"
            board_hours = round(float(rng.gamma(2.3, 1.7)), 1)
            request = "requested" if rng.random() < 0.22 else "none"
            for event_type, message_type, timestamp in [("admission", "ADT^A01", admitted), ("transfer", "ADT^A02", transfer)]:
                row = _base_row(len(rows) + 1, enc_id, unit, bed, timestamp, event_type, message_type, rng)
                row.update({"discharge_readiness_status": readiness, "ed_boarding_duration_hours": board_hours,
                            "transfer_request_status": request})
                rows.append(row)
            current_number += 1

    df = pd.DataFrame(rows)
    assert len(df) == event_count
    ack_idx = df.index[df["event_type"].eq("admission")][100:122]
    df.loc[ack_idx, "ack_timestamp"] = pd.NaT
    df.loc[ack_idx, "interface_status"] = "Missing ACK"
    unmapped_idx = df.index[df["event_type"].eq("admission")][220:236]
    df.loc[unmapped_idx, "unit"] = "UNMAPPED-X"
    violation_encounters = {f"SYN-{number:05d}" for number in range(100, 112)}
    transfer_idx = df[df["event_type"].eq("transfer") & df["encounter_id"].isin(violation_encounters)].groupby("encounter_id").head(1).index
    for idx in transfer_idx:
        enc = df.at[idx, "encounter_id"]
        admission_time = df.loc[(df["encounter_id"] == enc) & df["event_type"].eq("admission"), "event_timestamp"].min()
        df.at[idx, "event_timestamp"] = admission_time - pd.Timedelta(hours=2)
    return df.reset_index(drop=True)
