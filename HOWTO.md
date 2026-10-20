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

Daten prüfen und automatisch bereitstellen, was geht:

```sh
.venv/bin/fluglaerm setup --check
```

(`zeigt, was fehlt; ohne --check wird automatisch bereitgestellt, was geht)

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
```

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

Own receiver against the ANP database (needs OpenSky client credentials —
here from `credentials.json`, s. §4f):

```sh
.venv/bin/fluglaerm own --egrid CH330877058702 --credentials credentials.json
# resolves E/N + terrain offset from the local GWR sqlite automatically.
# Unknown EGRID or missing DB fails loudly (exit 1); then pass --east/--north.
```

## 3. Commands

| Command | Purpose | Output |
|---|---|---|
| `fluglaerm engine` | Rating levels for approved operations at one receiver | stdout: `Lrt`, `Lrn[nacht1]`, `Lrn[nacht2]`, `Lrk`, `Lrg`, `AGL` |
| `fluglaerm parcel` | Full Nachweis: engine (+ optional Ist comparison) | stdout + `nachweis.md` + `result.json` in CWD |
| `fluglaerm ist` | Actual traffic Leq from OpenSky ADS-B | stdout: `Leq_ist`, flight count |
| `fluglaerm own` | Instantaneous LAmax/SEL at the receiver from own OpenSky states vs ANP DB | stdout: per-aircraft rows + `L_jetzt` |
| `fluglaerm collect` | Poll the tar1090 feeder and append states to the local SQLite history | stdout: `N States gespeichert`; DB `data/own_states.sqlite` |

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
- `own`: either `--egrid TEXT` **or** `--east` + `--north` (same receiver
  resolution as `parcel`, s. §4a/§4e — including the fatal terrain-offset
  lookup). Plus `--radius FLOAT` (default 15000, search radius around the
  receiver in m), `--serials INT` (repeatable; default: all own receivers),
  `--time INT` (Unix time, default now), `--window INT` (default 0: backfill
  window in seconds; 0 = only the current snapshot), `--interval INT`
  (default 60: backfill sampling step in seconds, minimum 5), `--db PATH`
  (default `data/anp.sqlite`), `--registry PATH`
  (default `data/aircraft_registry.json`), `--client-id`/`--client-secret`
  (or `OPENSKY_CLIENT_ID`/`OPENSKY_CLIENT_SECRET` env; required),
  `--credentials PATH` (JSON mit `clientId`/`clientSecret`, oder
  `client_id`/`client_secret`; fills whatever `--client-id`/`--client-secret`/
  env leave unset), `--debug` (Debug-Log auf stderr),
  `--list-aircraft` (prints the ANP aircraft table and exits),
  `--source opensky|local` (default opensky; local reads the SQLite history
  from `--states-db` — `window=0` loads the last `interval` seconds,
  `--serials` ignored, no credentials needed),
  `--states-db PATH` (default `data/own_states.sqlite`, only with
  `--source local`).
- `setup`: `--check` (report only, changes nothing), `--gwr` (also fetch
  `data/ch.sqlite`, 1.7 GB, `--egrid` only). With the aircraft database
  present, `setup` also builds `data/aircraft_registry.json` automatically.
  It also fetches the EASA ANP Archive v2.3 (`data/anp_archive.sqlite`) and
  the EASA substitution table (`substitutions` in `data/anp.sqlite`) that
  `own` uses for aircraft types the ANP database does not carry (e.g.
- `collect`: `--host TEXT` (required, feeder IP or mDNS name), `--port INT`
  (default 8080), `--db PATH` (default `data/own_states.sqlite`),
  `--interval INT` (default 5, sampling interval in seconds),
  `--duration FLOAT` (total run time in seconds; default: endless until
  Ctrl-C), `--once` (query once, store, exit — for cron/launchd),
  `--debug` (Debug-Log auf stderr). `--once` wins over `--duration`.

## 4. Data required

### a) Receiver (parcel under assessment) — always required

- LV95 East/North (EPSG:2056, in metres, e.g. `E 2684000 / N 1256000`) —
  required unless `--egrid` is given (`parcel`/`own` need EITHER `--egrid` OR
  `--east` + `--north`; otherwise `UsageError`, exit 2), **or**
  EGRID (`parcel`/`own`; resolved from the local GWR sqlite, s. §4e).
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

`parcel --egrid` / `own --egrid` auto-fetch the terrain offset: `resolve_height(parcel) −
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

### f) `own` only: ANP sqlite, registry, credentials

- `data/anp.sqlite` (EASA-ANP v9, git-ignored via `data/*.sqlite`): build with
  `.venv/bin/python data/import_anp.py` from the nine `.xlsx` workbooks in
  `data/easa_anp/`. Missing DB fails loudly (`FileNotFoundError` →
  `ClickException`, exit 1).
- `data/aircraft_registry.json` (generated by `fluglaerm setup`, git-ignored):
  maps lowercase OpenSky `icao24` hex to ANP `acft_id`, e.g.
  `{"3c6444": "A320-250N"}`. States carry no aircraft type, so unmapped icao24
  are reported as `unbekannt:` and excluded — never guessed. `setup` fills it
  from the aircraft database below (~12 k entries, ~0.3 MB), so an `own` run
  needs no manual step. Hexes missing from the database stay `unbekannt:`; add
  them by hand to the file if you know their ANP type.
- Aircraft database (feeds the registry; downloaded by `setup`). Source:
  [wiedehopf/tar1090-db](https://github.com/wiedehopf/tar1090-db), csv branch —
  the Mictronics database that readsb/tar1090 use as well (~8 MB, ~622 k rows,
  snapshot weekly; format `icao24;registration;typecode;flags;description`, no
  header). `fluglaerm setup` fetches it to `data/aircraft.csv.gz` (git-ignored
  like the ANP sqlite). Manual load:

  ```sh
  curl -L -o data/aircraft.csv.gz \
    https://github.com/wiedehopf/tar1090-db/raw/refs/heads/csv/aircraft.csv.gz
  ```

  Only typecodes with exactly one ANP counterpart are mapped (A21N, A332/A333,
  A338/A339, A359, B744, B763, B77W, B789, E190, E195, A20N). The database
  carries no A320neo engine variant: `A20N` defaults to `A320-250N` (LEAP-1A)
  — set the PW row `A320-270N` by hand for affected registrations; your entry
  wins whenever `setup` merges (the file is git-ignored, so keep a note of
  hand edits if you re-clone). Types with no ANP row (A220, B738, …) stay
  `unbekannt:`.
- EASA ANP Archive v2.3 + substitution table (both downloaded by `setup`,
  git-ignored like the other EASA data). The registry maps only typecodes with
  a direct ANP counterpart, so types absent from ANP v9 — A320-ceo, B738,
  A332/A333, E190/E195, B789, B763, B744 … — would otherwise stay `unbekannt:`.
  `own` therefore falls back to the EASA table
  [ANP aircraft substitutions – Jets & heavy props](https://www.easa.europa.eu/en/downloads/138165/en)
  (list dated 22/02/2018): ICAO code → `ANP_PROXY` plus the mandated
  `DELTA_DEP_dB`/`DELTA_APP_dB` (positive = modelled aircraft is louder than
  the proxy), chosen per ICAO Doc 9911 / ECAC Doc 29. The proxies are v2-era
  aircraft, so `setup` also imports the EASA-published
  [ANP Archive v2.3](https://www.easa.europa.eu/en/downloads/138164/en) into
  `data/anp_archive.sqlite`; v9 is always preferred when it carries the type.
  Example: `A320` → `A320-211` with Δdep +0.2 dB / Δapp 0.0 dB; the correction
  is added to each substituted aircraft's LAmax and SEL, and each substitution
  is printed as `ersetzt: CALL (hex): A320 → A320-211 (Δdep +0.2 dB, …)`.
  Manual load:

  ```sh
  .venv/bin/python data/import_anp_archive.py        # nach curl -L -o data/easa_anp/anp_archive_2_3.zip https://www.easa.europa.eu/en/downloads/138164/en
  .venv/bin/python data/import_substitutions.py      # nach curl -L -o "data/easa_anp/anp_aircraft_substitutions_-_jets_heavy_props_22022018_.xlsx" https://www.easa.europa.eu/en/downloads/138165/en
  ```

  Only ICAO-code rows are imported (sheet `by ICAO code`, 210 rows); the
  per-engine `by aircraft configuration` sheet needs an engine variant the
  traffic sample does not provide. When several proxies exist for one ICAO
  code, the one with the smallest total |Δ| wins. Hexes whose typecode has no
  proxy in the archive stay `unbekannt:`.
- OpenSky OAuth2 client credentials (receiver feed must push to OpenSky) —
  three interchangeable ways, precedence `--client-id`/`--client-secret` (or
  their env vars) over `--credentials`:
  1. env: `export OPENSKY_CLIENT_ID=... OPENSKY_CLIENT_SECRET=...`
  2. options: `--client-id ... --client-secret ...`
  3. JSON file: `--credentials credentials.json` with
     `{"clientId": "...", "clientSecret": "..."}`
     (snake_case `client_id`/`client_secret` also accepted; `own` uses it for
     whatever the options/env leave unset; unreadable file or missing keys
     abort with a clear error). `credentials.json` is
     git-ignored — never commit secrets.

Example with receiver EGRID (resolves E/N + terrain offset like `parcel`,
s. §4a/§4e):

```sh
.venv/bin/fluglaerm own --egrid CH330877058702 --radius 20000 --credentials credentials.json
#    SWA123 abc123 A320-250N  departure MaxTakeoff   24288 lb/eng   2276 m  Lmax= 51.9  SEL= 67.2
# L_jetzt=52.5 dB aus 1 Flugzeugen
# informativ, nicht rechtsgültig (Ist-Verkehr, keine Anhang-5-Korrektur)
```

### e) GWR sqlite (EGRID lookup) — required for `parcel --egrid` / `own --egrid`

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

### g) Local state history (`collect` + `own --source local`)

OpenSky `/states/own` is live-only (no retention), so the project keeps its
own history: `collect` polls the adsb.im feeder's tar1090 endpoint
(`http://<pi>:8080/data/aircraft.json`, refreshed ~1 s) and appends snapshots
to `data/own_states.sqlite` (git-ignored via `data/*.sqlite`):

```sh
.venv/bin/fluglaerm collect --host <pi> --once --debug   # single snapshot (cron/launchd)
.venv/bin/fluglaerm collect --host <pi> --duration 3600  # 1 h at 5 s sampling
```

Read-back with `own --source local` (no OpenSky credentials needed; the
feeder already is this receiver's data, so `--serials` is ignored):

```sh
.venv/bin/fluglaerm own --source local --states-db data/own_states.sqlite --window 3600 --egrid CH330877058702 --es 2 --nutzung wohnen
```

`--window 3600` loads the last hour ending now; `--window 0` loads the last
`--interval` seconds (default 60). A missing DB file fails loudly
(`States-DB nicht gefunden`, exit 1); `collect --host 127.0.0.1 --once`
against a dead feeder likewise (`Feeder nicht erreichbar`, exit 1), while
the loop mode only logs a warning and retries.

## 5. Interpreting output

- `Lrt`: day rating level; `Lrn[nacht1/nacht2]`: night-hour rating levels.
- `Lrk`/`Lrg`: Kleinflugzeug / Grossflugzeug partial levels.
- `Status`: `eingehalten` | `IGW überschritten` | `AW` (+ note at `lrt = 66`)
  per ES/Nutzung.
- `AGL`: `innerhalb` iff `Lrt > 60` or `Lrn[nacht1] > 55` (IGW ES II).
- `parcel` additionally lists Auflagen and writes `nachweis.md`/`result.json`
  (overwritten on each run; both git-ignored).
- `own`: per-aircraft `LAmax`/`SEL` at the receiver plus the energetic sum
  `L_jetzt`; `unbekannt:` (no registry hit, excluded) and `übersprungen:`
  (with reason) lines explain non-contributing tracks. Overflights above
  10,000 ft AFE (ANP procedures end there) are evaluated as a
  departure/`MaxClimb` estimate and marked `[Schätzung]` in the row — they
  flow into `L_jetzt`. Such rows are indicative, not ANP-covered.
- `own --window N [--interval S]`: backfills `[now−N, now)` (`--time`, if
  given, moves the window end to that timestamp) in S-second steps
  (default N/S calls; `/states/own` is exempt from credits and rate limits).
  Repeated snapshots are deduped by `(icao24, last_contact)`; each aircraft is
  reported at its **loudest sample of the window** with UTC time
  (`HH:MM:SSZ`), and `L_jetzt` is the energetic sum over **all evaluated
  samples** of the window — not just the peak rows. 3600 s at
  `--interval 60` = 60 calls. Without `--window` the behaviour is the single
  current snapshot (unchanged).

`own --debug` writes the full decision chain to **stderr** (stdout stays
parseable): resolved receiver/registry/credentials source, the fetched state
and track counts, and per aircraft the newest sample, the phase decision
(vr, alt AFE, cutback → op_mode/rating), the B-1 inputs (coefficient rows,
VC from TAS, ISA temperature, HiTemp flat-rating), the NPD curves picked, the
geometry (slant, elevation, lateral) and each correction (ΔI, Λ, ΔV) with the
base and final `Lmax`/`SEL`. The exact request URL is logged before and after
the call — `GET …/states/own?serials=…&time=… -> HTTP 200, 0 eigene States` —
plus token fetch/reuse and `X-Rate-Limit-Remaining`, so "0 States" is
traceable to the query (serials/time) or quota. Secrets (client secret, token)
are never logged; `urllib3` debug is suppressed.

## 6. Limitations (read before relying on results)

- Seed run = method demonstration: nominal routes + placeholder NPD tables.
  The report says so explicitly; it is not a legal Nachweis.
- Ground roll excluded; Klein-T day window is 14 h (06–20).
- `-inf` levels (e.g. silent night hours) are legitimate zeros in the log sum.
