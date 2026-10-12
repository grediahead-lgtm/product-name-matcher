import argparse
import csv
import json
import sys

from .match import match_lists


def read_names(path, column):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f, delimiter=_delim(path)))
    if not rows or column not in rows[0]:
        raise ValueError("column %r not found in %s" % (column, path))
    return [r[column].strip() for r in rows if r[column].strip()]


def _delim(path):
    with open(path, encoding="utf-8-sig") as f:
        head = f.readline()
    return ";" if head.count(";") > head.count(",") else ","


def main(argv=None):
    ap = argparse.ArgumentParser(prog="name_matcher", description="Match product names between two CSV lists.")
    ap.add_argument("a_csv")
    ap.add_argument("b_csv")
    ap.add_argument("--col-a", default="name")
    ap.add_argument("--col-b", default="name")
    ap.add_argument("--out", default="matches.csv")
    ap.add_argument("--hi", type=float, default=0.8, help="score for a confident match")
    ap.add_argument("--lo", type=float, default=0.55, help="below this a pair is not even suggested")
    args = ap.parse_args(argv)
    rows, left = match_lists(read_names(args.a_csv, args.col_a), read_names(args.b_csv, args.col_b), args.hi, args.lo)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["status", "score", "a", "b"])
        w.writeheader()
        for r in rows:
            w.writerow({k: ("'" + str(v) if k in ("a", "b") and str(v).startswith(("=", "+", "-", "@")) else v) for k, v in r.items()})
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print(json.dumps({"counts": counts, "only_in_b": len(left)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
