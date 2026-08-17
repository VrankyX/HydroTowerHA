from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from .const import *

class HydroponicTowerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    async def async_step_user(self, user_input=None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if user_input is not None:
            title = user_input.pop("name")
            return self.async_create_entry(title=title, data=user_input)
        ent = selector.EntitySelector
        schema = vol.Schema({
            vol.Required("name", default="Hydroponik Tower"): str,
            vol.Required(CONF_PUMP): ent(selector.EntitySelectorConfig(domain="switch")),
            vol.Required(CONF_PH_PLUS): ent(selector.EntitySelectorConfig(domain="switch")),
            vol.Required(CONF_PH_MINUS): ent(selector.EntitySelectorConfig(domain="switch")),
            vol.Required(CONF_NUTRIENT): ent(selector.EntitySelectorConfig(domain="switch")),
            vol.Required(CONF_GROW_LIGHT): ent(selector.EntitySelectorConfig(domain="switch")),
            vol.Required(CONF_LEAK): ent(selector.EntitySelectorConfig(domain="binary_sensor")),
            vol.Required(CONF_PH_SENSOR): ent(selector.EntitySelectorConfig(domain="sensor")),
            vol.Required(CONF_EC_SENSOR): ent(selector.EntitySelectorConfig(domain="sensor")),
            vol.Required(CONF_WATER_TEMP): ent(selector.EntitySelectorConfig(domain="sensor")),
            vol.Required(CONF_DISTANCE): ent(selector.EntitySelectorConfig(domain="sensor")),
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return HydroponicTowerOptionsFlow(config_entry)

class HydroponicTowerOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        c = {**DEFAULTS, **self.config_entry.options}
        def n(lo, hi, step):
            return selector.NumberSelector(selector.NumberSelectorConfig(min=lo,max=hi,step=step,mode=selector.NumberSelectorMode.BOX))
        schema = vol.Schema({
            vol.Required("sensor_to_bottom_cm", default=c["sensor_to_bottom_cm"]): n(25,60,0.1),
            vol.Required("critical_level_cm", default=c["critical_level_cm"]): n(1,20,0.5),
            vol.Required("refill_level_cm", default=c["refill_level_cm"]): n(2,25,0.5),
            vol.Required("target_level_cm", default=c["target_level_cm"]): n(5,28,0.5),
            vol.Required("overfill_level_cm", default=c["overfill_level_cm"]): n(12,30,0.5),
            vol.Required("watering_enabled", default=c["watering_enabled"]): bool,
            vol.Required("watering_run_sec", default=c["watering_run_sec"]): n(10,1800,10),
            vol.Required("watering_pause_min", default=c["watering_pause_min"]): n(1,240,1),
            vol.Required("ph_auto_enabled", default=c["ph_auto_enabled"]): bool,
            vol.Required("ph_min", default=c["ph_min"]): n(4,8,0.05),
            vol.Required("ph_max", default=c["ph_max"]): n(4,8,0.05),
            vol.Required("ph_plus_pulse_sec", default=c["ph_plus_pulse_sec"]): n(1,30,0.5),
            vol.Required("ph_minus_pulse_sec", default=c["ph_minus_pulse_sec"]): n(1,30,0.5),
            vol.Required("ph_plus_ml_sec", default=c["ph_plus_ml_sec"]): n(0.01,20,0.01),
            vol.Required("ph_minus_ml_sec", default=c["ph_minus_ml_sec"]): n(0.01,20,0.01),
            vol.Required("ph_daily_limit_ml", default=c["ph_daily_limit_ml"]): n(1,500,1),
            vol.Required("nutrient_auto_enabled", default=c["nutrient_auto_enabled"]): bool,
            vol.Required("ec_min", default=c["ec_min"]): n(0,5000,10),
            vol.Required("nutrient_pulse_sec", default=c["nutrient_pulse_sec"]): n(1,60,0.5),
            vol.Required("nutrient_ml_sec", default=c["nutrient_ml_sec"]): n(0.01,50,0.01),
            vol.Required("nutrient_daily_limit_ml", default=c["nutrient_daily_limit_ml"]): n(1,2000,1),
            vol.Required("mix_time_min", default=c["mix_time_min"]): n(5,120,1),
            vol.Required("dose_lock_min", default=c["dose_lock_min"]): n(10,240,5),
            vol.Required("water_temp_max", default=c["water_temp_max"]): n(10,40,0.5),
            vol.Required("grow_light_auto_enabled", default=c["grow_light_auto_enabled"]): bool,
            vol.Required("grow_light_on", default=c["grow_light_on"]): str,
            vol.Required("grow_light_off", default=c["grow_light_off"]): str,
        })
        return self.async_show_form(step_id="init", data_schema=schema)
