SHEETPILE_REFERENCE_PROFILES = [
    {"label": "AZ12-770", "area_tip_specific": 0.00925, "area_shaft_specific": 1.86},
    {"label": "AZ13-770", "area_tip_specific": 0.00969, "area_shaft_specific": 1.86},
    {"label": "AZ14-770", "area_tip_specific": 0.01013, "area_shaft_specific": 1.86},
    {"label": "AZ12-700", "area_tip_specific": 0.00862, "area_shaft_specific": 1.72},
    {"label": "AZ13-700", "area_tip_specific": 0.00943, "area_shaft_specific": 1.72},
    {"label": "AZ14-700", "area_tip_specific": 0.01023, "area_shaft_specific": 1.72},
    {"label": "AZ17-700", "area_tip_specific": 0.00931, "area_shaft_specific": 1.86},
    {"label": "AZ18-700", "area_tip_specific": 0.00975, "area_shaft_specific": 1.86},
    {"label": "AZ19-700", "area_tip_specific": 0.01019, "area_shaft_specific": 1.86},
    {"label": "AZ20-700", "area_tip_specific": 0.01064, "area_shaft_specific": 1.86},
    {"label": "AZ24-700", "area_tip_specific": 0.01219, "area_shaft_specific": 1.94},
    {"label": "AZ26-700", "area_tip_specific": 0.0131, "area_shaft_specific": 1.94},
    {"label": "AZ28-700", "area_tip_specific": 0.01402, "area_shaft_specific": 1.94},
    {"label": "AZ36-700N", "area_tip_specific": 0.01511, "area_shaft_specific": 2.06},
    {"label": "AZ38-700N", "area_tip_specific": 0.0161, "area_shaft_specific": 2.06},
    {"label": "AZ40-700N", "area_tip_specific": 0.01709, "area_shaft_specific": 2.06},
    {"label": "AZ42-700N", "area_tip_specific": 0.01811, "area_shaft_specific": 2.06},
    {"label": "AZ44-700N", "area_tip_specific": 0.0191, "area_shaft_specific": 2.06},
    {"label": "AZ46-700N", "area_tip_specific": 0.02009, "area_shaft_specific": 2.06},
    {"label": "AZ48-700", "area_tip_specific": 0.02019, "area_shaft_specific": 2.04},
    {"label": "AZ50-700", "area_tip_specific": 0.02118, "area_shaft_specific": 2.04},
    {"label": "AZ52-700", "area_tip_specific": 0.02217, "area_shaft_specific": 2.04},
    {"label": "PU18-1", "area_tip_specific": 0.00925, "area_shaft_specific": 1.74},
    {"label": "PU18+1", "area_tip_specific": 0.01034, "area_shaft_specific": 1.74},
    {"label": "PU22-1", "area_tip_specific": 0.01043, "area_shaft_specific": 1.80},
    {"label": "PU22+1", "area_tip_specific": 0.01152, "area_shaft_specific": 1.80},
    {"label": "PU28-1", "area_tip_specific": 0.01241, "area_shaft_specific": 1.86},
    {"label": "PU28+1", "area_tip_specific": 0.01353, "area_shaft_specific": 1.86},
    {"label": "PU32-1", "area_tip_specific": 0.014, "area_shaft_specific": 1.84},
    {"label": "PU32+1", "area_tip_specific": 0.01508, "area_shaft_specific": 1.84},
    {"label": "PU12", "area_tip_specific": 0.00842, "area_shaft_specific": 1.60},
    {"label": "PU12S", "area_tip_specific": 0.00905, "area_shaft_specific": 1.60},
    {"label": "PU22", "area_tip_specific": 0.01097, "area_shaft_specific": 1.80},
    {"label": "PU18", "area_tip_specific": 0.0098, "area_shaft_specific": 1.74},
    {"label": "PU32", "area_tip_specific": 0.01454, "area_shaft_specific": 1.84},
    {"label": "PU28", "area_tip_specific": 0.01297, "area_shaft_specific": 1.86},
]

SOIL_REFERENCE = [
    # CUR 166-1997 Tabel 5.16 parameters voor het inheien buispalen
    {
        "location": "Amsterdam",
        "method": "driving",
        "vibration_direction": "vertical",
        "Uo": 0.03,
        "alpha": 0.03,
        "Vo": 0.6,
    },
    {
        "location": "Maasvlakte",
        "method": "driving",
        "vibration_direction": "vertical",
        "Uo": 0.04,
        "alpha": 0.02,
        "Vo": 0.6,
    },
    {
        "location": "Rotterdam",
        "method": "driving",
        "vibration_direction": "vertical",
        "Uo": 0.017,
        "alpha": 0.03,
        "Vo": 0.6,
    },
    {
        "location": "Rotterdam",
        "method": "driving",
        "vibration_direction": "horizontal",
        "Uo": 0.026,
        "alpha": 0.03,
        "Vo": 0.6,
    },
    # CUR 166-1997 Tabel 5.17 Parameters voor het intrillen van stale planken (tot 14 meter)
    {
        "location": "Amsterdam",
        "method": "vibrate",
        "vibration_direction": "vertical",
        "Uo": 1.1,
        "alpha": 0.02,
        "Vo": 0.9,
    },
    {
        "location": "Amsterdam",
        "method": "vibrate",
        "vibration_direction": "horizontal",
        "Uo": 1.6,
        "alpha": 0.02,
        "Vo": 1.5,
    },
    {
        "location": "Eindhoven",
        "method": "vibrate",
        "vibration_direction": "vertical",
        "Uo": 1.9,
        "alpha": 0.02,
        "Vo": 1.1,
    },
    {
        "location": "Eindhoven",
        "method": "vibrate",
        "vibration_direction": "horizontal",
        "Uo": 2.6,
        "alpha": 0.02,
        "Vo": 0.8,
    },
    {
        "location": "Groningen",
        "method": "vibrate",
        "vibration_direction": "vertical",
        "Uo": 1.7,
        "alpha": 0.02,
        "Vo": 1.8,
    },
    {
        "location": "Groningen",
        "method": "vibrate",
        "vibration_direction": "horizontal",
        "Uo": 0.9,
        "alpha": 0.02,
        "Vo": 0.5,
    },
    {
        "location": "Den Haag",
        "method": "vibrate",
        "vibration_direction": "vertical",
        "Uo": 1.9,
        "alpha": 0.02,
        "Vo": 1.1,
    },
    {
        "location": "Den Haag",
        "method": "vibrate",
        "vibration_direction": "horizontal",
        "Uo": 2.6,
        "alpha": 0.02,
        "Vo": 0.8,
    },
    {
        "location": "Rotterdam",
        "method": "vibrate",
        "vibration_direction": "vertical",
        "Uo": 1.1,
        "alpha": 0.02,
        "Vo": 0.9,
    },
    {
        "location": "Rotterdam",
        "method": "vibrate",
        "vibration_direction": "horizontal",
        "Uo": 1.6,
        "alpha": 0.02,
        "Vo": 1.5,
    },
    {
        "location": "Tiel",
        "method": "vibrate",
        "vibration_direction": "vertical",
        "Uo": 1.1,
        "alpha": 0.02,
        "Vo": 0.9,
    },
    {
        "location": "Tiel",
        "method": "vibrate",
        "vibration_direction": "horizontal",
        "Uo": 1.6,
        "alpha": 0.02,
        "Vo": 1.5,
    },
]
