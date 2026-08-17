from __future__ import annotations
import asyncio, logging, math
from datetime import datetime, timedelta
from homeassistant.const import STATE_ON
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store
from .const import *

_LOGGER = logging.getLogger(__name__)

class HydroponicTowerManager:
    def __init__(self, hass, entry):
        self.hass, self.entry, self.data = hass, entry, entry.data
        self.options = {**DEFAULTS, **entry.options}
        self.store = Store(hass, 1, "hydroponic_tower_state")
        self.unsub = None
        self.tasks = set()
        self.last_distance_ok = datetime.now()
        self.last_dose = None
        self.next_watering = None
        self.daily_date = datetime.now().date()
        self.ph_plus_today = self.ph_minus_today = self.nutrient_today = 0.0
        self.status = "initializing"

    async def async_setup(self):
        old = await self.store.async_load() or {}
        self.ph_plus_today = float(old.get("ph_plus_today",0))
        self.ph_minus_today = float(old.get("ph_minus_today",0))
        self.nutrient_today = float(old.get("nutrient_today",0))
        await self.all_outputs_off()
        self.unsub = async_track_time_interval(self.hass, self._tick, timedelta(seconds=30))
        self.next_watering = datetime.now() + timedelta(seconds=10)
        self.status = "ready"

    async def async_unload(self):
        if self.unsub: self.unsub()
        for t in list(self.tasks): t.cancel()
        await self.all_outputs_off()

    def _float(self, entity):
        s = self.hass.states.get(entity)
        try: return float(s.state) if s else None
        except (TypeError, ValueError): return None

    @property
    def leak(self):
        s = self.hass.states.get(self.data[CONF_LEAK])
        return bool(s and s.state == STATE_ON)

    @property
    def distance_cm(self):
        v = self._float(self.data[CONF_DISTANCE])
        if v is not None and 3 <= v <= self.options["sensor_to_bottom_cm"] + 5:
            self.last_distance_ok = datetime.now()
            return v
        return None

    @property
    def level_sensor_ok(self):
        return datetime.now() - self.last_distance_ok < timedelta(minutes=float(self.options["distance_timeout_min"]))

    @property
    def fill_height_cm(self):
        d = self.distance_cm
        return None if d is None else max(0.0, min(30.0, float(self.options["sensor_to_bottom_cm"]) - d))

    @property
    def volume_l(self):
        h = self.fill_height_cm
        if h is None: return None
        r0, r = 13.0, 13.0 + h/6.0
        return math.pi*h/3.0*(r0*r0+r0*r+r*r)/1000.0

    @property
    def fill_percent(self):
        h, target = self.fill_height_cm, float(self.options["target_level_cm"])
        return None if h is None or target <= 0 else max(0.0,min(125.0,h/target*100.0))

    @property
    def safe(self):
        h = self.fill_height_cm
        return (not self.leak and self.level_sensor_ok and h is not None
                and h >= float(self.options["critical_level_cm"])
                and h < float(self.options["overfill_level_cm"]))

    @property
    def ph(self): return self._float(self.data[CONF_PH_SENSOR])
    @property
    def ec(self): return self._float(self.data[CONF_EC_SENSOR])
    @property
    def water_temp(self): return self._float(self.data[CONF_WATER_TEMP])

    async def _switch(self, entity, on):
        await self.hass.services.async_call("switch", "turn_on" if on else "turn_off", {"entity_id":entity}, blocking=True)

    async def all_outputs_off(self):
        for e in (self.data[CONF_PUMP],self.data[CONF_PH_PLUS],self.data[CONF_PH_MINUS],self.data[CONF_NUTRIENT],self.data[CONF_GROW_LIGHT]):
            try: await self._switch(e,False)
            except Exception: _LOGGER.exception("Could not switch off %s", e)

    async def emergency_stop(self, reason="Safety condition"):
        self.status = f"alarm: {reason}"
        await self.all_outputs_off()
        self.next_watering = None
        self.hass.components.persistent_notification.async_create(
            f"{reason}. Alle Ausgänge wurden ausgeschaltet.",
            title="Hydroponic Tower – Notabschaltung", notification_id="hydroponic_tower_alarm")

    def _task(self, coro):
        t = self.hass.async_create_task(coro); self.tasks.add(t); t.add_done_callback(self.tasks.discard)

    async def water_once(self):
        if not self.safe:
            await self.emergency_stop("Bewässerung blockiert: Sicherheitsbedingung nicht erfüllt"); return
        self.status = "watering"; await self._switch(self.data[CONF_PUMP],True)
        try: await asyncio.sleep(float(self.options["watering_run_sec"]))
        finally: await self._switch(self.data[CONF_PUMP],False)
        self.next_watering = datetime.now()+timedelta(minutes=float(self.options["watering_pause_min"]))
        self.status = "ready"

    def _dose_allowed(self):
        return self.safe and (self.last_dose is None or datetime.now()-self.last_dose >= timedelta(minutes=float(self.options["dose_lock_min"])))

    async def dose(self, kind):
        if not self._dose_allowed(): return
        m = {
          "ph_plus":(CONF_PH_PLUS,"ph_plus_pulse_sec","ph_plus_ml_sec","ph_plus_today","ph_daily_limit_ml"),
          "ph_minus":(CONF_PH_MINUS,"ph_minus_pulse_sec","ph_minus_ml_sec","ph_minus_today","ph_daily_limit_ml"),
          "nutrient":(CONF_NUTRIENT,"nutrient_pulse_sec","nutrient_ml_sec","nutrient_today","nutrient_daily_limit_ml")}
        ck, pk, fk, counter, limit = m[kind]
        pulse=float(self.options[pk]); amount=pulse*float(self.options[fk])
        if getattr(self,counter)+amount > float(self.options[limit]):
            self.status=f"daily limit: {kind}"; return
        for e in (self.data[CONF_PH_PLUS],self.data[CONF_PH_MINUS],self.data[CONF_NUTRIENT]): await self._switch(e,False)
        await self._switch(self.data[CONF_PUMP],True); await asyncio.sleep(5)
        relay=self.data[ck]; self.status=f"dosing {kind}"
        try: await self._switch(relay,True); await asyncio.sleep(pulse)
        finally: await self._switch(relay,False)
        setattr(self,counter,getattr(self,counter)+amount); self.last_dose=datetime.now(); await self._save()
        self.status="mixing"; await asyncio.sleep(float(self.options["mix_time_min"])*60)
        await self._switch(self.data[CONF_PUMP],False); self.status="ready"

    async def _save(self):
        await self.store.async_save({"ph_plus_today":self.ph_plus_today,"ph_minus_today":self.ph_minus_today,"nutrient_today":self.nutrient_today})

    async def _tick(self, now):
        if now.date()!=self.daily_date:
            self.daily_date=now.date(); self.ph_plus_today=self.ph_minus_today=self.nutrient_today=0.0; await self._save()
        if self.leak: await self.emergency_stop("Wasserleck erkannt"); return
        _=self.distance_cm
        if not self.level_sensor_ok: await self.emergency_stop("A02YYUW Füllstandsensor ausgefallen"); return
        h=self.fill_height_cm
        if h is None: return
        if h<float(self.options["critical_level_cm"]): await self.emergency_stop(f"Wasserstand kritisch niedrig ({h:.1f} cm)"); return
        if h>=float(self.options["overfill_level_cm"]): await self.emergency_stop(f"Überfüllungsgrenze erreicht ({h:.1f} cm)"); return
        if h<float(self.options["refill_level_cm"]):
            self.hass.components.persistent_notification.async_create(f"Füllhöhe {h:.1f} cm / {self.volume_l:.1f} L.",title="Hydroponic Tower – Wasser nachfüllen",notification_id="hydroponic_tower_refill")
        temp=self.water_temp
        if temp is not None and temp>float(self.options["water_temp_max"]):
            self.hass.components.persistent_notification.async_create(f"Wassertemperatur {temp:.1f} °C.",title="Hydroponic Tower – Temperatur",notification_id="hydroponic_tower_temperature")
        if self.options["grow_light_auto_enabled"]:
            try:
                oh,om=map(int,self.options["grow_light_on"].split(":")); fh,fm=map(int,self.options["grow_light_off"].split(":")); cur=now.hour*60+now.minute; on=oh*60+om; off=fh*60+fm
                should = on<=cur<off if on<off else (cur>=on or cur<off); await self._switch(self.data[CONF_GROW_LIGHT],should)
            except Exception: _LOGGER.exception("Invalid grow light time")
        if any(not t.done() for t in self.tasks): return
        if self.options["watering_enabled"] and (self.next_watering is None or now>=self.next_watering): self._task(self.water_once()); return
        if self.options["ph_auto_enabled"] and self._dose_allowed() and self.ph is not None:
            if self.ph<float(self.options["ph_min"]): self._task(self.dose("ph_plus")); return
            if self.ph>float(self.options["ph_max"]): self._task(self.dose("ph_minus")); return
        if self.options["nutrient_auto_enabled"] and self._dose_allowed() and self.ec is not None and self.ec<float(self.options["ec_min"]): self._task(self.dose("nutrient"))
