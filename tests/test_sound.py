import matplotlib.pyplot as plt

from pyvibracore.input.vibration_properties import (
    BAG_WFS_URL,
    get_buildings_geodataframe,
)
from pyvibracore.results.sound_result import get_normative_building, map_sound


def test_map_sound(requests_mock, mock_bag_response, mock_source_location):
    requests_mock.get(BAG_WFS_URL, json=mock_bag_response)
    gdf = get_buildings_geodataframe(1, 2, 3, 4)

    fig = map_sound(
        gdf,
        source_location=mock_source_location,
        building_name="0",
        power=140,
        k2=5,
        period=5,
    )

    plt.savefig("tpm.png")

    assert isinstance(fig, plt.Figure)


def test_get_normative_building(requests_mock, mock_bag_response, mock_source_location):
    requests_mock.get(BAG_WFS_URL, json=mock_bag_response)
    gdf = get_buildings_geodataframe(1, 2, 3, 4)

    name = get_normative_building(
        gdf,
        location=mock_source_location,
    )

    assert isinstance(name, str)
