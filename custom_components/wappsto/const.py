"""Constants for the Wappsto integration."""
from typing import List

from homeassistant.const import Platform


DOMAIN = "wappsto"
WAPPSTO_HAS_BEEN_SETUP = "wappsto_uniqe_string"

DEFAULT_url = "https://wappsto.com"

NETWORK_UUID = "network_uuid"
ENTITY_LIST = "entities"
# SUPPORTED_MODEL_TYPES = ["2600", "2601"]

NAME = "TEST NAME"

VERSION = "0.0.1"
STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to do stufff
-------------------------------------------------------------------
"""

SUPPORTED_DOMAINS = [
    # "alarm_control_panel",
    # "automation",
    "binary_sensor",
    "button",
    "climate",
    # "cover",
    # "device_tracker",
    # "fan",
    # "humidifier",
    "input_boolean",
    "input_button",
    # "input_select",
    "light",
    # "lock",
    "person",
    # "scene",
    # "script",
    # "select",
    "sensor",
    "switch",
    # "vacuum",
    # "water_heater",
]
