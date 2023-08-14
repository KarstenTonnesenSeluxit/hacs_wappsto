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
)

from .const import NETWORK_UUID, DOMAIN, STARTUP_MESSAGE, SUPPORTED_DOMAINS

from .binary_sensor import test_sensor
from homeassistant.const import CONF_API_KEY, CONF_NAME, Platform

_LOGGER = logging.getLogger(__name__)


class WappstoApi:
    def __init__(self, hass: HomeAssistant, entity_list: list) -> None:
        _LOGGER.info("TESTING WAPPSTO API __INIT__")
        self.hass = hass
        self.entity_list = entity_list
        self.valueList = {}
        self.deviceList = {}

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

        test_sensor.turn_on()

    def updateEntityList(self, entity_list: list):
        self.entity_list = entity_list
        # TODO check for create or disable values/devices

    def handleEvent(self, event):
        entity_id = event.data.get("entity_id", "")
        _LOGGER.warning("Event id: %s [%s]", entity_id, event)
        if entity_id in self.valueList:
            self.updateValueReport(entity_id, event)

    def createOrGetDevice(self, entity_id: str) -> Device | None:
        entity_list = er.async_get(self.hass)
        tmp_entity = entity_list.async_get(entity_id)
        dev_id = tmp_entity.device_id
        if not dev_id or len(dev_id) == 0:
            return None

        dev_list = dr.async_get(self.hass)
        tmp_dev = dev_list.async_get(str(dev_id))
        name = tmp_dev.name
        if not name or len(name) == 0:
            return None

        if not dev_id in self.deviceList:
            self.deviceList[dev_id] = self.network.createDevice(name)

        return self.deviceList[dev_id]

    def createValue(self, entity_id: str):
        # TODO missing initial value - report / control
        (entity_type, entity_name) = entity_id.split(".")
        if entity_type in SUPPORTED_DOMAINS:
            use_device = self.createOrGetDevice(entity_id)
            if not use_device:
                use_device = self.temp_device

            self.valueList[entity_id] = use_device.createValue(
                name=entity_id,
                permission=wappstoiot.PermissionType.READWRITE,
                value_template=wappstoiot.ValueTemplate.BOOLEAN_TRUEFALSE,
            )

    def updateValueReport(self, entity_id, event):
        testing = event.data["new_state"].state

        _LOGGER.error("Report [%s]", testing)

        self.valueList[entity_id].report(1 if testing == "on" else 0)
