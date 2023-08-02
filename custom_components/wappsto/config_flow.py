import logging

from homeassistant import config_entries
from .const import DOMAIN
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_HOST,
    CONF_NAME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

class WappstoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""
    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    _LOGGER.error("ConfigFlow TEST WappstoConfigFlow")
    VERSION = 1

    def __init__(self):
        _LOGGER.warning("Init ConfibFLow")

class WappstoOptionsConfigFlow(config_entries.Optionsflow)
    _LOGGER.error("ConfigFlow TEST WappstooptionsConfigFlow")

    def __init__(self):
        _LOGGER.warning("Init OptionsConfigFlow")

