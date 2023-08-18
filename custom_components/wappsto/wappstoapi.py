import logging
import wappstoiot

from wappstoiot import Device

from homeassistant.config_entries import ConfigEntry
from homeassistant.components import is_on
from homeassistant.const import (
    EVENT_STATE_CHANGED,
    EVENT_HOMEASSISTANT_STOP,
    EVENT_SERVICE_REGISTERED,
)
from homeassistant.core import Event, HomeAssistant

from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import async_generate_entity_id, DeviceInfo
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import (
    device_registry as dr,
    entity_registry as er,
    entity_values as ev,
    entity as ent_help,
)

from .const import (
    SUPPORTED_DOMAINS,
    INPUT_BOOLEAN,
    INPUT_BUTTON,
    BINARY_SENSOR,
    LIGHT,
    SENSOR,
)

from .binary_sensor import wappsto_connected_sensor
from homeassistant.const import CONF_API_KEY, CONF_NAME, Platform

_LOGGER = logging.getLogger(__name__)

from .handle_input import HandleInput
from .handle_binary_sensor import HandleBinarySensor
from .handle_light import HandleLight
from .handle_sensor import HandleSensor

from homeassistant.helpers.entity import get_supported_features, get_capability

import homeassistant.exceptions


class WappstoApi:
    def __init__(self, hass: HomeAssistant, entity_list: list) -> None:
        _LOGGER.info("TESTING WAPPSTO API __INIT__")
        self.hass = hass
        self.entity_list = entity_list
        self.valueList = {}
        self.deviceList = {}
        self.handle_input = HandleInput(self.hass)
        self.handle_binary_sensor = HandleBinarySensor(self.hass)
        self.handle_light = HandleLight(self.hass)
        self.handle_sensor = HandleSensor(self.hass)

        self.handlerDomain = {}
        self.handlerDomain[INPUT_BUTTON] = self.handle_input
        self.handlerDomain[INPUT_BOOLEAN] = self.handle_input
        self.handlerDomain[BINARY_SENSOR] = self.handle_binary_sensor
        self.handlerDomain[LIGHT] = self.handle_light
        self.handlerDomain[SENSOR] = self.handle_sensor

        wappstoiot.config(
            config_folder="./config/custom_components/wappsto",
            fast_send=False,
        )
        self.network = wappstoiot.createNetwork(name="HomeAssistant")
        self.temp_device = self.network.createDevice("Default device")

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
        wappsto_connected_sensor.turn_on()

    def updateEntityList(self, entity_list: list):
        self.entity_list = entity_list
        for values in entity_list:
            self.createValue(values)

    def handleEvent(self, event):
        entity_id = event.data.get("entity_id", "")
        _LOGGER.warning("Event id: %s [%s]", entity_id, event)
        (entity_type, entity_name) = entity_id.split(".")
        if entity_type in SUPPORTED_DOMAINS:
            self.updateValueReport(entity_id, event)

    def createOrGetDevice(self, entity_id: str) -> Device | None:
        entity_list = er.async_get(self.hass)
        tmp_entity = entity_list.async_get(entity_id)

        if not tmp_entity:
            return None
        dev_id = tmp_entity.device_id
        if not dev_id or len(dev_id) == 0:
            return None

        dev_list = dr.async_get(self.hass)
        tmp_dev = dev_list.async_get(str(dev_id))

        if not tmp_dev:
            return None
        name = tmp_dev.name
        if not name or len(name) == 0:
            return None

        if not dev_id in self.deviceList:
            self.deviceList[dev_id] = self.network.createDevice(name)

        return self.deviceList[dev_id]

    def createValue(self, entity_id: str):
        (entity_type, entity_name) = entity_id.split(".")
        if entity_type in SUPPORTED_DOMAINS:
            use_device = self.createOrGetDevice(entity_id)
            if not use_device:
                use_device = self.temp_device

            current_entity = self.hass.states.get(entity_id)
            # _LOGGER.error("TESTING !!!!!!!!!!!!!!!!! STATE: [%s]", current_entity)
            initial_data = None
            if current_entity:
                _LOGGER.info(
                    "Set initial report[%s]:[%s]", entity_id, current_entity.state
                )
                initial_data = current_entity.state

            self.handlerDomain[entity_type].createValue(
                use_device, entity_type, entity_id, initial_data
            )

    def updateValueReport(self, entity_id, event):
        testing = event.data["new_state"].state
        (entity_type, entity_name) = entity_id.split(".")
        _LOGGER.info("Report [%s]", testing)
        self.handlerDomain[entity_type].getReport(entity_type, entity_id, testing)
