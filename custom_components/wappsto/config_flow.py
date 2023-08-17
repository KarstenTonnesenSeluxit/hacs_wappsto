import logging
import voluptuous as vol
from typing import Any, Dict, Optional

from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from homeassistant.helpers import (
    device_registry as dr,
    entity_registry as er,
)

from homeassistant import config_entries, exceptions
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import (
    CONF_UUID,
    CONF_EMAIL,
    CONF_PASSWORD,
)
from homeassistant.helpers.entity_registry import (
    async_entries_for_config_entry,
    async_get,
)
from homeassistant.const import (
    ATTR_FRIENDLY_NAME,
    ATTR_DEVICE_CLASS,
)
from .const import DOMAIN, ENTITY_LIST, SUPPORTED_DOMAINS, WAPPSTO_HAS_BEEN_SETUP


from config.custom_components.wappsto.setup_network import (
    get_session,
    create_network,
    claim_network,
    create_certificaties_files,
)

_LOGGER = logging.getLogger(__name__)

NETWORK_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, str]:
    session = await hass.async_add_executor_job(
        get_session,
        data[CONF_EMAIL],
        data[CONF_PASSWORD],
    )
    if not session:
        raise InvalidLogin

    _LOGGER.error("WHAT IS SESSION: %s", session)

    creator = await hass.async_add_executor_job(create_network, session)

    if not creator:
        raise CouldNotCreate

    network_uuid = creator.get("network", {}).get("id")
    data[CONF_UUID] = network_uuid

    await hass.async_add_executor_job(
        claim_network,
        session,
        network_uuid,
    )
    _LOGGER.warning("Created Network uuid: %s", network_uuid)

    saved_files = await hass.async_add_executor_job(create_certificaties_files, creator)
    if not saved_files:
        raise CouldNotCreate

    return {CONF_UUID: network_uuid}


class WappstoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""

    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    _LOGGER.error("ConfigFlow TEST WappstoConfigFlow")
    VERSION = 1

    def __init__(self) -> None:
        _LOGGER.warning("Init ConfigFLow")

    async def async_step_user(self, user_input):
        errors = {}

        await self.async_set_unique_id(WAPPSTO_HAS_BEEN_SETUP)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            try:
                # _LOGGER.warning(user_input)
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info[CONF_UUID], data=user_input)
            except InvalidLogin:
                errors[CONF_EMAIL] = "cannot_connect"
            except CouldNotCreate:
                errors[CONF_EMAIL] = "cannot_connect"

        return self.async_show_form(
            step_id="user", data_schema=NETWORK_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class InvalidLogin(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid username/password."""


class CouldNotCreate(exceptions.HomeAssistantError):
    """Error to indicate culd not create network."""


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        _LOGGER.info("Init OptionsConfigFlow")
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        _LOGGER.info("Async step init options flow [%s]", self.options)

        entity_id_list = {}
        for state in self.hass.states.async_all():
            # _LOGGER.info("Testing states id: %s", state.entity_id)

            (entity_type, dontcare) = state.entity_id.split(".")
            if entity_type in SUPPORTED_DOMAINS:
                entity_id_list[state.entity_id] = state.entity_id

        if user_input is not None:
            _LOGGER.warning("User_input: [%s]", user_input)
            self.options.update(user_input)
            return await self._update_options()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        ENTITY_LIST,
                        default=list(self.options[ENTITY_LIST]),  # type: ignore list is a valid type
                    ): cv.multi_select(entity_id_list),
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_UUID), data=self.options
        )
