import json

import pygef
import pytest
from pygef.cpt import CPTData
from shapely.geometry import Polygon


@pytest.fixture
def mock_classify_response() -> dict:
    with open("tests/response/classify_response.json", "r") as file:
        data = json.load(file)
    return data


@pytest.fixture
def cpt() -> CPTData:
    return pygef.read_cpt("tests/data/cpt.gef", engine="gef")


@pytest.fixture
def mock_impact_force_response() -> dict:
    with open("tests/response/impact_force_response.json", "r") as file:
        data = json.load(file)
    return data


@pytest.fixture
def mock_bag_response() -> dict:
    with open("tests/response/bag_response.json", "r") as file:
        data = json.load(file)
    return data


@pytest.fixture
def mock_source_location() -> Polygon:
    return Polygon(
        [
            [120434.347344895664719, 486290.957240115036257],
            [120492.474963364205905, 486244.753235691343434],
            [120492.474963364205905, 486244.753235691343434],
            [120541.659871299110819, 486145.638193943712395],
            [120434.347344895664719, 486290.957240115036257],
        ]
    )
