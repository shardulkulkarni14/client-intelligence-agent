"""Client lookup: turn what the rep typed into one client ID, or stop.

Resolution never guesses. Each tier is tried in order of strictness and the first
tier that matches anything decides: one match resolves, several are returned as
candidates for the rep to choose from.
"""

from __future__ import annotations

import re

from client_intel.db import Dataset, Row
from client_intel.evidence import NO_DATA, OK, PARTIAL, FactBuilder, ToolResult, cite, fmt_date

_ID = re.compile(r"^C\d+$", re.IGNORECASE)
# An ID standing on its own inside a longer request: "Client C001", "c001 please".
_ID_INSIDE = re.compile(r"(?<![A-Za-z0-9])C\d+(?![A-Za-z0-9])", re.IGNORECASE)
# "&" and "and" are dropped so "Velmont Casino and Sport" equals "Velmont Casino & Sport".
_IGNORED_WORDS = {"and"}


def _words(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", text.casefold()) if w not in _IGNORED_WORDS]


MIN_PARTIAL = 3  # "x" is inside one name by accident; that is not a request for it


def _part_of(typed: str, name_word: str) -> bool:
    return typed == name_word or (len(typed) >= MIN_PARTIAL and typed in name_word)


def _candidate(row: Row) -> dict[str, str]:
    return {"client_id": row["client_id"], "client_name": row["client_name"]}


def _match(ds: Dataset, query: str) -> tuple[str, list[Row]]:
    """Return (match type, matching clients). An empty list means not found."""
    clients = list(ds.clients.values())

    if _ID.match(query):
        hit = ds.clients.get(query.upper())
        return "id", [hit] if hit else []

    exact = [c for c in clients if c["client_name"] == query]
    if exact:
        return "exact", exact

    q_words = _words(query)
    if not q_words:
        return "none", []
    same = [c for c in clients if _words(c["client_name"]) == q_words]
    if same:
        return "case_insensitive", same

    q_set = set(q_words)
    names = {c["client_id"]: _words(c["client_name"]) for c in clients}

    # A valid client ID inside the request: "Client C001", "client c001 please".
    ids = sorted({m.upper() for m in _ID_INSIDE.findall(query)} & set(ds.clients))
    if ids:
        by_id = [ds.clients[i] for i in ids]
        # A different client named in full next to the ID is a contradiction, not a hit.
        named = [
            c
            for c in clients
            if set(names[c["client_id"]]) <= q_set and c["client_id"] not in ids
        ]
        return "id_in_query", by_id + named

    # Loosest tier, also used to list every plausible candidate when a tier is ambiguous.
    loose = [
        c for c in clients
        if all(any(_part_of(w, n) for n in names[c["client_id"]]) for w in q_words)
    ]

    # Every word typed is a whole word of the name: "Brenmoor League".
    whole = [c for c in clients if q_set <= set(names[c["client_id"]])]
    if len(whole) == 1:
        # One typed word can be a whole word of one name and the start of a word in
        # another ("Athletic" FC, "Athletics" Federation); that is not a unique match.
        if len(q_words) == 1 and len(loose) > 1:
            return "substring", loose
        return "words", whole
    if whole:
        return "words", loose

    # The name is contained in what was typed: "Halden Bet plc".
    inside = [c for c in clients if set(names[c["client_id"]]) <= q_set]
    if inside:
        return "name_in_query", inside

    # Partial words: "Marrow", "Sport" (which also matches "Sports").
    return "substring", loose


def resolve_client(ds: Dataset, query: str) -> ToolResult:
    """Resolve an ID or a typed name to exactly one client, or report why not."""
    fb = FactBuilder("resolve_client")
    cleaned = (query or "").strip()
    match_type, hits = _match(ds, cleaned) if cleaned else ("none", [])
    candidates = [_candidate(c) for c in hits]
    data = {
        "query": query,
        "status": "not_found",
        "client_id": None,
        "match_type": match_type,
        "candidates": candidates,
    }

    if not hits:
        fb.gap("client_not_found", f'No client matches "{cleaned}" by ID or by name.')
        return fb.result(NO_DATA, data)

    if len(hits) > 1:
        listing = ", ".join(f"{c['client_name']} ({c['client_id']})" for c in candidates)
        fb.gap(
            "ambiguous_client",
            f'"{cleaned}" matches several clients and none was chosen: {listing}.',
            [cite("client", c["client_id"]) for c in candidates],
        )
        data["status"] = "ambiguous"
        return fb.result(PARTIAL, data)

    client = hits[0]
    data["status"] = "resolved"
    data["client_id"] = client["client_id"]
    fb.data(
        cite("client", client["client_id"]),
        f'The request "{cleaned}" refers to client {client["client_name"]} '
        f"({client['client_id']}).",
        topic="client",
    )
    return fb.result(OK, data)


def get_client_profile(ds: Dataset, client_id: str) -> ToolResult:
    """Segment, country, owner, tier and customer-since date for one client."""
    fb = FactBuilder("get_client_profile")
    client = ds.clients.get(client_id)
    if client is None:
        fb.gap("client_not_found", f"No client has the ID {client_id}.")
        return fb.result(NO_DATA, {"client_id": client_id})

    ref = cite("client", client_id)
    fields = ["client_name", "segment", "country", "account_owner", "tier", "customer_since"]
    missing = [f for f in fields if client.get(f) is None]

    def shown(name: str) -> str:
        return str(client[name]) if client.get(name) is not None else "not recorded"

    since = (
        fmt_date(client["customer_since"]) if client.get("customer_since") else "not recorded"
    )
    fb.data(
        ref,
        f"{shown('client_name')} ({client_id}) is a client in the {shown('segment')} segment, "
        f"based in country {shown('country')}, with tier {shown('tier')}, account owner "
        f"{shown('account_owner')} and customer since {since}.",
        topic="profile",
    )
    if missing:
        fb.gap(
            "blank_field",
            f"Client {client_id} has no value recorded for: {', '.join(missing)}.",
            [ref],
        )
    data = {
        "client_id": client_id,
        "client_name": client.get("client_name"),
        "segment": client.get("segment"),
        "country": client.get("country"),
        "account_owner": client.get("account_owner"),
        "tier": client.get("tier"),
        "customer_since": client.get("customer_since"),
        "missing_fields": missing,
    }
    return fb.result(PARTIAL if missing else OK, data)
