# HOW-TO: Fluglärm-Rechner

Two strictly separated modules (see `README.md`):

1. **Engine** (`fluglaerm/engine/`): legally-oriented assessment per LSV Anhang 5 /
   ECAC Doc 29 from **approved** operations. Output: rating levels Lrt/Lrn,
   limit comparison, AGL status, Auflagen, Nachweis document.
2. **Ist module** (`fluglaerm/ist_laerm/`, informative only): estimates SEL/Leq from
   real ADS-B tracks (OpenSky Network). **No legal effect.**

The binding result for authorities remains FLULA2 (Empa) via an acoustic office.

## 1. Setup

```sh
cd ~/Work/flightnoise
python3.11 -m venv .venv
.venv/bin/pip install -e ".[dev]"   # runtime + pytest
```

(`.venv` uses absolute paths — rebuild it after moving the project directory.)

Check the install:

```sh
.venv/bin/fluglaerm --help
.venv/bin/pytest -q
```

IMPORTANT: run every command below from the project root (`~/Work/flightnoise`).
The NPD loader resolves `data/anp` relative to the current directory, so
`engine`/`parcel` fail with `Keine NPD-Tabelle ...` when invoked elsewhere —
even with an absolute `--dataset` path.

## 2. Quick start

Minimal engine run for one receiver (LV95 coordinates, sensitivity level, land use):

```sh
cd ~/Work/flightnoise
.venv/bin/fluglaerm engine --east 2684000 --north 1256000 --es 2 --nutzung wohnen
# Lrt=60.1 dB [IGW überschritten]
# Lrn[nacht1]=56.7 dB [IGW überschritten]
# Lrn[nacht2]=46.8 dB [eingehalten]
# Lrk=12.2 Lrg=60.1 AGL=innerhalb
```

Receiver on a hill / upper floor (height above airport ground, s. §4a2):

```sh
.venv/bin/fluglaerm engine --east 2684000 --north 1256000 --es 2 --nutzung wohnen --height 50
.venv/bin/fluglaerm ist --east 2684000 --north 1256000 --height 50 \
  --from 2026-10-01T00:00 --to 2026-10-01T00:15

Full Nachweis report (writes `nachweis.md` + `result.json` into the **current directory**):

```sh
.venv/bin/fluglaerm parcel --east 2684000 --north 1256000 --es 2 --nutzung wohnen
```

With parcel identifier (EGRID resolved from the local GWR sqlite, s. §4e —
no `--east`/`--north`/`--height` needed):

```sh
.venv/bin/fluglaerm parcel --egrid CH330877058702 --es 2 --nutzung wohnen
# resolves E 2686073 / N 1256366 + terrain offset 12.5 m automatically.
# Unknown EGRID or missing DB fails loudly (exit 1); then pass real LV95 E/N.
```

Informative actual-traffic check (live OpenSky snapshot, no account needed):

```sh
.venv/bin/fluglaerm ist --east 2684000 --north 1256000 \
  --from 2026-10-01T00:00 --to 2026-10-01T00:15
```

## 3. Commands

| Command | Purpose | Output |
|---|---|---|
| `fluglaerm engine` | Rating levels for approved operations at one receiver | stdout: `Lrt`, `Lrn[nacht1]`, `Lrn[nacht2]`, `Lrk`, `Lrg`, `AGL` |
| `fluglaerm parcel` | Full Nachweis: engine (+ optional Ist comparison) | stdout + `nachweis.md` + `result.json` in CWD |
| `fluglaerm ist` | Actual traffic Leq from OpenSky ADS-B | stdout: `Leq_ist`, flight count |

Options:

- `engine`: `--east FLOAT` (LV95 E, EPSG:2056), `--north FLOAT` (LV95 N),
  `--es 1|2|3|4`, `--nutzung wohnen|betrieb`, `--height FLOAT` (default 0,
  Empfängerhöhe über Flughafen-Grund in m, s. §4a), `--dataset PATH`
  (default `data/seed/zrh_vbr2012.json`). `--egrid`/`--ist` are accepted but
  currently only honoured by `parcel` — use `parcel` for those.
- `parcel`: either `--egrid TEXT` **or** `--east` + `--north` (one of the two
  is required; `--east`/`--north` are `default=None`). EGRID path auto-adds
  the terrain offset parcel−airport from the geo.admin.ch height service onto
  `--height` (**fatal**: lookup failure aborts the run, exit 1); manual
  `--east`/`--north` does no lookup — `--height` is then the height above
  airport ground verbatim. Plus `--ist/--no-ist` (adds the live-traffic
  comparison to the report).
- `ist`: `--east`, `--north`, `--height FLOAT` (default 0, same semantics),
  `--from ISO`, `--to ISO`
  (window length is `max(to-from, 900 s)`), `--username`/`--password`
  (only needed for OpenSky history; live snapshot works anonymously).

## 4. Data required

### a) Receiver (parcel under assessment) — always required

- LV95 East/North (EPSG:2056, in metres, e.g. `E 2684000 / N 1256000`) —
  required unless `--egrid` is given (`parcel` needs EITHER `--egrid` OR
  `--east` + `--north`; otherwise `UsageError`, exit 2), **or**
  EGRID (`parcel` only; resolved from the local GWR sqlite, s. §4e).
- `es`: Empfindlichkeitsstufe 1–4 (sensitivity level of the zone).
- `nutzung`: `wohnen` (residential) or `betrieb` (commercial/industrial).
  ES + Nutzung jointly determine limits (IGW/AW per LSV Anhang 5) and Auflagen.

### a2) Receiver height — optional, default 0

`--height FLOAT`: receiver height **above the airport ground plane** (the same
reference as segment `alt_m`: ground roll 0, liftoff ~400 m) — i.e. terrain
offset vs. ARP **plus** mic/floor height. Default 0 reproduces prior results
exactly. Effect is small: ~5 m (balcony) ≈ 0.02–0.05 dB, ~50 m (hillside)
≈ 0.2–0.5 dB. Above-aircraft receivers are clamped to horizontal distance
(conservative).

`parcel --egrid` auto-fetches the terrain offset: `resolve_height(parcel) −
resolve_height(airport)` via `https://api3.geo.admin.ch/rest/services/height`
(`?easting=…&northing=…&sr=2056` → `{"height":"422.1"}`) and adds it onto
`--height`. **Fatal**: on lookup failure the run aborts (exit 1) instead of
silently using `--height` unchanged. Manual `--east/--north` does no lookup —
`--height` is then the height above airport ground verbatim. The report shows
`Empfängerhöhe (über Flughafen-Grund): X.X m`; `result.json` carries
`"receiver": {..., "height_m": X.X}`.

### b) Movement dataset (approved operations) — required by engine/parcel

JSON file, default `data/seed/zrh_vbr2012.json`. Schema
(`fluglaerm/common/types.py`, loader `load_dataset` in `fluglaerm/cli.py`):

```json
{
  "airport_icao": "LSZH",
  "airport_east": 2684000.0,
  "airport_north": 1256000.0,
  "periods": [{"id": "tag", "start_hour": 6, "end_hour": 22}],
  "routes": [{"id": "DEP-16", "kind": "departure", "runway": "16",
              "share": 0.25,
              "segments": [{"east": 2684500.0, "north": 1255000.0,
                            "alt_m": 400.0, "thrust": null}]}],
  "movements": [{"route_id": "DEP-16", "aircraft_anp": "A320-214",
                 "period": "tag", "count": 20000, "weight_class": "gross"}]
}
```

Field notes:

- `routes[].kind`: `departure` | `arrival` (selects thrust/speed defaults).
- `segments[]`: ground track with altitude profile; `thrust: null` = phase default
  (departure 0.85/200 kn, arrival 0.35/160 kn). Segments with both ends
  `alt_m <= 0` are skipped (pure ground roll, SOR directivity out of scope).
- `movements[].count`: **annual** movements on that route (engine divides by
  T×365: day 16 h, night hours 1 h each; Kleinflugzeuge day window 14 h, 06–20).
- `weight_class`: `gross` (> 8'618 kg) | `klein` (≤ 8'618 kg, day only,
  enters via `Lrk`).
- `period`: `tag` | `nacht1` (22–23) | `nacht2` (23–24) | `letzte_nacht`
  (05–06, ZRH closed → no value).
- `source: "nominal_placeholder"` flags the seed's nominal routes; the report
  then carries the disclaimer *"Methode demonstriert, nicht rechtsgültig —
  genehmigter Routendatensatz fehlt"*.

Real legal use replaces the seed with the **approved** operations: routes
digitised from SIL/Betriebsreglement and authoritative movement counts
(rebuild via `data/seed/build_seed.py` as template). The seed's nominal straight
tracks and its vBR-2012 aggregates are smoke-test data, not a legal Nachweis.

### c) NPD tables (aircraft noise-power-distance) — required, placeholders bundled

One JSON per aircraft at `data/anp/<ANP-ID>.json`, e.g. `A320-214.json`:

```json
{"aircraft": "A320-214", "source": "EASA-ANP v2.1", "engine_mount": "wing",
 "max_thrust_lbf": 27000, "ref_speed_kn": 160,
 "powers_lbf": [...], "distances_m": [...],
 "le": [[...]], "lmax": [[...]]}
```

- Shipped files have `"source": "SYNTHETIC_PLACEHOLDER"` — calibrated order of
  magnitude for method demonstration, **not** real ANP data.
- Real tables: request EASA access via the web form
  (<https://www.easa.europa.eu/en/anp-data-request>), then store the tables in
  the schema above; `source` becomes `EASA-ANP`. Helper/explainer:
  `data/fetch_anp.py`, `data/anp/make_placeholders.py`.
- `data/anp/*.json` is git-ignored (EASA T&C §6g: no modification, publication,
  redistribution). Only tool outputs (dB values, Nachweis) may be shared —
  never raw NPD tables.

Every `aircraft_anp` referenced by the dataset needs a matching table file;

### d) Ist module only (optional, informative)

- Network access to `https://opensky-network.org/api` (anonymous live snapshot
  is rate-limited; history queries need a free research account).
- Receiver E/N as above. No dataset or NPD tables needed
  (empirical SEL estimate from ADS-B tracks).

### e) GWR sqlite (EGRID lookup) — required only for `parcel --egrid`

One-time download (1.7 GB, git-ignored via `data/*.sqlite`, never committed):

```sh
curl -C - -o data/ch.sqlite https://public.madd.bfs.admin.ch/data_ch.sqlite
```

`resolve_egrid` (`fluglaerm/common/geo.py`) normalises the EGRID (spaces
removed, uppercased, missing `CH` prefix added) and returns the LV95
coordinate (`GKODE`/`GKODN`) of the lowest-`EGID` building on the parcel.
No index on `EGRID` — one full scan (~2 s) per run. Unknown EGRID or missing
DB fails loudly (`ClickException`, exit 1); an empty lot or GWR gap then
falls back to manual `--east`/`--north`. Same CWD rule as §1: run from the
project root, `data/ch.sqlite` resolves relative to CWD.

## 5. Interpreting output

- `Lrt`: day rating level; `Lrn[nacht1/nacht2]`: night-hour rating levels.
- `Lrk`/`Lrg`: Kleinflugzeug / Grossflugzeug partial levels.
- `Status`: `eingehalten` | `IGW überschritten` | `AW` (+ note at `lrt = 66`)
  per ES/Nutzung.
- `AGL`: `innerhalb` iff `Lrt > 60` or `Lrn[nacht1] > 55` (IGW ES II).
- `parcel` additionally lists Auflagen and writes `nachweis.md`/`result.json`
  (overwritten on each run; both git-ignored).

## 6. Limitations (read before relying on results)

- Seed run = method demonstration: nominal routes + placeholder NPD tables.
  The report says so explicitly; it is not a legal Nachweis.
- Ground roll excluded; Klein-T day window is 14 h (06–20).
- `-inf` levels (e.g. silent night hours) are legitimate zeros in the log sum.
