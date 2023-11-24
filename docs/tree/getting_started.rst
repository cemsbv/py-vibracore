Installing py-vibracore
=======================
To install :code:`pyvibracore`, we strongly recommend using Python Package Index (PyPI).
You can install :code:`pyvibracore` with:

.. code-block:: python

    pip install py-vibracore[notebook]

We installed the `notebook` variant of :code:`pyvibracore` which include additional dependencies,
and thereby enable additional functionality.


Risk of damage during construction [SBR-A]
===========================================

VibraCore is an API service based on a Python library that automates the risk management
of building damage during vibration works, such as the installation of sheet piles or driven piles.
Based on the attributes of the nearby buildings the failure vibration velocity is
calculated (according to SBR A). If the check fails the building has a unacceptable risk (according to SBR A) of
being damaged by the installation of the piles or sheet piles.

- Building properties CUR166 or PrePal + SBR-A
- Data (vibration) source
- Soil properties data

A `jupyter notebook` that guides you through this steps can be found at :file:`/notebooks/NBxxxxx_SBRA.ipynb`

Impact force determination [CUR166]
====================================

Based on the soil profile (GEF file) the maximum impact force is calculated (according to CUR 166 3rd edition).
This is used to predict the maximum vibration velocity.

- Cone Penetration Test (CPT)
- Soil properties (classification)
- Pile properties and installation method

A `jupyter notebook` that guides you through this steps can be found at :file:`notebooks/NBxxxxx_impact_force.ipynb`

Guided usage
============

Getting started with pyvibracore is easy done by importing the :code:`pyvibracore` library:

.. ipython:: python

    import pyvibracore

or any equivalent :code:`import` statement.

Create payload
---------------

If you’re not so comfortable with creating your own schema’s the SDK provides usefully
functions to creates a dictionary with the payload content for the VibraCore endpoints.
You can find the function at :code:`pyvibracore.input`. Please read the reference page for more
information:

- :ref:`impactForceInput`
- :ref:`SBRAInput`
- :ref:`PerPalInput`
- :ref:`CUR166Input`

.. code-block:: python

    from pyvibracore.input.vibration_properties import (
        create_cur166_payload, get_buildings_geodataframe
    )

    buildings = get_buildings_geodataframe(
        west, south, east, north
    )

    location = Point[[x, y]]

    payload = create_cur166_payload(
        buildings,
        location,
        force=500
    )

Call endpoint
--------------

With the created payload and :code:`nuclei.client` it is possible to create a request.
SDK provides functions to assist with this process:

- :ref:`API`

.. code-block:: python

    from nuclei.client import NucleiClient
    from pyvibracore import api

    client = NucleiClient()
    response = api.get_cur166_calculation(client, payload=multi_vibration_payload)

Create results
...............

To help the user with generating tables and plots based on the response
of the API call the SDK provides classes that store the data in a structured
way.

- :ref:`impactForceResult`
- :ref:`SBRAResult`


.. code-block:: python

    from pyvibracore.results.vibration_result import VibrationResults

    results = VibrationResults.from_api_response(response)