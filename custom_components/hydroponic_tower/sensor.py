from datetime import timedelta
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.event import async_track_time_interval
from .const import DOMAIN
SENSORS=(
 ("status","Status",None,None),("fill_height","Füllhöhe","cm",SensorDeviceClass.DISTANCE),
 ("volume","Wassermenge","L",SensorDeviceClass.VOLUME),("fill_percent","Füllstand","%",None),
 ("ph_plus_today","pH+ heute","mL",SensorDeviceClass.VOLUME),("ph_minus_today","pH− heute","mL",SensorDeviceClass.VOLUME),
 ("nutrient_today","Dünger heute","mL",SensorDeviceClass.VOLUME))
async def async_setup_entry(hass,entry,async_add_entities):
    m=hass.data[DOMAIN][entry.entry_id]; async_add_entities([HydroSensor(m,entry,*x) for x in SENSORS])
class HydroSensor(SensorEntity):
    _attr_has_entity_name=True
    def __init__(self,m,e,key,name,unit,dc):
        self.m,self.e,self.key=m,e,key; self._attr_name=name; self._attr_unique_id=f"{e.entry_id}_{key}"; self._attr_native_unit_of_measurement=unit; self._attr_device_class=dc
        if key!="status": self._attr_state_class=SensorStateClass.MEASUREMENT
    @property
    def device_info(self): return DeviceInfo(identifiers={(DOMAIN,self.e.entry_id)},name=self.e.title,manufacturer="Custom / Home Assistant",model="Hydroponic Tower Controller")
    @property
    def native_value(self):
        v={"status":self.m.status,"fill_height":self.m.fill_height_cm,"volume":self.m.volume_l,"fill_percent":self.m.fill_percent,"ph_plus_today":self.m.ph_plus_today,"ph_minus_today":self.m.ph_minus_today,"nutrient_today":self.m.nutrient_today}[self.key]
        return round(v,2) if isinstance(v,float) else v
    async def async_added_to_hass(self): self.async_on_remove(async_track_time_interval(self.hass,lambda now:self.async_write_ha_state(),timedelta(seconds=30)))
