"""
parse_translations.py

Extracts ORACC English translations from teiCorpus XML files.

For each Neo-Assyrian letter, collects the project-provided English translation
from:  <div1 type="translation" subtype="project" xml:lang="en">

Output columns:
  text_id, project, translation, token_count

Usage:
  python scripts/parse_translations.py
  python scripts/parse_translations.py --project saao_saa01
  python scripts/parse_translations.py --output processed_data/letters_translations.csv
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
RAW_DATA_DIR  = PROJECT_ROOT / "raw_data"
PROCESSED_DIR = PROJECT_ROOT / "processed_data"
DEFAULT_OUTPUT = PROCESSED_DIR / "letters_translations.csv"

TEI_NS = "http://www.tei-c.org/ns/1.0"
XML_NS = "http://www.w3.org/XML/1998/namespace"

DIV1   = f"{{{TEI_NS}}}div1"
DIV3   = f"{{{TEI_NS}}}div3"
P      = f"{{{TEI_NS}}}p"
SPAN   = f"{{{TEI_NS}}}span"
NAME   = f"{{{TEI_NS}}}name"
TEI_EL = f"{{{TEI_NS}}}TEI"

XML_ID   = f"{{{XML_NS}}}id"
XML_LANG = f"{{{XML_NS}}}lang"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def text_id_from_header(tei_element) -> str:
    """
    Extract the P-number text ID from a TEI element's header.
    Looks for: <name type="file">saao/saa01/P224395.xtf</name>
    """
    for name_el in tei_element.iter(NAME):
        if name_el.get("type") == "file":
            val = (name_el.text or "").strip()
            stem = Path(val).stem  # e.g. 'P224395'
            if re.match(r"[A-Z]\d+", stem):
                return stem
    # Fallback: xml:id on the TEI element itself
    return tei_element.get(XML_ID, "") or "UNKNOWN"


def extract_translation(div1_el) -> tuple[str, int]:
    """
    Extract translation text and word count from a translation <div1> element.

    Words are in <span type="w"> elements; itertext() on each <p> captures
    surrounding punctuation and editorial marks (brackets, parentheses).

    Returns (translation_text, token_count).
    """
    paragraphs = []
    word_count = 0

    for div3 in div1_el.iter(DIV3):
        # Count word tokens
        for span in div3.iter(SPAN):
            if span.get("type") == "w":
                word_count += 1

        # Collect paragraph text (preserves punctuation between words)
        for p_el in div3.iter(P):
            text = "".join(p_el.itertext()).strip()
            if text:
                paragraphs.append(text)

    translation = " ".join(paragraphs)
    translation = re.sub(r"\s+", " ", translation).strip()
    return translation, word_count


def parse_tei_translations(tei_element, project: str) -> dict | None:
    """
    Parse the English translation from a single <TEI> element.
    Returns a row dict or None if no translation is found.
    """
    text_id = text_id_from_header(tei_element)
    if text_id in ("UNKNOWN", ""):
        return None

    for div1 in tei_element.iter(DIV1):
        if (div1.get("type") == "translation"
                and div1.get("subtype") == "project"
                and div1.get(XML_LANG) == "en"):
            translation, token_count = extract_translation(div1)
            if not translation:
                continue
            return {
                "text_id":     text_id,
                "project":     project,
                "translation": translation,
                "token_count": token_count,
            }

    return None


def parse_corpus_xml(xml_path: Path, project: str) -> list[dict]:
    """Parse a full teiCorpus XML file and return one translation row per text."""
    parser = etree.XMLParser(recover=True, ns_clean=True, encoding="utf-8")
    try:
        tree = etree.parse(str(xml_path), parser)
    except etree.XMLSyntaxError as exc:
        print(f"  XML parse error in {xml_path.name}: {exc}")
        return []

    root = tree.getroot()
    rows = []
    for tei_el in tqdm(list(root.iter(TEI_EL)), desc=xml_path.stem[:20], unit="text", leave=False):
        row = parse_tei_translations(tei_el, project)
        if row:
            rows.append(row)

    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Extract ORACC English translations to CSV."
    )
    parser.add_argument(
        "--project", default=None,
        help="Process only this project folder (e.g. saao_saa01).",
    )
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.project:
        project_dirs = [RAW_DATA_DIR / args.project]
    else:
        project_dirs = [d for d in sorted(RAW_DATA_DIR.iterdir()) if d.is_dir()]

    if not project_dirs:
        print(f"No project directories found in {RAW_DATA_DIR}. Run fetch_oracc.py first.")
        return

    all_rows = []
    for pdir in project_dirs:
        xml_files = list(pdir.glob("*teiCorpus*.xml"))
        if not xml_files:
            print(f"  WARNING: No teiCorpus XML in {pdir.name} — run fetch_oracc.py first.")
            continue
        xml_path = xml_files[0]
        print(f"Parsing {pdir.name} ({xml_path.name}) ...")
        rows = parse_corpus_xml(xml_path, pdir.name)
        print(f"  {len(rows):,} translations extracted.")
        all_rows.extend(rows)

    if not all_rows:
        print("No translations extracted.")
        return

    df = pd.DataFrame(all_rows)
    df["translation"] = df["translation"].str.strip().replace("", pd.NA)
    df["token_count"] = pd.to_numeric(df["token_count"], errors="coerce").astype("Int64")

    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\nSaved {len(df):,} translations | {df['project'].nunique()} projects -> {output_path}")


if __name__ == "__main__":
    main()
