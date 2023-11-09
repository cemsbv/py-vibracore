from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, List, Literal

import numpy as np
from pygef.cpt import CPTData

from .constants import SHEETPILE_REFERENCE_PROFILES

CustomInterval = 0.5
UnitWeightWater = 9.81


@dataclass(frozen=True)
class VibrationSource:
    """

    Attributes
    -----------
    areaShaftSpecific: float
        Specific shaft area of the single sheet pile (1 sheet) per unit length [m^2/m].
    areaTipSpecific: float
        Specific tip area of the single sheet pile (1 sheet) [m^2].
    amountOfSheetPiles: int = 1
        Number of sheets
            - push = 1
            - vibrate = 2
    slotResistanceSpecific: float
        Specific sheet pile slot resistance [kN/m] based on CUR 166 6th edition.
        for new sheet piles:
            - push = 5
            - vibrate = 10
    sheetPileName: str = "User defined"
        Sheet pile name
    """

    areaShaftSpecific: float
    areaTipSpecific: float
    slotResistanceSpecific: float
    amountOfSheetPiles: int = 1
    sheetPileName: str = "User defined"

    @classmethod
    def from_sheet_pile_name(
        cls,
        name: str,
        amount_of_sheet_piles: int = 1,
        slot_resistance_specific: float = 10.0,
    ) -> "VibrationSource":
        """

        Parameters
        ----------
        name: str
            Sheet pile name
        amount_of_sheet_piles: int = 1
            Number of sheets
        slot_resistance_specific: float = 10
            Specific sheet pile slot resistance [kN/m] based on CUR 166 6th edition.
        Returns
        -------
        VibrationSource
        """
        props = next(
            (item for item in SHEETPILE_REFERENCE_PROFILES if item["label"] == name),
            None,
        )
        if props is None:
            raise ValueError(
                f"{name} is not a valid sheet pile name. "
                "Please specify the areaShaftSpecific and areaTipSpecific in the "
                "main class or update the SHEETPILE_REFERENCE_PROFILES table."
            )

        return cls(
            areaShaftSpecific=props.get("area_shaft_specific"),  # type: ignore
            areaTipSpecific=props.get("area_tip_specific"),  # type: ignore
            amountOfSheetPiles=amount_of_sheet_piles,
            slotResistanceSpecific=slot_resistance_specific,
            sheetPileName=name,
        )


def create_multi_cpt_impact_force_payload(
    cptdata_objects: List[CPTData],
    classify_tables: Dict[str, dict],
    vibration_source: VibrationSource,
    friction_strategy: Literal["CPTFrictionStrategy", "SlipFrictionStrategy"],
    drive_strategy: Literal["vibrate", "push"],
    installation_level_offset: float,
    zeta: float = 0.6,
) -> dict:
    """
    Creates a dictionary with the payload content for the VibraCore endpoint
    "/impact-force/calculation/multi"

    This dictionary can be passed directly to `nuclei.client.call_endpoint()`.

    Parameters
    ----------
    cptdata_objects:
        A list of pygef.CPTData objects
    classify_tables:
        A dictionary, mapping `CPTData.alias` values to dictionary with the resulting response
        of a call to CPTCore `classify/*` information, containing the following keys:

            - geotechnicalSoilName: Sequence[str]
                Geotechnical Soil Name related to the ISO
            - lowerBoundary: Sequence[float]
                Lower boundary of the layer [m]
            - upperBoundary: Sequence[float]
                Upper boundary of the layer [m]
            - color: Sequence[str]
                Hex color code
            - mainComponent: Sequence[Literal["rocks", "gravel", "sand", "silt", "clay", "peat"]]
                Main soil component
            - cohesion: Sequence[float]
                Cohesion of the layer [kPa]
            - gamma_sat: Sequence[float]
                Saturated unit weight [kN/m^3]
            - gamma_unsat: Sequence[float]
                Unsaturated unit weight [kN/m^3]
            - phi: Sequence[float]
                Phi [degrees]
            - undrainedShearStrength: Sequence[float]
                Undrained shear strength [kPa]
    vibration_source: VibrationSource
        Vibration source object
    friction_strategy: Literal["CPTFrictionStrategy", "SlipFrictionStrategy"],
        Defines the strategy on how to compute the sleeve friction:

            - CPTFrictionStrategy

        The CPT Friction Strategy takes the sleeve friction provided by the cpt.
        Note that this method is only valid when the sleeve friction is provided within
        the cpt object.


            - SlipFrictionStrategy

        The Slip Friction Strategy calculated the sleeve friction based on the gamma,
        gamma saturation, phi and the undrained shear strength. To use this methode the
        values must be provided within the cpt object.
    drive_strategy: Literal["vibrate", "push"]
        Defines the strategy on how to compute the impact force:

            - vibrate

        The vibration strategy calculates the impact force based on a vibration installation method.

            - push

        The push strategy calculates the impact force based on a push installation method.
    installation_level_offset: float
        Installation level of the sheet pile [m w.r.t REF]
    zeta: float = 0.6
        verknedingsfactor [-], used in the push drive strategy based on CUR 166 6th edition.

    Returns
    -------
    payload: dict
    """

    payload = {
        "soilProperties": [
            {
                "cptObject": {
                    "coneResistance": cpt.data.get_column("coneResistance")
                    .clip(lower_bound=0, upper_bound=1e10)
                    .to_list(),
                    "depthOffset": cpt.data.get_column("depthOffset").to_list(),
                    "localFriction": cpt.data.get_column("localFriction")
                    .clip(lower_bound=0, upper_bound=1e10)
                    .to_list(),
                    "name": cpt.alias,
                    "verticalPositionOffset": cpt.delivered_vertical_position_offset,
                    "x": cpt.delivered_location.x,
                    "y": cpt.delivered_location.y,
                },
                "customInterval": CustomInterval,
                "groundwaterLevelOffset": cpt.groundwater_level_offset
                if cpt.groundwater_level_offset
                else cpt.delivered_vertical_position_offset - 1,
                "layerTable": {
                    "gamma_sat": classify_tables[cpt.alias].get("gamma_sat"),
                    "gamma_unsat": classify_tables[cpt.alias].get("gamma_unsat"),
                    "phi": classify_tables[cpt.alias].get("phi"),
                    "soilcode": classify_tables[cpt.alias].get("mainComponent"),
                    "undrainedShearStrength": classify_tables[cpt.alias].get(
                        "undrainedShearStrength"
                    ),
                    "upperBoundary": (
                        cpt.delivered_vertical_position_offset
                        - np.array(classify_tables[cpt.alias].get("upperBoundary"))
                    ).tolist(),
                },
                "unitWeightWater": UnitWeightWater,
            }
            for cpt in cptdata_objects
        ],
        "vibrationSource": {
            "areaShaftSpecific": vibration_source.areaShaftSpecific,
            "areaTipSpecific": vibration_source.areaTipSpecific,
            "numSheets": vibration_source.amountOfSheetPiles,
            "sheetPileName": vibration_source.sheetPileName,
            "slotResistanceSpecific": vibration_source.slotResistanceSpecific,
        },
        "frictionStrategy": friction_strategy,
        "impactForceCalculation": {
            "driveStrategy": drive_strategy,
            "installationLevel": installation_level_offset,
            "zeta": zeta,
        },
    }
    return payload


def create_multi_cpt_impact_force_report_payload(
    multi_cpt_payload: dict,
    project_name: str,
    project_id: str,
    author: str,
) -> dict:
    """
    Creates a dictionary with the payload content for the VibraCore endpoint
    "/impact-force/report"

    This dictionary can be passed directly to `nuclei.client.call_endpoint()`.

    Parameters
    ----------
    multi_cpt_payload:
        The result of a call to `create_multi_cpt_impact_force_payload()`
    project_name:
        The name of the project.
    project_id:
        The identifier (code) of the project.
    author:
        The author of the report.

    Returns
    -------
    payload: dict
    """
    payload = deepcopy(multi_cpt_payload)
    payload.update(
        dict(
            reportProperties=dict(
                author=author,
                projectNumber=project_id,
                projectName=project_name,
            ),
        )
    )
    return payload


def create_single_cpt_impact_force_payload(multi_cpt_payload: dict, name: str) -> dict:
    """
    Creates a dictionary with the payload content for the VibraCore endpoint
    "/impact-force/calculation/single"

    This dictionary can be passed directly to `nuclei.client.call_endpoint()`.

    Parameters
    ----------
    multi_cpt_payload: dict
        The result of a call to `create_multi_cpt_impact_force_payload()`
    name: str
        CPT name

    Returns
    -------
    payload: dict
    """
    payload = deepcopy(multi_cpt_payload)

    props = next(
        (
            item
            for item in payload["soilProperties"]
            if item["cptObject"]["name"] == name
        ),
        None,
    )
    if props is None:
        raise ValueError(f"{name} is not a valid CPT name.")
    payload.update(dict(soilProperties=props))

    return payload
