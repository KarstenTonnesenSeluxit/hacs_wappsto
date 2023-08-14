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

import wappstoiot

from .const import (
    NETWORK_UUID,
    DOMAIN,
    # GATEWAY_SERIAL_PATTERN,
    PLATFORMS,
    STARTUP_MESSAGE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up this integration using YAML is not supported."""
    _LOGGER.error("Configflow async_setup is this supported? no, but must return True")

    wappstoiot.config(
        config_folder="./config/custom_components/wappsto",
        fast_send=False,
    )
    network = wappstoiot.createNetwork(name="HomeAssistant")

    def event_handler(event):
        entity_id = event.data.get("entity_id", "")

    def event_started(event):
        domain = event.data["domain"]
        _LOGGER.warning("Event started, domain: %s [%s]", domain, event)

    hass.bus.async_listen(event_type=EVENT_STATE_CHANGED, listener=event_handler)
    hass.bus.async_listen(  # NOTE: et it to work to create the value!!
        event_type=EVENT_SERVICE_REGISTERED, listener=event_started
    )

    hass.bus.async_listen(
        event_type=EVENT_HOMEASSISTANT_STOP,
        listener=lambda *args, **kwargs: wappstoiot.close(),
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    conf = entry.data
    options = entry.options

    _LOGGER.warning("Async_setup_entry")
    # _LOGGER.warning("Configuration received: %s", conf)

    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.warning(STARTUP_MESSAGE)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    _LOGGER.error("Async_unload_entry")
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    _LOGGER.error("Async_reload_entry")
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
    return True
