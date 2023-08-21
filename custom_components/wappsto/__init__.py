"""The Wappsto integration."""
from pathlib import Path
import logging
import os
from datetime import timedelta

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import async_generate_entity_id, DeviceInfo
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.typing import ConfigType

from homeassistant.components import is_on
from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.const import EVENT_SERVICE_REGISTERED
from homeassistant.helpers.entity_platform import AddEntitiesCallback

import wappstoiot

from .wappstoapi import WappstoApi

from .const import (
    NETWORK_UUID,
    DOMAIN,
    STARTUP_MESSAGE,
    ENTITY_LIST,
    CA_CRT_KEY,
    CLIENT_CRT_KEY,
    CLIENT_KEY_KEY,
)

from .binary_sensor import wappsto_connected_sensor
from .setup_network import create_certificaties_files_if_not_exist


from homeassistant.const import CONF_API_KEY, CONF_NAME, Platform

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up this integration using YAML is not supported."""
    _LOGGER.info("Configflow async_setup is this supported? no, but must return True")

    _LOGGER.error("CONFIG STARTT [%s]", config)

    return True


async def update_listener(hass, entry):
    """Handle options update."""
    _LOGGER.error("UPDATE CONFIG NOT HANDLED: [%s]", entry.options)
    hass.data[DOMAIN][entry.entry_id].updateEntityList(entry.options[ENTITY_LIST])


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    conf = entry.data
    options = entry.options

    _LOGGER.info("Async_setup_entry")
    # _LOGGER.warning("Configuration received: %s", conf)

    saved_files = await hass.async_add_executor_job(
        create_certificaties_files_if_not_exist, conf
    )
    if not saved_files:
        _LOGGER.error("Certificate files not found")

    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.warning(STARTUP_MESSAGE)

    _LOGGER.info("STARTUP config: [%s]", entry.options)
    entry.async_on_unload(entry.add_update_listener(update_listener))

    wappstoApi = WappstoApi(hass, entity_list=options[ENTITY_LIST])
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = wappstoApi

    await hass.config_entries.async_forward_entry_setup(entry, Platform.BINARY_SENSOR)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    _LOGGER.error("Async_unload_entry - not handled yet")
    # listener = (lambda *args, **kwargs: wappstoiot.close(),)
    # try:
    #     os.remove("./config/custom_components/wappsto/ca.crt")
    #     os.remove("./config/custom_components/wappsto/client.key")
    #     os.remove("./config/custom_components/wappsto/client.crt")
    # except OSError as e:  # this would be "except OSError, e:" before Python 2.6
    #     # if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
    #     #    raise  # re-raise exception if a different error occurred
    #     _LOGGER.warning("Deleting files response %s", e)
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    _LOGGER.info("Async_reload_entry")
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
    # return True
