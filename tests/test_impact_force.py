import matplotlib.pyplot as plt
import pytest

from pyvibracore.input.impact_force_properties import (
    VibrationSource,
    create_multi_cpt_impact_force_payload,
    create_multi_cpt_impact_force_report_payload,
    create_single_cpt_impact_force_payload,
)
from pyvibracore.results.impact_force_result import MultiCalculationData


def test_vibration_source():
    VibrationSource.from_sheet_pile_name("AZ12-770")

    with pytest.raises(ValueError):
        VibrationSource.from_sheet_pile_name("abc")


def test_create_multi_cpt_impact_force_payload(cpt, mock_classify_response):
    create_multi_cpt_impact_force_payload(
        [cpt],
        {"S-TUN-016-PG": mock_classify_response},
        VibrationSource.from_sheet_pile_name("AZ12-770"),
        friction_strategy="CPTFrictionStrategy",
        drive_strategy="vibrate",
        installation_level_offset=-20,
    )


def test_create_multi_cpt_impact_force_report_payload(cpt, mock_classify_response):
    payload = create_multi_cpt_impact_force_payload(
        [cpt],
        {"S-TUN-016-PG": mock_classify_response},
        VibrationSource.from_sheet_pile_name("AZ12-770"),
        friction_strategy="CPTFrictionStrategy",
        drive_strategy="vibrate",
        installation_level_offset=-20,
    )
    create_multi_cpt_impact_force_report_payload(
        payload,
        project_name="Test project",
        project_id="123",
        author="Test User",
    )


def test_create_single_cpt_impact_force_payload(cpt, mock_classify_response):
    payload = create_multi_cpt_impact_force_payload(
        [cpt],
        {"S-TUN-016-PG": mock_classify_response},
        VibrationSource.from_sheet_pile_name("AZ12-770"),
        friction_strategy="CPTFrictionStrategy",
        drive_strategy="vibrate",
        installation_level_offset=-20,
    )

    create_single_cpt_impact_force_payload(payload, "S-TUN-016-PG")


def test_multi_calculation_data(mock_impact_force_response):
    result = MultiCalculationData.from_api_response(mock_impact_force_response)

    assert isinstance(result.plot(), plt.Figure)
