from typing import Any
import logging

from homeassistant.core import Event, State, HomeAssistant
from homeassistant.const import SERVICE_TURN_ON, SERVICE_TURN_OFF

import wappstoiot
from wappstoiot import Device, Value
from .handler import Handler

ONOFF_VALUE = "onoff"
BRIGHTNESS_VALUE = "brightness"
COLOR_VALUE = "color"
COLOR_TEMP_VALUE = "temp_color"

_LOGGER = logging.getLogger(__name__)

# other helpers
# def get_device_class(hass: HomeAssistant, entity_id: str)
# def get_capability(hass: HomeAssistant, entity_id: str, capability: str)
# def get_supported_features(hass: HomeAssistant, entity_id: str) -> int
# def get_unit_of_measurement(hass: HomeAssistant, entity_id: str) -> str | None:


class HandleLight(Handler):
    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.valueList: dict[str, dict[str, Value]] = {}

    def createRgbValue(self, device: Device, entity_id: str, state: State):
        # # Lists holding color values
        # ATTR_RGB_COLOR = "rgb_color"
        # ATTR_RGBW_COLOR = "rgbw_color"
        # ATTR_RGBWW_COLOR = "rgbww_color"
        # ATTR_XY_COLOR = "xy_color"
        # ATTR_HS_COLOR = "hs_color"
        pass

    def createColorTempValue(self, device: Device, entity_id: str, state: State):
        # # ATTR_COLOR_TEMP = "color_temp"  # Deprecated in HA Core 2022.11
        # # ATTR_KELVIN = "kelvin"  # Deprecated in HA Core 2022.11
        # # ATTR_MIN_MIREDS = "min_mireds"  # Deprecated in HA Core 2022.11
        # # ATTR_MAX_MIREDS = "max_mireds"  # Deprecated in HA Core 2022.11
        # ATTR_COLOR_TEMP_KELVIN = "color_temp_kelvin"
        # ATTR_MIN_COLOR_TEMP_KELVIN = "min_color_temp_kelvin"
        # ATTR_MAX_COLOR_TEMP_KELVIN = "max_color_temp_kelvin"
        if state.attributes.get("min_color_temp_kelvin") and state.attributes.get(
            "max_color_temp_kelvin"
        ):
            minKelvin = state.attributes.get("min_color_temp_kelvin")
            maxKelvin = state.attributes.get("max_color_temp_kelvin")
            self.valueList[entity_id][COLOR_TEMP_VALUE] = device.createNumberValue(
                name="temp Kelvin " + entity_id,
                permission=wappstoiot.PermissionType.READWRITE,
                type="color_temperature",
                min=int(minKelvin) if minKelvin else 0,
                max=int(maxKelvin) if maxKelvin else 0,
                step=1,
                unit="kelvin",
            )
        elif state.attributes.get("min_mireds") and state.attributes.get("max_mireds"):
            minReds = state.attributes.get("min_mireds")
            maxReds = state.attributes.get("max_mireds")
            self.valueList[entity_id][COLOR_TEMP_VALUE] = device.createNumberValue(
                name="temp mireds " + entity_id,
                permission=wappstoiot.PermissionType.READWRITE,
                type="color_temperature",
                min=int(minReds) if minReds else 0,
                max=int(maxReds) if maxReds else 0,
                step=1,
                unit="mireds",
            )

    def createBrightnessValue(self, device: Device, entity_id: str, state: State):
        # # Brightness of the light, 0..255 or percentage
        # ATTR_BRIGHTNESS = "brightness"
        # ATTR_BRIGHTNESS_PCT = "brightness_pct"
        # ATTR_BRIGHTNESS_STEP = "brightness_step"
        # ATTR_BRIGHTNESS_STEP_PCT = "brightness_step_pct"
        max_length = 0
        if state.attributes.get("brightness"):
            # Create 0-255 brightness
            max_length = 255
        elif state.attributes.get("brightness_pct"):
            # Create 0-100 brightness
            max_length = 100
        if max_length > 0:
            self.valueList[entity_id][BRIGHTNESS_VALUE] = device.createNumberValue(
                name=entity_id,
                permission=wappstoiot.PermissionType.READWRITE,
                type="brightness",
                min=0,
                max=max_length,
                step=1,
                unit="",
            )

    def createValue(
        self, device: Device, domain: str, entity_id: str, initial_data: str | None
    ) -> None:
        state = self.hass.states.get(entity_id)

        # ATTR_COLOR_NAME = "color_name"
        # ATTR_WHITE = "white"

        self.valueList[entity_id] = {}
        if state:
            ### FOR DEBUG START
            debug_name = entity_id + " config"
            tmpDebugValue = device.createStringValue(
                name=debug_name,
                type="debug",
                permission=wappstoiot.PermissionType.READ,
                max=500,
            )
            tmpDebugValue.report(str(state))
            ### FOR DEBUG END

            self.createRgbValue(device, entity_id, state)
            self.createColorTempValue(device, entity_id, state)
            self.createBrightnessValue(device, entity_id, state)

        self.valueList[entity_id]["debug"] = device.createStringValue(
            name=entity_id + " debug",
            type="debug",
            permission=wappstoiot.PermissionType.READ,
            max=500,
        )

        self.valueList[entity_id][ONOFF_VALUE] = device.createNumberValue(
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
                # "rgb_color": event.data.get("rgb_color", [255, 255, 255]),
                # "brightness": 255
            }
            self.hass.services.call(
                domain="light",
                service=SERVICE_TURN_ON if data == 1 else SERVICE_TURN_OFF,
                service_data=service_data,
                blocking=False,
            )

        if initial_data:
            self.valueList[entity_id][ONOFF_VALUE].report(
                "1" if initial_data == "on" else "0"
            )
            self.valueList[entity_id][ONOFF_VALUE].control(
                "1" if initial_data == "on" else "0"
            )
        self.valueList[entity_id][ONOFF_VALUE].onControl(callback=setControl)

    def getReport(self, domain: str, entity_id: str, data: str, event: str) -> None:
        if entity_id not in self.valueList:
            return
        _LOGGER.warning("Testing light report: [%s]", data)
        self.valueList[entity_id][ONOFF_VALUE].report("1" if data == "on" else "0")
        self.valueList[entity_id]["debug"].report(event)
