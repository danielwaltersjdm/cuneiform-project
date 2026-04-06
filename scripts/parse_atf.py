"""
parse_atf.py

Parses the CDLI Old Assyrian ATF file into a structured CSV.

Each row is one tablet with:
  cdli_id, publication, authors, excavation_no, genre, language, period,
  translation_status, has_atf, atf_line_count, has_translation,
  transliteration_text, translation_text

Usage:
  python scripts/parse_atf.py
  python scripts/parse_atf.py --input raw_data/kanesh/cdli_old_assyrian_atf.txt
  python scripts/parse_atf.py --output processed_data/kanesh/kanesh_tablets.csv
"""

import argparse
import re
from pathlib import Path

import pandas as pd
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent
ATF_FILE     = PROJECT_ROOT / "raw_data" / "kanesh" / "cdli_old_assyrian_atf.txt"
OUTPUT_FILE  = PROJECT_ROOT / "processed_data" / "kanesh" / "kanesh_tablets.csv"

# ---------------------------------------------------------------------------
# ATF parsing
# ---------------------------------------------------------------------------

# Matches transliteration lines: "1." or "1'." or "1')" at start
TRANSLIT_LINE = re.compile(r"^\d+['.]")
# Matches dollar lines (editorial annotations) — skip these
DOLLAR_LINE   = re.compile(r"^\$")
# Matches section markers (@tablet, @obverse, etc.) — skip
SECTION_LINE  = re.compile(r"^@")
# Matches comment/control lines (#atf, #note, etc.) — skip unless #tr.en
COMMENT_LINE  = re.compile(r"^#")


def parse_metadata(meta_text: str) -> dict:
    """Parse the metadata block (key: value pairs) into a dict."""
    fields = {
        "publication":        "",
        "authors":            "",
        "excavation_no":      "",
        "genre":              "",
        "language":           "",
        "period":             "",
        "translation_status": "",
        "cdli_id":            "",
    }
    field_map = {
        "Primary publication": "publication",
        "Author(s)":           "authors",
        "Excavation no.":      "excavation_no",
        "Genre":               "genre",
        "Language":            "language",
        "Period":              "period",
        "Translation":         "translation_status",
        "CDLI no.":            "cdli_id",
    }
    for line in meta_text.splitlines():
        for key, col in field_map.items():
            if line.startswith(key + ":"):
                val = line[len(key) + 1:].strip()
                fields[col] = val
                break
    return fields


def parse_atf_body(atf_text: str) -> dict:
    """
    Parse the ATF body (everything after 'Transliteration:').
    Returns: has_atf, atf_line_count, has_translation, transliteration_text, translation_text
    """
    lines = atf_text.splitlines()

    has_atf = False
    translit_lines = []
    translation_lines = []

    for line in lines:
        line = line.rstrip()

        # ATF identification line: &PXXXXXX = ...
        if line.startswith("&P") or line.startswith("&Q") or line.startswith("&X"):
            has_atf = True
            continue

        # English translation line
        if line.startswith("#tr.en:"):
            val = line[len("#tr.en:"):].strip()
            translation_lines.append(val)
            continue

        # Transliteration lines
        if TRANSLIT_LINE.match(line):
            # Strip leading line number ("1. " or "1'. ")
            text = re.sub(r"^\d+['.]?\s*", "", line).strip()
            if text:
                translit_lines.append(text)
            continue

        # Everything else (@, $, #, blank) — skip

    return {
        "has_atf":              has_atf,
        "atf_line_count":       len(translit_lines),
        "has_translation":      len(translation_lines) > 0,
        "transliteration_text": " | ".join(translit_lines) if translit_lines else "",
        "translation_text":     " ".join(translation_lines) if translation_lines else "",
    }


def parse_block(block_text: str) -> dict | None:
    """Parse one tablet block (metadata + ATF body) into a row dict."""
    # Split at "Transliteration:"
    if "Transliteration:" in block_text:
        split_idx = block_text.index("Transliteration:")
        meta_text = block_text[:split_idx]
        atf_text  = block_text[split_idx + len("Transliteration:"):]
    else:
        meta_text = block_text
        atf_text  = ""

    meta = parse_metadata(meta_text)
    atf  = parse_atf_body(atf_text)

    # If no CDLI ID found in metadata, try to extract from ATF body
    if not meta["cdli_id"]:
        m = re.search(r"&([PQX]\d+)", atf_text)
        if m:
            meta["cdli_id"] = m.group(1)

    if not meta["cdli_id"]:
        return None  # Skip records with no ID

    return {**meta, **atf}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Parse CDLI Old Assyrian ATF to CSV.")
    parser.add_argument("--input",  default=str(ATF_FILE))
    parser.add_argument("--output", default=str(OUTPUT_FILE))
    args = parser.parse_args()

    atf_path    = Path(args.input)
    output_path = Path(args.output)

    if not atf_path.exists():
        print(f"ATF file not found: {atf_path}")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Reading {atf_path} ...")
    text = atf_path.read_text(encoding="utf-8", errors="replace")

    # Split into per-tablet blocks on "Primary publication:"
    blocks = re.split(r"(?=^Primary publication:)", text, flags=re.MULTILINE)
    blocks = [b for b in blocks if b.strip() and "Primary publication:" in b]
    print(f"  {len(blocks):,} tablet blocks found.")

    rows = []
    for block in tqdm(blocks, desc="Parsing tablets", unit="tablet"):
        row = parse_block(block)
        if row:
            rows.append(row)

    print(f"  {len(rows):,} tablets parsed.")

    df = pd.DataFrame(rows, columns=[
        "cdli_id", "publication", "authors", "excavation_no",
        "genre", "language", "period", "translation_status",
        "has_atf", "atf_line_count", "has_translation",
        "transliteration_text", "translation_text",
    ])

    # Clean up
    for col in ["genre", "language", "period", "translation_status"]:
        df[col] = df[col].str.strip().replace("", pd.NA)

    df["atf_line_count"] = pd.to_numeric(df["atf_line_count"], errors="coerce").astype("Int64")

    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\nSaved {len(df):,} tablets -> {output_path}")

    # Summary
    print(f"\nSummary:")
    print(f"  Has ATF body:        {df['has_atf'].sum():,}")
    print(f"  Has translation:     {df['has_translation'].sum():,}")
    print(f"  Genre distribution:")
    genre_counts = df['genre'].fillna('(blank)').value_counts().head(10)
    for genre, count in genre_counts.items():
        print(f"    {genre}: {count:,}")


if __name__ == "__main__":
    main()
