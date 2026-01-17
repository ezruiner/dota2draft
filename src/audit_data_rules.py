#!/usr/bin/env python3
"""Audit heroes data vs rules.

Outputs:
- unique roles/tags with counts
- roles/tags referenced by roles.json / synergies.json
- dead rule keys (where at least one side tag/role never appears in heroes)

Run:
  python src/audit_data_rules.py
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERO_DIR = ROOT / "data" / "heroes"
ROLES_FILE = ROOT / "data" / "roles.json"
SYNERGIES_FILE = ROOT / "data" / "synergies.json"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def split_pairs(d: dict) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for k in d.keys():
        if "+" not in k:
            continue
        a, b = k.split("+", 1)
        out.append((a, b))
    return out


def main() -> int:
    roles = Counter()
    tags = Counter()

    hero_files = sorted(HERO_DIR.glob("*.json"))
    for path in hero_files:
        hero = load_json(path)
        for r in hero.get("roles", []):
            roles[r] += 1
        for t in hero.get("tags", []):
            tags[t] += 1

    roles_rules = load_json(ROLES_FILE)
    role_synergies = roles_rules.get("role_synergies", {})
    role_conflicts = roles_rules.get("role_conflicts", {})

    syn_rules = load_json(SYNERGIES_FILE)
    tag_synergies = syn_rules.get("tag_synergies", {})
    tag_counters = syn_rules.get("tag_counters", {})
    phase_bias = syn_rules.get("phase_bias", {})

    roles_in_rules = set([a for a, b in split_pairs(role_synergies) + split_pairs(role_conflicts)] + [b for a, b in split_pairs(role_synergies) + split_pairs(role_conflicts)])
    tags_in_rules = set([a for a, b in split_pairs(tag_synergies) + split_pairs(tag_counters)] + [b for a, b in split_pairs(tag_synergies) + split_pairs(tag_counters)])
    tags_in_phase_bias = set()
    for phase_map in phase_bias.values():
        if isinstance(phase_map, dict):
            tags_in_phase_bias.update(phase_map.keys())

    roles_set = set(roles.keys())
    tags_set = set(tags.keys())

    dead_role_keys = []
    for k in list(role_synergies.keys()) + list(role_conflicts.keys()):
        if "+" not in k:
            continue
        a, b = k.split("+", 1)
        if a not in roles_set or b not in roles_set:
            dead_role_keys.append(k)

    dead_tag_synergy_keys = []
    for k in tag_synergies.keys():
        if "+" not in k:
            continue
        a, b = k.split("+", 1)
        if a not in tags_set or b not in tags_set:
            dead_tag_synergy_keys.append(k)

    dead_tag_counter_keys = []
    for k in tag_counters.keys():
        if "+" not in k:
            continue
        a, b = k.split("+", 1)
        if a not in tags_set or b not in tags_set:
            dead_tag_counter_keys.append(k)

    print(f"heroes_files\t{len(hero_files)}")
    print(f"roles_unique\t{len(roles)}")
    print(f"tags_unique\t{len(tags)}")

    print("\n== ROLES (count) ==")
    for r, c in roles.most_common():
        print(f"{r}\t{c}")

    print("\n== TAGS top-200 (count) ==")
    for t, c in tags.most_common(200):
        print(f"{t}\t{c}")

    print("\n== RULES ROLES referenced ==")
    for r in sorted(roles_in_rules):
        print(r)

    print("\n== RULES TAGS referenced ==")
    for t in sorted(tags_in_rules):
        print(t)

    if tags_in_phase_bias:
        print("\n== PHASE_BIAS tags referenced ==")
        for t in sorted(tags_in_phase_bias):
            print(t)

    print("\n== DEAD role keys (do not match any hero role) ==")
    for k in dead_role_keys:
        print(k)

    print("\n== DEAD tag_synergies keys (missing tag in heroes) ==")
    for k in dead_tag_synergy_keys:
        print(k)

    print("\n== DEAD tag_counters keys (missing tag in heroes) ==")
    for k in dead_tag_counter_keys:
        print(k)

    missing_roles = sorted(roles_in_rules - roles_set)
    missing_tags = sorted(tags_in_rules - tags_set)
    print("\n== MISSING roles (in rules, not in heroes) ==")
    for r in missing_roles:
        print(r)

    print("\n== MISSING tags (in rules, not in heroes) ==")
    for t in missing_tags:
        print(t)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
