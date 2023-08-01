from homeassistant import config_entries
from .const import DOMAIN
from homeassistant.data_entry_flow import FlowResult

from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
)


# class ExampleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

#     async def async_step_user(
#         self, user_input: dict[str, Any] | None = None
#     ) -> FlowResult:
#         """Handle a flow initialized by the user."""
#         errors: dict[str, str] = {}
#         if user_input is not None:
#             self._host = user_input[CONF_HOST]
#             self._name = user_input[CONF_NAME]
#             return await self.async_step_pairing()

#         return self.async_show_form(
#             step_id=step_id,
#             data_schema=data_schema,
#             errors=errors or {},
#             description_placeholders=description_placeholders,
#         )
