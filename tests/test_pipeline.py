import pandas as pd

from src.generate_synthetic_data import generate_events
from src.pipeline import bed_inventory, build_actions, planning_scenario, reconcile, validate_events


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
