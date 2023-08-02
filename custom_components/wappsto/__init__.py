"""The Wappsto integration."""
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.typing import ConfigType

from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.const import EVENT_SERVICE_REGISTERED
from homeassistant.const import STATE_ON
from homeassistant.const import STATE_OFF

from .const import (
    NETWORK_UUID,
    DOMAIN,
    # GATEWAY_SERIAL_PATTERN,
    PLATFORMS,
    STARTUP_MESSAGE,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    _LOGGER.error("async_setup")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""

    _LOGGER.error("async_setup_entry")

    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    _LOGGER.error("async_unload_entry")

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    _LOGGER.error("async_reload_entry")
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)