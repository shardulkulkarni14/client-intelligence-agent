"""Contract position and CRM opportunities for one client.

"In force" is decided by status AND dates together: a filter on status alone misses
a contract that has run out, and a filter on dates alone would treat an unsigned
draft as binding. Anything not in force is always labelled as such in the sentence.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from client_intel.db import Dataset, Row
from client_intel.evidence import (
    NO_DATA,
    OK,
    PARTIAL,
    FactBuilder,
    ToolResult,
    cite,
    fmt_date,
    fmt_eur,
    fmt_num,
    fmt_pct,
    pct_change,
)

NOTICE_RISK_DAYS = 30  # notice deadline passed or this close counts as a risk
RENEWAL_HORIZON_DAYS = 180  # a contract ending this soon should have a renewal opportunity
CLOSED_STAGES = {"Closed Won", "Closed Lost"}
_TYPE_LABEL = {"cross_sell": "cross-sell", "new_business": "new business"}


def _k(contract: Row) -> str:
    return cite("contracts", contract["contract_id"])


def _split(ds: Dataset, client_id: str) -> tuple[list[Row], list[Row], list[Row]]:
    """Return (in force, signed and ended, pending signature), each oldest first."""
    rows = sorted(ds.for_client("contracts", client_id), key=lambda c: c["start_date"])
    in_force = [
        c
        for c in rows
        if c["status"] == "active" and c["start_date"] <= ds.as_of <= c["end_date"]
    ]
    pending = [c for c in rows if c["status"] == "pending_signature"]
    ended = [c for c in rows if c["status"] != "pending_signature" and c["end_date"] < ds.as_of]
    return in_force, sorted(ended, key=lambda c: c["end_date"]), pending


def _product_label(ds: Dataset, product_id: str) -> str:
    product = ds.products.get(product_id)
    return f"{product['product_name']} ({product_id})" if product else product_id


def _lines(ds: Dataset, contract: Row) -> list[dict[str, Any]]:
    return [
        {
            "line_id": line["line_id"],
            "product_id": line["product_id"],
            "annual_fee_eur": line["annual_fee_eur"],
            "included_units_monthly": line["included_units_monthly"],
            "overage_rate_eur_per_unit": line["overage_rate_eur_per_unit"],
        }
        for line in ds.lines_for(contract["contract_id"])
    ]


def _contract_data(ds: Dataset, contract: Row) -> dict[str, Any]:
    keys = [
        "contract_id",
        "contract_type",
        "status",
        "start_date",
        "end_date",
        "term_months",
        "auto_renew",
        "notice_period_days",
        "arr_eur",
        "signed_date",
    ]
    out: dict[str, Any] = {k: contract.get(k) for k in keys}
    out["lines"] = _lines(ds, contract)
    return out


def _term(contract: Row) -> str:
    return (
        f"{fmt_date(contract['start_date'])} to {fmt_date(contract['end_date'])} "
        f"({fmt_num(contract['term_months'])} months)"
    )


def _line_facts(fb: FactBuilder, ds: Dataset, contract: Row, label: str) -> None:
    for line in ds.lines_for(contract["contract_id"]):
        product = ds.products.get(line["product_id"])
        unit = f" (unit: {product['usage_unit']})" if product and product.get("usage_unit") else ""
        fact = fb.data(
            _k(contract),
            f"{label} {contract['contract_id']} includes "
            f"{_product_label(ds, line['product_id'])} for an annual fee of "
            f"{fmt_eur(line['annual_fee_eur'])} with an included monthly volume of "
            f"{fmt_num(line['included_units_monthly'])}{unit}.",
            topic="contract_lines",
        )
        if product:
            # The product name and unit come from the catalogue row, not the contract.
            fact.rows.append(cite("product", line["product_id"]))


def _change_fact(
    fb: FactBuilder, new: Row, new_label: str, old: Row, old_label: str, topic: str
) -> dict[str, Any]:
    pct = pct_change(new["arr_eur"], old["arr_eur"])
    data = {
        "contract_id": new["contract_id"],
        "arr_eur": new["arr_eur"],
        "compared_to_contract_id": old["contract_id"],
        "compared_to_arr_eur": old["arr_eur"],
        "pct": pct,
    }
    if pct is None:
        fb.gap(
            "change_not_computable",
            f"The annual value change between contracts {old['contract_id']} and "
            f"{new['contract_id']} cannot be computed because a value is missing or zero.",
            [_k(old), _k(new)],
        )
        return data
    fb.calc(
        f"The annual value of {new_label} {new['contract_id']} is {fmt_eur(new['arr_eur'])}, "
        f"a change of {fmt_pct(pct)} versus {fmt_eur(old['arr_eur'])} on {old_label} "
        f"{old['contract_id']}.",
        [_k(new), _k(old)],
        topic=topic,
        signal="risk" if pct < 0 else "neutral",
    )
    return data


def get_contract_status(ds: Dataset, client_id: str) -> ToolResult:
    """The contract in force as of ds.as_of, or the labelled alternatives if there is none."""
    fb = FactBuilder("contract_status")
    as_of: date = ds.as_of
    in_force_all, ended, pending = _split(ds, client_id)
    data: dict[str, Any] = {
        "client_id": client_id,
        "as_of": as_of,
        "in_force_contract_id": None,
        "in_force": None,
        "last_expired_contract_id": None,
        "last_expired": None,
        "previous_contract_id": None,
        "pending": [_contract_data(ds, c) for c in pending],
        "pending_contract_ids": [c["contract_id"] for c in pending],
        "held_product_ids": [],
        "held_products_source": "none",
        "held_from_expired": False,
        "arr_change": None,
        "term_change": None,
        "pending_vs_reference": [],
        "contract_count": len(ds.for_client("contracts", client_id)),
    }
    if not (in_force_all or ended or pending):
        fb.gap("no_contracts", f"No contract of any status is on file for client {client_id}.")
        return fb.result(NO_DATA, data)

    current = in_force_all[-1] if in_force_all else None
    last_expired = ended[-1] if ended else None
    if len(in_force_all) > 1:
        ids = ", ".join(c["contract_id"] for c in in_force_all)
        fb.gap(
            "multiple_contracts_in_force",
            f"More than one contract is in force as of {fmt_date(as_of)} ({ids}); the "
            f"latest, {current['contract_id']}, is reported.",
            [_k(c) for c in in_force_all],
        )

    if current is not None:
        _in_force_facts(fb, ds, current, data)
        earlier = [c for c in ended if c["end_date"] < current["start_date"]]
        if earlier:
            previous = earlier[-1]
            data["previous_contract_id"] = previous["contract_id"]
            data["arr_change"] = _change_fact(
                fb, current, "contract", previous, "the previous contract", "contract_change"
            )
            _term_change(fb, current, previous, data)
        else:
            fb.gap(
                "no_previous_contract",
                f"Contract {current['contract_id']} is the only signed contract on file, so "
                "the change in annual value at the last renewal cannot be computed.",
                [_k(current)],
            )
    else:
        fb.gap(
            "no_contract_in_force",
            f"No contract is in force for client {client_id} as of {fmt_date(as_of)}.",
            [_k(c) for c in [last_expired, *pending] if c is not None],
        )

    if last_expired is not None:
        data["last_expired_contract_id"] = last_expired["contract_id"]
        data["last_expired"] = _contract_data(ds, last_expired)
    if current is None and last_expired is not None:
        days_since = (as_of - last_expired["end_date"]).days
        data["last_expired"]["days_since_end"] = days_since
        fb.calc(
            f"Expired contract {last_expired['contract_id']} is not in force: it ran "
            f"{_term(last_expired)} with an annual value of {fmt_eur(last_expired['arr_eur'])} "
            f"and ended {fmt_num(days_since)} days before {fmt_date(as_of)}.",
            [_k(last_expired)],
            topic="contract",
            signal="risk",
        )
        _line_facts(fb, ds, last_expired, "Expired contract")
        data["held_product_ids"] = [x["product_id"] for x in data["last_expired"]["lines"]]
        data["held_products_source"] = "last_expired"
        data["held_from_expired"] = True

    reference = current or last_expired
    for draft in pending:
        signed = (
            f"signed {fmt_date(draft['signed_date'])}"
            if draft.get("signed_date")
            else "no signed date"
        )
        fb.data(
            _k(draft),
            f"Contract {draft['contract_id']} is pending signature and not in force: it is "
            f"drafted to run {_term(draft)} with an annual value of "
            f"{fmt_eur(draft['arr_eur'])} and has {signed}.",
            topic="pending_contract",
            signal="risk" if current is None else "neutral",
        )
        _line_facts(fb, ds, draft, "Pending (unsigned) contract")
        if reference is not None:
            old_label = "the contract in force" if current else "the expired contract"
            data["pending_vs_reference"].append(
                _change_fact(
                    fb, draft, "pending (unsigned) contract", reference, old_label,
                    "pending_contract",
                )
            )

    return fb.result(OK if current is not None else PARTIAL, data)


def _in_force_facts(fb: FactBuilder, ds: Dataset, current: Row, data: dict[str, Any]) -> None:
    as_of = ds.as_of
    cid = current["contract_id"]
    ref = _k(current)
    fb.data(
        ref,
        f"Contract {cid} is in force as of {fmt_date(as_of)}: it runs {_term(current)} with "
        f"an annual value of {fmt_eur(current['arr_eur'])}.",
        topic="contract",
    )
    auto = current.get("auto_renew") == "Y"
    notice_days = current.get("notice_period_days")
    renew_text = (
        "renews automatically for the same term unless notice is given"
        if auto
        else "does not renew automatically and ends on its end date unless a renewal is signed"
    )
    fb.data(
        ref,
        f"Contract {cid} {renew_text}; its notice period is {fmt_num(notice_days)} days "
        "before the end date.",
        topic="renewal",
    )

    days_to_end = (current["end_date"] - as_of).days
    fb.calc(
        f"Contract {cid} ends on {fmt_date(current['end_date'])}, {fmt_num(days_to_end)} days "
        f"after {fmt_date(as_of)}.",
        [ref],
        topic="renewal",
        signal="risk" if days_to_end <= NOTICE_RISK_DAYS else "neutral",
    )

    info = _contract_data(ds, current)
    info["days_to_end"] = days_to_end
    info["notice_deadline"] = None
    info["days_to_notice_deadline"] = None
    info["notice_deadline_passed"] = None
    if notice_days is None:
        fb.gap(
            "no_notice_period",
            f"Contract {cid} has no notice period recorded, so no notice deadline is known.",
            [ref],
        )
    else:
        deadline = current["end_date"] - timedelta(days=notice_days)
        days_to_notice = (deadline - as_of).days
        passed = days_to_notice < 0
        basis = (
            f"end date {fmt_date(current['end_date'])} minus {fmt_num(notice_days)} days"
        )
        if passed:
            text = (
                f"The notice deadline for contract {cid} was {fmt_date(deadline)} ({basis}) "
                f"and passed {fmt_num(-days_to_notice)} days before {fmt_date(as_of)}."
            )
        else:
            text = (
                f"The notice deadline for contract {cid} is {fmt_date(deadline)} ({basis}), "
                f"{fmt_num(days_to_notice)} days after {fmt_date(as_of)}."
            )
        fb.calc(
            text,
            [ref],
            topic="renewal",
            signal="risk" if days_to_notice <= NOTICE_RISK_DAYS else "neutral",
        )
        info["notice_deadline"] = deadline
        info["days_to_notice_deadline"] = days_to_notice
        info["notice_deadline_passed"] = passed

    _line_facts(fb, ds, current, "Contract")
    data["in_force_contract_id"] = cid
    data["in_force"] = info
    data["held_product_ids"] = [x["product_id"] for x in info["lines"]]
    data["held_products_source"] = "in_force"


def _term_change(fb: FactBuilder, current: Row, previous: Row, data: dict[str, Any]) -> None:
    new, old = current.get("term_months"), previous.get("term_months")
    if new is None or old is None or new == old:
        return
    data["term_change"] = {"previous_term_months": old, "current_term_months": new}
    fb.calc(
        f"The term changed from {fmt_num(old)} months on the previous contract "
        f"{previous['contract_id']} to {fmt_num(new)} months on contract "
        f"{current['contract_id']}.",
        [_k(previous), _k(current)],
        topic="contract_change",
        signal="risk" if new < old else "neutral",
    )


# --- opportunities ------------------------------------------------------------


def _o(opp: Row) -> str:
    return cite("opp", opp["opp_id"])


def _opp_data(opp: Row, is_open: bool) -> dict[str, Any]:
    keys = [
        "opp_id",
        "opp_type",
        "product_id",
        "stage",
        "amount_eur",
        "created_date",
        "expected_close_date",
        "owner",
        "next_step",
    ]
    out: dict[str, Any] = {k: opp.get(k) for k in keys}
    out["is_open"] = is_open
    return out


def _contract_reflecting(ds: Dataset, opp: Row) -> Row | None:
    """A signed contract carrying the product, agreed on or after the deal was opened."""
    for contract in ds.for_client("contracts", opp["client_id"]):
        if contract["status"] == "pending_signature":
            continue
        agreed = contract.get("signed_date") or contract["start_date"]
        products = {x["product_id"] for x in ds.lines_for(contract["contract_id"])}
        if opp["product_id"] in products and agreed >= opp["created_date"]:
            return contract
    return None


def _latest_with_product(ds: Dataset, opp: Row) -> Row | None:
    rows = [
        c
        for c in ds.for_client("contracts", opp["client_id"])
        if c["status"] != "pending_signature"
        and opp["product_id"] in {x["product_id"] for x in ds.lines_for(c["contract_id"])}
    ]
    return max(rows, key=lambda c: c["start_date"]) if rows else None


def get_opportunities(ds: Dataset, client_id: str) -> ToolResult:
    """Open and closed CRM opportunities, and where they disagree with the contracts."""
    fb = FactBuilder("opportunities")
    as_of = ds.as_of
    opps = sorted(ds.for_client("opportunities", client_id), key=lambda o: o["opp_id"])
    open_opps = [o for o in opps if o["stage"] not in CLOSED_STAGES]
    closed_opps = [o for o in opps if o["stage"] in CLOSED_STAGES]
    in_force_all, ended, _pending = _split(ds, client_id)
    current = in_force_all[-1] if in_force_all else None
    reference = current or (ended[-1] if ended else None)

    lost = [o for o in closed_opps if o["stage"] == "Closed Lost" and o["product_id"]]

    data: dict[str, Any] = {
        "client_id": client_id,
        "as_of": as_of,
        "open": [_opp_data(o, True) for o in open_opps],
        "closed": [_opp_data(o, False) for o in closed_opps],
        "open_product_ids": sorted({o["product_id"] for o in open_opps if o["product_id"]}),
        "open_products": [
            {"product_id": o["product_id"], "opp_id": o["opp_id"], "stage": o["stage"]}
            for o in open_opps
            if o["product_id"]
        ],
        "lost_product_ids": sorted({o["product_id"] for o in lost}),
        "lost_products": [
            {"product_id": o["product_id"], "opp_id": o["opp_id"], "reason": o["next_step"]}
            for o in lost
        ],
        "renewal_vs_contract": [],
        "stale_opp_ids": [],
        "won_not_contracted": [],
        "no_renewal_opportunity": False,
    }

    for opp in opps:
        is_open = opp["stage"] not in CLOSED_STAGES
        kind = _TYPE_LABEL.get(opp["opp_type"], opp["opp_type"])
        product = f" for {_product_label(ds, opp['product_id'])}" if opp["product_id"] else ""
        state = f"an open {kind} opportunity{product} at stage" if is_open else (
            f"a closed {kind} opportunity{product} with stage"
        )
        fb.data(
            _o(opp),
            f"Opportunity {opp['opp_id']} is {state} {opp['stage']}, with an amount of "
            f"{fmt_eur(opp['amount_eur'])}, created {fmt_date(opp['created_date'])} and "
            f"expected close date {fmt_date(opp['expected_close_date'])}.",
            topic="open_opportunity" if is_open else "closed_opportunity",
        )
        if opp.get("next_step"):
            fb.reported(
                _o(opp),
                f'The CRM next step recorded on opportunity {opp["opp_id"]} reads: '
                f'"{opp["next_step"]}".',
                topic="open_opportunity" if is_open else "closed_opportunity",
            )

    for opp in open_opps:
        if opp["opp_type"] == "renewal" and reference is not None:
            pct = pct_change(opp["amount_eur"], reference["arr_eur"])
            label = "contract in force" if current else "expired contract (none is in force)"
            entry = {
                "opp_id": opp["opp_id"],
                "amount_eur": opp["amount_eur"],
                "contract_id": reference["contract_id"],
                "contract_in_force": current is not None,
                "arr_eur": reference["arr_eur"],
                "pct": pct,
            }
            data["renewal_vs_contract"].append(entry)
            if pct is not None:
                fb.calc(
                    f"The amount of renewal opportunity {opp['opp_id']}, "
                    f"{fmt_eur(opp['amount_eur'])}, is {fmt_pct(pct)} versus the annual value "
                    f"of {fmt_eur(reference['arr_eur'])} on {label} "
                    f"{reference['contract_id']}.",
                    [_o(opp), _k(reference)],
                    topic="renewal",
                    signal="risk" if pct < 0 else "opportunity" if pct > 0 else "neutral",
                )
        close = opp.get("expected_close_date")
        if close is not None and close < as_of:
            data["stale_opp_ids"].append(opp["opp_id"])
            fb.calc(
                f"Open opportunity {opp['opp_id']} is stale: its expected close date "
                f"{fmt_date(close)} is {fmt_num((as_of - close).days)} days before "
                f"{fmt_date(as_of)} and its stage is still {opp['stage']}.",
                [_o(opp)],
                topic="stale_opportunity",
                signal="risk",
            )

    for opp in closed_opps:
        if opp["stage"] != "Closed Won" or not opp["product_id"]:
            continue
        if _contract_reflecting(ds, opp) is not None:
            continue
        latest = _latest_with_product(ds, opp)
        kind = _TYPE_LABEL.get(opp["opp_type"], opp["opp_type"])
        head = (
            f"Opportunity {opp['opp_id']} ({kind} for {opp['product_id']}, "
            f"{fmt_eur(opp['amount_eur'])}) is Closed Won, but "
        )
        if latest is None:
            text = head + f"{opp['product_id']} is not on any signed contract for the client."
            rows = [_o(opp)]
        else:
            agreed = latest.get("signed_date") or latest["start_date"]
            text = head + (
                f"no contract including {opp['product_id']} was signed on or after the "
                f"opportunity was created on {fmt_date(opp['created_date'])}; the latest "
                f"contract with that product, {latest['contract_id']}, dates from "
                f"{fmt_date(agreed)}."
            )
            rows = [_o(opp), _k(latest)]
        data["won_not_contracted"].append(
            {
                "opp_id": opp["opp_id"],
                "product_id": opp["product_id"],
                "amount_eur": opp["amount_eur"],
                "latest_contract_id": latest["contract_id"] if latest else None,
            }
        )
        fb.gap("won_not_contracted", text, rows)
        fb.calc(text, rows, topic="source_conflict", signal="risk")

    if current is not None:
        days_to_end = (current["end_date"] - as_of).days
        has_renewal = any(o["opp_type"] == "renewal" for o in open_opps)
        if 0 <= days_to_end <= RENEWAL_HORIZON_DAYS and not has_renewal:
            data["no_renewal_opportunity"] = True
            text = (
                f"Contract {current['contract_id']} ends on {fmt_date(current['end_date'])}, "
                f"{fmt_num(days_to_end)} days after {fmt_date(as_of)}, and no open renewal "
                "opportunity exists in the CRM."
            )
            fb.gap("no_renewal_opportunity", text, [_k(current)])
            fb.calc(text, [_k(current)], topic="renewal", signal="risk")

    if not opps:
        fb.gap("no_opportunities", f"No CRM opportunity is on file for client {client_id}.")
        return fb.result(NO_DATA, data)
    return fb.result(OK, data)
