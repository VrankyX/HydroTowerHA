from datetime import timedelta
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.event import async_track_time_interval
from .const import DOMAIN
async def async_setup_entry(hass,entry,async_add_entities):
    m=hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HydroBinary(m,entry,"safe","Betriebssicher",BinarySensorDeviceClass.SAFETY),HydroBinary(m,entry,"refill","Nachfüllen",BinarySensorDeviceClass.PROBLEM),HydroBinary(m,entry,"overfill","Überfüllung",BinarySensorDeviceClass.PROBLEM),HydroBinary(m,entry,"level_sensor","Füllstandsensor",BinarySensorDeviceClass.CONNECTIVITY)])
class HydroBinary(BinarySensorEntity):
    _attr_has_entity_name=True
    def __init__(self,m,e,key,name,dc): self.m,self.e,self.key=m,e,key; self._attr_name=name; self._attr_unique_id=f"{e.entry_id}_{key}"; self._attr_device_class=dc
    @property
    def device_info(self): return DeviceInfo(identifiers={(DOMAIN,self.e.entry_id)},name=self.e.title,manufacturer="Custom / Home Assistant",model="Hydroponic Tower Controller")
    @property
    def is_on(self):
        h=self.m.fill_height_cm
        if self.key=="safe": return self.m.safe
        if self.key=="refill": return h is not None and h<float(self.m.options["refill_level_cm"])
        if self.key=="overfill": return h is not None and h>=float(self.m.options["overfill_level_cm"])
        if self.key=="level_sensor": return self.m.level_sensor_ok
        return False
    async def async_added_to_hass(self): self.async_on_remove(async_track_time_interval(self.hass,lambda now:self.async_write_ha_state(),timedelta(seconds=30)))
