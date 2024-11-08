"""The Wappsto integration."""
from pathlib import Path
import logging
import os
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import async_generate_entity_id, DeviceInfo
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.const import EVENT_SERVICE_REGISTERED
from homeassistant.const import CONF_API_KEY, CONF_NAME, Platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .wappstoapi import WappstoApi
from .const import (
    DOMAIN,
    ENTITY_LIST,
)
from .binary_sensor import wappsto_connected_sensor
from .setup_network import (
    create_certificaties_files_if_not_exist,
    delete_certificate_files,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up this integration using YAML is not supported."""
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

    _LOGGER.info("STARTUP config: [%s]", entry.options)
    entry.async_on_unload(entry.add_update_listener(update_listener))
    wappstoApi = WappstoApi(hass, entity_list=options[ENTITY_LIST])
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = wappstoApi

    await hass.config_entries.async_forward_entry_setup(entry, Platform.BINARY_SENSOR)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    _LOGGER.info("Async_unload_entry - disconnect and clear certificates")
    wappstoApi = hass.data[DOMAIN][entry.entry_id]
    wappstoApi.close()
    delete_certificate_files()
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    _LOGGER.info("Async_reload_entry")
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
    # return True
