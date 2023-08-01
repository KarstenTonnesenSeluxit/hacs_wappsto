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
from homeassistant.const import STATE_ON
from homeassistant.const import STATE_OFF

from .const import (
    NETWORK_UUID,
    DOMAIN,
    # GATEWAY_SERIAL_PATTERN,
    PLATFORMS,
)

import wappstoiot
import rich

_LOGGER = logging.getLogger(__name__)

network: wappstoiot.Network
device: wappstoiot.Device
values: list[wappstoiot.Value]
event_db: dict[str, wappstoiot.Value] = {}


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the weather component."""
    rich.print("-------------------- async_setup ------------------------")

    global network
    global device
    global values

    component = hass.data[DOMAIN] = EntityComponent(
        _LOGGER, DOMAIN, hass, timedelta(seconds=30)
    )

    # logging.getLogger("wappstoiot").setLevel(logging.DEBUG)

    wappstoiot.config(
        config_folder="/workspaces/core/config/custom_components/wappsto",
        fast_send=False,
    )
    network = wappstoiot.createNetwork(name="HomeAssistant")
    device = network.createDevice(
        name="Light Integration",
        product="",
        version="0.0.1",  # Should be HomeAssistant version.
        description="A list of integrations on the home assistant.",
    )

    def event_handler(event):
        entity_id = event.data.get('entity_id', "")
        rich.print(f"New Entity id: {entity_id}")
        if 'light.' in entity_id:
            global event_db 
            # rich.print(f"Changed: {event=}")
            # rich.print(f"New State: {event.data['new_state'].state=}")
            if entity_id not in event_db.keys():
                event_db[entity_id] = device.createNumberValue(                                         
                    name=entity_id,                                                         
                    permission=wappstoiot.PermissionType.READWRITE,                              
                    type="boolean",                                                         
                    min=0,                                                                  
                    max=1,                                                                  
                    step=1,                                                                 
                    unit=None,                                                              
                    mapping={'0': 'off', '1': 'on'},                               
                    ordered_mapping=True                                                    
                )
                # event_db[entity_id] = device.createValue(
                #     name=entity_id,
                #     value_template=wappstoiot.ValueTemplate.BOOLEAN_ONOFF,
                #     permission=wappstoiot.PermissionType.READ
                # )
                def change(value, data):
                    service_data = {
                        "entity_id": entity_id,
                        # "rgb_color": event.data.get("rgb_color", [255, 255, 255]),
                        # "brightness": 255
                    }
                    hass.services.call(
                        domain="light",
                        service="turn_on" if data == 1 else "turn_off",
                        service_data=service_data,
                        blocking=False
                    )

                event_db[entity_id].onControl(
                    callback=change
                )
            event_db[entity_id].control(
                1 if event.data['new_state'].state == "on" else 0
            )
            event_db[entity_id].report(
                1 if event.data['new_state'].state == "on" else 0
            )
            rich.print(f"Event DB: {event_db}")

    def event_started(event):
        # rich.print(f"ID: {event}")
        # rich.print(f"ID: {event.data['domain']}")
        domain = event.data['domain']
        if domain in ['hue', 'light']:
            service = event.data['service']
            rich.print(f"{domain}: {service}")
            rich.print(f"{hass.services.has_service(domain=domain, service=service)=}")

    hass.bus.async_listen(
        event_type=EVENT_STATE_CHANGED,
        listener=event_handler
    )
    hass.bus.async_listen(  # NOTE: et it to work to create the value!!
        event_type=EVENT_SERVICE_REGISTERED,
        listener=event_started
    )

    rich.print(f"{hass.bus.async_listeners()=}")
    # rich.print(f"{hass.bus.listeners()=}")
    hass.bus.async_listen(
        event_type=EVENT_HOMEASSISTANT_STOP,
        listener=lambda *args, **kwargs: wappstoiot.close()
    )
    await component.async_setup(config)
    rich.print("---------------------------------------------------------")
    return True


# async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
#     """Set up the devolo account from a config entry."""
#     hass.data.setdefault(DOMAIN, {})

#     rich.print("-------------------- async_setup_entry ------------------------")

#     user = entry.data[CONF_USERNAME]
#     password = entry.data[CONF_PASSWORD]
#     the_uuid = entry.data.get(NETWORK_UUID)

#     print(f"{user=}")
#     print(f"{password=}")

#     rich.print(hass.data.keys)

#     # # if not the_uuid:
#     # #   create certificates
#     # #   entry.data[NETWORK_UUID] = network_uuid

#     # # createValue  # for each intergration

#     # # credentials_valid = await hass.async_add_executor_job(mydevolo.credentials_valid)

#     # # if not credentials_valid:
#     # #     raise ConfigEntryAuthFailed

#     # # if await hass.async_add_executor_job(mydevolo.maintenance):
#     # #     raise ConfigEntryNotReady

#     # gateway_ids = await hass.async_add_executor_job(mydevolo.get_gateway_ids)

#     # if entry.unique_id and GATEWAY_SERIAL_PATTERN.match(entry.unique_id):
#     #     uuid = await hass.async_add_executor_job(mydevolo.uuid)
#     #     hass.config_entries.async_update_entry(entry, unique_id=uuid)

#     # # hass.config_entries.async_setup_platforms(entry, PLATFORMS)

#     # # Listen when EVENT_HOMEASSISTANT_STOP is fired
#     # hass.data[DOMAIN][entry.entry_id]["listener"] = hass.bus.async_listen_once(
#     #     EVENT_HOMEASSISTANT_STOP, wappstoiot.close
#     # )

#     return True


# # async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
# #     """Unload a config entry."""
# #     unload = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
# #     await asyncio.gather(
# #         *(
# #             hass.async_add_executor_job(gateway.websocket_disconnect)
# #             for gateway in hass.data[DOMAIN][entry.entry_id]["gateways"]
# #         )
# #     )
# #     hass.data[DOMAIN][entry.entry_id]["listener"]()
# #     hass.data[DOMAIN].pop(entry.entry_id)
# #     return unload
