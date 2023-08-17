import logging

from homeassistant.core import Event, HomeAssistant
from homeassistant.const import SERVICE_TURN_ON, SERVICE_TURN_OFF

import wappstoiot
from wappstoiot import Device, Value
from .handler import Handler

_LOGGER = logging.getLogger(__name__)


class HandleInput(Handler):
    def __init__(self, hass: HomeAssistant) -> None:
        self.valueList: dict[str, Value] = {}
        self.hass = hass

    def createValue(
        self, device: Device, domain: str, entity_id: str, initial_data: str | None
    ) -> None:
        if domain == "input_button":
            self.valueList[entity_id] = device.createNumberValue(
                name=entity_id,
                permission=wappstoiot.PermissionType.READ,
                type="event",
                min=0,
                max=0,
                step=0,
                unit="",
                mapping=None,
            )
            return

        # Assuming input_boolean for now
        self.valueList[entity_id] = device.createNumberValue(
            name=entity_id,
            permission=wappstoiot.PermissionType.READWRITE,
            type="boolean",
            min=0,
            max=1,
            step=1,
            unit="",
            mapping={"0": "off", "1": "on"},
            meaningful_zero=True,
            ordered_mapping=True,
        )

        def setControl(value, data):
            service_data = {
                "entity_id": entity_id,
            }
            self.hass.services.call(
                domain="input_boolean",
                service=SERVICE_TURN_ON if data == 1 else SERVICE_TURN_OFF,
                service_data=service_data,
                blocking=False,
            )

        if initial_data:
            if domain == "input_button":
                self.valueList[entity_id].report("NA")
            else:
                self.valueList[entity_id].report("1" if initial_data == "on" else "0")
                self.valueList[entity_id].control("1" if initial_data == "on" else "0")
            self.valueList[entity_id].onControl(callback=setControl)

    def getReport(self, domain: str, entity_id: str, data: str) -> None:
        if not entity_id in self.valueList:
            return
        self.valueList[entity_id].report("1" if data == "on" else "0")
        if domain == "input_boolean":
            self.valueList[entity_id].control("1" if data == "on" else "0")
