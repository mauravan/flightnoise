# Ist-Lärmpegel am Empfänger (fluglaerm own)

**Empfänger:** E=2656781 m, N=1244154 m, h=78.7 m über Flughafen-Grund
**Suchradius:** 15000 m
**Fenster:** 3600 s (lautester Sample im Fenster), min 2026-10-19 11:36:11Z (ts=1792409771), max 2026-10-19 12:31:11Z (ts=1792413071)
**ANP-Datenbank:** data/anp.sqlite
**Registry:** data/aircraft_registry.json

## Tabelle
| Rufzeichen | ICAO24 | Flugzeug | Phase | Rating | Schub (lb) | Distanz (m) | Lmax (dB) | SEL (dB) | Zeit | Bemerkungen |
|---|---|---|---|---|---|---|---|---|---|---|
| DAL53 | a11d47 | 7673ER | departure | MaxClimb | 46100 | 3812 | 58.2 | 73.2 | 11:50:12Z | HiTemp; ΔI -0.7, Λ 0.0, ΔV -2.2 |
| EDW10K | 4b15d6 | A350-1041 | departure | MaxClimb | 61970 | 3134 | 55.6 | 70.5 | 11:57:12Z | HiTemp; ΔI -0.6, Λ 0.0, ΔV -2.7 |
| SWR64E | 4b191d | 7773ER | departure | MaxClimb | 70107 | 4603 | 52.0 | 66.3 | 11:42:12Z | HiTemp; Schätzung (>10 000 ft AFE); ΔI -0.7, Λ 0.1, ΔV -3.5 |
| SWR8T | 4b1920 | 7773ER | departure | MaxClimb | 68955 | 4707 | 51.5 | 65.7 | 11:53:12Z | HiTemp; Schätzung (>10 000 ft AFE); ΔI -0.7, Λ 0.1, ΔV -3.8 |
| SWR54B | 4b15a4 | A350-1041 | departure | MaxClimb | 62082 | 4132 | 51.0 | 66.4 | 11:43:12Z | HiTemp; Schätzung (>10 000 ft AFE); ΔI -0.7, Λ 0.1, ΔV -3.2 |
| SWR72 | 4b187e | A330-743L | departure | MaxClimb | 49801 | 4887 | 50.8 | 66.6 | 12:06:12Z | HiTemp; Schätzung (>10 000 ft AFE); ΔI -0.8, Λ 0.3, ΔV -3.0 |
| SWR40 | 4b1921 | 7773ER | departure | MaxClimb | 69776 | 5704 | 48.5 | 63.7 | 12:05:12Z | HiTemp; Schätzung (>10 000 ft AFE); ΔI -0.8, Λ 0.4, ΔV -3.6 |
| SWR2AY | 4b194b | A321-270N | departure | MaxClimb | 23920 | 4072 | 47.3 | 62.7 | 11:36:11Z | HiTemp; ΔI -0.8, Λ 0.2, ΔV -2.6 |
| SWR533X | 4b1815 | A320-250N | departure | MaxClimb | 22278 | 4451 | 42.7 | 57.9 | 12:27:12Z | HiTemp; Schätzung (>10 000 ft AFE); ΔI -0.6, Λ 0.0, ΔV -3.2 |
| EZY3836 | 406017 | A320-211 | departure | MaxClimb | 22580 | 15217 | 42.3 | 59.0 | 12:14:11Z | Ersatz A320 → A320-211, Δ +0.2 dB; HiTemp; Schätzung (>10 000 ft AFE); ΔI -0.8, Λ 0.4, ΔV -4.3 |
| EDW115 | 4b161e | A320-211 | departure | MaxClimb | 19083 | 6506 | 41.8 | 59.9 | 12:31:11Z | Ersatz A320 → A320-211, Δ +0.2 dB; HiTemp; Schätzung (>10 000 ft AFE); ΔI -0.8, Λ 0.4, ΔV -2.4 |
| EZS27BL | 4b1a67 | A320-211 | departure | MaxClimb | 21207 | 12948 | 41.0 | 58.1 | 12:05:12Z | Ersatz A320 → A320-211, Δ +0.2 dB; HiTemp; Schätzung (>10 000 ft AFE); ΔI -0.8, Λ 0.5, ΔV -3.9 |
| SWR1LE | 4b18fe | A340-211 | departure | MaxClimb | 24234 | 7730 | 38.7 | 58.1 | 12:03:12Z | Ersatz A343 → A340-211, Δ +1.3 dB; HiTemp; ΔI -0.8, Λ 1.0, ΔV -3.1 |
| EZS29ZA | 4b027f | A320-250N | departure | MaxClimb | 26941 | 9861 | 36.9 | 53.9 | 12:10:12Z | HiTemp; Schätzung (>10 000 ft AFE); ΔI -0.6, Λ 0.0, ΔV -3.9 |
| BAW733 | 408227 | A321-270N | departure | MaxClimb | 24061 | 9107 | 35.4 | 52.7 | 12:00:12Z | HiTemp; Schätzung (>10 000 ft AFE); ΔI -0.8, Λ 0.9, ΔV -3.5 |
| IBE06HE | 346186 | A320-250N | departure | MaxClimb | 23227 | 11868 | 32.5 | 50.0 | 11:41:12Z | HiTemp; Schätzung (>10 000 ft AFE); ΔI -0.8, Λ 1.1, ΔV -3.1 |

## Herleitung je Flugzeug
### DAL53 (a11d47) — 7673ER
| Schritt | Wert | Quelle |
|---|---|---|
|Flugzeugzuordnung|Registry → 7673ER|data/aircraft_registry.json|
|Flugzeugdaten|Boeing 767-300ER / CF6-80C2B6F, 2 TW, Wing, NPD-ID 7673ER, Max-Schub 61500 lb|data/anp.sqlite · Tabelle aircraft|
|State|ts=1792410612 E=2659129 N=1244833 alt=3436.6 m v=264.7 kn trk=238° vr=+8.78 m/s on_ground=False|OpenSky-State (own_states/own_history)|
|Höhe MSL|3436.6 m = 11275 ft|alt_m × 3.28084|
|Höhe AFE|9858 ft|alt_msl_ft − ARP(432.0 m) × 3.28084|
|Phase|D / MaxClimb|pick_phase(vr=+8.78 m/s, alt_afe=9858 ft, cutback=1500.0)|
|B-1 Koeffizienten|e=47210.8987 f=-47.5984 ga=0.78953 gb=-8.47e-06 h=0 + HiTemp e=51100.9361 f=-29.497 ga=-0.044119 gb=1.53e-05 h=-261.6588|data/anp.sqlite · Tabelle jet_engine_coefficients (7673ER, MaxClimb)|
|VC (CAS)|187.7 kt (TAS 264.7 kn)|calibrated_airspeed_kt|
|T (ISA)|-7.3 °C|15 − 0.0019812 × 11275 ft|
|CNT|46100 lbf|corrected_net_thrust(low[, hi], VC, alt_msl_ft, T)|
|NPD-Tabelle|7673ER D wing 61500 lb · 5 Leistungsstufen · ref 160 kn|EASA-ANP v9 (data/anp.sqlite) · Tabelle npd_data|
|Slant-Distanz|3812.4 m|slant_m(E, N, alt−ARP, Empfänger)|
|Elevation|50.1°|asin((alt−ARP−h)/slant)|
|Lateral-Offset|676 m|lateral_offset_m(…)|
|base Lmax|58.88 dB|interp_npd(LAmax, CNT, slant)|
|base SEL|76.07 dB|interp_npd(SEL, CNT, slant)|
|ΔI|-0.68 dB|installation_correction(elev, mount=wing)|
|Λ|0.00 dB|lateral_attenuation(elev, lat)|
|ΔV|-2.19 dB|duration_correction(v=264.7 kn, ref=160 kn)|
|**Lmax**|**58.20 dB**|base_Lmax + ΔI − Λ + Δ|
|**SEL**|**73.20 dB**|base_SEL + ΔV + ΔI − Λ + Δ|
> HiTemp-Flat-Rating zieht (Min aus low/hi B-1)

### EDW10K (4b15d6) — A350-1041
| Schritt | Wert | Quelle |
|---|---|---|
|Flugzeugzuordnung|Registry → A350-1041|data/aircraft_registry.json|
|Flugzeugdaten|Airbus A350-1041 / RR Trent XWB-97, 2 TW, Wing, NPD-ID A350-1041, Max-Schub 97000 lb|data/anp.sqlite · Tabelle aircraft|
|State|ts=1792411032 E=2658602 N=1243827 alt=3040.4 m v=295.6 kn trk=243° vr=+10.40 m/s on_ground=False|OpenSky-State (own_states/own_history)|
|Höhe MSL|3040.4 m = 9975 ft|alt_m × 3.28084|
|Höhe AFE|8558 ft|alt_msl_ft − ARP(432.0 m) × 3.28084|
|Phase|D / MaxClimb|pick_phase(vr=+10.40 m/s, alt_afe=8558 ft, cutback=1500.0)|
|B-1 Koeffizienten|e=72185.7 f=-89.88632 ga=1.70847 gb=-5.562e-05 h=0 + HiTemp e=71441.8 f=-50.35066 ga=0 gb=0 h=-321|data/anp.sqlite · Tabelle jet_engine_coefficients (A350-1041, MaxClimb)|
|VC (CAS)|218.5 kt (TAS 295.6 kn)|calibrated_airspeed_kt|
|T (ISA)|-4.8 °C|15 − 0.0019812 × 9975 ft|
|CNT|61970 lbf|corrected_net_thrust(low[, hi], VC, alt_msl_ft, T)|
|NPD-Tabelle|A350-1041 D wing 97000 lb · 5 Leistungsstufen · ref 160 kn|EASA-ANP v9 (data/anp.sqlite) · Tabelle npd_data|
|Slant-Distanz|3134.1 m|slant_m(E, N, alt−ARP, Empfänger)|
|Elevation|53.8°|asin((alt−ARP−h)/slant)|
|Lateral-Offset|1122 m|lateral_offset_m(…)|
|base Lmax|56.21 dB|interp_npd(LAmax, CNT, slant)|
|base SEL|73.75 dB|interp_npd(SEL, CNT, slant)|
|ΔI|-0.62 dB|installation_correction(elev, mount=wing)|
|Λ|0.00 dB|lateral_attenuation(elev, lat)|
|ΔV|-2.67 dB|duration_correction(v=295.6 kn, ref=160 kn)|
|**Lmax**|**55.59 dB**|base_Lmax + ΔI − Λ + Δ|
|**SEL**|**70.47 dB**|base_SEL + ΔV + ΔI − Λ + Δ|
> HiTemp-Flat-Rating zieht (Min aus low/hi B-1)

### SWR64E (4b191d) — 7773ER
| Schritt | Wert | Quelle |
|---|---|---|
|Flugzeugzuordnung|Registry → 7773ER|data/aircraft_registry.json|
|Flugzeugdaten|Boeing 777-300ER / GE90-115B, 2 TW, Wing, NPD-ID 7773ER, Max-Schub 115000 lb|data/anp.sqlite · Tabelle aircraft|
|State|ts=1792410132 E=2654974 N=1241435 alt=3756.7 m v=361.0 kn trk=264° vr=+8.13 m/s on_ground=False|OpenSky-State (own_states/own_history)|
|Höhe MSL|3756.7 m = 12325 ft|alt_m × 3.28084|
|Höhe AFE|10908 ft|alt_msl_ft − ARP(432.0 m) × 3.28084|
|Phase|D / MaxClimb|pick_phase(vr=+8.13 m/s, alt_afe=10908 ft, cutback=None)|
|B-1 Koeffizienten|e=92110 f=-119 ga=1.14 gb=-7e-06 h=0 + HiTemp e=96550 f=-69.4 ga=-0.542 gb=-5e-05 h=-533|data/anp.sqlite · Tabelle jet_engine_coefficients (7773ER, MaxClimb)|
|VC (CAS)|247.7 kt (TAS 361.0 kn)|calibrated_airspeed_kt|
|T (ISA)|-9.4 °C|15 − 0.0019812 × 12325 ft|
|CNT|70107 lbf|corrected_net_thrust(low[, hi], VC, alt_msl_ft, T)|
|NPD-Tabelle|7773ER D wing 115000 lb · 6 Leistungsstufen · ref 160 kn|EASA-ANP v9 (data/anp.sqlite) · Tabelle npd_data|
|Slant-Distanz|4603.4 m|slant_m(E, N, alt−ARP, Empfänger)|
|Elevation|44.8°|asin((alt−ARP−h)/slant)|
|Lateral-Offset|2513 m|lateral_offset_m(…)|
|base Lmax|52.89 dB|interp_npd(LAmax, CNT, slant)|
|base SEL|70.73 dB|interp_npd(SEL, CNT, slant)|
|ΔI|-0.75 dB|installation_correction(elev, mount=wing)|
|Λ|0.13 dB|lateral_attenuation(elev, lat)|
|ΔV|-3.53 dB|duration_correction(v=361.0 kn, ref=160 kn)|
|**Lmax**|**52.02 dB**|base_Lmax + ΔI − Λ + Δ|
|**SEL**|**66.32 dB**|base_SEL + ΔV + ΔI − Λ + Δ|
> Schätzung: über 10 000 ft AFE — D/MaxClimb ohne NPD-Prozedur
> HiTemp-Flat-Rating zieht (Min aus low/hi B-1)

### SWR8T (4b1920) — 7773ER
| Schritt | Wert | Quelle |
|---|---|---|
|Flugzeugzuordnung|Registry → 7773ER|data/aircraft_registry.json|
|Flugzeugdaten|Boeing 777-300ER / GE90-115B, 2 TW, Wing, NPD-ID 7773ER, Max-Schub 115000 lb|data/anp.sqlite · Tabelle aircraft|
|State|ts=1792410792 E=2653988 N=1242627 alt=3977.6 m v=382.5 kn trk=265° vr=+9.43 m/s on_ground=False|OpenSky-State (own_states/own_history)|
|Höhe MSL|3977.6 m = 13050 ft|alt_m × 3.28084|
|Höhe AFE|11633 ft|alt_msl_ft − ARP(432.0 m) × 3.28084|
|Phase|D / MaxClimb|pick_phase(vr=+9.43 m/s, alt_afe=11633 ft, cutback=None)|
|B-1 Koeffizienten|e=92110 f=-119 ga=1.14 gb=-7e-06 h=0 + HiTemp e=96550 f=-69.4 ga=-0.542 gb=-5e-05 h=-533|data/anp.sqlite · Tabelle jet_engine_coefficients (7773ER, MaxClimb)|
|VC (CAS)|256.4 kt (TAS 382.5 kn)|calibrated_airspeed_kt|
|T (ISA)|-10.9 °C|15 − 0.0019812 × 13050 ft|
|CNT|68955 lbf|corrected_net_thrust(low[, hi], VC, alt_msl_ft, T)|
|NPD-Tabelle|7773ER D wing 115000 lb · 6 Leistungsstufen · ref 160 kn|EASA-ANP v9 (data/anp.sqlite) · Tabelle npd_data|
|Slant-Distanz|4706.5 m|slant_m(E, N, alt−ARP, Empfänger)|
|Elevation|47.4°|asin((alt−ARP−h)/slant)|
|Lateral-Offset|1272 m|lateral_offset_m(…)|
|base Lmax|52.32 dB|interp_npd(LAmax, CNT, slant)|
|base SEL|70.24 dB|interp_npd(SEL, CNT, slant)|
|ΔI|-0.72 dB|installation_correction(elev, mount=wing)|
|Λ|0.06 dB|lateral_attenuation(elev, lat)|
|ΔV|-3.79 dB|duration_correction(v=382.5 kn, ref=160 kn)|
|**Lmax**|**51.53 dB**|base_Lmax + ΔI − Λ + Δ|
|**SEL**|**65.67 dB**|base_SEL + ΔV + ΔI − Λ + Δ|
> Schätzung: über 10 000 ft AFE — D/MaxClimb ohne NPD-Prozedur
> HiTemp-Flat-Rating zieht (Min aus low/hi B-1)

### SWR54B (4b15a4) — A350-1041
| Schritt | Wert | Quelle |
|---|---|---|
|Flugzeugzuordnung|Registry → A350-1041|data/aircraft_registry.json|
|Flugzeugdaten|Airbus A350-1041 / RR Trent XWB-97, 2 TW, Wing, NPD-ID A350-1041, Max-Schub 97000 lb|data/anp.sqlite · Tabelle aircraft|
|State|ts=1792410192 E=2659624 N=1244416 alt=3497.6 m v=333.7 kn trk=242° vr=+4.23 m/s on_ground=False|OpenSky-State (own_states/own_history)|
|Höhe MSL|3497.6 m = 11475 ft|alt_m × 3.28084|
|Höhe AFE|10058 ft|alt_msl_ft − ARP(432.0 m) × 3.28084|
|Phase|D / MaxClimb|pick_phase(vr=+4.23 m/s, alt_afe=10058 ft, cutback=None)|
|B-1 Koeffizienten|e=72185.7 f=-89.88632 ga=1.70847 gb=-5.562e-05 h=0 + HiTemp e=71441.8 f=-50.35066 ga=0 gb=0 h=-321|data/anp.sqlite · Tabelle jet_engine_coefficients (A350-1041, MaxClimb)|
|VC (CAS)|235.2 kt (TAS 333.7 kn)|calibrated_airspeed_kt|
|T (ISA)|-7.7 °C|15 − 0.0019812 × 11475 ft|
|CNT|62082 lbf|corrected_net_thrust(low[, hi], VC, alt_msl_ft, T)|
|NPD-Tabelle|A350-1041 D wing 97000 lb · 5 Leistungsstufen · ref 160 kn|EASA-ANP v9 (data/anp.sqlite) · Tabelle npd_data|
|Slant-Distanz|4131.9 m|slant_m(E, N, alt−ARP, Empfänger)|
|Elevation|46.3°|asin((alt−ARP−h)/slant)|
|Lateral-Offset|1098 m|lateral_offset_m(…)|
|base Lmax|51.83 dB|interp_npd(LAmax, CNT, slant)|
|base SEL|70.43 dB|interp_npd(SEL, CNT, slant)|
|ΔI|-0.73 dB|installation_correction(elev, mount=wing)|
|Λ|0.09 dB|lateral_attenuation(elev, lat)|
|ΔV|-3.19 dB|duration_correction(v=333.7 kn, ref=160 kn)|
|**Lmax**|**51.01 dB**|base_Lmax + ΔI − Λ + Δ|
|**SEL**|**66.41 dB**|base_SEL + ΔV + ΔI − Λ + Δ|
> Schätzung: über 10 000 ft AFE — D/MaxClimb ohne NPD-Prozedur
> HiTemp-Flat-Rating zieht (Min aus low/hi B-1)

### SWR72 (4b187e) — A330-743L
| Schritt | Wert | Quelle |
|---|---|---|
|Flugzeugzuordnung|Registry → A330-743L|data/aircraft_registry.json|
|Flugzeugdaten|Airbus A330-743L / RR Trent 772B, 2 TW, Wing, NPD-ID A330-743L, Max-Schub 71100 lb|data/anp.sqlite · Tabelle aircraft|
|State|ts=1792411572 E=2654052 N=1241405 alt=3490.0 m v=320.7 kn trk=242° vr=+4.23 m/s on_ground=False|OpenSky-State (own_states/own_history)|
|Höhe MSL|3490.0 m = 11450 ft|alt_m × 3.28084|
|Höhe AFE|10033 ft|alt_msl_ft − ARP(432.0 m) × 3.28084|
|Phase|D / MaxClimb|pick_phase(vr=+4.23 m/s, alt_afe=10033 ft, cutback=None)|
|B-1 Koeffizienten|e=44549.3 f=-18.01457 ga=0.91803 gb=-9.036e-06 h=0 + HiTemp e=61630 f=-48.29699 ga=0 gb=0 h=-390|data/anp.sqlite · Tabelle jet_engine_coefficients (A330-743L, MaxClimb)|
|VC (CAS)|226.2 kt (TAS 320.7 kn)|calibrated_airspeed_kt|
|T (ISA)|-7.7 °C|15 − 0.0019812 × 11450 ft|
|CNT|49801 lbf|corrected_net_thrust(low[, hi], VC, alt_msl_ft, T)|
|NPD-Tabelle|A330-743L D wing 71100 lb · 5 Leistungsstufen · ref 160 kn|EASA-ANP v9 (data/anp.sqlite) · Tabelle npd_data|
|Slant-Distanz|4886.8 m|slant_m(E, N, alt−ARP, Empfänger)|
|Elevation|37.6°|asin((alt−ARP−h)/slant)|
|Lateral-Offset|1167 m|lateral_offset_m(…)|
|base Lmax|51.88 dB|interp_npd(LAmax, CNT, slant)|
|base SEL|70.78 dB|interp_npd(SEL, CNT, slant)|
|ΔI|-0.79 dB|installation_correction(elev, mount=wing)|
|Λ|0.32 dB|lateral_attenuation(elev, lat)|
|ΔV|-3.02 dB|duration_correction(v=320.7 kn, ref=160 kn)|
|**Lmax**|**50.77 dB**|base_Lmax + ΔI − Λ + Δ|
|**SEL**|**66.65 dB**|base_SEL + ΔV + ΔI − Λ + Δ|
> Schätzung: über 10 000 ft AFE — D/MaxClimb ohne NPD-Prozedur
> HiTemp-Flat-Rating zieht (Min aus low/hi B-1)

### SWR40 (4b1921) — 7773ER
| Schritt | Wert | Quelle |
|---|---|---|
|Flugzeugzuordnung|Registry → 7773ER|data/aircraft_registry.json|
|Flugzeugdaten|Boeing 777-300ER / GE90-115B, 2 TW, Wing, NPD-ID 7773ER, Max-Schub 115000 lb|data/anp.sqlite · Tabelle aircraft|
|State|ts=1792411512 E=2653054 N=1241396 alt=3832.9 m v=367.1 kn trk=257° vr=+6.50 m/s on_ground=False|OpenSky-State (own_states/own_history)|
|Höhe MSL|3832.9 m = 12575 ft|alt_m × 3.28084|
|Höhe AFE|11158 ft|alt_msl_ft − ARP(432.0 m) × 3.28084|
|Phase|D / MaxClimb|pick_phase(vr=+6.50 m/s, alt_afe=11158 ft, cutback=None)|
|B-1 Koeffizienten|e=92110 f=-119 ga=1.14 gb=-7e-06 h=0 + HiTemp e=96550 f=-69.4 ga=-0.542 gb=-5e-05 h=-533|data/anp.sqlite · Tabelle jet_engine_coefficients (7773ER, MaxClimb)|
|VC (CAS)|249.8 kt (TAS 367.1 kn)|calibrated_airspeed_kt|
|T (ISA)|-9.9 °C|15 − 0.0019812 × 12575 ft|
|CNT|69776 lbf|corrected_net_thrust(low[, hi], VC, alt_msl_ft, T)|
|NPD-Tabelle|7773ER D wing 115000 lb · 6 Leistungsstufen · ref 160 kn|EASA-ANP v9 (data/anp.sqlite) · Tabelle npd_data|
|Slant-Distanz|5703.8 m|slant_m(E, N, alt−ARP, Empfänger)|
|Elevation|35.6°|asin((alt−ARP−h)/slant)|
|Lateral-Offset|1868 m|lateral_offset_m(…)|
|base Lmax|49.71 dB|interp_npd(LAmax, CNT, slant)|
|base SEL|68.47 dB|interp_npd(SEL, CNT, slant)|
|ΔI|-0.79 dB|installation_correction(elev, mount=wing)|
|Λ|0.38 dB|lateral_attenuation(elev, lat)|
|ΔV|-3.61 dB|duration_correction(v=367.1 kn, ref=160 kn)|
|**Lmax**|**48.54 dB**|base_Lmax + ΔI − Λ + Δ|
|**SEL**|**63.69 dB**|base_SEL + ΔV + ΔI − Λ + Δ|
> Schätzung: über 10 000 ft AFE — D/MaxClimb ohne NPD-Prozedur
> HiTemp-Flat-Rating zieht (Min aus low/hi B-1)

### SWR2AY (4b194b) — A321-270N
| Schritt | Wert | Quelle |
|---|---|---|
|Flugzeugzuordnung|Registry → A321-270N|data/aircraft_registry.json|
|Flugzeugdaten|Airbus A321-270N / PW1130G-JM, 2 TW, Wing, NPD-ID A321-270N, Max-Schub 33110 lb|data/anp.sqlite · Tabelle aircraft|
|State|ts=1792409771 E=2659752 N=1244473 alt=3276.6 m v=293.9 kn trk=243° vr=+17.56 m/s on_ground=False|OpenSky-State (own_states/own_history)|
|Höhe MSL|3276.6 m = 10750 ft|alt_m × 3.28084|
|Höhe AFE|9333 ft|alt_msl_ft − ARP(432.0 m) × 3.28084|
|Phase|D / MaxClimb|pick_phase(vr=+17.56 m/s, alt_afe=9333 ft, cutback=1500.0)|
|B-1 Koeffizienten|e=28591.3 f=-35.34956 ga=0.260241 gb=1.98e-07 h=0 + HiTemp e=29810.2 f=-30.92756 ga=0 gb=0 h=-122|data/anp.sqlite · Tabelle jet_engine_coefficients (A321-270N, MaxClimb)|
|VC (CAS)|211.9 kt (TAS 293.9 kn)|calibrated_airspeed_kt|
|T (ISA)|-6.3 °C|15 − 0.0019812 × 10750 ft|
|CNT|23920 lbf|corrected_net_thrust(low[, hi], VC, alt_msl_ft, T)|
|NPD-Tabelle|A321-270N D wing 33110 lb · 5 Leistungsstufen · ref 160 kn|EASA-ANP v9 (data/anp.sqlite) · Tabelle npd_data|
|Slant-Distanz|4071.6 m|slant_m(E, N, alt−ARP, Empfänger)|
|Elevation|42.8°|asin((alt−ARP−h)/slant)|
|Lateral-Offset|1082 m|lateral_offset_m(…)|
|base Lmax|48.27 dB|interp_npd(LAmax, CNT, slant)|
|base SEL|66.28 dB|interp_npd(SEL, CNT, slant)|
|ΔI|-0.77 dB|installation_correction(elev, mount=wing)|
|Λ|0.18 dB|lateral_attenuation(elev, lat)|
|ΔV|-2.64 dB|duration_correction(v=293.9 kn, ref=160 kn)|
|**Lmax**|**47.33 dB**|base_Lmax + ΔI − Λ + Δ|
|**SEL**|**62.69 dB**|base_SEL + ΔV + ΔI − Λ + Δ|
> HiTemp-Flat-Rating zieht (Min aus low/hi B-1)

### SWR533X (4b1815) — A320-250N
| Schritt | Wert | Quelle |
|---|---|---|
|Flugzeugzuordnung|Registry → A320-250N|data/aircraft_registry.json|
|Flugzeugdaten|Airbus A320-250N / LEAP-1A20, 2 TW, Wing, NPD-ID A320-250N, Max-Schub 27120 lb|data/anp.sqlite · Tabelle aircraft|
|State|ts=1792412832 E=2659181 N=1244144 alt=4259.6 m v=334.1 kn trk=242° vr=+21.46 m/s on_ground=False|OpenSky-State (own_states/own_history)|
|Höhe MSL|4259.6 m = 13975 ft|alt_m × 3.28084|
|Höhe AFE|12558 ft|alt_msl_ft − ARP(432.0 m) × 3.28084|
|Phase|D / MaxClimb|pick_phase(vr=+21.46 m/s, alt_afe=12558 ft, cutback=None)|
|B-1 Koeffizienten|e=24570 f=-34.93 ga=0.4774 gb=-6.964e-06 h=0 + HiTemp e=26420 f=-27.4 ga=0 gb=0 h=-143|data/anp.sqlite · Tabelle jet_engine_coefficients (A320-250N, MaxClimb)|
|VC (CAS)|217.4 kt (TAS 334.1 kn)|calibrated_airspeed_kt|
|T (ISA)|-12.7 °C|15 − 0.0019812 × 13975 ft|
|CNT|22278 lbf|corrected_net_thrust(low[, hi], VC, alt_msl_ft, T)|
|NPD-Tabelle|A320-250N D wing 27120 lb · 5 Leistungsstufen · ref 160 kn|EASA-ANP v9 (data/anp.sqlite) · Tabelle npd_data|
|Slant-Distanz|4451.2 m|slant_m(E, N, alt−ARP, Empfänger)|
|Elevation|57.4°|asin((alt−ARP−h)/slant)|
|Lateral-Offset|1122 m|lateral_offset_m(…)|
|base Lmax|43.24 dB|interp_npd(LAmax, CNT, slant)|
|base SEL|61.70 dB|interp_npd(SEL, CNT, slant)|
|ΔI|-0.55 dB|installation_correction(elev, mount=wing)|
|Λ|0.00 dB|lateral_attenuation(elev, lat)|
|ΔV|-3.20 dB|duration_correction(v=334.1 kn, ref=160 kn)|
|**Lmax**|**42.69 dB**|base_Lmax + ΔI − Λ + Δ|
|**SEL**|**57.95 dB**|base_SEL + ΔV + ΔI − Λ + Δ|
> Schätzung: über 10 000 ft AFE — D/MaxClimb ohne NPD-Prozedur
> HiTemp-Flat-Rating zieht (Min aus low/hi B-1)

### EZY3836 (406017) — A320-211
| Schritt | Wert | Quelle |
|---|---|---|
|Flugzeugzuordnung|Ersatz A320 → A320-211 (Δ +0.2 dB)|data/anp.sqlite · Tabelle substitutions|
|Flugzeugdaten|Airbus A320-211 / CFM56-5A1, 2 TW, Wing, NPD-ID CFM565, Max-Schub 25000 lb|data/anp.sqlite · Tabelle aircraft|
|State|ts=1792412051 E=2668850 N=1241903 alt=9502.1 m v=434.3 kn trk=139° vr=+0.00 m/s on_ground=False|OpenSky-State (own_states/own_history)|
|Höhe MSL|9502.1 m = 31175 ft|alt_m × 3.28084|
|Höhe AFE|29758 ft|alt_msl_ft − ARP(432.0 m) × 3.28084|
|Phase|D / MaxClimb|pick_phase(vr=+0.00 m/s, alt_afe=29758 ft, cutback=None)|
|B-1 Koeffizienten|e=16859.1 f=-4.3786 ga=0.183576 gb=2.99e-06 h=0 + HiTemp e=19148.5 f=-6.50173 ga=0 gb=0 h=-95|data/anp.sqlite · Tabelle jet_engine_coefficients (A320-211, MaxClimb)|
|VC (CAS)|155.6 kt (TAS 434.3 kn)|calibrated_airspeed_kt|
|T (ISA)|-46.8 °C|15 − 0.0019812 × 31175 ft|
|CNT|22580 lbf|corrected_net_thrust(low[, hi], VC, alt_msl_ft, T)|
|NPD-Tabelle|CFM565 D wing 25000 lb · 4 Leistungsstufen · ref 160 kn|EASA-ANP v9 (data/anp.sqlite) · Tabelle npd_data|
|Slant-Distanz|15217.5 m|slant_m(E, N, alt−ARP, Empfänger)|
|Elevation|36.2°|asin((alt−ARP−h)/slant)|
|Lateral-Offset|7571 m|lateral_offset_m(…)|
|base Lmax|43.30 dB|interp_npd(LAmax, CNT, slant)|
|base SEL|64.30 dB|interp_npd(SEL, CNT, slant)|
|ΔI|-0.79 dB|installation_correction(elev, mount=wing)|
|Λ|0.36 dB|lateral_attenuation(elev, lat)|
|ΔV|-4.34 dB|duration_correction(v=434.3 kn, ref=160 kn)|
|Δ (Ersatz)|+0.20 dB|data/anp.sqlite · Tabelle substitutions|
|**Lmax**|**42.35 dB**|base_Lmax + ΔI − Λ + Δ|
|**SEL**|**59.01 dB**|base_SEL + ΔV + ΔI − Λ + Δ|
> Schätzung: über 10 000 ft AFE — D/MaxClimb ohne NPD-Prozedur
> HiTemp-Flat-Rating zieht (Min aus low/hi B-1)

### EDW115 (4b161e) — A320-211
| Schritt | Wert | Quelle |
|---|---|---|
|Flugzeugzuordnung|Ersatz A320 → A320-211 (Δ +0.2 dB)|data/anp.sqlite · Tabelle substitutions|
|Flugzeugdaten|Airbus A320-211 / CFM56-5A1, 2 TW, Wing, NPD-ID CFM565, Max-Schub 25000 lb|data/anp.sqlite · Tabelle aircraft|
|State|ts=1792413071 E=2662185 N=1244520 alt=4114.8 m v=275.0 kn trk=333° vr=-9.75 m/s on_ground=False|OpenSky-State (own_states/own_history)|
|Höhe MSL|4114.8 m = 13500 ft|alt_m × 3.28084|
|Höhe AFE|12083 ft|alt_msl_ft − ARP(432.0 m) × 3.28084|
|Phase|D / MaxClimb|pick_phase(vr=-9.75 m/s, alt_afe=12083 ft, cutback=None)|
|B-1 Koeffizienten|e=16859.1 f=-4.3786 ga=0.183576 gb=2.99e-06 h=0 + HiTemp e=19148.5 f=-6.50173 ga=0 gb=0 h=-95|data/anp.sqlite · Tabelle jet_engine_coefficients (A320-211, MaxClimb)|
|VC (CAS)|181.7 kt (TAS 275.0 kn)|calibrated_airspeed_kt|
|T (ISA)|-11.7 °C|15 − 0.0019812 × 13500 ft|
|CNT|19083 lbf|corrected_net_thrust(low[, hi], VC, alt_msl_ft, T)|
|NPD-Tabelle|CFM565 D wing 25000 lb · 4 Leistungsstufen · ref 160 kn|EASA-ANP v9 (data/anp.sqlite) · Tabelle npd_data|
|Slant-Distanz|6505.6 m|slant_m(E, N, alt−ARP, Empfänger)|
|Elevation|33.6°|asin((alt−ARP−h)/slant)|
|Lateral-Offset|4997 m|lateral_offset_m(…)|
|base Lmax|42.88 dB|interp_npd(LAmax, CNT, slant)|
|base SEL|63.31 dB|interp_npd(SEL, CNT, slant)|
|ΔI|-0.79 dB|installation_correction(elev, mount=wing)|
|Λ|0.45 dB|lateral_attenuation(elev, lat)|
|ΔV|-2.35 dB|duration_correction(v=275.0 kn, ref=160 kn)|
|Δ (Ersatz)|+0.20 dB|data/anp.sqlite · Tabelle substitutions|
|**Lmax**|**41.84 dB**|base_Lmax + ΔI − Λ + Δ|
|**SEL**|**59.92 dB**|base_SEL + ΔV + ΔI − Λ + Δ|
> Schätzung: über 10 000 ft AFE — D/MaxClimb ohne NPD-Prozedur
> HiTemp-Flat-Rating zieht (Min aus low/hi B-1)

### EZS27BL (4b1a67) — A320-211
| Schritt | Wert | Quelle |
|---|---|---|
|Flugzeugzuordnung|Ersatz A320 → A320-211 (Δ +0.2 dB)|data/anp.sqlite · Tabelle substitutions|
|Flugzeugdaten|Airbus A320-211 / CFM56-5A1, 2 TW, Wing, NPD-ID CFM565, Max-Schub 25000 lb|data/anp.sqlite · Tabelle aircraft|
|State|ts=1792411512 E=2667585 N=1242778 alt=7513.3 m v=391.9 kn trk=136° vr=+12.03 m/s on_ground=False|OpenSky-State (own_states/own_history)|
|Höhe MSL|7513.3 m = 24650 ft|alt_m × 3.28084|
|Höhe AFE|23233 ft|alt_msl_ft − ARP(432.0 m) × 3.28084|
|Phase|D / MaxClimb|pick_phase(vr=+12.03 m/s, alt_afe=23233 ft, cutback=None)|
|B-1 Koeffizienten|e=16859.1 f=-4.3786 ga=0.183576 gb=2.99e-06 h=0 + HiTemp e=19148.5 f=-6.50173 ga=0 gb=0 h=-95|data/anp.sqlite · Tabelle jet_engine_coefficients (A320-211, MaxClimb)|
|VC (CAS)|177.8 kt (TAS 391.9 kn)|calibrated_airspeed_kt|
|T (ISA)|-33.8 °C|15 − 0.0019812 × 24650 ft|
|CNT|21207 lbf|corrected_net_thrust(low[, hi], VC, alt_msl_ft, T)|
|NPD-Tabelle|CFM565 D wing 25000 lb · 4 Leistungsstufen · ref 160 kn|EASA-ANP v9 (data/anp.sqlite) · Tabelle npd_data|
|Slant-Distanz|12948.2 m|slant_m(E, N, alt−ARP, Empfänger)|
|Elevation|32.7°|asin((alt−ARP−h)/slant)|
|Lateral-Offset|6882 m|lateral_offset_m(…)|
|base Lmax|42.08 dB|interp_npd(LAmax, CNT, slant)|
|base SEL|63.08 dB|interp_npd(SEL, CNT, slant)|
|ΔI|-0.79 dB|installation_correction(elev, mount=wing)|
|Λ|0.48 dB|lateral_attenuation(elev, lat)|
|ΔV|-3.89 dB|duration_correction(v=391.9 kn, ref=160 kn)|
|Δ (Ersatz)|+0.20 dB|data/anp.sqlite · Tabelle substitutions|
|**Lmax**|**41.01 dB**|base_Lmax + ΔI − Λ + Δ|
|**SEL**|**58.12 dB**|base_SEL + ΔV + ΔI − Λ + Δ|
> Schätzung: über 10 000 ft AFE — D/MaxClimb ohne NPD-Prozedur
> HiTemp-Flat-Rating zieht (Min aus low/hi B-1)

### SWR1LE (4b18fe) — A340-211
| Schritt | Wert | Quelle |
|---|---|---|
|Flugzeugzuordnung|Ersatz A343 → A340-211 (Δ +1.3 dB)|data/anp.sqlite · Tabelle substitutions|
|Flugzeugdaten|Airbus A340-211 / CFM56-5C2, 4 TW, Wing, NPD-ID CF565C, Max-Schub 31200 lb|data/anp.sqlite · Tabelle aircraft|
|State|ts=1792411392 E=2649783 N=1245615 alt=3451.9 m v=323.5 kn trk=260° vr=+3.90 m/s on_ground=False|OpenSky-State (own_states/own_history)|
|Höhe MSL|3451.9 m = 11325 ft|alt_m × 3.28084|
|Höhe AFE|9908 ft|alt_msl_ft − ARP(432.0 m) × 3.28084|
|Phase|D / MaxClimb|pick_phase(vr=+3.90 m/s, alt_afe=9908 ft, cutback=1500.0)|
|B-1 Koeffizienten|e=26802.9 f=-28.82639 ga=0.31673 gb=3.5e-06 h=0 + HiTemp e=31091.8 f=-31.44921 ga=0 gb=0 h=-160|data/anp.sqlite · Tabelle jet_engine_coefficients (A340-211, MaxClimb)|
|VC (CAS)|229.1 kt (TAS 323.5 kn)|calibrated_airspeed_kt|
|T (ISA)|-7.4 °C|15 − 0.0019812 × 11325 ft|
|CNT|24234 lbf|corrected_net_thrust(low[, hi], VC, alt_msl_ft, T)|
|NPD-Tabelle|CF565C D wing 31200 lb · 3 Leistungsstufen · ref 160 kn|EASA-ANP v9 (data/anp.sqlite) · Tabelle npd_data|
|Slant-Distanz|7730.4 m|slant_m(E, N, alt−ARP, Empfänger)|
|Elevation|22.4°|asin((alt−ARP−h)/slant)|
|Lateral-Offset|2609 m|lateral_offset_m(…)|
|base Lmax|39.24 dB|interp_npd(LAmax, CNT, slant)|
|base SEL|61.64 dB|interp_npd(SEL, CNT, slant)|
|ΔI|-0.78 dB|installation_correction(elev, mount=wing)|
|Λ|1.03 dB|lateral_attenuation(elev, lat)|
|ΔV|-3.06 dB|duration_correction(v=323.5 kn, ref=160 kn)|
|Δ (Ersatz)|+1.30 dB|data/anp.sqlite · Tabelle substitutions|
|**Lmax**|**38.72 dB**|base_Lmax + ΔI − Λ + Δ|
|**SEL**|**58.07 dB**|base_SEL + ΔV + ΔI − Λ + Δ|
> HiTemp-Flat-Rating zieht (Min aus low/hi B-1)

### EZS29ZA (4b027f) — A320-250N
| Schritt | Wert | Quelle |
|---|---|---|
|Flugzeugzuordnung|Registry → A320-250N|data/aircraft_registry.json|
|Flugzeugdaten|Airbus A320-250N / LEAP-1A20, 2 TW, Wing, NPD-ID A320-250N, Max-Schub 27120 lb|data/anp.sqlite · Tabelle aircraft|
|State|ts=1792411812 E=2662514 N=1244846 alt=8503.9 m v=391.7 kn trk=135° vr=+6.83 m/s on_ground=False|OpenSky-State (own_states/own_history)|
|Höhe MSL|8503.9 m = 27900 ft|alt_m × 3.28084|
|Höhe AFE|26483 ft|alt_msl_ft − ARP(432.0 m) × 3.28084|
|Phase|D / MaxClimb|pick_phase(vr=+6.83 m/s, alt_afe=26483 ft, cutback=None)|
|B-1 Koeffizienten|e=24570 f=-34.93 ga=0.4774 gb=-6.964e-06 h=0 + HiTemp e=26420 f=-27.4 ga=0 gb=0 h=-143|data/anp.sqlite · Tabelle jet_engine_coefficients (A320-250N, MaxClimb)|
|VC (CAS)|158.3 kt (TAS 391.7 kn)|calibrated_airspeed_kt|
|T (ISA)|-40.3 °C|15 − 0.0019812 × 27900 ft|
|CNT|26941 lbf|corrected_net_thrust(low[, hi], VC, alt_msl_ft, T)|
|NPD-Tabelle|A320-250N D wing 27120 lb · 5 Leistungsstufen · ref 160 kn|EASA-ANP v9 (data/anp.sqlite) · Tabelle npd_data|
|Slant-Distanz|9860.7 m|slant_m(E, N, alt−ARP, Empfänger)|
|Elevation|54.2°|asin((alt−ARP−h)/slant)|
|Lateral-Offset|4530 m|lateral_offset_m(…)|
|base Lmax|37.47 dB|interp_npd(LAmax, CNT, slant)|
|base SEL|58.36 dB|interp_npd(SEL, CNT, slant)|
|ΔI|-0.62 dB|installation_correction(elev, mount=wing)|
|Λ|0.00 dB|lateral_attenuation(elev, lat)|
|ΔV|-3.89 dB|duration_correction(v=391.7 kn, ref=160 kn)|
|**Lmax**|**36.86 dB**|base_Lmax + ΔI − Λ + Δ|
|**SEL**|**53.85 dB**|base_SEL + ΔV + ΔI − Λ + Δ|
> Schätzung: über 10 000 ft AFE — D/MaxClimb ohne NPD-Prozedur
> HiTemp-Flat-Rating zieht (Min aus low/hi B-1)

### BAW733 (408227) — A321-270N
| Schritt | Wert | Quelle |
|---|---|---|
|Flugzeugzuordnung|Registry → A321-270N|data/aircraft_registry.json|
|Flugzeugdaten|Airbus A321-270N / PW1130G-JM, 2 TW, Wing, NPD-ID A321-270N, Max-Schub 33110 lb|data/anp.sqlite · Tabelle aircraft|
|State|ts=1792411212 E=2648561 N=1245371 alt=4236.7 m v=355.1 kn trk=260° vr=+6.83 m/s on_ground=False|OpenSky-State (own_states/own_history)|
|Höhe MSL|4236.7 m = 13900 ft|alt_m × 3.28084|
|Höhe AFE|12483 ft|alt_msl_ft − ARP(432.0 m) × 3.28084|
|Phase|D / MaxClimb|pick_phase(vr=+6.83 m/s, alt_afe=12483 ft, cutback=None)|
|B-1 Koeffizienten|e=28591.3 f=-35.34956 ga=0.260241 gb=1.98e-07 h=0 + HiTemp e=29810.2 f=-30.92756 ga=0 gb=0 h=-122|data/anp.sqlite · Tabelle jet_engine_coefficients (A321-270N, MaxClimb)|
|VC (CAS)|231.6 kt (TAS 355.1 kn)|calibrated_airspeed_kt|
|T (ISA)|-12.5 °C|15 − 0.0019812 × 13900 ft|
|CNT|24061 lbf|corrected_net_thrust(low[, hi], VC, alt_msl_ft, T)|
|NPD-Tabelle|A321-270N D wing 33110 lb · 5 Leistungsstufen · ref 160 kn|EASA-ANP v9 (data/anp.sqlite) · Tabelle npd_data|
|Slant-Distanz|9106.8 m|slant_m(E, N, alt−ARP, Empfänger)|
|Elevation|24.2°|asin((alt−ARP−h)/slant)|
|Lateral-Offset|2589 m|lateral_offset_m(…)|
|base Lmax|37.05 dB|interp_npd(LAmax, CNT, slant)|
|base SEL|57.82 dB|interp_npd(SEL, CNT, slant)|
|ΔI|-0.78 dB|installation_correction(elev, mount=wing)|
|Λ|0.90 dB|lateral_attenuation(elev, lat)|
|ΔV|-3.46 dB|duration_correction(v=355.1 kn, ref=160 kn)|
|**Lmax**|**35.38 dB**|base_Lmax + ΔI − Λ + Δ|
|**SEL**|**52.68 dB**|base_SEL + ΔV + ΔI − Λ + Δ|
> Schätzung: über 10 000 ft AFE — D/MaxClimb ohne NPD-Prozedur
> HiTemp-Flat-Rating zieht (Min aus low/hi B-1)

### IBE06HE (346186) — A320-250N
| Schritt | Wert | Quelle |
|---|---|---|
|Flugzeugzuordnung|Registry → A320-250N|data/aircraft_registry.json|
|Flugzeugdaten|Airbus A320-250N / LEAP-1A20, 2 TW, Wing, NPD-ID A320-250N, Max-Schub 27120 lb|data/anp.sqlite · Tabelle aircraft|
|State|ts=1792410072 E=2646078 N=1246919 alt=4831.1 m v=330.3 kn trk=330° vr=-5.85 m/s on_ground=False|OpenSky-State (own_states/own_history)|
|Höhe MSL|4831.1 m = 15850 ft|alt_m × 3.28084|
|Höhe AFE|14433 ft|alt_msl_ft − ARP(432.0 m) × 3.28084|
|Phase|D / MaxClimb|pick_phase(vr=-5.85 m/s, alt_afe=14433 ft, cutback=None)|
|B-1 Koeffizienten|e=24570 f=-34.93 ga=0.4774 gb=-6.964e-06 h=0 + HiTemp e=26420 f=-27.4 ga=0 gb=0 h=-143|data/anp.sqlite · Tabelle jet_engine_coefficients (A320-250N, MaxClimb)|
|VC (CAS)|202.1 kt (TAS 330.3 kn)|calibrated_airspeed_kt|
|T (ISA)|-16.4 °C|15 − 0.0019812 × 15850 ft|
|CNT|23227 lbf|corrected_net_thrust(low[, hi], VC, alt_msl_ft, T)|
|NPD-Tabelle|A320-250N D wing 27120 lb · 5 Leistungsstufen · ref 160 kn|EASA-ANP v9 (data/anp.sqlite) · Tabelle npd_data|
|Slant-Distanz|11868.4 m|slant_m(E, N, alt−ARP, Empfänger)|
|Elevation|21.3°|asin((alt−ARP−h)/slant)|
|Lateral-Offset|7836 m|lateral_offset_m(…)|
|base Lmax|34.36 dB|interp_npd(LAmax, CNT, slant)|
|base SEL|55.04 dB|interp_npd(SEL, CNT, slant)|
|ΔI|-0.79 dB|installation_correction(elev, mount=wing)|
|Λ|1.12 dB|lateral_attenuation(elev, lat)|
|ΔV|-3.15 dB|duration_correction(v=330.3 kn, ref=160 kn)|
|**Lmax**|**32.46 dB**|base_Lmax + ΔI − Λ + Δ|
|**SEL**|**49.99 dB**|base_SEL + ΔV + ΔI − Λ + Δ|
> Schätzung: über 10 000 ft AFE — D/MaxClimb ohne NPD-Prozedur
> HiTemp-Flat-Rating zieht (Min aus low/hi B-1)

## Ersetzt
- SWR1LE (4b18fe): A343 → A340-211 (Δdep +1.3 dB, Δapp +0.1 dB)
- EZS27BL (4b1a67): A320 → A320-211 (Δdep +0.2 dB, Δapp +0.0 dB)
- EZY3836 (406017): A320 → A320-211 (Δdep +0.2 dB, Δapp +0.0 dB)
- EDW115 (4b161e): A320 → A320-211 (Δdep +0.2 dB, Δapp +0.0 dB)

## Unbekannt
- AFR95LC (39bb22)
- TVF4409 (39ceb2)

## Übersprungen
—

## Ergebnis
L_jetzt = 62.7 dB aus 16 Flugzeugen
> informativ, nicht rechtsgültig (Ist-Verkehr, keine Anhang-5-Korrektur)

## Methodik & Näherungen
- Kette: OpenSky-State → Registry/Ersatztabelle → aircraft/engine → B-1/B-23 CNT → NPD-Interpolation → ΔI/Λ/ΔV → Lmax/SEL
- Näherungen: ISA-Temperatur, Ground Speed ≡ TAS, kein Wind, SEL als unendlicher Pfad ohne ΔF, keine atmosphärische Re-Normierung (ECAC Doc 29 App. D)
- Über 10 000 ft AFE: Schätzung D/MaxClimb (Prozedurabdeckung endet dort)
- Quellen: ECAC Doc 29, 5. Aufl., Vol. 2 · EASA-ANP v9 (data/anp.sqlite) · OpenSky-States · data/aircraft_registry.json

## Glossar
| Begriff | Erklärung |
|---|---|
| Lmax | Maximalpegel des Überflugs in dB(A) |
| SEL | Sound Exposure Level in dB(A): auf 1 s normierte Schallenergie des Ereignisses |
| L_jetzt | energetische Summe aller Lmax: 10·log10(Σ 10^(Lmax/10)) |
| CNT | korrigierter Nettoschub (corrected net thrust) in lbf, aus B-1/B-23-Koeffizienten |
| B-1 | Doc-29-Triebwerksmodell: Schub als Funktion von CAS, Druckhöhe und Temperatur |
| HiTemp-Flat-Rating | Min(low, hi)-Schub bei hohen Temperaturen (hi-Koeffizienten aktiv) |
| NPD | Noise-Power-Distance: Tabellen LAmax/SEL über Schub und Slant-Distanz |
| base Lmax / base SEL | NPD-Interpolationswerte vor Korrekturen: interp_npd(CNT, slant) |
| ΔI | Installationskorrektur: 10·log10([(a·cos²φ + sin²φ)^b] · [c·sin²(2φ) + cos²(2φ)]), φ = Elevation, a/b/c je Triebwerksanbau |
| Λ | laterale Dämpfung: Λ = Γ(ℓ)·Λ(β), Γ(ℓ) = 1.089·(1 − e^(−0.00274·ℓ)) für ℓ ≤ 914 m sonst 1, Λ(β) = 1.137 − 0.0229·β + 9.72·e^(−0.142·β) für 0 ≤ β ≤ 50° (β < 0: 10.857, β > 50°: 0) |
| ΔV | Dauerkorrektur: 10·log10(Vref / V), V = Ground Speed, Vref = NPD-Referenzgeschwindigkeit |
| Δ (Ersatz) | EASA-Ersatzzuschlag bei Proxy-Typen: Δdep (Departure) bzw. Δapp (Approach) |
| Lmax-Formel | Lmax = base_Lmax + ΔI − Λ + Δ |
| SEL-Formel | SEL = base_SEL + ΔV + ΔI − Λ + Δ |
| op_mode | NPD-Betriebsart: D (Departure) oder A (Approach) |
| Rating | Schubrate: MaxTakeoff / MaxClimb / MaxClimbHiTemp / IdleApproach |
| Phase | departure (op_mode D) oder approach (op_mode A) |
| AFE | Höhe über Flughafen-Grund: alt_msl_ft − ARP(432.0 m) × 3.28084 |
| Slant | Schrägdistanz Empfänger–Flugzeug in m |
| Elevation | Höhenwinkel Empfänger→Flugzeug: asin((alt−ARP−h)/slant) |
| Lateral-Offset |Querabstand zur Bodenspur in m: lateral_offset_m(…) |
| VC (CAS) | kalibrierte Fluggeschwindigkeit in kt aus TAS und Flughöhe |
| T (ISA) | Standardatmosphärentemperatur: 15 − 0.0019812 × alt_msl_ft (°C) |
| ICAO24 | 24-Bit-Transponderadresse des Flugzeugs (Hex) |
| cutback | Cutback-Höhe in ft: Umschaltpunkt MaxTakeoff → MaxClimb (None bei Schätzung) |
| Estimate/Schätzung | Über 10 000 ft AFE: D/MaxClimb ohne NPD-Prozedur, Betrag konservativ-hoch |
| TS | Sample-Zeitpunkt (Unix); Fenster min/max = ältester/neuester Sample |
