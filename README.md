# Hydroponic Tower – HACS Custom Integration

Custom Integration zur Steuerung des Hydroponik-Towers über bereits in Home Assistant vorhandene Entities.

## Hardware
- Shelly Smart Plug: Haupt-/Umwälzpumpe
- Tuya 4-fach-Relais: pH+, pH−, Dünger, Grow-LED
- Tuya Yinmik: pH, EC, Wassertemperatur
- 1× Tuya-Lecksensor
- A02YYUW + ESP32/ESPHome: kontinuierlicher Füllstand
- optionaler zweiter Mindeststandsensor: **nicht aktiv**, nur für spätere Erweiterung vorgesehen

## Behälter
- unten Ø 26 cm
- oben Ø 36 cm
- Höhe 30 cm
- Gesamtvolumen ca. 22,84 L
- Soll 24 cm ≈ 17,07 L
- Nachfüllen unter 10 cm
- Not-Aus unter 7 cm
- Überfüllungs-Not-Aus ab 26 cm

## Installation über HACS
Dieses ZIP ist ein Repository-Template. Für HACS muss es zunächst in ein GitHub-Repository geladen werden.
1. GitHub-Repository anlegen, z. B. `hydroponic-tower`.
2. Inhalt dieses Pakets hochladen.
3. In `manifest.json` `DEIN_GITHUB_NAME` ersetzen.
4. HACS → Drei-Punkte-Menü → Benutzerdefinierte Repositories.
5. Repository-URL hinzufügen, Typ **Integration**.
6. Hydroponic Tower installieren und Home Assistant neu starten.
7. Einstellungen → Geräte & Dienste → Integration hinzufügen → Hydroponic Tower.

## Einrichtung
Der Config Flow fragt die vorhandenen Shelly-/Tuya-/Yinmik-/ESPHome-Entities ab. Danach können über **Konfigurieren** alle Grenzwerte, Laufzeiten, Kalibrierwerte und Automatiken eingestellt werden.

Automatische Bewässerung, pH-Regelung, Düngerdosierung und Grow-LED-Automatik sind standardmäßig **AUS**.

## Aktionen
- `hydroponic_tower.emergency_stop`
- `hydroponic_tower.water_once`
- `hydroponic_tower.dose_ph_plus`
- `hydroponic_tower.dose_ph_minus`
- `hydroponic_tower.dose_nutrient`

## Sicherheitslogik
- Leck → Not-Aus
- A02YYUW länger als 2 Minuten ungültig → Not-Aus
- Pegel < 7 cm → Not-Aus
- Pegel < 10 cm → Nachfüllmeldung
- Pegel ≥ 26 cm → Not-Aus
- pH+, pH− und Dünger werden vor jedem Impuls gegenseitig verriegelt
- Dosiersperrzeit und Tageslimits
- alle Ausgänge werden beim Laden/Entladen der Integration ausgeschaltet

## Hinweis
Version 0.1.0 ist eine erste Custom-Integration und sollte vor dem Anschluss von pH-Chemikalien und Dünger ausschließlich mit Wasser getestet werden. Home Assistant ist keine Safety-SPS.
