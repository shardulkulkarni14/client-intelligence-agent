"""Usage trend per product: year-on-year change, utilisation, overage and data gaps.

Every figure is computed here and formatted with the evidence helpers, so the writer
only repeats sentences. Units are never added across products, a month without a row
is unknown (never zero), and a blank included volume is a gap (never zero).
"""

from __future__ import annotations

from datetime import date
from typing import Any

from client_intel.db import Dataset, Row
from client_intel.evidence import (
    NO_DATA,
    OK,
    PARTIAL,
    FactBuilder,
    ToolResult,
    cite,
    fmt_eur,
    fmt_num,
    fmt_pct,
    pct_change,
)

TOOL = "usage_trend"

# Three months smooths single-month noise while still describing "now".
RECENT_MONTHS = 3
# Year-on-year needs the same months one year earlier, so 12 months is the minimum history.
MIN_HISTORY_MONTHS = 12
# Window for counting months above the included volume: one full seasonal cycle.
OVER_LOOKBACK_MONTHS = 12
# A year-on-year fall of 15% or more is well outside normal month-to-month variation.
YOY_DECLINE_RISK_PCT = -15.0
# Growth of 15% or more year on year suggests the client is outgrowing its allowance.
YOY_GROWTH_OPPORTUNITY_PCT = 15.0
# Using under half of the paid volume invites a downsell at renewal.
LOW_UTILISATION_RISK_PCT = 50.0
# Over the included volume in 2 of the last 3 months is sustained, not a one-off spike.
OVER_MONTHS_FOR_OPPORTUNITY = 2

_MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# --- month arithmetic on 'YYYY-MM' strings ------------------------------------


def shift_month(month: str, delta: int) -> str:
    year, mon = int(month[:4]), int(month[5:7])
    index = year * 12 + (mon - 1) + delta
    return f"{index // 12:04d}-{index % 12 + 1:02d}"


def last_complete_month(as_of: date) -> str:
    """Usage is complete through the month before the extract date."""
    return shift_month(f"{as_of.year:04d}-{as_of.month:02d}", -1)


def month_range(first: str, last: str) -> list[str]:
    out: list[str] = []
    current = first
    while current <= last:
        out.append(current)
        current = shift_month(current, 1)
    return out


def _one(month: str) -> str:
    return f"{_MONTH_NAMES[int(month[5:7]) - 1]} {month[:4]}"


def month_label(months: list[str]) -> str:
    """['2026-08','2026-09','2026-10'] -> 'Aug-Oct 2026'; non-contiguous months are listed."""
    months = sorted(months)
    if not months:
        return "no months"
    if len(months) == 1:
        return _one(months[0])
    if months != month_range(months[0], months[-1]):
        return ", ".join(_one(m) for m in months)
    first, last = months[0], months[-1]
    if first[:4] == last[:4]:
        return f"{_MONTH_NAMES[int(first[5:7]) - 1]}-{_one(last)}"
    return f"{_one(first)}-{_one(last)}"


# --- shared lookups (also used by the data-quality tool) ----------------------


def usage_by_product(ds: Dataset, client_id: str) -> dict[str, dict[str, Row]]:
    """product_id -> month -> row, for complete months only. The loader already de-duplicated."""
    cutoff = last_complete_month(ds.as_of)
    out: dict[str, dict[str, Row]] = {}
    for row in ds.for_client("usage", client_id):
        if row["month"] <= cutoff:
            out.setdefault(row["product_id"], {})[row["month"]] = row
    return {pid: dict(sorted(months.items())) for pid, months in sorted(out.items())}


def missing_months(by_month: dict[str, Row], cutoff: str) -> list[str]:
    """Months with no row between the first reported month and the last complete month."""
    if not by_month:
        return []
    return [m for m in month_range(min(by_month), cutoff) if m not in by_month]


def relevant_contract(ds: Dataset, client_id: str) -> Row | None:
    """The contract in force, else the most recently ended signed one (for its rates)."""
    current = ds.contract_in_force(client_id)
    if current is not None:
        return current
    signed = [
        c
        for c in ds.for_client("contracts", client_id)
        if c["signed_date"] is not None and c["status"] != "pending_signature"
    ]
    return max(signed, key=lambda c: c["end_date"], default=None)


def product_label(ds: Dataset, product_id: str) -> str:
    product = ds.products.get(product_id)
    return f"{product_id} ({product['product_name']})" if product else product_id


# --- the tool -----------------------------------------------------------------


def _cites(rows: list[Row]) -> list[str]:
    return [cite("usage", r["usage_id"]) for r in rows]


def _total(rows: list[Row]) -> float:
    # WIDGETS has one decimal; rounding stops float noise reaching the formatted figure.
    return round(sum(r["units_used"] for r in rows), 4)


def _util(used: float, included: float | None) -> float | None:
    if included is None or included == 0:
        return None
    return used / included * 100.0


def _window_label(months: list[str], cutoff: str) -> str:
    """Name the months actually compared. "The last N months" is only true when they
    are consecutive and end at the last complete month; otherwise say what was used."""
    count = fmt_num(len(months))
    first, last = _one(months[0]), _one(months[-1])
    if months == month_range(months[0], cutoff):
        return f"the last {count} months ({first} to {last})"
    return f"the {count} months with data between {first} and {last}"


def _yoy_signal(pct: float | None) -> str:
    if pct is None:
        return ""
    if pct <= YOY_DECLINE_RISK_PCT:
        return "risk"
    if pct >= YOY_GROWTH_OPPORTUNITY_PCT:
        return "opportunity"
    return "neutral"


def _product_trend(
    ds: Dataset, fb: FactBuilder, client_id: str, product_id: str, by_month: dict[str, Row]
) -> dict[str, Any]:
    cutoff = last_complete_month(ds.as_of)
    product = ds.products.get(product_id, {})
    unit = product.get("usage_unit") or "units"
    label = product_label(ds, product_id)
    rows = list(by_month.values())
    decimals = 0 if all(float(r["units_used"]).is_integer() for r in rows) else 1
    flags: list[str] = []

    def num(value: float | None) -> str:
        return fmt_num(value, decimals)

    recent_months = month_range(shift_month(cutoff, -(RECENT_MONTHS - 1)), cutoff)
    year_ago_months = [shift_month(m, -12) for m in recent_months]
    prior_months = [shift_month(m, -RECENT_MONTHS) for m in recent_months]
    recent_rows = [by_month[m] for m in recent_months if m in by_month]

    info: dict[str, Any] = {
        "product_id": product_id,
        "product_name": product.get("product_name"),
        "unit": unit,
        "history_months": len(rows),
        "first_month": rows[0]["month"],
        "last_month": rows[-1]["month"],
        "series": [
            {
                "month": r["month"],
                "units_used": r["units_used"],
                "included_units": r["included_units"],
                "usage_id": r["usage_id"],
            }
            for r in rows
        ],
        "missing_months": missing_months(by_month, cutoff),
        "recent_months": recent_months,
        "recent_total": None,
        "year_ago_months": year_ago_months,
        "year_ago_total": None,
        "yoy_pct": None,
        "prior_months": prior_months,
        "prior_total": None,
        "prior_period_pct": None,
        "latest": None,
        "utilisation_recent_pct": None,
        "utilisation_recent_months": [],
        "peak": None,
        "months_over_included": None,
        "months_over_compared": 0,
        "recent_months_over_included": None,
        "overage_units_recent": None,
        "overage_rate_eur_per_unit": None,
        "overage_eur_indicative": None,
        "signals": [],
        "flags": flags,
    }

    # History and gaps.
    fb.calc(
        f"{label}: {fmt_num(len(rows))} months of usage data, from {_one(rows[0]['month'])} "
        f"to {_one(rows[-1]['month'])}; usage is measured in {unit}.",
        _cites([rows[0], rows[-1]]),
        topic="history",
    )
    if info["missing_months"]:
        flags.append("missing_month")
        fb.gap(
            "missing_month",
            f"{label}: no usage row for {', '.join(info['missing_months'])}. Usage in "
            "these months is unknown, not zero, and they are left out of every total.",
        )
    short = len(rows) < MIN_HISTORY_MONTHS
    if short:
        flags.append("short_history")
        fb.gap(
            "short_history",
            f"{label}: only {fmt_num(len(rows))} months of usage history (fewer than "
            f"{fmt_num(MIN_HISTORY_MONTHS)}), so no year-on-year comparison is possible.",
            _cites(rows),
        )

    # Latest month.
    latest = rows[-1]
    latest_util = _util(latest["units_used"], latest["included_units"])
    info["latest"] = {
        "month": latest["month"],
        "units_used": latest["units_used"],
        "included_units": latest["included_units"],
        "utilisation_pct": latest_util,
        "usage_id": latest["usage_id"],
    }
    if latest_util is None:
        fb.calc(
            f"{label}: {num(latest['units_used'])} {unit} used in {_one(latest['month'])}.",
            _cites([latest]),
            topic="usage_latest",
        )
    else:
        fb.calc(
            f"{label}: {num(latest['units_used'])} {unit} used in {_one(latest['month'])} "
            f"against {num(latest['included_units'])} included, a utilisation of "
            f"{fmt_pct(latest_util, signed=False)}.",
            _cites([latest]),
            topic="usage_latest",
        )

    # Year on year: the only seasonally fair comparison.
    if len(recent_rows) == RECENT_MONTHS:
        info["recent_total"] = _total(recent_rows)
    if not short:
        absent = [m for m in recent_months + year_ago_months if m not in by_month]
        if absent:
            flags.append("yoy_not_computable")
            fb.gap(
                "yoy_not_computable",
                f"{label}: year-on-year change for {month_label(recent_months)} cannot be "
                f"computed because usage is missing for {', '.join(sorted(absent))}.",
            )
        else:
            year_ago_rows = [by_month[m] for m in year_ago_months]
            info["year_ago_total"] = _total(year_ago_rows)
            yoy = pct_change(info["recent_total"], info["year_ago_total"])
            info["yoy_pct"] = yoy
            if yoy is None:
                flags.append("yoy_not_computable")
                fb.gap(
                    "yoy_not_computable",
                    f"{label}: usage in {month_label(year_ago_months)} was zero, so a "
                    "year-on-year percentage is undefined.",
                    _cites(year_ago_rows),
                )
            else:
                signal = _yoy_signal(yoy)
                if signal in ("risk", "opportunity"):
                    info["signals"].append(f"yoy_{signal}")
                fb.calc(
                    f"{label}: {num(info['recent_total'])} {unit} in "
                    f"{month_label(recent_months)} versus {num(info['year_ago_total'])} in "
                    f"{month_label(year_ago_months)}, a change of {fmt_pct(yoy)} year on year.",
                    _cites(recent_rows + year_ago_rows),
                    topic="usage_yoy",
                    signal=signal,
                )

        # Previous period: secondary, and misleading alone because of the summer dip.
        if len(recent_rows) == RECENT_MONTHS and all(m in by_month for m in prior_months):
            prior_rows = [by_month[m] for m in prior_months]
            info["prior_total"] = _total(prior_rows)
            prior_pct = pct_change(info["recent_total"], info["prior_total"])
            info["prior_period_pct"] = prior_pct
            if prior_pct is not None:
                fb.calc(
                    f"{label}: {num(info['recent_total'])} {unit} in "
                    f"{month_label(recent_months)} versus {num(info['prior_total'])} in "
                    f"{month_label(prior_months)}, a change of {fmt_pct(prior_pct)} against "
                    "the previous three months (not seasonally adjusted).",
                    _cites(recent_rows + prior_rows),
                    topic="usage_prior_period",
                    signal="neutral",
                )

    # Utilisation and overage need the included volume; a blank one is a gap.
    blank = [r for r in rows if r["included_units"] is None]
    if blank:
        flags.append("blank_included_units")
        fb.gap(
            "blank_included_units",
            f"{label}: the included volume is blank for "
            f"{', '.join(r['month'] for r in blank)} (no signed contract covered the "
            "month), so utilisation and overage are not computed for those months.",
            _cites(blank),
        )

    known_recent = [r for r in recent_rows if r["included_units"] is not None]
    if known_recent:
        used = _total(known_recent)
        included = round(sum(r["included_units"] for r in known_recent), 4)
        util = _util(used, included)
        months = [r["month"] for r in known_recent]
        info["utilisation_recent_pct"] = util
        info["utilisation_recent_months"] = months
        if util is not None:
            # A product only just switched on has not had time to ramp up, so low
            # utilisation over a short history is not evidence of a downsell risk.
            low = util < LOW_UTILISATION_RISK_PCT and not short
            if low:
                info["signals"].append("low_utilisation_risk")
            caveat = (
                f" This figure covers only {fmt_num(len(rows))} months of usage history."
                if short
                else ""
            )
            partial = (
                ""
                if len(months) == RECENT_MONTHS
                else f" ({fmt_num(len(months))} of the last {fmt_num(RECENT_MONTHS)} months "
                "have usage and a known included volume)"
            )
            fb.calc(
                f"{label}: average utilisation of {fmt_pct(util, signed=False)} in "
                f"{month_label(months)}{partial}: {num(used)} {unit} used against "
                f"{num(included)} included.{caveat}",
                _cites(known_recent),
                topic="utilisation",
                signal="risk" if low else "neutral",
            )

    lookback = [r for r in rows[-OVER_LOOKBACK_MONTHS:] if r["included_units"] is not None]
    if lookback:
        window = _window_label([r["month"] for r in lookback], cutoff)
        # The recent average hides a seasonal peak (summer sports peak mid-year), and the
        # peak is what the included volume has to cover.
        peak = max(lookback, key=lambda r: _util(r["units_used"], r["included_units"]) or 0.0)
        peak_util = _util(peak["units_used"], peak["included_units"])
        if peak_util is not None:
            info["peak"] = {
                "month": peak["month"],
                "units_used": peak["units_used"],
                "included_units": peak["included_units"],
                "utilisation_pct": peak_util,
                "usage_id": peak["usage_id"],
            }
            fb.calc(
                f"{label}: highest utilisation in {window} was "
                f"{fmt_pct(peak_util, signed=False)} in {_one(peak['month'])}: "
                f"{num(peak['units_used'])} {unit} used against "
                f"{num(peak['included_units'])} included.",
                _cites([peak]),
                topic="utilisation_peak",
                signal="neutral",
            )
        # Numeric comparison on the loader's floats; the raw TEXT columns would mis-order.
        over = [r for r in lookback if r["units_used"] > r["included_units"]]
        recent_over = [r for r in known_recent if r["units_used"] > r["included_units"]]
        sustained = len(recent_over) >= OVER_MONTHS_FOR_OPPORTUNITY
        info["months_over_included"] = len(over)
        info["months_over_compared"] = len(lookback)
        info["months_over_list"] = [r["month"] for r in over]
        info["recent_months_over_included"] = len(recent_over)
        if sustained:
            info["signals"].append("sustained_over_included_opportunity")
        fb.calc(
            f"{label}: usage was above the included volume in {fmt_num(len(over))} of "
            f"{window}, including "
            f"{fmt_num(len(recent_over))} of {fmt_num(len(known_recent))} in "
            f"{month_label([r['month'] for r in known_recent]) if known_recent else 'n/a'}.",
            _cites(lookback),
            topic="over_included",
            signal="opportunity" if sustained else "neutral",
        )

        overage = round(sum(r["units_used"] - r["included_units"] for r in recent_over), 4)
        info["overage_units_recent"] = overage
        if overage > 0:
            text = (
                f"{label}: usage exceeded the included volume by an estimated "
                f"{num(overage)} {unit} in {month_label([r['month'] for r in recent_over])}."
            )
            sources = _cites(recent_over)
            contract = relevant_contract(ds, client_id)
            line = next(
                (
                    ln
                    for ln in (ds.lines_for(contract["contract_id"]) if contract else [])
                    if ln["product_id"] == product_id
                    and ln["overage_rate_eur_per_unit"] is not None
                ),
                None,
            )
            if line is not None and contract is not None:
                rate = line["overage_rate_eur_per_unit"]
                amount = overage * rate
                info["overage_rate_eur_per_unit"] = rate
                info["overage_eur_indicative"] = amount
                info["overage_contract_id"] = contract["contract_id"]
                rate_text = fmt_num(rate, 0 if float(rate).is_integer() else 2)
                text += (
                    f" At the overage rate of EUR {rate_text} per unit on contract "
                    f"{contract['contract_id']} that is an indicative {fmt_eur(amount)}; "
                    "indicative only, there is no billing data to confirm it was charged."
                )
                sources += [
                    cite("contract_lines", line["line_id"]),
                    cite("contracts", contract["contract_id"]),
                ]
            fb.calc(text, sources, topic="overage", signal="opportunity")

    return info


def get_usage_trend(ds: Dataset, client_id: str) -> ToolResult:
    """Usage facts per product for one client. Units are never combined across products."""
    fb = FactBuilder(TOOL)
    cutoff = last_complete_month(ds.as_of)
    base: dict[str, Any] = {
        "client_id": client_id,
        "as_of": ds.as_of,
        "last_complete_month": cutoff,
        "products": {},
    }
    by_product = usage_by_product(ds, client_id)
    if not by_product:
        fb.gap("no_usage_data", f"No usage rows exist for client {client_id}.")
        return fb.result(NO_DATA, base)
    for product_id, by_month in by_product.items():
        base["products"][product_id] = _product_trend(ds, fb, client_id, product_id, by_month)
    return fb.result(PARTIAL if fb.gaps else OK, base)
