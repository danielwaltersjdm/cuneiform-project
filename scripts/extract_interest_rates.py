"""
extract_interest_rates.py

Extracts interest rate data from APIS papyri translations.

Standard Ptolemaic/Roman Egypt formats:
  - 1 drachma per mina per month  = 1%/month = 12%/year
  - 2 drachmas per mina per month = 2%/month = 24%/year
  - 1 obol per mina per month     = 1/6 %/month = 2%/year
  - X% per month                  = X*12 %/year

Output: processed_data/papyri/interest_rates.csv

Usage:
  python scripts/extract_interest_rates.py
"""

import re
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
PROC_DIR     = PROJECT_ROOT / "processed_data" / "papyri"

# ---------------------------------------------------------------------------
# Rate patterns: (compiled_re, converter_fn, type_label)
# converter returns annual percent given the match object
# ---------------------------------------------------------------------------
RATE_PATTERNS = [
    (
        re.compile(r"(\d+(?:\s+\d+/\d+)?)\s+drachm\w+\s+(?:per|a|the|for\s+each)\s+mina\s+(?:per|a|each)\s+month", re.IGNORECASE),
        lambda m: _parse_num(m.group(1)) * 12,
        "dr/mina/month",
    ),
    (
        re.compile(r"(\d+(?:\s+\d+/\d+)?)\s+obol\w*\s+(?:per|a|the)\s+mina\s+(?:per|a|each)\s+month", re.IGNORECASE),
        lambda m: _parse_num(m.group(1)) / 6 * 12,
        "obol/mina/month",
    ),
    (
        re.compile(r"(\d+(?:\.\d+)?)\s*%\s*(?:a|per)\s*month", re.IGNORECASE),
        lambda m: float(m.group(1)) * 12,
        "pct/month",
    ),
    (
        re.compile(r"(\d+(?:\.\d+)?)\s*%\s*(?:per\s+)?(?:year|annum|annually)", re.IGNORECASE),
        lambda m: float(m.group(1)),
        "pct/year",
    ),
    (
        re.compile(r"(\d+(?:\.\d+)?)\s+drachm\w+\s+(?:the|per|a)\s+mina\b", re.IGNORECASE),
        lambda m: float(m.group(1)) * 12,
        "dr/mina",
    ),
]


def _parse_num(s: str) -> float:
    from fractions import Fraction
    total = 0.0
    for part in s.strip().split():
        if "/" in part:
            try:
                total += float(Fraction(part))
            except Exception:
                pass
        else:
            try:
                total += float(part)
            except Exception:
                pass
    return total


def extract_rates(df: pd.DataFrame) -> pd.DataFrame:
    interest_docs = df[
        df["translation_text"].str.contains(r"interest", case=False, na=False)
    ].copy()

    records = []
    for _, row in interest_docs.iterrows():
        text = str(row["translation_text"])
        for ctx_m in re.finditer(r".{0,150}interest.{0,250}", text, re.IGNORECASE | re.DOTALL):
            ctx = ctx_m.group().replace("\n", " ")
            for pattern, converter, ptype in RATE_PATTERNS:
                rm = pattern.search(ctx)
                if rm:
                    try:
                        annual_pct = converter(rm)
                        records.append({
                            "doc_id":         row["doc_id"],
                            "institution":    row["institution"],
                            "date_text":      str(row.get("date_text", ""))[:40],
                            "date_year":      row.get("date_year_approx"),
                            "rate_type":      ptype,
                            "rate_annual_pct": round(annual_pct, 2),
                            "rate_raw":       rm.group(0).strip()[:50],
                            "context":        ctx[:250],
                        })
                    except Exception:
                        pass
                    break  # one rate per context window

    out = pd.DataFrame(records).drop_duplicates(subset=["doc_id", "rate_annual_pct"])
    return out.sort_values("date_year")


def main():
    print("Loading APIS combined CSV...")
    df = pd.read_csv(PROC_DIR / "apis_combined.csv")
    translated = df[df["has_translation"] == True]
    print(f"  {len(translated):,} translated documents")

    print("Extracting interest rates...")
    rates = extract_rates(translated)
    print(f"  {len(rates)} observations extracted")
    print()

    if not rates.empty:
        print("Annual rate distribution:")
        print(rates["rate_annual_pct"].describe().round(1).to_string())
        print()
        print("All extracted rates:")
        for _, r in rates.iterrows():
            print(f"  {str(r['date_text']):35s}  {r['rate_annual_pct']:5.1f}%/yr  "
                  f"[{r['institution']}] {r['doc_id']}")

    out = PROC_DIR / "interest_rates.csv"
    rates.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"\n-> {out}")


if __name__ == "__main__":
    main()
