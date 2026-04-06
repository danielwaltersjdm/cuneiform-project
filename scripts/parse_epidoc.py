"""
parse_epidoc.py

Parses papyri.info EpiDoc XML files into a structured CSV.
Handles both DDB transcription files and HGV translation files.

For each document extracts:
  doc_id, hgv_id, tm_id, ddb_hybrid, collection, date_text, date_year_approx,
  provenance, language, transcription_text, translation_text, has_translation

Output:
  processed_data/papyri/{collection}_parsed.csv

Usage:
  python scripts/parse_epidoc.py                          # all collections
  python scripts/parse_epidoc.py --collection p.zen.pestm
"""

import argparse
import re
from pathlib import Path

import pandas as pd
from lxml import etree
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT  = Path(__file__).parent.parent
RAW_PAPYRI    = PROJECT_ROOT / "raw_data" / "papyri"
PROCESSED_DIR = PROJECT_ROOT / "processed_data" / "papyri"

TEI_NS   = "http://www.tei-c.org/ns/1.0"
XML_NS   = "http://www.w3.org/XML/1998/namespace"
XML_LANG = f"{{{XML_NS}}}lang"

# HGV translations are in a separate flat directory
HGV_TRANS_DIR = RAW_PAPYRI / "hgv_trans"

TRANSCRIPTION_COLLECTIONS = [
    "p.zen.pestm",
    "p.oxy",
    "p.mich",
    "p.eleph",
    "p.eleph.wagner",
    "t.vindol",
    "t.vindon",
    "p.ness",
    "p.babatha",
    "p.dura",
    "p.cair.zen",
    "p.iand.zen",
]

APIS_INSTITUTIONS = [
    # Sequential ID institutions
    "michigan",
    "columbia",
    "oxford-ipap",
    "berkeley",
    "chicago",
    "oslo",
    "upenn",
    # Listing institutions
    "duke",
    "yale",
    "princeton",
    "stanford",
    "nyu",
    "toronto",
    "lund",
    "gothenburg",
    "hermitage",
    "wisconsin",
    "leidenpapinst",
    "trimithis",
    "petra",
    "fordham",
    "perkins",
    "psr",
    "pts",
    "pullman",
    "sacramento",
    "uts",
    "berenike",
    "britmus",
]

APIS_DIR = RAW_PAPYRI / "apis"


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def ns(tag: str) -> str:
    return f"{{{TEI_NS}}}{tag}"


def get_text(el, xpath: str, default: str = "") -> str:
    results = el.xpath(xpath, namespaces={"tei": TEI_NS, "xml": XML_NS})
    if results:
        if isinstance(results[0], str):
            return results[0].strip()
        return "".join(results[0].itertext()).strip()
    return default


def extract_year(date_text: str) -> int | None:
    """Convert a date string like '257 BC' or '1st century CE' to approx year."""
    if not date_text:
        return None
    # e.g. "257 BC" -> -257
    m = re.search(r'(\d+)\s*BC', date_text, re.IGNORECASE)
    if m:
        return -int(m.group(1))
    # e.g. "257" or "257 CE" -> 257
    m = re.search(r'(\d+)\s*(?:CE|AD)?$', date_text.strip(), re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None


def parse_transcription_xml(xml_path: Path) -> dict | None:
    """Parse a DDB EpiDoc transcription XML file."""
    parser = etree.XMLParser(recover=True, ns_clean=True)
    try:
        tree = etree.parse(str(xml_path), parser)
    except Exception:
        return None

    root = tree.getroot()

    # IDs
    doc_id   = root.get(f"{{{XML_NS}}}id", xml_path.stem)
    hgv_id   = get_text(root, "//tei:idno[@type='HGV']/text()")
    tm_id    = get_text(root, "//tei:idno[@type='TM']/text()")
    ddb_hyb  = get_text(root, "//tei:idno[@type='ddb-hybrid']/text()")
    filename = get_text(root, "//tei:idno[@type='filename']/text()") or xml_path.stem

    # Date and provenance from <head>
    date_text   = get_text(root, "//tei:body/tei:head/tei:date/text()")
    provenance  = get_text(root, "//tei:body/tei:head/tei:placeName/text()")

    # Language from langUsage
    lang_els = root.xpath("//tei:langUsage/tei:language", namespaces={"tei": TEI_NS})
    languages = [el.get("ident", "") for el in lang_els if el.get("ident") not in ("en", "")]
    language = "; ".join(languages) if languages else ""

    # Transcription text from <div type="edition">
    edition_divs = root.xpath(
        "//tei:div[@type='edition']",
        namespaces={"tei": TEI_NS}
    )
    trans_lines = []
    for div in edition_divs:
        text = " ".join(div.itertext()).strip()
        text = re.sub(r"\s+", " ", text)
        if text:
            trans_lines.append(text)
    transcription = " | ".join(trans_lines)

    return {
        "doc_id":              doc_id,
        "hgv_id":              hgv_id,
        "tm_id":               tm_id,
        "ddb_hybrid":          ddb_hyb,
        "filename":            filename,
        "date_text":           date_text,
        "date_year_approx":    extract_year(date_text),
        "provenance":          provenance,
        "language":            language,
        "transcription_text":  transcription,
        "translation_text":    "",
        "has_translation":     False,
    }


def load_hgv_translations() -> dict[str, str]:
    """
    Load all HGV translation files into a dict mapping hgv_id -> translation_text.
    """
    translations = {}
    if not HGV_TRANS_DIR.exists():
        return translations

    parser = etree.XMLParser(recover=True, ns_clean=True)
    for xml_file in HGV_TRANS_DIR.glob("*.xml"):
        try:
            tree = etree.parse(str(xml_file), parser)
        except Exception:
            continue
        root = tree.getroot()

        hgv_id = get_text(root, "//tei:idno[@type='HGV']/text()")
        tm_id  = get_text(root, "//tei:idno[@type='TM']/text()")
        key    = hgv_id or tm_id or xml_file.stem

        # Extract translation divs with xml:lang="en" or any language
        trans_divs = root.xpath(
            "//tei:div[@type='translation']",
            namespaces={"tei": TEI_NS}
        )
        parts = []
        for div in trans_divs:
            lang = div.get(XML_LANG, "")
            text = " ".join(div.itertext()).strip()
            text = re.sub(r"\s+", " ", text)
            if text:
                parts.append(text)
        if parts:
            translations[key] = " ".join(parts)

    return translations


# ---------------------------------------------------------------------------
# APIS parser
# ---------------------------------------------------------------------------

def parse_apis_xml(xml_path: Path) -> dict | None:
    """Parse an APIS institutional XML file (contains translation, not transcription)."""
    parser = etree.XMLParser(recover=True, ns_clean=True)
    try:
        tree = etree.parse(str(xml_path), parser)
    except Exception:
        return None

    root = tree.getroot()

    # IDs
    apis_id  = get_text(root, "//tei:idno[@type='apisid']/text()") or xml_path.stem
    hgv_id   = get_text(root, "//tei:idno[@type='HGV']/text()")
    tm_id    = get_text(root, "//tei:idno[@type='TM']/text()")
    ddb_hyb  = get_text(root, "//tei:idno[@type='ddb-hybrid']/text()")

    # Title / summary
    title   = get_text(root, "//tei:titleStmt/tei:title/text()")
    summary = get_text(root, "//tei:summary/text()")

    # Date — prefer numeric attrs, fall back to element text
    orig_date_els = root.xpath("//tei:origDate", namespaces={"tei": TEI_NS})
    date_text = ""
    date_year_approx = None
    if orig_date_els:
        el = orig_date_els[0]
        date_text = "".join(el.itertext()).strip()
        not_before = el.get("notBefore") or el.get("notBefore-custom")
        not_after  = el.get("notAfter")  or el.get("notAfter-custom")
        if not_before and not_after:
            try:
                date_year_approx = (int(not_before) + int(not_after)) // 2
            except (ValueError, TypeError):
                pass
        if date_year_approx is None:
            date_year_approx = extract_year(date_text)

    # Provenance
    provenance = get_text(root, "//tei:origPlace/text()")
    if not provenance:
        provenance = get_text(root, "//tei:provenance/tei:p/text()")

    # Language (mainLang attribute on textLang element)
    lang_els = root.xpath("//tei:textLang", namespaces={"tei": TEI_NS})
    language = lang_els[0].get("mainLang", "") if lang_els else ""

    # Keywords / genre
    kw_els = root.xpath("//tei:keywords/tei:term[@type='genre_form']", namespaces={"tei": TEI_NS})
    genre = "; ".join(el.text for el in kw_els if el.text)

    # Translation (directly in <div type="translation"><ab>)
    trans_divs = root.xpath("//tei:div[@type='translation']", namespaces={"tei": TEI_NS})
    parts = []
    for div in trans_divs:
        text = " ".join(div.itertext()).strip()
        text = re.sub(r"\s+", " ", text)
        if text:
            parts.append(text)
    translation = " ".join(parts)

    return {
        "doc_id":             apis_id,
        "hgv_id":             hgv_id,
        "tm_id":              tm_id,
        "ddb_hybrid":         ddb_hyb,
        "filename":           apis_id,
        "title":              title,
        "summary":            summary,
        "date_text":          date_text,
        "date_year_approx":   date_year_approx,
        "provenance":         provenance,
        "language":           language,
        "genre":              genre,
        "transcription_text": "",
        "translation_text":   translation,
        "has_translation":    bool(translation),
    }


def parse_apis_institution(institution: str) -> pd.DataFrame:
    xml_dir = APIS_DIR / institution
    if not xml_dir.exists():
        print(f"  Directory not found: {xml_dir}")
        return pd.DataFrame()

    xml_files = list(xml_dir.glob("*.xml"))
    if not xml_files:
        print(f"  No XML files in {xml_dir}")
        return pd.DataFrame()

    print(f"  {len(xml_files):,} files in apis/{institution}")

    rows = []
    for xml_path in tqdm(xml_files, desc=institution, unit="doc", leave=False):
        row = parse_apis_xml(xml_path)
        if row:
            rows.append(row)

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_collection(name: str, hgv_translations: dict[str, str]) -> pd.DataFrame:
    xml_dir = RAW_PAPYRI / name
    if not xml_dir.exists():
        print(f"  Directory not found: {xml_dir}")
        return pd.DataFrame()

    xml_files = list(xml_dir.glob("*.xml"))
    if not xml_files:
        print(f"  No XML files in {xml_dir}")
        return pd.DataFrame()

    print(f"  {len(xml_files):,} files in {name}")

    rows = []
    for xml_path in tqdm(xml_files, desc=name, unit="doc", leave=False):
        row = parse_transcription_xml(xml_path)
        if not row:
            continue

        # Attach translation if available
        for key in [row["hgv_id"], row["tm_id"], row["filename"]]:
            if key and key in hgv_translations:
                row["translation_text"] = hgv_translations[key]
                row["has_translation"]  = True
                break

        rows.append(row)

    return pd.DataFrame(rows)


def main():
    all_choices = (
        TRANSCRIPTION_COLLECTIONS
        + ["apis/" + i for i in APIS_INSTITUTIONS]
        + ["all", "apis"]
    )
    parser = argparse.ArgumentParser(description="Parse papyri EpiDoc XML to CSV.")
    parser.add_argument("--collection", default="all", choices=all_choices)
    args = parser.parse_args()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    (PROCESSED_DIR / "apis").mkdir(parents=True, exist_ok=True)

    # APIS-only mode
    if args.collection == "apis":
        for inst in APIS_INSTITUTIONS:
            print(f"\nParsing apis/{inst}...")
            df = parse_apis_institution(inst)
            if df.empty:
                print(f"  Skipped (empty).")
                continue
            out = PROCESSED_DIR / "apis" / f"{inst}_parsed.csv"
            df.to_csv(out, index=False, encoding="utf-8-sig")
            translated = df["has_translation"].sum()
            print(f"  {len(df):,} docs | {translated:,} with translation -> {out.name}")
        print("\nDone.")
        return

    if args.collection.startswith("apis/"):
        inst = args.collection.removeprefix("apis/")
        print(f"\nParsing apis/{inst}...")
        df = parse_apis_institution(inst)
        if not df.empty:
            out = PROCESSED_DIR / "apis" / f"{inst}_parsed.csv"
            df.to_csv(out, index=False, encoding="utf-8-sig")
            translated = df["has_translation"].sum()
            print(f"  {len(df):,} docs | {translated:,} with translation -> {out.name}")
        print("\nDone.")
        return

    # DDB EpiDoc collections
    print("Loading HGV translations...")
    hgv_trans = load_hgv_translations()
    print(f"  {len(hgv_trans):,} HGV translation records loaded.")

    targets = TRANSCRIPTION_COLLECTIONS if args.collection == "all" else [args.collection]

    for name in targets:
        print(f"\nParsing {name}...")
        df = parse_collection(name, hgv_trans)
        if df.empty:
            print(f"  Skipped (empty).")
            continue

        out = PROCESSED_DIR / f"{name}_parsed.csv"
        df.to_csv(out, index=False, encoding="utf-8-sig")
        translated = df["has_translation"].sum()
        print(f"  {len(df):,} docs | {translated:,} with translation -> {out.name}")

    print("\nDone.")


if __name__ == "__main__":
    main()
