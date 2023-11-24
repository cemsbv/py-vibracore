import logging
from time import sleep

from nuclei.client import NucleiClient
from requests import Response


def wait_until_ticket_is_ready(client: NucleiClient, ticket: Response) -> None:
    if ticket.status_code != 200:
        raise RuntimeError(rf"{ticket.text}")

    status = "STARTED"
    sleep_time = 0.05
    while status in ["PENDING", "STARTED", "RETRY"]:
        sleep_time = min(sleep_time * 2, 10)
        sleep(sleep_time)
        response = client.call_endpoint(
            "VibraCore", "/get-task-status", schema=ticket.json(), return_response=True
        )
        if response.status_code != 200:
            raise RuntimeError(rf"{response.text}")
        status = response.json()["state"]

    if status == "FAILURE":
        raise RuntimeError(
            f'{response.json().get("msg")}\n{response.json().get("traceback")}'
        )


def get_impact_force_report(client: NucleiClient, payload: dict) -> bytes:
    """
    Wrapper around the VibraCore endpoint "/impact-force/report".

    Parameters
    ----------
    client: NucleiClient
        client object created by [nuclei](https://github.com/cemsbv/nuclei)
    payload: dict
        the payload of the request, can be created by calling `create_multi_cpt_impact_force_report_payload()`
    """
    logging.info(
        "Generate report... \n"
        "Depending on the amount of CPT's this can take a while."
    )
    ticket = client.call_endpoint(
        "VibraCore",
        "/impact-force/report",
        schema=payload,
        return_response=True,
    )

    wait_until_ticket_is_ready(client=client, ticket=ticket)

    return client.call_endpoint("VibraCore", "/get-task-results", schema=ticket.json())


def get_impact_force_calculation(client: NucleiClient, payload: dict) -> bytes:
    """
    Wrapper around the VibraCore endpoint "/impact-force/calculation/multi".

    Parameters
    ----------
    client: NucleiClient
        client object created by [nuclei](https://github.com/cemsbv/nuclei)
    payload: dict
        the payload of the request, can be created by calling `create_multi_cpt_impact_force_payload()`
    """
    logging.info(
        "Calculation impact force... \n"
        "Depending on the amount of CPT's this can take a while."
    )
    ticket = client.call_endpoint(
        "VibraCore",
        "/impact-force/calculation/multi",
        schema=payload,
        return_response=True,
    )

    wait_until_ticket_is_ready(client=client, ticket=ticket)

    return client.call_endpoint("VibraCore", "/get-task-results", schema=ticket.json())


def get_prepal_calculation(client: NucleiClient, payload: dict) -> bytes:
    """
    Wrapper around the VibraCore endpoint "/prepal/validation/multi".

    Parameters
    ----------
    client: NucleiClient
        client object created by [nuclei](https://github.com/cemsbv/nuclei)
    payload: dict
        the payload of the request, can be created by calling `create_prepal_payload()`
    """
    logging.info(
        "Prepal prediction... \n"
        "Depending on the amount of buildings this can take a while."
    )
    ticket = client.call_endpoint(
        "VibraCore",
        "/prepal/validation/multi",
        schema=payload,
        return_response=True,
    )

    wait_until_ticket_is_ready(client=client, ticket=ticket)

    return client.call_endpoint("VibraCore", "/get-task-results", schema=ticket.json())


def get_cur166_calculation(client: NucleiClient, payload: dict) -> bytes:
    """
    Wrapper around the VibraCore endpoint "/cur166/validation/multi".

    Parameters
    ----------
    client: NucleiClient
        client object created by [nuclei](https://github.com/cemsbv/nuclei)
    payload: dict
        the payload of the request, can be created by calling `create_cur166_payload()`
    """
    logging.info(
        "CUR166 prediction... \n"
        "Depending on the amount of buildings this can take a while."
    )
    ticket = client.call_endpoint(
        "VibraCore",
        "/cur166/validation/multi",
        schema=payload,
        return_response=True,
    )

    wait_until_ticket_is_ready(client=client, ticket=ticket)

    return client.call_endpoint("VibraCore", "/get-task-results", schema=ticket.json())


def get_cur166_report(client: NucleiClient, payload: dict) -> bytes:
    """
    Wrapper around the VibraCore endpoint "/cur166/report".

    Parameters
    ----------
    client: NucleiClient
        client object created by [nuclei](https://github.com/cemsbv/nuclei)
    payload: dict
        the payload of the request, can be created by calling `create_vibration_report_payload()`
    """
    logging.info(
        "Generate report... \n"
        "Depending on the amount of buildings this can take a while."
    )
    ticket = client.call_endpoint(
        "VibraCore",
        "/cur166/report",
        schema=payload,
        return_response=True,
    )

    wait_until_ticket_is_ready(client=client, ticket=ticket)

    return client.call_endpoint("VibraCore", "/get-task-results", schema=ticket.json())


def get_prepal_report(client: NucleiClient, payload: dict) -> bytes:
    """
    Wrapper around the VibraCore endpoint "/cur166/report".

    Parameters
    ----------
    client: NucleiClient
        client object created by [nuclei](https://github.com/cemsbv/nuclei)
    payload: dict
        the payload of the request, can be created by calling `create_vibration_report_payload()`
    """
    logging.info(
        "Generate report... \n"
        "Depending on the amount of buildings this can take a while."
    )
    ticket = client.call_endpoint(
        "VibraCore",
        "/prepal/report",
        schema=payload,
        return_response=True,
    )

    wait_until_ticket_is_ready(client=client, ticket=ticket)

    return client.call_endpoint("VibraCore", "/get-task-results", schema=ticket.json())
