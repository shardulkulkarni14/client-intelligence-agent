"""White-space: products a client does not hold, with the evidence for and against each.

The tool gathers evidence and ranks; it does not decide what to pitch. Peer counts come
from contracts in force, demand signals from tickets and the CRM, and blockers from lost
opportunities and from prerequisites that exist only in the product description text.
"""

from __future__ import annotations

import re
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
)

TOOL = "whitespace"

# Below this many peers a share is anecdote, not evidence: no percentage, and a gap.
MIN_PEERS = 3

# Ranking score. Deliberately simple and additive so a reviewer can recompute it by hand.
# It orders candidates only; it is never printed as a figure in a fact.
SCORE_PEER_SHARE = 3.0  # times the share of peers holding the product (0..1)
SCORE_PEER_SHARE_SMALL_GROUP = 1.0  # same, when the peer group is below MIN_PEERS
SCORE_SEGMENT_FIT = 2.0  # product is typically sold to the client's segment
SCORE_BOUGHT_WITH = 1.0  # per held product linked by often_bought_with (either direction)
SCORE_BOUGHT_WITH_CAP = 2.0
SCORE_TICKET_SIGNAL = 2.0  # the client raised a ticket about a product it does not hold
SCORE_OPEN_OPP = 3.0  # an opportunity for it is already open
SCORE_LOST_OPP = -4.0  # it was pitched before and lost
SCORE_PREREQ_BLOCKER = -3.0  # it needs a product the client lacks

TOP_N = 3  # at most this many candidates are marked "opportunity"
MIN_SCORE_FOR_OPPORTUNITY = 3.0

# Wording that marks a prerequisite sentence in a product description.
_PREREQ_RE = re.compile(r"\b(requires?|required|prerequisites?|depends on|needs)\b", re.I)
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")

_CLOSED_LOST = "Closed Lost"
_CLOSED_WON = "Closed Won"


def _held_products(ds: Dataset, client_id: str) -> tuple[set[str], list[Row], bool]:
    """Products held, the contracts they come from, and whether that base is expired.

    In force is Dataset.contract_in_force, the one definition every tool shares. With
    nothing in force, fall back to the most recently ended contract so the caller can
    still describe the base.
    """
    contracts = ds.for_client("contracts", client_id)
    current = ds.contract_in_force(client_id)
    expired = False
    base = [current] if current is not None else []
    if not base:
        ended = [c for c in contracts if c["end_date"] is not None and c["end_date"] < ds.as_of]
        ended = [c for c in ended if c["status"] != "pending_signature"]
        base = sorted(ended, key=lambda c: c["end_date"], reverse=True)[:1]
        expired = bool(base)
    held = {
        line["product_id"] for c in base for line in ds.lines_for(c["contract_id"])
    }
    return held, base, expired


def _prerequisites(ds: Dataset, product: Row) -> list[str]:
    """Product IDs the description says this product requires (free text only)."""
    description = product.get("description") or ""
    found: list[str] = []
    for sentence in _SENTENCE_RE.split(description):
        if not _PREREQ_RE.search(sentence):
            continue
        lowered = sentence.lower()
        for other_id, other in ds.products.items():
            if other_id == product["product_id"] or other_id in found:
                continue
            name = (other.get("product_name") or "").lower()
            if other_id.lower() in lowered or (name and name in lowered):
                found.append(other_id)
    return found


def _name(ds: Dataset, product_id: str) -> str:
    product = ds.products.get(product_id)
    name = product.get("product_name") if product else None
    return f"{name} ({product_id})" if name else product_id


def get_whitespace(ds: Dataset, client_id: str) -> ToolResult:
    fb = FactBuilder(TOOL)
    client = ds.clients.get(client_id)
    if client is None:
        fb.gap("unknown_client", f"No client with ID {client_id} in the data.")
        return fb.result(NO_DATA)

    segment = client.get("segment")
    held, base_contracts, base_expired = _held_products(ds, client_id)
    base_rows = [cite("contracts", c["contract_id"]) for c in base_contracts]
    status = OK

    if not base_contracts:
        status = PARTIAL
        fb.gap(
            "no_contract",
            "No contract in force and no ended contract found, so held products are unknown; "
            "every catalogue product is listed as not held.",
        )
    elif base_expired:
        status = PARTIAL
        contract = base_contracts[0]
        fb.gap(
            "holding_based_on_expired_contract",
            f"No contract is in force at {fmt_date(ds.as_of)}; held products are taken from "
            f"{contract['contract_id']}, which ended {fmt_date(contract['end_date'])}.",
            base_rows,
        )

    # Peers: the other clients in the same segment, holdings by the same rule.
    peer_ids = sorted(
        cid for cid, c in ds.clients.items() if cid != client_id and c.get("segment") == segment
    )
    peer_held: dict[str, set[str]] = {}
    peers_on_expired: list[str] = []
    for peer_id in peer_ids:
        products, _, peer_expired = _held_products(ds, peer_id)
        peer_held[peer_id] = products
        if peer_expired:
            peers_on_expired.append(peer_id)
    n_peers = len(peer_ids)
    peer_rows = [cite("client", p) for p in peer_ids]

    # Base: what the client holds today.
    for product_id in sorted(held):
        fb.data(
            cite("product", product_id),
            f"Client holds {_name(ds, product_id)}"
            + (" (based on an expired contract)." if base_expired else "."),
            topic="held_products",
            signal="neutral",
        ).rows = [cite("product", product_id), *base_rows]

    missing = sorted(p for p in ds.products if p not in held)
    fb.calc(
        f"Client holds {fmt_num(len(held))} of {fmt_num(len(ds.products))} catalogue products; "
        f"{fmt_num(len(missing))} are not held.",
        rows=base_rows + [cite("product", p) for p in sorted(held)],
        topic="whitespace_summary",
        signal="neutral",
    )
    fb.calc(
        f"Peer group: {fmt_num(n_peers)} other "
        f"{'client' if n_peers == 1 else 'clients'} in segment {segment}.",
        rows=peer_rows,
        topic="peer_group",
        signal="neutral",
    )
    if n_peers < MIN_PEERS:
        fb.gap(
            "small_peer_group",
            f"Only {fmt_num(n_peers)} other {'client' if n_peers == 1 else 'clients'} in "
            f"segment {segment}; peer adoption is a weak comparison and no percentage is given.",
            peer_rows,
        )
    if peers_on_expired:
        fb.gap(
            "peer_holding_based_on_expired_contract",
            "Peer holdings for " + ", ".join(peers_on_expired) + " are taken from an expired "
            "contract because none is in force.",
            [cite("client", p) for p in peers_on_expired],
        )

    tickets = ds.for_client("tickets", client_id)
    opps = ds.for_client("opportunities", client_id)
    candidates: list[dict[str, Any]] = []

    for product_id in missing:
        product = ds.products[product_id]
        holders = [p for p in peer_ids if product_id in peer_held[p]]
        share = len(holders) / n_peers if n_peers else None
        fits = segment in (product.get("typical_segments") or [])
        linked = sorted(
            h
            for h in held
            if h in (product.get("often_bought_with") or [])
            or product_id in (ds.products.get(h, {}).get("often_bought_with") or [])
        )
        prereqs = _prerequisites(ds, product)
        prereq_missing = [p for p in prereqs if p not in held]
        prod_tickets = sorted(
            (t for t in tickets if t.get("product_id") == product_id),
            key=lambda t: t["ticket_id"],
        )
        prod_opps = [o for o in opps if o.get("product_id") == product_id]
        lost = [o for o in prod_opps if o["stage"] == _CLOSED_LOST]
        won = [o for o in prod_opps if o["stage"] == _CLOSED_WON]
        open_opps = [o for o in prod_opps if o["stage"] not in (_CLOSED_LOST, _CLOSED_WON)]

        score = 0.0
        if share is not None:
            weight = SCORE_PEER_SHARE if n_peers >= MIN_PEERS else SCORE_PEER_SHARE_SMALL_GROUP
            score += weight * share
        if fits:
            score += SCORE_SEGMENT_FIT
        score += min(SCORE_BOUGHT_WITH * len(linked), SCORE_BOUGHT_WITH_CAP)
        if prod_tickets:
            score += SCORE_TICKET_SIGNAL
        if open_opps:
            score += SCORE_OPEN_OPP
        if lost:
            score += SCORE_LOST_OPP
        if prereq_missing:
            score += SCORE_PREREQ_BLOCKER

        candidates.append(
            {
                "product_id": product_id,
                "product_name": product.get("product_name"),
                "list_price_from_eur": product.get("list_price_from_eur"),
                "peers_holding": len(holders),
                "peer_count": n_peers,
                "peer_holders": holders,
                "peer_share_pct": None if share is None else share * 100.0,
                "segment_fit": fits,
                "bought_with_held": linked,
                "prerequisites": prereqs,
                "prerequisites_missing": prereq_missing,
                "tickets": [t["ticket_id"] for t in prod_tickets],
                "open_opps": [o["opp_id"] for o in open_opps],
                "lost_opps": [o["opp_id"] for o in lost],
                "won_opps": [o["opp_id"] for o in won],
                "score": round(score, 3),
                "_tickets": prod_tickets,
                "_open": open_opps,
                "_lost": lost,
                "_won": won,
            }
        )

    # Rank: score first, product ID to keep ties stable.
    candidates.sort(key=lambda c: (-c["score"], c["product_id"]))
    marked = 0
    for rank, cand in enumerate(candidates, start=1):
        cand["rank"] = rank
        if cand["lost_opps"]:
            cand["signal"] = "risk"
        elif (
            marked < TOP_N
            and not cand["prerequisites_missing"]
            and cand["score"] >= MIN_SCORE_FOR_OPPORTUNITY
        ):
            cand["signal"] = "opportunity"
            marked += 1
        else:
            cand["signal"] = "neutral"

    for cand in candidates:
        product_id = cand["product_id"]
        parts: list[str] = []
        if n_peers == 0:
            parts.append("no segment peers to compare with")
        else:
            peer_text = (
                f"held by {fmt_num(cand['peers_holding'])} of {fmt_num(n_peers)} segment "
                f"{'peer' if n_peers == 1 else 'peers'}"
            )
            if n_peers >= MIN_PEERS:
                peer_text += f" ({fmt_pct(cand['peer_share_pct'], signed=False)})"
            else:
                peer_text += " (peer group too small for a reliable comparison)"
            parts.append(peer_text)
        parts.append(
            f"typically sold to {segment}"
            if cand["segment_fit"]
            else f"not typically sold to {segment}"
        )
        if cand["bought_with_held"]:
            parts.append("often bought with held " + ", ".join(cand["bought_with_held"]))
        if cand["prerequisites_missing"]:
            parts.append(
                "blocker: its description says it requires "
                + ", ".join(_name(ds, p) for p in cand["prerequisites_missing"])
                + ", which the client does not hold"
            )
        elif cand["prerequisites"]:
            parts.append(
                "prerequisite " + ", ".join(cand["prerequisites"]) + " is already held"
            )
        if cand["tickets"]:
            n = len(cand["tickets"])
            parts.append(
                f"{fmt_num(n)} support {'ticket' if n == 1 else 'tickets'} from the client "
                "about it"
            )
        if cand["open_opps"]:
            parts.append("open opportunity " + ", ".join(cand["open_opps"]))
        if cand["lost_opps"]:
            parts.append("pitched before and lost (" + ", ".join(cand["lost_opps"]) + ")")
        if cand["won_opps"]:
            parts.append(
                "CRM shows a won opportunity ("
                + ", ".join(cand["won_opps"])
                + ") but it is not on the contract"
            )
        parts.append(f"indicative entry price {fmt_eur(cand['list_price_from_eur'])} per year")

        fact = fb.data(
            cite("product", product_id),
            f"Not held: {_name(ds, product_id)}; " + "; ".join(parts) + ".",
            topic="whitespace",
            signal=cand["signal"],
        )
        fact.rows = (
            [cite("product", product_id)]
            + [cite("client", p) for p in cand["peer_holders"]]
            + [cite("ticket", t) for t in cand["tickets"]]
            + [cite("opp", o) for o in cand["open_opps"] + cand["lost_opps"] + cand["won_opps"]]
        )

        for ticket in cand.pop("_tickets"):
            fb.reported(
                cite("ticket", ticket["ticket_id"]),
                f"Ticket {ticket['ticket_id']} opened {fmt_date(ticket['opened_date'])} about "
                f"{product_id}, which the client does not hold; subject as reported: "
                f"\"{ticket.get('subject') or ''}\".",
                topic="whitespace_demand",
                signal="opportunity",
            )
        for opp in cand.pop("_open"):
            fb.reported(
                cite("opp", opp["opp_id"]),
                f"Open opportunity {opp['opp_id']} for {product_id}: stage {opp['stage']}, "
                f"{fmt_eur(opp.get('amount_eur'))}, expected close "
                f"{fmt_date(opp.get('expected_close_date'))}; next step as reported: "
                f"\"{opp.get('next_step') or 'none recorded'}\".",
                topic="whitespace_demand",
                signal="opportunity",
            )
        for opp in cand.pop("_lost"):
            fb.reported(
                cite("opp", opp["opp_id"]),
                f"{product_id} was pitched before and lost: opportunity {opp['opp_id']} "
                f"({fmt_eur(opp.get('amount_eur'))}, expected close "
                f"{fmt_date(opp.get('expected_close_date'))}); reason as reported: "
                f"\"{opp.get('next_step') or 'none recorded'}\".",
                topic="whitespace_lost",
                signal="risk",
            )
        for opp in cand.pop("_won"):
            fb.reported(
                cite("opp", opp["opp_id"]),
                f"Opportunity {opp['opp_id']} for {product_id} is Closed Won in the CRM "
                f"(\"{opp.get('next_step') or 'none recorded'}\") but {product_id} is not on "
                "the contract used for holdings.",
                topic="whitespace_conflict",
                signal="neutral",
            )
            fb.gap(
                "won_opp_not_on_contract",
                f"{opp['opp_id']} is Closed Won for {product_id} but the product is not on the "
                "contract; CRM and contract data disagree.",
                [cite("opp", opp["opp_id"])],
            )

    if not missing:
        fb.calc(
            "Client already holds every catalogue product; there is no white space.",
            rows=[cite("product", p) for p in sorted(held)],
            topic="whitespace_summary",
            signal="neutral",
        )

    return fb.result(
        status,
        data={
            "client_id": client_id,
            "segment": segment,
            "held_products": sorted(held),
            "held_from_contracts": [c["contract_id"] for c in base_contracts],
            "held_based_on_expired_contract": base_expired,
            "peer_ids": peer_ids,
            "peer_count": n_peers,
            "small_peer_group": n_peers < MIN_PEERS,
            "candidates": candidates,
            "top_candidates": [c["product_id"] for c in candidates if c["signal"] == "opportunity"],
            "score_weights": {
                "peer_share": SCORE_PEER_SHARE,
                "peer_share_small_group": SCORE_PEER_SHARE_SMALL_GROUP,
                "segment_fit": SCORE_SEGMENT_FIT,
                "bought_with": SCORE_BOUGHT_WITH,
                "bought_with_cap": SCORE_BOUGHT_WITH_CAP,
                "ticket_signal": SCORE_TICKET_SIGNAL,
                "open_opp": SCORE_OPEN_OPP,
                "lost_opp": SCORE_LOST_OPP,
                "prereq_blocker": SCORE_PREREQ_BLOCKER,
            },
        },
    )
