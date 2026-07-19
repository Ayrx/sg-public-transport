"""SG Public Transport integration."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    return True
