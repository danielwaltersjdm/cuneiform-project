"""
extract_diary_prices.py

Extracts commodity price observations from the Babylonian Astronomical Diaries.

The Diaries record monthly market prices in a standard formula:
  "the equivalent for 1 shekel of silver was: barley, X pānu Y sūtu; dates, ..."

Commodities: barley, dates, mustard, cress, sesame, wool
Measures:    kur (180 qa), pānu (30 qa), sūtu (6 qa), qa (base unit)
             Wool recorded in minas per shekel.

Output: processed_data/babylonian_diaries/diary_prices.csv
Columns: text_id, year_signed (negative = BCE), commodity, qty_qa, unit

Usage:
  python scripts/extract_diary_prices.py
"""

import re
import glob
from fractions import Fraction
from pathlib import Path

import pandas as pd
from lxml import etree

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR      = PROJECT_ROOT / "raw_data" / "babylonian_diaries"
PROC_DIR     = PROJECT_ROOT / "processed_data" / "babylonian_diaries"

TEI_NS = "http://www.tei-c.org/ns/1.0"


# ---------------------------------------------------------------------------
# Build text_id -> year map from ADART TEI corpus files
# ---------------------------------------------------------------------------

def build_year_map() -> dict[str, int]:
    ns = {"tei": TEI_NS}
    id_year: dict[str, int] = {}
    for vol in ["adart1", "adart2", "adart3"]:
        xml_files = list((RAW_DIR / vol).glob("*.xml"))
        if not xml_files:
            continue
        tree = etree.parse(str(xml_files[0]))
        root = tree.getroot()
        for t in root.xpath("//tei:TEI", namespaces=ns):
            all_text = "".join(t.itertext())
            m = re.search(r"(X\d+)\s*=\s*AD\s+(-?\d+)", all_text)
            if m:
                id_year[m.group(1)] = int(m.group(2))
    return id_year


# ---------------------------------------------------------------------------
# Quantity parser (handles fractions like '2 1/3')
# ---------------------------------------------------------------------------

def parse_qty(s: str | None) -> float:
    if not s:
        return 0.0
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


# ---------------------------------------------------------------------------
# Price extraction regexes
# ---------------------------------------------------------------------------

# Two-part: 'barley, 4 pānu 4 sūtu'
TWO_PART_RE = re.compile(
    r"(barley|dates?|sesame|cress|mustard|wool|cardamom|lard|oil)\s*[,;:]?\s*"
    r"(?:\[.*?\]\s*)?"
    r"([\d\s/]+)\s*p[a\u0101]nu\s*([\d\s/]+)\s*s[u\u016b]tu",
    re.IGNORECASE,
)

# Single-unit: 'barley, 3 kur' or 'sesame, 2 sūtu 3 qa' or 'wool, 3 1/2 minas'
SINGLE_RE = re.compile(
    r"(barley|dates?|sesame|cress|mustard|wool|cardamom|lard|oil)\s*[,;:]?\s*"
    r"(?:\[.*?\]\s*)?"
    r"([\d\s/]+)\s*(kur|p[a\u0101]nu|s[u\u016b]tu|qa|min[ae]s?)",
    re.IGNORECASE,
)


def normalize_commodity(name: str) -> str:
    name = name.lower().strip()
    # Normalize partial matches of 'cress'
    if name.startswith("cre"):
        return "cress"
    if name == "date":
        return "dates"
    return name


def extract_prices(df: pd.DataFrame, id_year: dict[str, int]) -> pd.DataFrame:
    records = []
    for _, row in df.iterrows():
        text = str(row["translation"])
        year = id_year.get(row["text_id"])
        seen: set = set()

        # Two-part quantities first (more specific)
        for m in TWO_PART_RE.finditer(text):
            commodity = normalize_commodity(m.group(1))
            panu = parse_qty(m.group(2))
            sutu = parse_qty(m.group(3))
            qty_qa = panu * 30 + sutu * 6
            if qty_qa == 0:
                continue
            key = (row["text_id"], commodity, qty_qa)
            if key in seen:
                continue
            seen.add(key)
            records.append({
                "text_id": row["text_id"],
                "year_signed": year,
                "commodity": commodity,
                "qty_qa": qty_qa,
                "unit": "qa/shekel",
            })

        # Single-unit quantities
        for m in SINGLE_RE.finditer(text):
            commodity = normalize_commodity(m.group(1))
            qty = parse_qty(m.group(2))
            unit_raw = m.group(3).lower()

            if "kur" in unit_raw:
                qty_qa = qty * 180
                unit = "qa/shekel"
            elif "p" in unit_raw:
                qty_qa = qty * 30
                unit = "qa/shekel"
            elif "t" in unit_raw:
                qty_qa = qty * 6
                unit = "qa/shekel"
            elif unit_raw == "qa":
                qty_qa = qty
                unit = "qa/shekel"
            elif "mina" in unit_raw:
                qty_qa = qty
                unit = "minas/shekel"
            else:
                continue

            if qty_qa == 0:
                continue
            key = (row["text_id"], commodity, qty_qa)
            if key in seen:
                continue
            seen.add(key)
            records.append({
                "text_id": row["text_id"],
                "year_signed": year,
                "commodity": commodity,
                "qty_qa": qty_qa,
                "unit": unit,
            })

    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Building year map from ADART TEI files...")
    id_year = build_year_map()
    print(f"  {len(id_year):,} text IDs mapped to years")

    print("Loading diary translations...")
    df = pd.read_csv(PROC_DIR / "diary_translations.csv")
    print(f"  {len(df):,} diary entries")

    print("Extracting prices...")
    prices = extract_prices(df, id_year)

    # Filter implausible single-qa values (likely parsing artifacts)
    prices = prices[prices["qty_qa"] >= 6]

    print(f"  {len(prices):,} price observations extracted")
    print()
    print("By commodity:")
    print(prices["commodity"].value_counts().to_string())
    print()
    print(f"Year range: {prices['year_signed'].min()} to {prices['year_signed'].max()} CE")

    out = PROC_DIR / "diary_prices.csv"
    prices.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"\n-> {out}")


if __name__ == "__main__":
    main()
