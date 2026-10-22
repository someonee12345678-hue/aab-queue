"""AAB-001 v0.4 synthetic ticket queue (T7 parse_ticket; T8 pick_ticket added in wake 2). Stdlib only."""
import re

_TICKET_ID_RE = re.compile(r"[A-Z][A-Z0-9_-]{0,23}", re.ASCII)
_PRIORITIES = ("HIGH", "MEDIUM", "LOW")


def parse_ticket(text):
    """T7: parse 'ID|PRIORITY' into (id, priority). Pure; no side effects."""
    if not isinstance(text, str):
        raise TypeError("ticket text must be str")
    parts = text.split("|")
    if len(parts) != 2:
        raise ValueError("ticket must contain exactly one '|' separator")
    ticket_id, priority = parts[0].strip(), parts[1].strip()
    if not ticket_id.isascii() or _TICKET_ID_RE.fullmatch(ticket_id) is None:
        raise ValueError(f"invalid ticket id: {ticket_id!r}")
    if priority not in _PRIORITIES:
        raise ValueError(f"invalid priority: {priority!r}")
    return ticket_id, priority


_RANK = {p: i for i, p in enumerate(_PRIORITIES)}


def pick_ticket(lines):
    """T8: id of the highest-priority ticket (HIGH > MEDIUM > LOW; first wins ties); None if empty.

    Every member is validated with parse_ticket. Inputs are not mutated.
    """
    if not isinstance(lines, list):
        raise TypeError("lines must be a list")
    best_id, best_rank = None, None
    for raw in lines:
        ticket_id, priority = parse_ticket(raw)
        rank = _RANK[priority]
        if best_rank is None or rank < best_rank:
            best_id, best_rank = ticket_id, rank
    return best_id
