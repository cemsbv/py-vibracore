from __future__ import annotations

import json
import logging
import uuid
from copy import deepcopy
from typing import Literal

import geopandas as gpd
import numpy as np
import requests
from shapely.geometry import LineString, Point, Polygon, mapping

from .constants import SOIL_REFERENCE

BAG_WFS_URL = "https://service.pdok.nl/lv/bag/wfs/v2_0"
THRESHOLD = 10000


def get_buildings_geodataframe(
    west: float,
    south: float,
    east: float,
    north: float,
    category: Literal["one", "two"] = "two",
    monumental: bool = False,
    structural_condition: Literal["sensitive", "normal"] = "normal",
    vibration_sensitive: bool = False,
    thickness: float = 8.0,
    foundation_element: Literal[
        "shallow foundation", "concrete piles", "timber piles", "steel piles"
    ] = "shallow foundation",
    material_floor: Literal["concrete", "wood"] = "concrete",
    feature: Literal[
        "bag:pand",
        "bag:ligplaats",
        "bag:verblijfsobject",
        "bag:woonplaats",
        "bag:standplaats",
    ] = "bag:pand",
    pagesize: Literal["10", "20", "50", "100", "1000"] = "1000",
) -> gpd.GeoDataFrame:
    """
    Get a GeoDataFrame with the default values for CUR166 and PrePal methode.

    Parameters
    ----------
    west:
        west coordinate in rd new (EPSG:28992)
    south:
        south coordinate in rd new (EPSG:28992)
    east:
        east coordinate in rd new (EPSG:28992)
    north:
        north coordinate in rd new (EPSG:28992)
    category:
        Building category based on the SBR A table 10.1.
    monumental:
        Has the building structure a monumental status. Based on the SBR A table 10.3.
    structural_condition:
        Based on the SBR A table 10.2.
    vibration_sensitive:
        Has the building structure a vibration sensitive foundation. Based on the SBR A chapter 10.2.5.
    thickness:
        Layer thickness settlement-sensitive layer [m]
    foundation_element:
        Based on CUR 166 3rd edition table 5.19
    material_floor:
        Based on CUR 166 3rd edition table 5.20
    feature:
        default is bag:pand
        item in the BAG, see https://www.nationaalgeoregister.nl/geonetwork/srv/dut/catalog.search#/metadata/1c0dcc64-91aa-4d44-a9e3-54355556f5e7
    pagesize:
        Results per page

    Returns
    -------
    gdf: gpd.GeoDataFrame
    """

    if west > east:
        raise ValueError("west coordinate is larger than east coordinate")

    if south > north:
        raise ValueError("south coordinate is larger than north coordinate")

    if east - west > THRESHOLD:
        raise ValueError(
            f"x dimension of the bbox is {east - west} meters, larger than threshold"
        )

    if north - south > THRESHOLD:
        raise ValueError(
            f"y dimension of the bbox is {north - south} meters, larger than threshold"
        )

    wfs_query_params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeName": feature,
        "srsname": "EPSG:28992",
        "outputFormat": "json",
        "bbox": str(west) + "," + str(south) + "," + str(east) + "," + str(north),
        "count": pagesize,
    }

    response = requests.get(
        url=BAG_WFS_URL,
        headers={"Content-Type": "application/json"},
        params=wfs_query_params,
        timeout=5,
    )
    if not response.ok:
        raise RuntimeError(response.text)

    gdf = gpd.read_file(json.dumps(response.json()), driver="GeoJSON").to_crs(
        "EPSG:28992"
    )

    # add default values
    gdf["name"] = gdf.index.astype(str)

    # sbr-A
    gdf["category"] = category
    gdf["structuralCondition"] = structural_condition
    gdf["vibrationSensitive"] = vibration_sensitive
    gdf["thickness"] = thickness
    gdf["monumental"] = monumental

    # prepal
    gdf["buildingDepth"] = np.clip(np.sqrt(gdf.area), 1.0, 18.0)
    gdf["buildingDepthVibrationSensitive"] = 1.0

    # cur166
    gdf["foundationElement"] = foundation_element
    gdf["material"] = material_floor

    return gdf


def create_prepal_payload(
    buildings: gpd.GeoDataFrame,
    location: Polygon | LineString | Point,
    pile_shape: Literal["square", "round"],
    pile_size: float,
    cone_resistance: float,
    reduction: float = 0.0,
    unit_weight: float = 20,
    elastic_modulus_factor: float = 15,
    poisson_ratio: float = 0.2,
    frequency: float = 20.0,
    vibration_type: Literal[
        "short-term", "repeated-short-term", "continuous"
    ] = "continuous",
    frequency_vibration_sensitive: float = 40.0,
    measurement_type: Literal["indicative", "limited", "extensive"] = "extensive",
    hysteretic_damping_barkan: float = -0.05,
):
    """
    Create payload for VibraCore call `cur166/validation/multi`

    Parameters
    ----------
    buildings
        GeoDataFrame that holds teh building information. Must have the following columns:
            - buildingDepth:
              The minimum building depth [m]
            - buildingDepthVibrationSensitive:
              The minimum building depth [m]
            - category
              Based on the SBR A table 10.1.
            - monumental
              Has the building structure a monumental status. Based on the SBR A table 10.3.
            - structuralCondition
              Based on the SBR A table 10.2.
            - thickness
              Layer thickness settlement-sensitive layer [m]
            - vibrationSensitive
              Has the building structure a vibration sensitive foundation. Based on the SBR A chapter 10.2.5.
    location:
        Location of the source
    poisson_ratio:
        Poisson’s ratio of the soil [-]
    elastic_modulus_factor:
        Elastic modulus factor of the soil [-].
    unit_weight:
        Volume weight of the soil [kN/m^3]
    cone_resistance:
        Cone resistance [MPa]
    reduction:
        Reduction of the cone resistance [%]
    pile_size:
        Size of the pile [m]
    pile_shape:
        Shape of the pile.
    frequency:
        The dominate frequency [Hz]
    vibration_type
        Based on the SBR A table 10.4.
    frequency_vibration_sensitive
        The dominate frequency for vibration sensitive building [Hz].
    measurement_type
        Type of measurement based on the SBR A table 9.2.
    hysteretic_damping_barkan:
        hysteretic damping barkan [m^-1]

    Returns
    -------
    payload: dict

    Raises
    -------
    KeyError:
        Missing column names in GeoDataFrame
    """
    columns = [
        "category",
        "structuralCondition",
        "vibrationSensitive",
        "thickness",
        "buildingDepth",
    ]
    if not set(columns).issubset(set(buildings.columns)):
        msg = (
            f"Column names:{list(set(columns) - set(buildings.columns))} must be in GeoDataFrame. "
            f"Found column names: {buildings.columns}"
        )
        raise KeyError(msg)

    payload = {
        "buildingInformation": [
            {
                "geometry": mapping(row.geometry),
                "metadata": {"ID": row.get("name", uuid.uuid4().__str__())},
                "properties_PrePal": {
                    "buildingDepth": row["buildingDepth"],
                    "buildingDepthVibrationSensitive": row.get(
                        "buildingDepthVibrationSensitive", 1
                    ),
                    "calculationHeight": None,
                },
                "properties_SBRa": {
                    "category": row["category"],
                    "frequency": frequency,
                    "frequencyVibrationSensitive": frequency_vibration_sensitive,
                    "monumental": row["monumental"],
                    "structuralCondition": row["structuralCondition"],
                    "thickness": row["thickness"],
                    "vibrationSensitive": row["vibrationSensitive"],
                    "vibrationType": vibration_type,
                },
            }
            for i, row in buildings.iterrows()
        ],
        "vibrationSource": {"shape": pile_shape, "size": pile_size},
        "soilProperties": {
            "coneResistance": cone_resistance * (100 - reduction) / 100,
            "elasticModulus": cone_resistance * elastic_modulus_factor,
            "poissonRatio": poisson_ratio,
            "unitWeight": unit_weight,
        },
        "prediction": {
            "hystereticDampingBarkan": hysteretic_damping_barkan,
            "measurementType": measurement_type,
        },
        "validation": {"sourceLocation": mapping(location)},
    }

    return payload


def create_cur166_payload(
    buildings: gpd.GeoDataFrame,
    location: Polygon | LineString | Point,
    force: float,
    reduction: float = 0,
    installation_type: Literal["vibrate", "driving"] = "vibrate",
    building_part: Literal["floor", "wall"] = "floor",
    safety_factor: float = 0.05,
    vibration_direction: Literal["vertical", "horizontal"] = "vertical",
    frequency: float = 30.0,
    vibration_type: Literal[
        "short-term", "repeated-short-term", "continuous"
    ] = "continuous",
    frequency_vibration_sensitive: float = 40.0,
    reference_location: Literal[
        "Amsterdam",
        "Maasvlakte",
        "Rotterdam",
        "Groningen",
        "Den Haag",
        "Tiel",
        "Eindhoven",
    ] = "Amsterdam",
    measurement_type: Literal["indicative", "limited", "extensive"] = "extensive",
    methode_safety_factor: Literal["CUR", "exact"] = "exact",
):
    """
    Create payload for VibraCore call `cur166/validation/multi`

    Parameters
    ----------
    buildings
        GeoDataFrame that holds teh building information. Must have the following columns:
            - foundationElement
              Based on CUR 166 3rd edition table 5.19
            - material
              Based on CUR 166 3rd edition table 5.20
            - category
              Based on the SBR A table 10.1.
            - monumental
              Has the building structure a monumental status. Based on the SBR A table 10.3.
            - structuralCondition
              Based on the SBR A table 10.2.
            - thickness
              Layer thickness settlement-sensitive layer [m]
            - vibrationSensitive
              Has the building structure a vibration sensitive foundation. Based on the SBR A chapter 10.2.5.
    location:
        Location of the source
    force:
        Impact force of the pile [kN]
    reduction:
        Reduction of impact [%]
    installation_type
        Based on CUR 166 3rd edition table 5.20 or 5.21
    building_part
        Based on CUR 166 3rd edition table 5.20 or 5.21
    safety_factor
        Based on CUR 166 3rd edition table 5.22
    vibration_direction
        Based on CUR 166 3rd edition table 5.22
    frequency:
        The dominate frequency [Hz]
    vibration_type
        Based on the SBR A table 10.4.
    frequency_vibration_sensitive
        The dominate frequency for vibration sensitive building [Hz].
        If not provided the frequency of 20 Hz is used for PrePal and 40
        for CUR 166 3rd edition high frequency vibration calculation.
    reference_location
        Based on CUR 166-1997 table 5.16 and 5.17
    measurement_type
        Type of measurement based on the SBR A table 9.2.
    methode_safety_factor
        Parameter that indicated how the safety factor is calculated.
        Find more info about the exact method here -> https://issuu.com/uitgeverijeducom/docs/geo_okt2014_totaal_v4_klein/36

    Returns
    -------
    payload: dict

    Raises
    -------
    ValueError:
        No reference values found for reference location
    KeyError:
        Missing column names in GeoDataFrame
    """
    reference = next(
        (
            item
            for item in SOIL_REFERENCE
            if item["location"] == reference_location
            and item["method"] == installation_type
            and item["vibration_direction"] == vibration_direction
        ),
        None,
    )

    if reference is None:
        raise ValueError(
            f"No reference values found for reference location: {reference_location}"
            f"with installation type: {installation_type} and vibration direction: {vibration_direction}."
        )

    columns = [
        "foundationElement",
        "material",
        "category",
        "monumental",
        "structuralCondition",
        "thickness",
        "vibrationSensitive",
    ]
    if not set(columns).issubset(set(buildings.columns)):
        msg = (
            f"Column names:{list(set(columns) - set(buildings.columns))} must be in GeoDataFrame. "
            f"Found column names: {buildings.columns}"
        )
        raise KeyError(msg)

    payload = {
        "buildingInformation": [
            {
                "geometry": mapping(row.geometry),
                "metadata": {"ID": row.get("name", uuid.uuid4().__str__())},
                "properties_CUR": {
                    "buildingPart": building_part,
                    "foundationElement": row["foundationElement"],
                    "installationType": installation_type,
                    "material": row["material"],
                    "safetyFactor": safety_factor,
                    "vibrationDirection": vibration_direction,
                },
                "properties_SBRa": {
                    "category": row["category"],
                    "frequency": frequency,
                    "frequencyVibrationSensitive": frequency_vibration_sensitive,
                    "monumental": row["monumental"],
                    "structuralCondition": row["structuralCondition"],
                    "thickness": row["thickness"],
                    "vibrationSensitive": row["vibrationSensitive"],
                    "vibrationType": vibration_type,
                },
            }
            for _, row in buildings.iterrows()
        ],
        "prediction": {
            "hystereticDampingBarkan": reference["Uo"],
            "force": force * (100 - reduction) / 100,
            "measurementType": measurement_type,
            "methodeSafetyFactor": methode_safety_factor,
            "referencesVelocity": reference["Vo"],
            "variationCoefficient": reference["alpha"],
        },
        "validation": {"sourceLocation": mapping(location)},
    }

    return payload


def get_normative_building(
    buildings: gpd.GeoDataFrame,
    location: Polygon | LineString | Point,
    category: Literal["one", "two"],
) -> str | None:
    """
    Get the name of the closest building

    Parameters
    ----------
    buildings:
        GeoDataFrame that holds the building information
    location:
        Geometry of the source location
    category:
        building category based on the SBR A table 10.1.

    Returns
    -------
    name: str
    """
    gdf = buildings.get(buildings["category"] == category)
    if gdf.empty:
        logging.error(f"ValueError: No buildings with category {category}.")
        return None
    gdf["distance"] = gdf.distance(location)
    return gdf.sort_values("distance", na_position="last").iloc[0].get("name")


def create_single_payload(
    multi_vibration_payload: dict,
    name: str,
) -> dict:
    """
    Create payload for VibraCore call `cur166/validation/single` or `prepal/validation/single`

    Parameters
    ----------
    multi_vibration_payload:
        result from `create_cur166_payload` or `create_prepal_payload`
    name:
        building name

    Returns
    -------
    payload: dict
    """
    payload = deepcopy(multi_vibration_payload)

    props = next(
        (
            item
            for item in payload["buildingInformation"]
            if item["metadata"]["ID"] == name
        ),
        None,
    )
    if props is None:
        raise ValueError(f"{name} is not a valid building name.")
    payload.update(dict(buildingInformation=props))

    return payload


def create_vibration_report_payload(
    multi_vibration_payload: dict,
    project_name: str,
    project_id: str,
    author: str,
) -> dict:
    """
    Creates a dictionary with the payload content for the VibraCore endpoint
    "/cur166/report" or "/prepal/report"

    This dictionary can be passed directly to `nuclei.client.call_endpoint()`.

    Parameters
    ----------
    vibration_payload:
        The result of a call to `create_cur166_payload()` or `create_prepal_payload()`
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
    payload = deepcopy(multi_vibration_payload)
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
