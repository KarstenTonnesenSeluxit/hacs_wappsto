import logging

from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.entity import get_device_class, get_unit_of_measurement
from homeassistant.components.sensor import SensorDeviceClass
import wappstoiot
from wappstoiot import Device, Value
from .handler import Handler

_LOGGER = logging.getLogger(__name__)


class HandleSensor(Handler):
    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.valueList: dict[str, Value] = {}

    def createValue(
        self, device: Device, domain: str, entity_id: str, initial_data: str | None
    ) -> None:
        valType = "unknown"
        createString = False
        device_class = get_device_class(self.hass, entity_id)
        if device_class:
            valType = device_class
            if (
                SensorDeviceClass(device_class) == SensorDeviceClass.TIMESTAMP
                or SensorDeviceClass(device_class) == SensorDeviceClass.DATE
            ):
                createString = True

        if createString:
            self.valueList[entity_id] = device.createStringValue(
                name=entity_id,
                permission=wappstoiot.PermissionType.READ,
                type=valType,
                max=600,
            )
            if initial_data:
                self.valueList[entity_id].report(initial_data)
            return

        minimum = -60000
        maximum = 60000
        measure = get_unit_of_measurement(self.hass, entity_id)

        if measure == "%":
            minimum = 0
            maximum = 100

        self.valueList[entity_id] = device.createNumberValue(
            name=entity_id,
            permission=wappstoiot.PermissionType.READ,
            type=valType,
            min=minimum,
            max=maximum,
            step=0.001,
            unit=measure if isinstance(measure, str) else "",
        )
        if initial_data:
            self.valueList[entity_id].report(initial_data)

    def getReport(self, domain: str, entity_id: str, data: str) -> None:
        if not entity_id in self.valueList:
            return
        self.valueList[entity_id].report(data)