"""
fetch_dmd.py

Scrapes the Deir el-Medina Database (dmd.wepwawet.nl) — 4,706 records.

Strategy:
1. Download totalindex2024.htm to extract all record IDs.
2. For each ID fetch scripts/dmdobject.asp?id=ID&m=i.
3. Cache raw HTML to raw_data/deir_el_medina/html/.
4. Parse and write processed_data/deir_el_medina/dmd_records.csv.

Usage:
  python scripts/fetch_dmd.py              # download all (resumes)
  python scripts/fetch_dmd.py --parse-only # re-parse from cached HTML
"""

import argparse
import re
import time
import urllib3
import requests
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_URL     = "https://dmd.wepwawet.nl"
INDEX_URL    = f"{BASE_URL}/totalindex2024.htm"
RECORD_URL   = f"{BASE_URL}/scripts/dmdobject.asp"

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR      = PROJECT_ROOT / "raw_data"  / "deir_el_medina" / "html"
PROC_DIR     = PROJECT_ROOT / "processed_data" / "deir_el_medina"

REQUEST_DELAY = 0.2   # seconds between requests
TIMEOUT       = 20

# ---------------------------------------------------------------------------
# Step 1: extract all record IDs from the index
# ---------------------------------------------------------------------------

def get_all_ids() -> list[str]:
    """Download totalindex2024.htm and extract all record IDs."""
    index_cache = PROJECT_ROOT / "raw_data" / "deir_el_medina" / "totalindex2024.htm"
    index_cache.parent.mkdir(parents=True, exist_ok=True)

    if not index_cache.exists():
        print("Downloading index...")
        r = requests.get(INDEX_URL, verify=False, timeout=30)
        r.raise_for_status()
        index_cache.write_bytes(r.content)
        print(f"  Saved {len(r.content):,} bytes -> {index_cache.name}")
    else:
        print(f"Index already cached: {index_cache.name}")

    html = index_cache.read_text(encoding="utf-8", errors="replace")
    # Links like: href="scripts/dmdobject.asp?id=O. Ashmolean Museum 0007&m=i"
    ids = re.findall(r'dmdobject\.asp\?id=([^&"]+)&m=i', html)
    # URL-decode space encoding
    ids = [id_.replace("+", " ").replace("%20", " ") for id_ in ids]
    ids = list(dict.fromkeys(ids))  # deduplicate, preserve order
    print(f"Found {len(ids):,} unique record IDs.")
    return ids


# ---------------------------------------------------------------------------
# Step 2: download raw HTML for each record
# ---------------------------------------------------------------------------

def download_records(ids: list[str]) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    to_fetch = [rid for rid in ids if not _cache_path(rid).exists()]
    print(f"{len(ids) - len(to_fetch):,} already cached; {len(to_fetch):,} to fetch.")

    for rid in tqdm(to_fetch, desc="Downloading", unit="record"):
        try:
            r = requests.get(
                RECORD_URL,
                params={"id": rid, "m": "i"},
                verify=False,
                timeout=TIMEOUT,
            )
            if r.status_code == 200:
                _cache_path(rid).write_bytes(r.content)
            else:
                print(f"\n  HTTP {r.status_code} for {rid!r}")
        except Exception as e:
            print(f"\n  Error fetching {rid!r}: {e}")
        time.sleep(REQUEST_DELAY)


def _cache_path(record_id: str) -> Path:
    """Sanitize ID to a safe filename."""
    safe = re.sub(r'[\\/:*?"<>|]', "_", record_id)
    return RAW_DIR / f"{safe}.html"


# ---------------------------------------------------------------------------
# Step 3: parse cached HTML to structured records
# ---------------------------------------------------------------------------

FIELD_MAP = {
    "Other nos.":       "other_nos",
    "Description:":     "description",
    "Classification:":  "classification",
    "Keywords:":        "keywords",
    "Provenance:":      "provenance",
    "Publication:":     "publication",
    "Dates mentioned:": "dates_mentioned",
    "Dates attributed:":"dates_attributed",
    "Contents:":        "contents",
    "Terminology:":     "terminology",
    "Names/Titles:":    "names_titles",
    "Remarks:":         "remarks",
}


def parse_record_html(html: str, record_id: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    row = {"record_id": record_id}

    # Title is the first large font cell (the record header)
    # Fields are in <tr> pairs: label-td / value-td
    trs = soup.find_all("tr")
    for tr in trs:
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue
        label_raw = tds[0].get_text(separator=" ", strip=True)
        # Match known labels
        for label, key in FIELD_MAP.items():
            if label.lower() in label_raw.lower():
                # Get value text; strip font tags and excess whitespace
                value = tds[1].get_text(separator=" ", strip=True)
                value = re.sub(r"\s+", " ", value).strip()
                row[key] = value
                break

    # Extract date attributes from dates_attributed
    row.setdefault("other_nos",        "")
    row.setdefault("description",      "")
    row.setdefault("classification",   "")
    row.setdefault("keywords",         "")
    row.setdefault("provenance",       "")
    row.setdefault("publication",      "")
    row.setdefault("dates_mentioned",  "")
    row.setdefault("dates_attributed", "")
    row.setdefault("contents",         "")
    row.setdefault("terminology",      "")
    row.setdefault("names_titles",     "")
    row.setdefault("remarks",          "")

    # Infer doc type: O = ostracon, P = papyrus
    if record_id.startswith("O."):
        row["doc_type"] = "ostracon"
    elif record_id.startswith("P."):
        row["doc_type"] = "papyrus"
    else:
        row["doc_type"] = "other"

    return row


def parse_all(ids: list[str]) -> pd.DataFrame:
    PROC_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    missing = 0
    for rid in tqdm(ids, desc="Parsing", unit="record"):
        path = _cache_path(rid)
        if not path.exists():
            missing += 1
            continue
        html = path.read_text(encoding="utf-8", errors="replace")
        rows.append(parse_record_html(html, rid))

    if missing:
        print(f"  {missing:,} records not yet downloaded (skipped).")

    df = pd.DataFrame(rows)
    out = PROC_DIR / "dmd_records.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"  {len(df):,} records parsed -> {out}")
    return df


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--parse-only", action="store_true",
                        help="Skip downloading; re-parse from cached HTML only.")
    args = parser.parse_args()

    ids = get_all_ids()

    if not args.parse_only:
        download_records(ids)

    print("\nParsing records...")
    df = parse_all(ids)

    # Quick summary
    print(f"\nTotal records:  {len(df):,}")
    print(f"Ostraca:        {(df.doc_type == 'ostracon').sum():,}")
    print(f"Papyri:         {(df.doc_type == 'papyrus').sum():,}")
    print(f"With contents:  {df.contents.str.len().gt(5).sum():,}")
    if not df.empty and "classification" in df.columns:
        print(f"\nTop classifications:")
        print(df.classification.value_counts().head(15).to_string())

    print("\nDone.")


if __name__ == "__main__":
    main()
