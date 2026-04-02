"""
parse_transliterations.py

Parses ORACC teiCorpus XML files into a flat, structured CSV of tokens.

TEI word element format:
  <w lemma="ana[to//to]PRP" xml:id="P224395.l043f1">a-na</w>

The lemma attribute encodes:  cf[gw//sense]POS
  ana      = citation form
  to       = guideword
  to       = sense
  PRP      = part of speech

Line numbers come from preceding <lb n="N"/> elements.
Text IDs come from <name type="file">saao/saa01/P224395.xtf</name> in each
embedded <TEI> header.

Output columns:
  text_id, project, surface, line_no, word_position,
  form, cf, gw, sense, pos

Usage:
  python scripts/parse_transliterations.py
  python scripts/parse_transliterations.py --project saao_saa01
  python scripts/parse_transliterations.py --output outputs/tokens.csv
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

PROJECT_ROOT     = Path(__file__).parent.parent
RAW_DATA_DIR     = PROJECT_ROOT / "raw_data"
PROCESSED_DIR    = PROJECT_ROOT / "processed_data"
DEFAULT_OUTPUT   = PROJECT_ROOT / "outputs" / "neo_assyrian_letters_tokens.csv"

TEI_NS  = "http://www.tei-c.org/ns/1.0"
W       = f"{{{TEI_NS}}}w"
LB      = f"{{{TEI_NS}}}lb"
DIV1    = f"{{{TEI_NS}}}div1"
NAME    = f"{{{TEI_NS}}}name"
TEXT    = f"{{{TEI_NS}}}text"
BODY    = f"{{{TEI_NS}}}body"
TEI_EL  = f"{{{TEI_NS}}}TEI"

# Lemma attribute pattern:  cf[gw//sense]POS  or  cf[gw]POS  or  X (unlexed)
LEMMA_RE = re.compile(
    r"^(?P<cf>[^\[]+)"           # citation form
    r"\[(?P<gw>[^/\]]+)"         # guideword
    r"(?://(?P<sense>[^\]]*))?"  # optional //sense
    r"\]"
    r"(?P<pos>\S+)$"             # POS tag
)


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def parse_lemma(lemma_attr: str) -> dict:
    """Parse an ORACC lemma attribute string into its components."""
    if not lemma_attr:
        return {"cf": "", "gw": "", "sense": "", "pos": ""}
    m = LEMMA_RE.match(lemma_attr.strip())
    if not m:
        return {"cf": lemma_attr, "gw": "", "sense": "", "pos": ""}
    return {
        "cf":    m.group("cf").strip(),
        "gw":    m.group("gw").strip(),
        "sense": (m.group("sense") or "").strip(),
        "pos":   m.group("pos").strip(),
    }


def inner_text(element) -> str:
    """Collect all text content inside an element, ignoring child tags."""
    return "".join(element.itertext()).strip()


def text_id_from_header(tei_element) -> str:
    """
    Extract the P-number text ID from a TEI element's header.
    Looks for:  <name type="file">saao/saa01/P224395.xtf</name>
    """
    for name_el in tei_element.iter(NAME):
        if name_el.get("type") == "file":
            val = (name_el.text or "").strip()
            # Extract P-number  e.g. 'saao/saa01/P224395.xtf' -> 'P224395'
            stem = Path(val).stem  # 'P224395'
            if re.match(r"[A-Z]\d+", stem):
                return stem
    # Fallback: use xml:id of the TEI element itself
    xml_id = tei_element.get("{http://www.w3.org/XML/1998/namespace}id", "")
    return xml_id or "UNKNOWN"


def parse_tei_text(tei_element, project: str) -> list[dict]:
    """
    Parse all <text type='transliteration'> blocks inside a single <TEI> element.
    Returns a list of token dicts.
    """
    text_id = text_id_from_header(tei_element)
    rows = []

    for text_el in tei_element.iter(TEXT):
        if text_el.get("type") != "transliteration":
            continue

        current_surface = ""
        current_line    = ""
        word_pos        = 1

        # Walk all descendants in document order
        for el in text_el.iter():
            tag = el.tag

            # Track surface (obverse/reverse/edge)
            if tag == DIV1:
                current_surface = el.get("subtype", el.get("type", ""))
                current_line = ""
                word_pos = 1

            # Line break resets word position counter
            elif tag == LB:
                current_line = el.get("n", "")
                word_pos = 1

            # Word token
            elif tag == W:
                lemma_attr = el.get("lemma", "")
                form = inner_text(el)
                if not form:
                    continue

                lem = parse_lemma(lemma_attr)
                rows.append({
                    "text_id":       text_id,
                    "project":       project,
                    "surface":       current_surface,
                    "line_no":       current_line,
                    "word_position": word_pos,
                    "form":          form,
                    "cf":            lem["cf"],
                    "gw":            lem["gw"],
                    "sense":         lem["sense"],
                    "pos":           lem["pos"],
                })
                word_pos += 1

    return rows


def parse_corpus_xml(xml_path: Path, project: str) -> list[dict]:
    """Parse a full teiCorpus XML file and return all token rows."""
    # recover=True tolerates invalid xml:id values that ORACC emits (e.g.
    # 'statusEnd:erasedP...' which contain colons, illegal in NCNames).
    parser = etree.XMLParser(recover=True, ns_clean=True, encoding="utf-8")
    try:
        tree = etree.parse(str(xml_path), parser)
    except etree.XMLSyntaxError as exc:
        print(f"  XML parse error in {xml_path.name}: {exc}")
        return []

    root = tree.getroot()
    rows = []
    tei_elements = list(root.iter(TEI_EL))

    for tei_el in tqdm(tei_elements, desc=xml_path.stem[:20], unit="text", leave=False):
        rows.extend(parse_tei_text(tei_el, project))

    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Parse ORACC TEI XML to CSV.")
    parser.add_argument("--project", default=None,
                        help="Process only this project folder (e.g. saao_saa01).")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

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
        print(f"  {len(rows):,} tokens extracted.")
        all_rows.extend(rows)

    if not all_rows:
        print("No tokens extracted.")
        return

    df = pd.DataFrame(all_rows)

    # Clean up
    str_cols = ["form", "cf", "gw", "sense", "pos", "surface", "line_no"]
    for col in str_cols:
        df[col] = df[col].str.strip().replace("", pd.NA)
    df["word_position"] = pd.to_numeric(df["word_position"], errors="coerce").astype("Int64")

    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\nSaved {len(df):,} tokens | {df['text_id'].nunique():,} texts -> {output_path}")

    # Per-text summary
    summary = (
        df.groupby(["project", "text_id"])
        .agg(
            token_count  = ("form", "count"),
            lemmatized   = ("cf",   lambda s: s.notna().sum()),
            line_count   = ("line_no", "nunique"),
        )
        .reset_index()
    )
    summary_path = PROCESSED_DIR / "text_summary.csv"
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")
    print(f"Saved per-text summary ({len(summary):,} texts) -> {summary_path}")


if __name__ == "__main__":
    main()
