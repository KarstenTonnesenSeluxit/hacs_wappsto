import json
from pathlib import Path
import uuid
import logging
import requests

_LOGGER = logging.getLogger(__name__)


def get_session(username, password):
    session_json = {"username": username, "password": password, "remember_me": False}

    url = f"https://wappsto.com/services/session"
    headers = {"Content-type": "application/json"}
    data = json.dumps(session_json)

    rdata = requests.post(url=url, headers=headers, data=data)

    if rdata.status_code >= 300:
        _LOGGER.error("An error occurred during login")
        return None

    rjson = json.loads(rdata.text)
    _LOGGER.info(rjson)
    return rjson["meta"]["id"]


def create_network(session):
    request = {}

    url = f"https://wappsto.com/services/2.1/creator"
    headers = {"Content-type": "application/json", "X-session": str(session)}
    data = json.dumps(request)
    rdata = requests.post(url=url, headers=headers, data=data)

    if rdata.status_code >= 300:
        _LOGGER.error("An error occurred during Certificate retrieval")
        return None
    rjson = json.loads(rdata.text)
    _LOGGER.info("Certificate generated for new network")
    return rjson


def claim_network(session, network_uuid, dry_run=False):
    url = f"https://wappsto.com/services/2.0/network/{network_uuid}"
    headers = {"Content-type": "application/json", "X-session": str(session)}
    rdata = requests.post(url=url, headers=headers, data="{}")

    if rdata.status_code >= 300:
        _LOGGER.error("An error occurred during claiming the network")
        return None

    rjson = json.loads(rdata.text)
    _LOGGER.info("Network: %s have been claimed", network_uuid)
    return rjson


def create_certificaties_files(creator):
    # creator["ca"], creator["certificate"], creator["private_key"]
    location = Path("./config/custom_components/wappsto")
    location.mkdir(exist_ok=True)
    try:
        with open(location / "ca.crt", "w") as file:
            file.write(creator["ca"])
        with open(location / "client.crt", "w") as file:
            file.write(creator["certificate"])
        with open(location / "client.key", "w") as file:
            file.write(creator["private_key"])
        return True
    except Exception as err:
        _LOGGER.error("An error occurred while saving Certificates: %s", err)
        return False
