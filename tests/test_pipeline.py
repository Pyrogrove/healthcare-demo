from pathlib import Path

import pandas as pd

from src.generate_synthetic_data import generate_events
from src.pipeline import (
    bed_inventory,
    boarding_hypothesis_test,
    build_actions,
    build_curated_encounters,
    capacity_what_if,
    census_forecast,
    map_adt_like,
    map_fhir_encounter,
    planning_scenario,
    reconcile,
    regression_holdout_evaluation,
    regression_ready_dataset,
    regression_summary,
    sql_examples,
    validate_events,
)


def test_fixed_seed_is_reproducible():
    pd.testing.assert_frame_equal(generate_events(), generate_events())


def test_prohibited_identifying_fields_absent():
    prohibited = {"patient_name", "staff_name", "mrn", "address", "phone", "email", "diagnosis", "clinical_result", "clinical_note"}
    assert prohibited.isdisjoint(generate_events().columns)


def test_duplicate_detection_works():
    checked = validate_events(generate_events())
    assert checked["is_duplicate"].sum() == 18


def test_late_discharge_detection_works():
    assert validate_events(generate_events())["is_late_discharge"].sum() == 28


def test_only_controlled_timestamp_violations_are_detected():
    assert validate_events(generate_events())["is_timestamp_violation"].sum() == 12


def test_missing_ack_detection_works():
    assert validate_events(generate_events())["is_missing_ack"].sum() == 22


def test_phantom_occupancy_reconciliation_works():
    latest, metrics = reconcile(generate_events())
    assert metrics["phantom_occupancy"] > 0
    assert metrics["reported_occupied"] - metrics["reconciled_occupied"] == metrics["phantom_occupancy"]
    assert latest.loc[latest["phantom_occupancy"], "physical_bed_status"].eq("available").all()


def test_action_rules_assign_correct_owner():
    actions = build_actions(generate_events())
    assert set(actions.loc[actions["Issue"].eq("Phantom occupancy"), "Accountable owner"]) == {"Bed Management"}
    assert set(actions.loc[actions["Issue"].eq("Missing acknowledgements"), "Accountable owner"]) == {"Interface Support"}
    assert set(actions.loc[actions["Issue"].eq("Discharge-ready cohort"), "Accountable owner"]) == {"Nursing Unit"}


def test_headline_totals_reconcile():
    latest, metrics = reconcile(generate_events())
    assert metrics["event_count"] == 5000
    assert metrics["reported_occupied"] == int(latest["reported_occupied"].sum())
    assert metrics["reconciled_occupied"] == int(latest["reconciled_occupied"].sum())


def test_bed_inventory_is_plausible_and_unique():
    inventory = bed_inventory(generate_events())
    assert len(inventory) == 240
    assert inventory["bed"].is_unique
    assert inventory["reported_occupied"].sum() <= len(inventory)
    assert inventory["reconciled_occupied"].sum() <= len(inventory)


def test_planning_scenario_is_transparent_and_action_case_improves():
    scenario = planning_scenario(generate_events(), 8)
    end = scenario[scenario["Hour"].eq(8)].set_index("Scenario")["Occupied beds"]
    assert end["Owned actions completed"] < end["Current practice"]


def test_curated_etl_has_required_schema_and_auditable_handling():
    curated, audit = build_curated_encounters(generate_events())
    required = {
        "patient_id", "encounter_id", "unit", "admission_time", "decision_to_admit_time",
        "bed_request_time", "bed_assigned_time", "transfer_time", "expected_discharge_time",
        "actual_discharge_time", "bed_status", "staffed_beds", "occupancy", "patient_acuity",
    }
    assert required.issubset(curated.columns)
    assert curated["encounter_id"].is_unique
    assert curated["patient_id"].str.startswith("PAT-SYN-").all()
    assert audit["duplicate_rows_quarantined"] == 18
    assert audit["invalid_sequence_rows_quarantined"] == 12
    assert audit["late_rows_retained_with_flag"] == 28


def test_simplified_integration_adapters_map_to_canonical_fields():
    fhir = map_fhir_encounter({
        "id": "ENC-1", "status": "in-progress", "subject": {"reference": "Patient/PAT-1"},
        "period": {"start": "2026-08-19T08:00:00"},
        "location": [{"location": {"display": "North-1"}}],
    })
    adt = map_adt_like("EVENT=A03|PID=PAT-2|ENC=ENC-2|UNIT=South-1|TIME=2026-08-19T09:00:00")
    assert fhir["encounter_id"] == "ENC-1" and fhir["bed_status"] == "occupied"
    assert adt["encounter_id"] == "ENC-2" and adt["bed_status"] == "available"


def test_sql_examples_execute_and_return_expected_outputs():
    curated, _ = build_curated_encounters(generate_events())
    outputs = sql_examples(curated)
    assert len(outputs) == 4
    assert all(not item["result"].empty for item in outputs)
    assert set(outputs[1]["result"]["unit"]) == {"North-1", "North-2", "South-1", "South-2", "East-1", "West-1"}


def test_forecast_has_history_and_requested_horizon():
    forecast = census_forecast(generate_events(), horizon=7)
    assert (forecast["series"] == "Historical actual").sum() == 28
    assert (forecast["series"] == "Baseline forecast").sum() == 7
    assert forecast["census"].between(0, 240).all()


def test_regression_and_hypothesis_outputs_are_explainable_and_deterministic():
    curated, _ = build_curated_encounters(generate_events())
    coefficients, metadata = regression_summary(curated)
    first_test = boarding_hypothesis_test(curated)
    second_test = boarding_hypothesis_test(curated)
    assert len(coefficients) == 3
    assert metadata["sample_size"] == 216
    assert 0 <= metadata["r_squared"] <= 1
    assert first_test == second_test
    assert 0 <= first_test["p_value"] <= 1


def test_capacity_what_if_is_deterministic_and_improvement_reduces_pressure():
    baseline = capacity_what_if(generate_events(), projected_admissions=35, expected_discharges=20, discharge_timing_improvement=0)
    improved = capacity_what_if(generate_events(), projected_admissions=35, expected_discharges=20, discharge_timing_improvement=30)
    assert improved["scenario_occupied"] < baseline["scenario_occupied"]
    assert improved["scenario_pressure"] <= baseline["scenario_pressure"]


def test_regression_ready_export_has_complete_reproducible_inputs():
    curated, _ = build_curated_encounters(generate_events())
    regression_data = regression_ready_dataset(curated)
    assert len(regression_data) == 216
    assert regression_data["encounter_id"].is_unique
    assert {"boarding_hours", "occupancy", "admission_volume_24h", "acuity_score"}.issubset(regression_data.columns)
    assert set(regression_data["acuity_score"]) == {1, 2, 3}


def test_time_ordered_holdout_is_deterministic_and_compares_a_baseline():
    curated, _ = build_curated_encounters(generate_events())
    first_predictions, first_metrics = regression_holdout_evaluation(curated)
    second_predictions, second_metrics = regression_holdout_evaluation(curated)
    pd.testing.assert_frame_equal(first_predictions, second_predictions)
    assert first_metrics == second_metrics
    assert first_metrics["training_rows"] == 151
    assert first_metrics["test_rows"] == 65
    assert first_metrics["model_mae"] >= 0
    assert first_metrics["baseline_mae"] >= 0


def test_r_companion_is_base_r_and_contains_the_same_model_workflow():
    script = (Path(__file__).parents[1] / "analysis" / "hospital_flow_regression.R").read_text(encoding="utf-8")
    required_tokens = ["read.csv", "duplicated", "is.na", "lm(", "predict(", "model_mae", "baseline_mae"]
    assert all(token in script for token in required_tokens)
    assert "library(" not in script
