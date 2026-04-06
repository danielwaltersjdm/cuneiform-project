"""
fetch_elephantine.py

Downloads TEI-XML files from the Elephantine ERC project
(elephantine.smb.museum / p612399.webspaceconfig.de).

Strategy:
1. Scrape objects listing to get all record IDs.
2. Download TEI-XML from p612399.webspaceconfig.de/xml/elephantine_erc_db_{ID}.tei.xml
3. Parse translations and metadata.

Usage:
  python scripts/fetch_elephantine.py
  python scripts/fetch_elephantine.py --parse-only
"""

import argparse
import re
import time
import urllib3
import requests
from pathlib import Path
from lxml import etree
import pandas as pd
from tqdm import tqdm

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROJECT_ROOT  = Path(__file__).parent.parent
RAW_DIR       = PROJECT_ROOT / "raw_data"       / "elephantine"
PROC_DIR      = PROJECT_ROOT / "processed_data" / "elephantine"
OBJECTS_URL   = "https://elephantine.smb.museum/objects/"
TEI_BASE      = "https://p612399.webspaceconfig.de/xml/elephantine_erc_db_{id}.tei.xml"
TEI_NS        = "http://www.tei-c.org/ns/1.0"
REQUEST_DELAY = 0.3


# ---------------------------------------------------------------------------
# Step 1: collect IDs
# ---------------------------------------------------------------------------

def get_all_ids() -> list[str]:
    print("Fetching objects listing...")
    r = requests.get(OBJECTS_URL, verify=False, timeout=20)
    ids = list(dict.fromkeys(re.findall(r'texts/view\.php\?t=(\d+)', r.text)))
    print(f"Found {len(ids)} unique record IDs.")
    return ids


# ---------------------------------------------------------------------------
# Step 2: download TEI-XML
# ---------------------------------------------------------------------------

def download_tei(ids: list[str]) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    to_fetch = [i for i in ids if not (RAW_DIR / f"{i}.tei.xml").exists()]
    print(f"{len(ids) - len(to_fetch)} already cached; {len(to_fetch)} to fetch.")

    for record_id in tqdm(to_fetch, desc="Downloading TEI-XML", unit="doc"):
        url = TEI_BASE.format(id=record_id)
        try:
            r = requests.get(url, verify=False, timeout=20)
            if r.status_code == 200:
                (RAW_DIR / f"{record_id}.tei.xml").write_bytes(r.content)
            else:
                print(f"\n  HTTP {r.status_code} for {record_id}")
        except Exception as e:
            print(f"\n  Error {record_id}: {e}")
        time.sleep(REQUEST_DELAY)


# ---------------------------------------------------------------------------
# Step 3: parse TEI-XML
# ---------------------------------------------------------------------------

NS = {"tei": TEI_NS}


def _text(el):
    if el is None:
        return ""
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def parse_tei(xml_path: Path) -> dict | None:
    parser = etree.XMLParser(recover=True, load_dtd=False, no_network=True)
    try:
        tree = etree.parse(str(xml_path), parser)
    except Exception:
        return None
    root = tree.getroot()

    def xpath(expr):
        result = root.xpath(expr, namespaces=NS)
        return result[0] if result else None

    def xpaths(expr):
        return root.xpath(expr, namespaces=NS)

    record_id = xml_path.stem  # e.g. "100089"

    title_el = xpath("//tei:titleStmt/tei:title")
    title = _text(title_el)

    # Summary / abstract
    summary_el = xpath("//tei:msContents/tei:summary") or xpath("//tei:abstract")
    summary = _text(summary_el)

    # Date
    date_els = xpaths("//tei:origDate")
    date_text = "; ".join(_text(el) for el in date_els if _text(el))
    date_when = date_els[0].get("when") or date_els[0].get("notBefore") if date_els else None

    # Language(s)
    lang_els = xpaths("//tei:textLang")
    language = "; ".join(
        (el.get("mainLang") or "") + " " + (el.get("otherLangs") or "")
        for el in lang_els
    ).strip()

    # Provenance
    prov_el = xpath("//tei:provenance[@type='found']") or xpath("//tei:origPlace")
    provenance = _text(prov_el)

    # Doc type from title (Pap. / Ostr.)
    if title.startswith("Pap."):
        doc_type = "papyrus"
    elif title.startswith("Ostr."):
        doc_type = "ostracon"
    elif title.startswith("Tablet"):
        doc_type = "tablet"
    else:
        doc_type = "other"

    # Translation — look for <div type="translation"> or <ab> under translation sections
    trans_divs = xpaths("//tei:div[@type='translation']")
    translation_parts = []
    for div in trans_divs:
        lang = div.get("{http://www.w3.org/XML/1998/namespace}lang") or div.get("n") or ""
        text_content = _text(div)
        if text_content:
            translation_parts.append(f"[{lang}] {text_content}" if lang else text_content)

    translation = " | ".join(translation_parts)

    # Transcription (edition)
    edition_divs = xpaths("//tei:div[@type='edition']")
    transcription_parts = []
    for div in edition_divs:
        t = _text(div)
        if t:
            transcription_parts.append(t)
    transcription = " ".join(transcription_parts)

    # Keywords
    keywords_els = xpaths("//tei:keywords/tei:term") or xpaths("//tei:term")
    keywords = "; ".join(_text(el) for el in keywords_els if _text(el))

    return {
        "record_id":    record_id,
        "title":        title,
        "doc_type":     doc_type,
        "date_text":    date_text,
        "date_when":    date_when,
        "language":     language,
        "provenance":   provenance,
        "summary":      summary,
        "keywords":     keywords,
        "transcription_text": transcription,
        "translation_text":   translation,
        "has_translation":    bool(translation),
    }


def parse_all(ids: list[str]) -> pd.DataFrame:
    PROC_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for record_id in tqdm(ids, desc="Parsing", unit="doc"):
        path = RAW_DIR / f"{record_id}.tei.xml"
        if not path.exists():
            continue
        row = parse_tei(path)
        if row:
            rows.append(row)

    df = pd.DataFrame(rows)
    out = PROC_DIR / "elephantine_records.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"  {len(df):,} records parsed -> {out}")
    return df


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--parse-only", action="store_true")
    args = parser.parse_args()

    ids = get_all_ids()

    if not args.parse_only:
        download_tei(ids)

    print("\nParsing records...")
    df = parse_all(ids)

    if df.empty:
        print("No records parsed.")
        return

    print(f"\nTotal: {len(df):,}")
    print(f"With translation: {df.has_translation.sum():,}")
    print(f"\nDoc types:\n{df.doc_type.value_counts().to_string()}")
    print(f"\nLanguages (top 10):\n{df.language.value_counts().head(10).to_string()}")

    if df.has_translation.any():
        sample = df[df.has_translation].iloc[0]
        print(f"\nSample ({sample.record_id}): {sample.title}")
        print(f"Summary: {sample.summary[:200]}")
        print(f"Translation: {str(sample.translation_text)[:400]}")

    print("\nDone.")


if __name__ == "__main__":
    main()
