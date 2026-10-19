"""Markdown-Report für `fluglaerm own`: Terminal-Tabelle + Herleitung je Flugzeug."""

import time
from fluglaerm.common.types import Receiver
from fluglaerm.ist_laerm.own import ARP_ALT_M, OwnResult


def _bullets(items: list[str]) -> list[str]:
    if not items:
        return ["—"]
    return [f"- {s}" for s in items]


def _window_bounds(result: OwnResult) -> str:
    stamps = [r.ts for r in result.rows if r.ts]
    if not stamps:
        return "keine Samples"
    lo, hi = min(stamps), max(stamps)
    fmt = lambda ts: time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts)) + "Z"
    return f"min {fmt(lo)} (ts={lo}), max {fmt(hi)} (ts={hi})"


def render_own_report(
    result: OwnResult,
    receiver: Receiver,
    db_path: str,
    registry_path: str,
    radius: float,
    window: int,
) -> str:
    """Gibt den Own-Report als Markdown-String zurück (endet mit `\\n`)."""
    lines = [
        "# Ist-Lärmpegel am Empfänger (fluglaerm own)",
        "",
        f"**Empfänger:** E={receiver.east:.0f} m, N={receiver.north:.0f} m, "
        f"h={receiver.height_m:.1f} m über Flughafen-Grund",
        f"**Suchradius:** {radius:.0f} m",
        (
            "**Fenster:** aktueller Stand (nur neuester Sample)"
            if window == 0
            else "".join([
                f"**Fenster:** {window} s (lautester Sample im Fenster), ",
                _window_bounds(result),
            ])
        ),
        f"**ANP-Datenbank:** {db_path}",
        f"**Registry:** {registry_path}",
        "",
        "## Tabelle",
        "| Rufzeichen | ICAO24 | Flugzeug | Phase | Rating | Schub (lb) | Distanz (m) | Lmax (dB) | SEL (dB) | Zeit | Bemerkungen |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in result.rows:
        stamp = time.strftime("%H:%M:%S", time.gmtime(r.ts)) + "Z" if r.ts else "--:--:--"
        lines.append(
            f"| {r.callsign or '-'} | {r.icao24} | {r.acft_id} | {r.phase} | "
            f"{r.thrust_rating} | {r.cnt_lbf:.0f} | {r.slant_m:.0f} | "
            f"{r.lmax_db:.1f} | {r.sel_db:.1f} | {stamp} | {r.bemerkungen} |"
        )
    lines += ["", "## Herleitung je Flugzeug"]
    for r in result.rows:
        d = r.detail
        lines.append(f"### {r.callsign or '-'} ({r.icao24}) — {r.acft_id}")
        lines += ["| Schritt | Wert | Quelle |", "|---|---|---|"]
        if d is None:
            lines += ["", ""]
            continue
        if d.via == "registry":
            zuordnung = f"Registry → {d.acft_id}"
            zuordnung_src = registry_path
        else:
            zuordnung = (
                f"Ersatz {d.sub_typecode} → {d.acft_id} "
                f"(Δ {d.delta_db:+.1f} dB)"
            )
            zuordnung_src = f"{db_path} · Tabelle substitutions"
        low = d.coeff_low
        coeff = (
            f"e={low['e']} f={low['f']} ga={low['ga']} "
            f"gb={low['gb']} h={low['h']}"
        )
        if d.coeff_hi is not None:
            hi = d.coeff_hi
            coeff += (
                f" + HiTemp e={hi['e']} f={hi['f']} ga={hi['ga']} "
                f"gb={hi['gb']} h={hi['h']}"
            )
        rows = [
            ("Flugzeugzuordnung", zuordnung, zuordnung_src),
            (
                "Flugzeugdaten",
                f"{d.description}, {d.engines} TW, {d.wing}, "
                f"NPD-ID {d.npd_id}, Max-Schub {d.max_thrust_lbf:.0f} lb",
                f"{db_path} · Tabelle aircraft",
            ),
            (
                "State",
                f"ts={d.ts} E={d.east:.0f} N={d.north:.0f} "
                f"alt={d.alt_m:.1f} m v={d.speed_kn:.1f} kn "
                f"trk={d.track_deg:.0f}° vr={d.vertical_rate_ms:+.2f} m/s "
                f"on_ground={d.on_ground}",
                "OpenSky-State (own_states/own_history)",
            ),
            (
                "Höhe MSL",
                f"{d.alt_m:.1f} m = {d.alt_msl_ft:.0f} ft",
                "alt_m × 3.28084",
            ),
            (
                "Höhe AFE",
                f"{d.alt_afe_ft:.0f} ft",
                f"alt_msl_ft − ARP({ARP_ALT_M} m) × 3.28084",
            ),
            (
                "Phase",
                f"{d.op_mode} / {d.rating}",
                f"pick_phase(vr={d.vertical_rate_ms:+.2f} m/s, "
                f"alt_afe={d.alt_afe_ft:.0f} ft, cutback={d.cutback_ft})",
            ),
            (
                "B-1 Koeffizienten",
                coeff,
                f"{db_path} · Tabelle jet_engine_coefficients "
                f"({d.acft_id}, {d.rating})",
            ),
            (
                "VC (CAS)",
                f"{d.vc_kt:.1f} kt (TAS {d.speed_kn:.1f} kn)",
                "calibrated_airspeed_kt",
            ),
            (
                "T (ISA)",
                f"{d.temp_c:.1f} °C",
                f"15 − 0.0019812 × {d.alt_msl_ft:.0f} ft",
            ),
            (
                "CNT",
                f"{d.cnt_lbf:.0f} lbf",
                "corrected_net_thrust(low[, hi], VC, alt_msl_ft, T)",
            ),
            (
                "NPD-Tabelle",
                f"{d.npd_id} {d.op_mode} {d.mount} "
                f"{d.max_thrust_lbf:.0f} lb · {len(d.powers_lbf)} "
                f"Leistungsstufen · ref {d.ref_speed_kn:.0f} kn",
                f"{d.npd_source} · Tabelle npd_data",
            ),
            (
                "Slant-Distanz",
                f"{d.slant_m:.1f} m",
                "slant_m(E, N, alt−ARP, Empfänger)",
            ),
            (
                "Elevation",
                f"{d.elev_deg:.1f}°",
                "asin((alt−ARP−h)/slant)",
            ),
            (
                "Lateral-Offset",
                f"{d.lateral_m:.0f} m",
                "lateral_offset_m(…)",
            ),
            (
                "base Lmax",
                f"{d.base_lmax_db:.2f} dB",
                "interp_npd(LAmax, CNT, slant)",
            ),
            (
                "base SEL",
                f"{d.base_sel_db:.2f} dB",
                "interp_npd(SEL, CNT, slant)",
            ),
            (
                "ΔI",
                f"{d.di_db:+.2f} dB",
                f"installation_correction(elev, mount={d.mount})",
            ),
            (
                "Λ",
                f"{d.lam_db:.2f} dB",
                "lateral_attenuation(elev, lat)",
            ),
            (
                "ΔV",
                f"{d.dv_db:+.2f} dB",
                f"duration_correction(v={d.speed_kn:.1f} kn, "
                f"ref={d.ref_speed_kn:.0f} kn)",
            ),
        ]
        if d.via == "substitution":
            rows.append(
                (
                    "Δ (Ersatz)",
                    f"{d.delta_db:+.2f} dB",
                    f"{db_path} · Tabelle substitutions",
                )
            )
        rows += [
            (
                "**Lmax**",
                f"**{d.lmax_db:.2f} dB**",
                "base_Lmax + ΔI − Λ + Δ",
            ),
            (
                "**SEL**",
                f"**{d.sel_db:.2f} dB**",
                "base_SEL + ΔV + ΔI − Λ + Δ",
            ),
        ]
        for schritt, wert, quelle in rows:
            lines.append(f"|{schritt}|{wert}|{quelle}|")
        if d.estimate:
            lines.append(
                "> Schätzung: über 10 000 ft AFE — D/MaxClimb ohne NPD-Prozedur"
            )
        if d.flat_rated:
            lines.append("> HiTemp-Flat-Rating zieht (Min aus low/hi B-1)")
        lines.append("")
    lines += ["## Ersetzt", *_bullets(result.substituted), ""]
    lines += ["## Unbekannt", *_bullets(result.unknown), ""]
    lines += ["## Übersprungen", *_bullets(result.skipped), ""]
    value = (
        "−∞" if result.level_db == float("-inf") else f"{result.level_db:.1f}"
    )
    lines += [
        "## Ergebnis",
        f"L_jetzt = {value} dB aus {len(result.rows)} Flugzeugen",
        f"> {result.label}",
        "",
        "## Methodik & Näherungen",
        "- Kette: OpenSky-State → Registry/Ersatztabelle → aircraft/engine → "
        "B-1/B-23 CNT → NPD-Interpolation → ΔI/Λ/ΔV → Lmax/SEL",
        "- Näherungen: ISA-Temperatur, Ground Speed ≡ TAS, kein Wind, SEL als "
        "unendlicher Pfad ohne ΔF, keine atmosphärische Re-Normierung "
        "(ECAC Doc 29 App. D)",
        "- Über 10 000 ft AFE: Schätzung D/MaxClimb (Prozedurabdeckung endet dort)",
        f"- Quellen: ECAC Doc 29, 5. Aufl., Vol. 2 · EASA-ANP v9 ({db_path}) · "
        f"OpenSky-States · {registry_path}",
        "",
        "## Glossar",
        "| Begriff | Erklärung |",
        "|---|---|",
        "| Lmax | Maximalpegel des Überflugs in dB(A) |",
        "| SEL | Sound Exposure Level in dB(A): auf 1 s normierte Schallenergie des Ereignisses |",
        "| L_jetzt | energetische Summe aller Lmax: 10·log10(Σ 10^(Lmax/10)) |",
        "| CNT | korrigierter Nettoschub (corrected net thrust) in lbf, aus B-1/B-23-Koeffizienten |",
        "| B-1 | Doc-29-Triebwerksmodell: Schub als Funktion von CAS, Druckhöhe und Temperatur |",
        "| HiTemp-Flat-Rating | Min(low, hi)-Schub bei hohen Temperaturen (hi-Koeffizienten aktiv) |",
        "| NPD | Noise-Power-Distance: Tabellen LAmax/SEL über Schub und Slant-Distanz |",
        "| base Lmax / base SEL | NPD-Interpolationswerte vor Korrekturen: interp_npd(CNT, slant) |",
        "| ΔI | Installationskorrektur: 10·log10([(a·cos²φ + sin²φ)^b] · [c·sin²(2φ) + cos²(2φ)]), φ = Elevation, a/b/c je Triebwerksanbau |",
        "| Λ | laterale Dämpfung: Λ = Γ(ℓ)·Λ(β), Γ(ℓ) = 1.089·(1 − e^(−0.00274·ℓ)) für ℓ ≤ 914 m sonst 1, Λ(β) = 1.137 − 0.0229·β + 9.72·e^(−0.142·β) für 0 ≤ β ≤ 50° (β < 0: 10.857, β > 50°: 0) |",
        "| ΔV | Dauerkorrektur: 10·log10(Vref / V), V = Ground Speed, Vref = NPD-Referenzgeschwindigkeit |",
        "| Δ (Ersatz) | EASA-Ersatzzuschlag bei Proxy-Typen: Δdep (Departure) bzw. Δapp (Approach) |",
        "| Lmax-Formel | Lmax = base_Lmax + ΔI − Λ + Δ |",
        "| SEL-Formel | SEL = base_SEL + ΔV + ΔI − Λ + Δ |",
        "| op_mode | NPD-Betriebsart: D (Departure) oder A (Approach) |",
        "| Rating | Schubrate: MaxTakeoff / MaxClimb / MaxClimbHiTemp / IdleApproach |",
        "| Phase | departure (op_mode D) oder approach (op_mode A) |",
        "| AFE | Höhe über Flughafen-Grund: alt_msl_ft − ARP(432.0 m) × 3.28084 |",
        "| Slant | Schrägdistanz Empfänger–Flugzeug in m |",
        "| Elevation | Höhenwinkel Empfänger→Flugzeug: asin((alt−ARP−h)/slant) |",
        "| Lateral-Offset |Querabstand zur Bodenspur in m: lateral_offset_m(…) |",
        "| VC (CAS) | kalibrierte Fluggeschwindigkeit in kt aus TAS und Flughöhe |",
        "| T (ISA) | Standardatmosphärentemperatur: 15 − 0.0019812 × alt_msl_ft (°C) |",
        "| ICAO24 | 24-Bit-Transponderadresse des Flugzeugs (Hex) |",
        "| cutback | Cutback-Höhe in ft: Umschaltpunkt MaxTakeoff → MaxClimb (None bei Schätzung) |",
        "| Estimate/Schätzung | Über 10 000 ft AFE: D/MaxClimb ohne NPD-Prozedur, Betrag konservativ-hoch |",
        "| TS | Sample-Zeitpunkt (Unix); Fenster min/max = ältester/neuester Sample |",
    ]
    return "\n".join(lines) + "\n"
