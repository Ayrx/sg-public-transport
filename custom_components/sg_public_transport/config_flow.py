from typing import Any

import voluptuous as vol

from homeassistant.const import CONF_API_KEY, CONF_SCAN_INTERVAL
from homeassistant.config_entries import (
    SOURCE_REAUTH,
    ConfigFlow,
    ConfigFlowResult,
)
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import DOMAIN, MIN_SCAN_INTERVAL_SECONDS

config_schema = vol.Schema(
    {
        vol.Required(CONF_API_KEY, default=None): TextSelector(
            TextSelectorConfig(
                type=TextSelectorType.PASSWORD, autocomplete="current-password"
            )
        ),
        vol.Required(CONF_SCAN_INTERVAL, default=MIN_SCAN_INTERVAL_SECONDS): vol.All(
            vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL_SECONDS)
        ),
    }
)

class SgPublicTransportConfigFlow(ConfigFlow, domain=DOMAIN):
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
            step_id="user", data_schema=config_schema, errors=errors
        )
