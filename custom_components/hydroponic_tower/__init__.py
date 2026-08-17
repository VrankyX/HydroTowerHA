from __future__ import annotations
import voluptuous as vol
from homeassistant.core import ServiceCall
from .const import DOMAIN, PLATFORMS
from .manager import HydroponicTowerManager

async def async_setup_entry(hass, entry):
    manager=HydroponicTowerManager(hass,entry); await manager.async_setup()
    hass.data.setdefault(DOMAIN,{})[entry.entry_id]=manager
    entry.async_on_unload(entry.add_update_listener(_updated))
    await hass.config_entries.async_forward_entry_setups(entry,PLATFORMS)
    if not hass.services.has_service(DOMAIN,"emergency_stop"):
        def mgr(): return next(iter(hass.data.get(DOMAIN,{}).values()),None)
        async def stop(call):
            if (m:=mgr()): await m.emergency_stop(call.data.get("reason","Manueller Not-Aus"))
        async def water(call):
            if (m:=mgr()): await m.water_once()
        async def php(call):
            if (m:=mgr()): await m.dose("ph_plus")
        async def phm(call):
            if (m:=mgr()): await m.dose("ph_minus")
        async def nut(call):
            if (m:=mgr()): await m.dose("nutrient")
        hass.services.async_register(DOMAIN,"emergency_stop",stop,schema=vol.Schema({vol.Optional("reason",default="Manueller Not-Aus"):str}))
        hass.services.async_register(DOMAIN,"water_once",water)
        hass.services.async_register(DOMAIN,"dose_ph_plus",php)
        hass.services.async_register(DOMAIN,"dose_ph_minus",phm)
        hass.services.async_register(DOMAIN,"dose_nutrient",nut)
    return True

async def _updated(hass,entry): await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass,entry):
    ok=await hass.config_entries.async_unload_platforms(entry,PLATFORMS)
    if ok: await hass.data[DOMAIN].pop(entry.entry_id).async_unload()
    return ok
