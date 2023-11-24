
Reference
=========

.. _API:
Application programming interface (API)
---------------------------------------

.. autofunction:: pyvibracore.api.get_impact_force_report

.. autofunction:: pyvibracore.api.get_impact_force_calculation

.. autofunction:: pyvibracore.api.get_prepal_calculation

.. autofunction:: pyvibracore.api.get_cur166_calculation

.. autofunction:: pyvibracore.api.get_cur166_report

.. autofunction:: pyvibracore.api.get_prepal_report


Impact Force
-------------

.. _impactForceInput:
Input
~~~~~~

.. autofunction:: pyvibracore.input.impact_force_properties.create_multi_cpt_impact_force_payload

.. autofunction:: pyvibracore.input.impact_force_properties.create_multi_cpt_impact_force_report_payload

.. autofunction:: pyvibracore.input.impact_force_properties.create_single_cpt_impact_force_payload

.. _impactForceResult:
Result
~~~~~~

.. autoclass:: pyvibracore.results.impact_force_result.MultiCalculationData
    :members:
    :inherited-members:
    :member-order: bysource

    .. automethod:: __init__


.. autoclass:: pyvibracore.results.impact_force_result.SingleCalculationData
    :members:
    :inherited-members:
    :member-order: bysource

    .. automethod:: __init__



SBR-A
------

.. _SBRAInput:
Input
~~~~~~

.. autofunction:: pyvibracore.input.vibration_properties.get_buildings_geodataframe

.. autofunction:: pyvibracore.input.vibration_properties.get_normative_building

.. autofunction:: pyvibracore.input.vibration_properties.create_single_payload

.. autofunction:: pyvibracore.input.vibration_properties.create_vibration_report_payload

.. _PerPalInput:
PerPal
"""""""

.. autofunction:: pyvibracore.input.vibration_properties.create_prepal_payload

.. _CUR166Input:
CUR166
"""""""

.. autofunction:: pyvibracore.input.vibration_properties.create_cur166_payload

.. _SBRAResult:
Result
~~~~~~

.. autoclass:: pyvibracore.results.vibration_result.VibrationResults
    :members:
    :inherited-members:
    :member-order: bysource

    .. automethod:: __init__


.. autofunction:: pyvibracore.results.vibration_result.map_payload

.. autofunction:: pyvibracore.results.vibration_result.plot_reduction


Sound
------

.. autofunction:: pyvibracore.results.sound_result.get_normative_building

.. autofunction:: pyvibracore.results.sound_result.map_sound