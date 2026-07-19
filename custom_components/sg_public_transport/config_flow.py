from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.core import callback
from homeassistant.const import CONF_API_KEY, CONF_SCAN_INTERVAL
from homeassistant.config_entries import (
    SOURCE_REAUTH,
    ConfigFlow,
    ConfigFlowResult,
    ConfigEntry,
    ConfigSubentryFlow,

)
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import DOMAIN, MIN_SCAN_INTERVAL_SECONDS, SUBENTRY_TYPE_BUS_STOP
from .subentry_flow import BusStopSubEntryFlowHandler

def get_config_schema(
    api_key: str | None = None, scan_interval: int = MIN_SCAN_INTERVAL_SECONDS
) -> vol.Schema:
    """Return the schema for the config flow."""
    return vol.Schema(
        {
            vol.Required(CONF_API_KEY, default=api_key): TextSelector(
                TextSelectorConfig(
                    type=TextSelectorType.PASSWORD, autocomplete="current-password"
                )
            ),
            vol.Required(CONF_SCAN_INTERVAL, default=scan_interval): vol.All(
                vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL_SECONDS)
            ),
        }
    )

class SgPublicTransportConfigFlow(ConfigFlow, domain=DOMAIN):

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Return subentries supported by this integration."""
        return {
            SUBENTRY_TYPE_BUS_STOP: BusStopSubEntryFlowHandler,
        }

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""

        errors: dict[str, str] = {}
        if user_input is not None:
            return self.async_create_entry(
                title="API", data=user_input
            )

        return self.async_show_form(
            step_id="user", data_schema=get_config_schema(), errors=errors
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            return self.async_update_reload_and_abort(
                self._get_reconfigure_entry(), data_updates=user_input
            )

        api_key: str = self._get_reconfigure_entry().data[CONF_API_KEY]
        scan_interval: int = self._get_reconfigure_entry().data[CONF_SCAN_INTERVAL]
        return self.async_show_form(
            step_id="user", data_schema=get_config_schema(api_key, scan_interval), errors=errors
        )
