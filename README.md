# HydroTowerHA v0.1.2

HACS-compatible Home Assistant custom integration for a hydroponic tower.

## Hardware model

- Shelly smart plug: circulation / watering pump
- Tuya 4-channel relay:
  - pH+
  - pH-
  - nutrient
  - grow light
- Tuya Yinmik water-quality sensor:
  - pH
  - EC
  - water temperature
- 1 Tuya leak sensor
- A02YYUW ultrasonic level sensor via ESPHome

The optional second minimum-level sensor is intentionally not active.

## Vessel defaults

- bottom diameter: 26 cm
- top diameter: 36 cm
- height: 30 cm
- target fill height: 24 cm
- refill warning: below 10 cm
- emergency low level: below 7 cm
- overfill shutdown: 26 cm and above

## Installation

1. Upload this repository to GitHub.
2. Add the repository to HACS as a custom repository of type **Integration**.
3. Install HydroTowerHA.
4. Restart Home Assistant.
5. Go to **Settings → Devices & services → Add integration**.
6. Search for **HydroTowerHA**.

## v0.1.2 fix

This release replaces `config_flow.py` with a clean, consistently indented
implementation and uses the current Home Assistant Options Flow pattern.

Automatic watering and dosing remain disabled by default.
