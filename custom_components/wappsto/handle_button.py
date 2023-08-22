import logging

from homeassistant.core import Event, HomeAssistant

import wappstoiot
from wappstoiot import Device, Value
from .handler import Handler

_LOGGER = logging.getLogger(__name__)


class HandleButton(Handler):
    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.valueList: dict[str, Value] = {}

    def createValue(
        self, device: Device, domain: str, entity_id: str, initial_data: str | None
    ) -> None:
        self.valueList[entity_id] = device.createStringValue(
            name=entity_id,
            permission=wappstoiot.PermissionType.READ,
            type="Button",
            max=25,
        )

        if initial_data:
            self.valueList[entity_id].report(initial_data)

    def getReport(self, domain: str, entity_id: str, data: str, event: str) -> None:
        if not entity_id in self.valueList:
            return
        self.valueList[entity_id].report(data)
