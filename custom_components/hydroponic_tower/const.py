DOMAIN = "hydroponic_tower"
PLATFORMS = ["sensor", "binary_sensor"]

CONF_PUMP = "pump"
CONF_PH_PLUS = "ph_plus"
CONF_PH_MINUS = "ph_minus"
CONF_NUTRIENT = "nutrient"
CONF_GROW_LIGHT = "grow_light"
CONF_LEAK = "leak"
CONF_PH_SENSOR = "ph_sensor"
CONF_EC_SENSOR = "ec_sensor"
CONF_WATER_TEMP = "water_temp"
CONF_DISTANCE = "distance"

DEFAULTS = {
    "sensor_to_bottom_cm": 33.0,
    "critical_level_cm": 7.0,
    "refill_level_cm": 10.0,
    "target_level_cm": 24.0,
    "overfill_level_cm": 26.0,
    "distance_timeout_min": 2,
    "watering_enabled": False,
    "watering_run_sec": 900,
    "watering_pause_min": 45,
    "ph_auto_enabled": False,
    "ph_min": 5.8,
    "ph_max": 6.2,
    "ph_plus_pulse_sec": 2.0,
    "ph_minus_pulse_sec": 2.0,
    "ph_plus_ml_sec": 1.0,
    "ph_minus_ml_sec": 1.0,
    "ph_daily_limit_ml": 50.0,
    "nutrient_auto_enabled": False,
    "ec_min": 1200.0,
    "nutrient_pulse_sec": 3.0,
    "nutrient_ml_sec": 1.0,
    "nutrient_daily_limit_ml": 200.0,
    "mix_time_min": 15,
    "dose_lock_min": 30,
    "water_temp_max": 25.0,
    "grow_light_auto_enabled": False,
    "grow_light_on": "06:00",
    "grow_light_off": "22:00"
}
