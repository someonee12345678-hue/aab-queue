"""AAB-S4-MVP-T1T2-20261016 candidate implementation. Standard library only."""


def normalize_label(text):
    """T1: lower-case, keep ASCII a-z/0-9, collapse other runs to '-', trim, default 'item'."""
    if not isinstance(text, str):
        raise TypeError("normalize_label expects str, got %s" % type(text).__name__)
    out = []
    pending_sep = False
    for ch in text.lower():
        if ('a' <= ch <= 'z') or ('0' <= ch <= '9'):
            if pending_sep and out:
                out.append('-')
            pending_sep = False
            out.append(ch)
        else:
            pending_sep = True
    return ''.join(out) or 'item'


def unique_labels(values):
    """T2: normalise each value via T1, preserving order, de-duplicating with lowest free -N suffix."""
    if not isinstance(values, list):
        raise TypeError("unique_labels expects list, got %s" % type(values).__name__)
    for item in values:
        if not isinstance(item, str):
            raise TypeError("unique_labels items must be str, got %s" % type(item).__name__)
    used = set()
    result = []
    for item in values:
        base = normalize_label(item)
        label = base
        n = 2
        while label in used:
            label = "%s-%d" % (base, n)
            n += 1
        used.add(label)
        result.append(label)
    return result
