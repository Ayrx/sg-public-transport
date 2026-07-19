from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    SUBENTRY_CONF_BUS_STOP_CODE,
    SUBENTRY_TYPE_BUS_STOP,
)

# Stub bus services available at every bus stop. This will be replaced by the
# services returned from the LTA DataMall API.
STUB_BUS_SERVICES: tuple[str, ...] = ("123", "145", "196")


@dataclass(frozen=True, kw_only=True)
class BusServiceSensorDescription(SensorEntityDescription):
    """Describes the bus arrival sensor entity."""

    # Number of sensor instances to create for a bus service. Bus arrival data
    # is reported for up to the next three arriving buses, so attributes such as
    # the estimated arrival time have a cardinality of three while attributes
    # that describe the service itself have a cardinality of one.
    cardinality: int
    value_fn: Callable[[str, int], StateType | datetime]


def _stub_bus_type(service_no: str, index: int) -> str:
    return ("single_deck", "double_deck", "bendy")[index % 3]


def _stub_arrival(service_no: str, index: int) -> datetime:
    return dt_util.utcnow() + timedelta(minutes=5 * (index + 1))


def _stub_load(service_no: str, index: int) -> str:
    return ("seats_available", "standing_available", "limited_standing")[index % 3]


def _stub_operator(service_no: str, index: int) -> str:
    return "sbst"


SENSOR_DESCRIPTIONS: tuple[BusServiceSensorDescription, ...] = (
    BusServiceSensorDescription(
        key="bus_type",
        translation_key="bus_type",
        device_class=SensorDeviceClass.ENUM,
        options=["single_deck", "double_deck", "bendy"],
        cardinality=3,
        value_fn=_stub_bus_type,
    ),
    BusServiceSensorDescription(
        key="arrival",
        translation_key="arrival",
        device_class=SensorDeviceClass.TIMESTAMP,
        cardinality=3,
        value_fn=_stub_arrival,
    ),
    BusServiceSensorDescription(
        key="load",
        translation_key="load",
        device_class=SensorDeviceClass.ENUM,
        options=["seats_available", "standing_available", "limited_standing"],
        cardinality=3,
        value_fn=_stub_load,
    ),
    BusServiceSensorDescription(
        key="operator",
        translation_key="operator",
        device_class=SensorDeviceClass.ENUM,
        options=["sbst", "smrt", "tts", "gas"],
        cardinality=1,
        value_fn=_stub_operator,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    device_registry = dr.async_get(hass)

    for subentry in config_entry.subentries.values():
        if subentry.subentry_type != SUBENTRY_TYPE_BUS_STOP:
            continue

        bus_stop_code: str = subentry.data[SUBENTRY_CONF_BUS_STOP_CODE]

        # Register the bus stop as a device so the individual bus service
        # devices can be nested underneath it.
        device_registry.async_get_or_create(
            config_entry_id=config_entry.entry_id,
            config_subentry_id=subentry.subentry_id,
            identifiers={(DOMAIN, bus_stop_code)},
            name=f"Bus Stop {bus_stop_code}",
            entry_type=DeviceEntryType.SERVICE,
        )

        entities: list[BusServiceSensor] = []
        for service_no in STUB_BUS_SERVICES:
            for description in SENSOR_DESCRIPTIONS:
                for index in range(description.cardinality):
                    entities.append(
                        BusServiceSensor(
                            bus_stop_code, service_no, description, index
                        )
                    )

        async_add_entities(entities, config_subentry_id=subentry.subentry_id)


class BusServiceSensor(SensorEntity):
    """A sensor representing a single piece of bus service information."""

    _attr_has_entity_name = True
    entity_description: BusServiceSensorDescription

    def __init__(
        self,
        bus_stop_code: str,
        service_no: str,
        description: BusServiceSensorDescription,
        index: int,
    ) -> None:
        self.entity_description = description
        self._bus_stop_code = bus_stop_code
        self._service_no = service_no
        self._index = index

        self._attr_unique_id = (
            f"{bus_stop_code}_{service_no}_{description.key}_{index}"
        )
        self._attr_translation_placeholders = {"index": str(index + 1)}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{bus_stop_code}_{service_no}")},
            name=f"Bus {service_no}",
            via_device=(DOMAIN, bus_stop_code),
        )

    @property
    def native_value(self) -> StateType | datetime:
        return self.entity_description.value_fn(self._service_no, self._index)
