import logging
import wappstoiot

from homeassistant.components import is_on
from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.const import EVENT_SERVICE_REGISTERED
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import async_generate_entity_id, DeviceInfo
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import (
    NETWORK_UUID,
    DOMAIN,
    # GATEWAY_SERIAL_PATTERN,
    PLATFORMS,
    STARTUP_MESSAGE,
)

from .binary_sensor import test_sensor
from homeassistant.const import CONF_API_KEY, CONF_NAME, Platform

_LOGGER = logging.getLogger(__name__)


class WappstoApi:
    def __init__(self, hass: HomeAssistant, entity_list: list) -> None:
        _LOGGER.info("TESTING WAPPSTO API __INIT__")
        self.hass = hass
        self.entity_list = entity_list
        self.valueList = {}
        self.supportedList = ["input_boolean"]

        wappstoiot.config(
            config_folder="./config/custom_components/wappsto",
            fast_send=False,
        )
        self.network = wappstoiot.createNetwork(name="HomeAssistant")
        self.temp_device = self.network.createDevice("Temp static device")

        for values in entity_list:
            self.createValue(values)

        def event_handler(event):
            self.handleEvent(event)

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

        test_sensor.turn_on()

    def updateEntityList(self, entity_list: list):
        self.entity_list = entity_list
        # TODO check for create or disable values/devices

    def handleEvent(self, event):
        entity_id = event.data.get("entity_id", "")
        _LOGGER.warning("Event id: %s [%s]", entity_id, event)
        if entity_id in self.valueList:
            self.updateValueReport(entity_id, event)

    def createValue(self, entity_id: str):
        (entity_type, entity_name) = entity_id.split(".")
        if entity_type in self.supportedList:
            self.valueList[entity_id] = self.temp_device.createValue(
                name=entity_id,
                permission=wappstoiot.PermissionType.READWRITE,
                value_template=wappstoiot.ValueTemplate.BOOLEAN_TRUEFALSE,
            )

    def updateValueReport(self, entity_id, event):
        testing = event.data["new_state"].state

        _LOGGER.error("Report [%s]", testing)

        self.valueList[entity_id].report(1 if testing == "on" else 0)
