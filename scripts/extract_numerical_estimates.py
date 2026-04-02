"""
extract_numerical_estimates.py

Identifies numerical estimates in Neo-Assyrian letter translations and
extracts them with surrounding context.

Detects:
  - Arabic numerals (with optional thousands commas and ORACC bracket notation):
      300, 1,500, [1],500, 2,[4]50
  - Written cardinal and ordinal numbers:
      one, two, half, quarter, 1st, 2nd, 3rd, 4th ...
  - Fractions written as words: "half a shekel", "one third"

Output columns:
  text_id, project, match_text, numeric_value, context

Usage:
  python scripts/extract_numerical_estimates.py
  python scripts/extract_numerical_estimates.py --input processed_data/letters_translations.csv
  python scripts/extract_numerical_estimates.py --output processed_data/numerical_estimates.csv
"""

import argparse
import re
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT   = Path(__file__).parent.parent
PROCESSED_DIR  = PROJECT_ROOT / "processed_data" / "neo_assyrian"
DEFAULT_INPUT  = PROCESSED_DIR / "letters_translations.csv"
DEFAULT_OUTPUT = PROCESSED_DIR / "numerical_estimates.csv"

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

# Arabic numeral, possibly with thousands commas and ORACC square-bracket
# reconstruction marks, e.g.:  300  |  1,500  |  [1],500  |  2,[4]50
_NUM_ARABIC = r"\[?\d+\]?(?:,\[?\d+\]?)*"

# Written cardinals and fractions
_WRITTEN_CARDINALS = (
    r"\b(?:"
    r"one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|"
    r"twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|"
    r"hundred|thousand|"
    r"half|quarter|third"
    r")\b"
)

# Ordinal suffixes: 1st, 2nd, 3rd, 4th, ...
_ORDINAL = r"\b\d+(?:st|nd|rd|th)\b"

# Combined: any of the above
ESTIMATE_PATTERN = re.compile(
    rf"(?:{_NUM_ARABIC}|{_WRITTEN_CARDINALS}|{_ORDINAL})",
    re.IGNORECASE,
)

# Words that look numeric but are almost certainly not quantity estimates
# in these texts (common false positives)
_STOPWORDS = {
    "one",          # "one day" can be real, but keep it — filtered below if needed
}

# Context window (characters on each side of the match)
CONTEXT_WINDOW = 60


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_num(raw: str) -> str | None:
    """
    Strip ORACC bracket notation and return a plain numeric string,
    or None if the raw value contains no digits (i.e. it's a written number).
    """
    digits_only = re.sub(r"[\[\],]", "", raw)
    return digits_only if digits_only.isdigit() else None


def extract_estimates(text: str) -> list[dict]:
    """
    Find all numerical estimates in *text* and return a list of dicts:
        match_text   – the matched token as it appears in the source
        numeric_value – integer value if parseable, else None (for written numbers)
        context      – surrounding text window
    """
    results = []
    for m in ESTIMATE_PATTERN.finditer(text):
        start, end = m.start(), m.end()
        match_text = m.group()

        # Parse numeric value where possible
        cleaned = _clean_num(match_text)
        if cleaned:
            numeric_value = int(cleaned)
        else:
            numeric_value = None  # written word — leave as NaN in the DataFrame

        # Grab surrounding context
        ctx_start = max(0, start - CONTEXT_WINDOW)
        ctx_end   = min(len(text), end + CONTEXT_WINDOW)
        context   = text[ctx_start:ctx_end].replace("\n", " ").strip()

        results.append({
            "match_text":    match_text,
            "numeric_value": numeric_value,
            "context":       context,
        })
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Extract numerical estimates from translated Neo-Assyrian letters."
    )
    parser.add_argument("--input",  default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    input_path  = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        print("Run parse_translations.py first.")
        return

    print(f"Loading translations from {input_path} ...")
    df = pd.read_csv(input_path, encoding="utf-8-sig")
    print(f"  {len(df):,} letters loaded.")

    rows = []
    for _, letter in df.iterrows():
        translation = letter.get("translation", "")
        if not isinstance(translation, str) or not translation.strip():
            continue
        estimates = extract_estimates(translation)
        for est in estimates:
            rows.append({
                "text_id":       letter["text_id"],
                "project":       letter["project"],
                "match_text":    est["match_text"],
                "numeric_value": est["numeric_value"],
                "context":       est["context"],
            })

    if not rows:
        print("No numerical estimates found.")
        return

    result_df = pd.DataFrame(rows)
    result_df["numeric_value"] = pd.to_numeric(
        result_df["numeric_value"], errors="coerce"
    ).astype("Int64")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(output_path, index=False, encoding="utf-8-sig")

    n_letters   = result_df["text_id"].nunique()
    n_estimates = len(result_df)
    n_arabic    = result_df["numeric_value"].notna().sum()
    n_written   = result_df["numeric_value"].isna().sum()

    print(f"\nResults:")
    print(f"  {n_estimates:,} numerical estimates across {n_letters:,} letters")
    print(f"  {n_arabic:,} Arabic-numeral matches  |  {n_written:,} written-word matches")
    print(f"  Saved -> {output_path}")

    # Preview
    print("\nSample estimates (first 10 rows):")
    print(result_df[["text_id", "match_text", "numeric_value", "context"]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
