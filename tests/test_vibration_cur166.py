import geopandas as gpd
import pytest

from pyvibracore.input.vibration_properties import (
    BAG_WFS_URL,
    create_cur166_payload,
    create_single_payload,
    get_buildings_geodataframe,
    get_normative_building,
)


def test_get_buildings_geodataframe(requests_mock, mock_bag_response):
    requests_mock.get(BAG_WFS_URL, json=mock_bag_response)

    gdf = get_buildings_geodataframe(1, 2, 3, 4)

    assert isinstance(gdf, gpd.GeoDataFrame)


def test_create_cur166_payload(requests_mock, mock_bag_response, mock_source_location):
    requests_mock.get(BAG_WFS_URL, json=mock_bag_response)
    gdf = get_buildings_geodataframe(1, 2, 3, 4)

    create_cur166_payload(
        gdf,
        location=mock_source_location,
        force=500,
    )

    with pytest.raises(ValueError):
        create_cur166_payload(
            gdf, location=mock_source_location, force=500, reference_location="Utrecht"
        )


def test_get_normative_building(requests_mock, mock_bag_response, mock_source_location):
    requests_mock.get(BAG_WFS_URL, json=mock_bag_response)
    gdf = get_buildings_geodataframe(1, 2, 3, 4)
    name = get_normative_building(
        gdf,
        location=mock_source_location,
        category="two",
    )

    assert isinstance(name, str)


def test_create_single_payload(requests_mock, mock_bag_response, mock_source_location):
    requests_mock.get(BAG_WFS_URL, json=mock_bag_response)
    gdf = get_buildings_geodataframe(1, 2, 3, 4)

    payload = create_cur166_payload(
        gdf,
        location=mock_source_location,
        force=500,
    )

    create_single_payload(payload, name="0")

    with pytest.raises(ValueError):
        create_single_payload(payload, name="-1")
