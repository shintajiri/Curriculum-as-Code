#!/usr/bin/env python3
"""Validate a Curriculum-as-Code YAML file: the formal checks a machine can do.

Checks
  E1  every DP referenced in courses[].dp exists in dp_definitions
  E2  every goal referenced in courses[].assessments[].goals exists in that course's goals
  E3  course IDs are unique
  E4  dp level words are among programme.dp_levels (when dp_levels is given)
  E5  assessment weights of a course sum to 100 (tolerance 0.01)
  E6  required keys are present (id, name, goals, dp, assessments)
  W1  a DP defined but referenced by no course
  W2  a goal defined but measured by no assessment

What it does NOT check: whether goals and assessments correspond educationally, whether DP levels are
placed sensibly. Those are human judgements.

Usage : python3 tools/validate.py curriculum.yaml
Exit  : 0 = no errors (warnings may be printed), 1 = errors found, 2 = cannot read file
"""
import sys
from collections import Counter

try:
    import yaml
except ImportError:
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


def load(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate(doc):
    errors, warnings = [], []
    dp_defs = doc.get("dp_definitions") or {}
    courses = doc.get("courses") or []
    levels = (doc.get("programme") or {}).get("dp_levels")
    if not dp_defs:
        errors.append("E6 dp_definitions is missing or empty")
    if not courses:
        errors.append("E6 courses is missing or empty")

    ids = Counter(c.get("id") for c in courses)
    for cid, n in ids.items():
        if n > 1:
            errors.append(f"E3 duplicate course id: {cid} ({n} times)")

    dp_used, goal_used = set(), {}
    for c in courses:
        cid = c.get("id", "<no id>")
        for key in ("id", "name", "goals", "dp", "assessments"):
            if key not in c:
                errors.append(f"E6 {cid}: missing key '{key}'")
        goals = c.get("goals") or {}
        for dp, level in (c.get("dp") or {}).items():
            dp_used.add(dp)
            if dp not in dp_defs:
                errors.append(f"E1 {cid}: dp '{dp}' is not defined in dp_definitions")
            if levels and level not in levels:
                errors.append(f"E4 {cid}: dp level '{level}' for {dp} is not in programme.dp_levels {levels}")
        total = 0.0
        measured = set()
        for i, a in enumerate(c.get("assessments") or [], 1):
            total += float(a.get("weight", 0) or 0)
            for g in a.get("goals") or []:
                measured.add(g)
                if g not in goals:
                    errors.append(f"E2 {cid}: assessment #{i} ({a.get('method')}) refers to goal '{g}' which the course does not define")
        if c.get("assessments") and abs(total - 100.0) > 0.01:
            errors.append(f"E5 {cid}: assessment weights sum to {total:g}, not 100")
        for g in goals:
            if g not in measured:
                warnings.append(f"W2 {cid}: goal {g} is measured by no assessment")
    for dp in dp_defs:
        if dp not in dp_used:
            warnings.append(f"W1 {dp} is defined but referenced by no course")
    return errors, warnings


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    try:
        doc = load(sys.argv[1])
    except Exception as e:
        print(f"cannot read {sys.argv[1]}: {e}", file=sys.stderr)
        sys.exit(2)
    errors, warnings = validate(doc)
    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    n_c = len(doc.get("courses") or [])
    n_dp = len(doc.get("dp_definitions") or {})
    print(f"checked {n_c} courses, {n_dp} DPs: {len(errors)} error(s), {len(warnings)} warning(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
