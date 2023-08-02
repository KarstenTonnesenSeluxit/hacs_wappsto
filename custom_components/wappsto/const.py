"""Constants for the Wappsto integration."""
from typing import List

from homeassistant.const import Platform


DOMAIN = "wappsto"

DEFAULT_url = "https://wappsto.com"
PLATFORMS: List[Platform] = []
NETWORK_UUID = "network_uuid"
# SUPPORTED_MODEL_TYPES = ["2600", "2601"]

NAME = "TEST NAME"

VERSION = "0.0.1"
STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""