"""Climate platform for Gecko."""
import logging

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACMode,
)

from .const import DOMAIN
from .entity import GeckoEntity
from .spa_manager import GeckoSpaManager

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup climate platform."""
    spaman: GeckoSpaManager = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            GeckoClimate(
                spaman, entry, spaman.facade.water_heater, spaman.facade.water_care
            )
        ]
    )


class GeckoClimate(GeckoEntity, ClimateEntity):
    """Gecko Climate class."""

    def __init__(self, spaman, config_entry, automation_entity, water_care):
        super().__init__(spaman, config_entry, automation_entity)
        self._water_care = water_care
        self._water_care.watch(self._on_change)

    @property
    def supported_features(self):
        """Return the list of supported features."""
        features = ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE

        # if self._client.have_blower():
        #    features |= SUPPORT_FAN_MODE

        return features

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:hot-tub"

    @property
    def hvac_modes(self):
        return [HVACMode.AUTO]

    @property
    def hvac_mode(self):
        return HVACMode.AUTO

    def set_hvac_mode(self, _hvac_mode):
        pass

    @property
    def hvac_action(self):
        """The current HVAC action"""
        # I happen to know that the operation modes match HA's modes but
        # they are proper cased, so we just move to lower ...
        return self._automation_entity.current_operation.lower()

    @property
    def preset_modes(self):
        return self._water_care.modes

    @property
    def preset_mode(self):
        if self._water_care.mode is None:
            return "Waiting..."
        return self._water_care.modes[self._water_care.mode]

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        await self._water_care.async_set_mode(preset_mode)

    @property
    def temperature_unit(self):
        return self._automation_entity.temperature_unit

    @property
    def current_temperature(self):
        return self._automation_entity.current_temperature

    @property
    def target_temperature(self):
        return self._automation_entity.target_temperature

    @property
    def min_temp(self):
        return self._automation_entity.min_temp

    @property
    def max_temp(self):
        return self._automation_entity.max_temp

    async def async_set_temperature(self, **kwargs) -> None:
        """Set the target temperature"""
        await self._automation_entity.async_set_target_temperature(
            kwargs["temperature"]
        )
