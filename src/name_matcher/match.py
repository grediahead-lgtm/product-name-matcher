"""Match products of list A to list B by name similarity. No guessing in silence:
every pair gets a score and a status (match / review / no_match)."""
import re

from difflib import SequenceMatcher

_TRANSLIT = str.maketrans({"і": "и", "ї": "и", "є": "е", "ґ": "г", "ё": "е", "ы": "и", "э": "е"})
_SIZE = re.compile(r"(\d+(?:[.,]\d+)?)\s*[xхXХ×*]\s*(\d+(?:[.,]\d+)?)(?:\s*[xхXХ×*]\s*(\d+(?:[.,]\d+)?))?")
STOP = {"для", "та", "и", "і", "з", "с", "the", "for", "and", "of", "шт", "см", "cm", "мм", "mm"}


def tokens(name):
    t = re.sub(r"['’ʼ`]", "", (name or "").lower()).translate(_TRANSLIT)
    sizes = ["x".join(p.replace(",", ".") for p in m.groups() if p) for m in _SIZE.finditer(t)]
    t = _SIZE.sub(" ", t)
    words = [w for w in re.findall(r"[0-9a-zа-я]+", t) if w not in STOP]
    return words, sizes


def score(a, b):
    """0..1. A size mismatch caps the score below the default "match" level, so such pairs are always sent to review."""
    wa, sa = tokens(a)
    wb, sb = tokens(b)
    if not wa or not wb:
        return 0.0
    ja = len(set(wa) & set(wb)) / len(set(wa) | set(wb))
    seq = SequenceMatcher(None, " ".join(sorted(wa)), " ".join(sorted(wb))).ratio()
    base = 0.6 * ja + 0.4 * seq
    if sa and sb and set(sa) != set(sb):
        base *= 0.65
    return round(base, 3)


def match_lists(list_a, list_b, hi=0.8, lo=0.55):
    """list_a, list_b: lists of names. Each B item can be used once (best score first).
    Returns rows {a, b, score, status}. A without a good partner: b='' and no_match."""
    pairs = []
    for i, a in enumerate(list_a):
        for j, b in enumerate(list_b):
            s = score(a, b)
            if s >= lo:
                pairs.append((s, i, j))
    pairs.sort(key=lambda p: (-p[0], p[1], p[2]))
    used_a, used_b, found = set(), set(), {}
    for s, i, j in pairs:
        if i in used_a or j in used_b:
            continue
        used_a.add(i)
        used_b.add(j)
        found[i] = (j, s)
    rows = []
    for i, a in enumerate(list_a):
        if i in found:
            j, s = found[i]
            rows.append({"a": a, "b": list_b[j], "score": s, "status": "match" if s >= hi else "review"})
        else:
            rows.append({"a": a, "b": "", "score": 0.0, "status": "no_match"})
    unmatched_b = [b for j, b in enumerate(list_b) if j not in used_b]
    return rows, unmatched_b
