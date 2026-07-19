from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigSubentry,
    ConfigSubentryFlow,
    SubentryFlowResult,
)

from .const import SUBENTRY_CONF_BUS_STOP_CODE, SUBENTRY_TYPE_BUS_STOP

BUS_STOP_CONFIG_SCHEMA: vol.Schema = vol.Schema(
    {vol.Required(SUBENTRY_CONF_BUS_STOP_CODE): str}
)

class BusStopSubEntryFlowHandler(ConfigSubentryFlow):
    """Subentry flow for adding a new bus stop."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            config_entry = self._get_entry()

            bus_stop_code = user_input[SUBENTRY_CONF_BUS_STOP_CODE]

            self.hass.config_entries.async_add_subentry(
                config_entry,
                ConfigSubentry(data=user_input,
                    subentry_type=SUBENTRY_TYPE_BUS_STOP,
                    title=f"Bus Stop: {bus_stop_code}",
                    unique_id=f"bus_stop_{bus_stop_code}",
                ),
            )

        return self.async_show_form(
            step_id="user", data_schema=BUS_STOP_CONFIG_SCHEMA, errors=errors
        )
