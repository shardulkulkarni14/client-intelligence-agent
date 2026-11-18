"""Data-quality check for one client: what is duplicated, missing, sparse or blank.

The briefing's "data gaps and confidence" section is written from this result, so
every gap has a stable code and the confidence rating follows a fixed rule.
"""

from __future__ import annotations

from client_intel.db import Dataset
from client_intel.evidence import NO_DATA, OK, PARTIAL, FactBuilder, ToolResult, cite, fmt_num
from client_intel.tools.usage import (
    MIN_HISTORY_MONTHS,
    contract_in_force,
    last_complete_month,
    missing_months,
    product_label,
    usage_by_product,
)

TOOL = "data_quality"

# Confidence rule: any SEVERE code -> "low"; otherwise any MODERATE code, or at least
# CONTEXT_CODES_FOR_MEDIUM context codes -> "medium"; otherwise "high".
# Severe: a core figure (current contract, trend, the usage value itself) cannot be trusted.
SEVERE_CODES = frozenset(
    {"no_contract_in_force", "short_history", "no_usage_data", "conflicting_natural_key"}
)
# Moderate: the figures stand, but part of the picture was repaired in code or is unknown.
MODERATE_CODES = frozenset(
    {
        "missing_month",
        "blank_included_units",
        "duplicate_row",
        "duplicate_natural_key",
        "usage_without_contract_line",
        "contract_product_without_usage",
    }
)
# Context: nothing is wrong with the numbers, there is just less to cross-check them with.
CONTEXT_CODES = frozenset({"no_support_tickets", "no_meeting_notes", "no_opportunities"})
# One absent context source is normal (15 of 25 clients have no notes); two leaves the
# numbers with almost no qualitative corroboration.
CONTEXT_CODES_FOR_MEDIUM = 2

# Citation prefix per source table, as in the tool catalogue.
_CITE_PREFIX = {
    "contracts": "contracts",
    "contract_lines": "contract_lines",
    "usage_monthly": "usage",
    "support_tickets": "ticket",
    "crm_opportunities": "opp",
    "meeting_notes": "note",
    "clients": "client",
    "products": "product",
}


def rate_confidence(codes: list[str]) -> str:
    """Apply the documented rule to the distinct gap codes found."""
    found = set(codes)
    if found & SEVERE_CODES:
        return "low"
    if found & MODERATE_CODES or len(found & CONTEXT_CODES) >= CONTEXT_CODES_FOR_MEDIUM:
        return "medium"
    return "high"


def check_data_quality(ds: Dataset, client_id: str) -> ToolResult:
    """Gaps for this client plus an overall confidence rating with its reasons."""
    fb = FactBuilder(TOOL)
    if client_id not in ds.clients:
        fb.gap("unknown_client", f"Client {client_id} is not in the client table.")
        return fb.result(NO_DATA, {"confidence": "low", "reasons": [], "codes": ["unknown_client"]})

    # Loader findings (duplicates removed or conflicts found while reading the tables).
    seen: set[tuple[str, str, tuple[str, ...]]] = set()
    for issue in ds.issues:
        key = (issue.code, issue.table, issue.rows)
        if issue.client_id != client_id or key in seen:
            continue
        seen.add(key)
        prefix = _CITE_PREFIX.get(issue.table, issue.table)
        fb.gap(issue.code, issue.message, [cite(prefix, row) for row in issue.rows])

    # Usage coverage per product.
    cutoff = last_complete_month(ds.as_of)
    by_product = usage_by_product(ds, client_id)
    if not by_product:
        fb.gap("no_usage_data", f"No usage rows exist for client {client_id}.")
    for product_id, by_month in by_product.items():
        label = product_label(ds, product_id)
        rows = list(by_month.values())
        absent = missing_months(by_month, cutoff)
        if absent:
            fb.gap(
                "missing_month",
                f"{label}: no usage row for {', '.join(absent)}; usage in these months is "
                "unknown, not zero.",
            )
        if len(rows) < MIN_HISTORY_MONTHS:
            fb.gap(
                "short_history",
                f"{label}: only {fmt_num(len(rows))} months of usage history (fewer than "
                f"{fmt_num(MIN_HISTORY_MONTHS)}), so trends and year-on-year comparisons "
                "are not available.",
                [cite("usage", r["usage_id"]) for r in rows],
            )
        blank = [r for r in rows if r["included_units"] is None]
        if blank:
            fb.gap(
                "blank_included_units",
                f"{label}: the included volume is blank for "
                f"{', '.join(r['month'] for r in blank)} (no signed contract covered the "
                "month), so utilisation is undefined there.",
                [cite("usage", r["usage_id"]) for r in blank],
            )

    # Contract coverage.
    contracts = ds.for_client("contracts", client_id)
    if contract_in_force(ds, client_id) is None:
        ids = ", ".join(f"{c['contract_id']} ({c['status']})" for c in contracts) or "none"
        fb.gap(
            "no_contract_in_force",
            f"No signed contract is in force for {client_id} on {ds.as_of.isoformat()}. "
            f"Contracts on file: {ids}.",
            [cite("contracts", c["contract_id"]) for c in contracts],
        )
    all_ids = {c["contract_id"] for c in contracts}
    signed_ids = {c["contract_id"] for c in contracts if c["status"] != "pending_signature"}
    on_any = {ln["product_id"] for ln in ds.contract_lines if ln["contract_id"] in all_ids}
    signed_lines = [ln for ln in ds.contract_lines if ln["contract_id"] in signed_ids]
    for product_id in sorted(set(by_product) - on_any):
        fb.gap(
            "usage_without_contract_line",
            f"{product_label(ds, product_id)}: usage is recorded but the product is not on "
            "any of the client's contracts.",
            [cite("usage", r["usage_id"]) for r in by_product[product_id].values()][:3],
        )
    for product_id in sorted({ln["product_id"] for ln in signed_lines} - set(by_product)):
        fb.gap(
            "contract_product_without_usage",
            f"{product_label(ds, product_id)}: the product is on a signed contract but no "
            "usage has been recorded for it.",
            [
                cite("contract_lines", ln["line_id"])
                for ln in signed_lines
                if ln["product_id"] == product_id
            ],
        )

    # Context sources. Absence is stated so the writer never implies "no complaints".
    for table, code, what in (
        ("tickets", "no_support_tickets", "support tickets"),
        ("notes", "no_meeting_notes", "meeting notes"),
        ("opportunities", "no_opportunities", "CRM opportunities"),
    ):
        if not ds.for_client(table, client_id):
            fb.gap(code, f"There are no {what} on file for {client_id}.")

    codes = list(dict.fromkeys(g.code for g in fb.gaps))
    confidence = rate_confidence(codes)
    # Reasons are the gaps that drove the rating, most serious class first.
    classes = {
        "low": [SEVERE_CODES, MODERATE_CODES],
        "medium": [MODERATE_CODES, CONTEXT_CODES],
        "high": [],
    }[confidence]
    drivers = [g for group in classes for g in fb.gaps if g.code in group]
    reasons = [g.text for g in drivers]
    driver_codes = list(dict.fromkeys(g.code for g in drivers))
    if confidence == "high":
        note = (
            "no duplicates, missing months, blank fields or contract gaps were found"
            if not codes
            else f"only a minor context gap was found ({', '.join(codes)})"
        )
    else:
        note = f"reasons: {', '.join(driver_codes)}"
    fb.calc(
        f"Data confidence for {client_id} is {confidence}; {note}.",
        list(dict.fromkeys(row for g in drivers for row in g.rows)),
        topic="confidence",
    )
    return fb.result(
        PARTIAL if fb.gaps else OK,
        {"confidence": confidence, "reasons": reasons, "codes": codes},
    )
