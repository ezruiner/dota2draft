#!/usr/bin/env python3
"""Generate tag synergy/counter rules from existing hero data.

Uses:
- explicit_synergies (positive): derive unordered tag pairs that correlate with good teammates
- explicit_counters (negative on victim): derive directional pairs (enemy_tag + our_tag) that correlate with good counters

This is a helper for curating `data/synergies.json`.

Run:
  python src/generate_synergy_rules.py
  python src/generate_synergy_rules.py --top 40 --min 12
  python src/generate_synergy_rules.py --write data/synergies.generated.json
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERO_DIR = ROOT / "data" / "heroes"


def load_heroes() -> dict[str, dict]:
    heroes: dict[str, dict] = {}
    for path in sorted(HERO_DIR.glob("*.json")):
        h = json.loads(path.read_text(encoding="utf-8"))
        heroes[h["name"]] = h
    return heroes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=30)
    ap.add_argument("--min", type=int, default=10, help="min samples per pair")
    ap.add_argument("--write", type=str, default="", help="write generated json to this path")
    args = ap.parse_args()

    heroes = load_heroes()

    tag_freq = Counter()
    for h in heroes.values():
        for t in h.get("tags", []):
            tag_freq[t] += 1

    # pair -> (sum, count)
    syn_sum = defaultdict(float)
    syn_cnt = Counter()

    # directional pair (enemy_tag, our_tag) -> (sum_abs, count)
    ctr_sum = defaultdict(float)
    ctr_cnt = Counter()

    for h in heroes.values():
        h_tags = list(h.get("tags", []))

        # Synergies: unordered tag pairs
        for ally_name, s in (h.get("explicit_synergies") or {}).items():
            if s <= 0:
                continue
            ally = heroes.get(ally_name)
            if not ally:
                continue
            a_tags = list(ally.get("tags", []))
            for t1 in h_tags:
                for t2 in a_tags:
                    if t1 == t2:
                        continue
                    a, b = sorted((t1, t2))
                    key = f"{a}+{b}"
                    syn_sum[key] += float(s)
                    syn_cnt[key] += 1

        # Counters: victim has explicit_counters (negative), counter hero is the listed enemy
        for counter_name, c in (h.get("explicit_counters") or {}).items():
            if c >= 0:
                continue
            counter_hero = heroes.get(counter_name)
            if not counter_hero:
                continue
            our_tags = list(counter_hero.get("tags", []))
            strength = abs(float(c))
            for enemy_tag in h_tags:
                for our_tag in our_tags:
                    if enemy_tag == our_tag:
                        continue
                    key = f"{enemy_tag}+{our_tag}"
                    ctr_sum[key] += strength
                    ctr_cnt[key] += 1

    # Filter + normalize
    def to_weight(avg: float) -> int:
        # avg is in "percentage points"; scale to integer rule weight
        w = round(avg * 2.0)
        if w < 4:
            w = 4
        if w > 24:
            w = 24
        return int(w)

    syn_items = []
    for k, cnt in syn_cnt.items():
        if cnt < args.min:
            continue
        avg = syn_sum[k] / cnt
        syn_items.append((avg, cnt, k))
    syn_items.sort(reverse=True)

    ctr_items = []
    for k, cnt in ctr_cnt.items():
        if cnt < args.min:
            continue
        avg = ctr_sum[k] / cnt
        ctr_items.append((avg, cnt, k))
    ctr_items.sort(reverse=True)

    print(f"heroes\t{len(heroes)}")
    print(f"tags_unique\t{len(tag_freq)}")

    print("\n== Tags (top 60) ==")
    for t, c in tag_freq.most_common(60):
        print(f"{t}\t{c}")

    print(f"\n== Inferred tag_synergies (top {args.top}, min={args.min}) ==")
    for avg, cnt, k in syn_items[: args.top]:
        print(f"{k}\tavg={avg:.2f}\tsamples={cnt}\tweight={to_weight(avg)}")

    print(f"\n== Inferred tag_counters (enemy_tag+our_tag) (top {args.top}, min={args.min}) ==")
    for avg, cnt, k in ctr_items[: args.top]:
        print(f"{k}\tavg={avg:.2f}\tsamples={cnt}\tweight={to_weight(avg)}")

    if args.write:
        out = {
            "tag_synergies": {k: to_weight(avg) for avg, cnt, k in syn_items[: args.top]},
            "tag_counters": {k: to_weight(avg) for avg, cnt, k in ctr_items[: args.top]},
        }
        out_path = (ROOT / args.write).resolve() if not Path(args.write).is_absolute() else Path(args.write)
        out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nWrote: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
