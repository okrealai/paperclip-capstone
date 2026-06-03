#!/usr/bin/env python3
"""
Paperclip eval runner / scorer.

Loads the cases in ``eval/cases/*.json``, scores each one, and writes a results
summary to ``eval/results/latest.json``. It implements the evaluation-driven
ladder the capstone describes:

    1. deterministic code checks   (default; no dependencies, no secrets)
    2. LLM judge for subjective    (optional, --judge; applies eval/judge/rubric.md)
    3. human review                (out of scope for a script — the unscored set)

Each case declares an ``expected`` block. The runner needs an observed
``actual`` block to score against. ``actual`` may come from:
  * the case file itself (``"actual": {...}``), or
  * a fixtures file (``--fixtures eval/fixtures.json``) keyed by ``case_id``.

A case with no recorded ``actual`` is reported **UNSCORED** — it is never
counted as a pass. The committed cases ship as unscored templates on purpose;
``eval/fixtures.json`` carries illustrative recorded outputs so the runner is
demonstrably functional. See eval/README.md § Provenance.

Usage:
    python eval/run.py                               # score; templates -> UNSCORED
    python eval/run.py --fixtures eval/fixtures.json  # score against recorded outputs
    python eval/run.py --fixtures eval/fixtures.json --judge   # + LLM judge subjective cases
"""
from __future__ import annotations
import argparse, glob, json, os, re, sys
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------------------- comparators
def _writes_pattern(expected: str) -> str:
    """Turn an expected write path into a regex (NNN/date/`*` are wildcards)."""
    rx = re.escape(expected)
    rx = (rx.replace("NNN", r"\d+").replace("YYYY", r"\d{4}")
            .replace("MM", r"\d{2}").replace("DD", r"\d{2}").replace(r"\*", r".*"))
    return f"^{rx}$"


def _check_writes(exp: list, act) -> tuple[bool, str]:
    if not isinstance(act, list):
        return False, f"writes: expected a list, got {type(act).__name__}"
    if not exp:
        return (len(act) == 0, "writes: expected none" + ("" if not act else f", got {act}"))
    if len(act) != len(exp):
        return False, f"writes: expected {len(exp)} item(s), got {len(act)}"
    for pat, got in zip(exp, act):
        if not re.match(_writes_pattern(pat), str(got)):
            return False, f"writes: '{got}' does not match pattern '{pat}'"
    return True, "writes: all match"


def _check_key(key: str, exp, actual: dict) -> tuple[bool, str]:
    """Generic, schema-agnostic check for one expected key."""
    if key == "routed_to":
        allowed = str(exp).split("_or_")
        got = actual.get("routed_to")
        return (got in allowed, f"routed_to: got '{got}', allowed {allowed}")
    if key == "writes":
        return _check_writes(exp, actual.get("writes", []))
    if key.endswith("_within_seconds"):
        got = actual.get(key, actual.get(key.replace("_within_seconds", "_seconds")))
        if got is None:
            return False, f"{key}: no observed value in actual"
        return (got <= exp, f"{key}: observed {got} vs limit {exp}")
    if isinstance(exp, bool):
        got = actual.get(key)
        return (got == exp, f"{key}: expected {exp}, got {got}")
    # counts, verdict strings, verdict_pre_fix/post_fix, etc. -> direct equality
    got = actual.get(key)
    return (got == exp, f"{key}: expected {exp!r}, got {got!r}")


def score_case(case: dict, actual) -> dict:
    cid = case.get("case_id", "?")
    expected = case.get("expected", {}) or {}
    if not actual:
        return {"case_id": cid, "verdict": "UNSCORED",
                "reason": "no recorded `actual` output (template case)", "checks": []}
    checks, ok_all = [], True
    for key, exp in expected.items():
        ok, detail = _check_key(key, exp, actual)
        checks.append({"key": key, "ok": ok, "detail": detail})
        ok_all = ok_all and ok
    return {"case_id": cid, "verdict": "PASS" if ok_all else "FAIL",
            "reason": "all expected fields satisfied" if ok_all
                      else "; ".join(c["detail"] for c in checks if not c["ok"]),
            "checks": checks}


# ---------------------------------------------------------------- LLM judge (optional)
def judge_case(case: dict, actual: dict, rubric: str) -> dict | None:
    """Apply eval/judge/rubric.md via an LLM. Returns None if unavailable."""
    try:
        import anthropic  # lazy: not a hard dependency
    except ImportError:
        return None
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    client = anthropic.Anthropic()
    prompt = (f"{rubric}\n\n---\nCASE INPUT: {case.get('input')}\n"
              f"EXPECTED: {json.dumps(case.get('expected'))}\n"
              f"ACTUAL: {json.dumps(actual)}\n\nReturn `PASS` or `FAIL` then a one-sentence reason.")
    msg = client.messages.create(model="claude-haiku-4-5", max_tokens=120,
                                 messages=[{"role": "user", "content": prompt}])
    text = msg.content[0].text.strip()
    verdict = "PASS" if text.upper().startswith("PASS") else "FAIL"
    return {"verdict": verdict, "explanation": text}


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description="Paperclip eval runner / scorer")
    ap.add_argument("--cases", default=str(EVAL_DIR / "cases"))
    ap.add_argument("--fixtures", default=None, help="JSON file: {case_id: actual} recorded outputs")
    ap.add_argument("--judge", action="store_true", help="also run the LLM judge on scorable cases")
    ap.add_argument("--out", default=str(EVAL_DIR / "results" / "latest.json"))
    args = ap.parse_args()

    fixtures = {}
    if args.fixtures and Path(args.fixtures).exists():
        fixtures = json.loads(Path(args.fixtures).read_text())
    rubric = (EVAL_DIR / "judge" / "rubric.md").read_text() if args.judge else ""

    results, tally = [], {"PASS": 0, "FAIL": 0, "UNSCORED": 0}
    for fp in sorted(glob.glob(os.path.join(args.cases, "*.json"))):
        case = json.loads(Path(fp).read_text())
        actual = case.get("actual") or fixtures.get(case.get("case_id"))
        r = score_case(case, actual)
        if args.judge and r["verdict"] != "UNSCORED":
            j = judge_case(case, actual, rubric)
            if j:
                r["judge"] = j
        tally[r["verdict"]] += 1
        results.append(r)
        print(f"  {r['case_id']:8} {r['verdict']:9} {r['reason']}")

    total = sum(tally.values())
    scored = tally["PASS"] + tally["FAIL"]
    summary = {"total": total, **tally,
               "pass_rate": round(tally["PASS"] / scored, 3) if scored else None}
    out = {"summary": summary, "results": results}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2) + "\n")

    print(f"\n  {total} cases — PASS {tally['PASS']} / FAIL {tally['FAIL']} / "
          f"UNSCORED {tally['UNSCORED']}"
          + (f"  (pass rate {summary['pass_rate']:.0%} of scored)" if scored else ""))
    print(f"  wrote {args.out}")
    # exit non-zero only on a real FAIL (UNSCORED templates are expected)
    return 1 if tally["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
