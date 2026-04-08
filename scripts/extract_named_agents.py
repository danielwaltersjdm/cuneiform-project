"""
extract_named_agents.py

Extracts named individuals from APIS Michigan papyri using patronymic patterns.
Tracks recurring agents across documents for longitudinal behavioral analysis.

Focus: Karanis grain transport ostraca (262–312 CE) — the densest longitudinal
archive in the Michigan collection.

Output:
  processed_data/papyri/michigan_agents.csv        — one row per mention
  processed_data/papyri/michigan_agents_summary.csv — one row per individual

Usage:
  python scripts/extract_named_agents.py [--institution michigan]
"""

import argparse
import re
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
PROC_DIR     = PROJECT_ROOT / "processed_data" / "papyri"

# Words that look like capitalized names but are not
SKIP_WORDS = {
    "Also", "This", "That", "From", "With", "Through", "While", "After",
    "Before", "Then", "When", "Upon", "Each", "Both", "Same", "Such",
    "Only", "Even", "Among", "Since", "Until", "Within", "Without",
    "Whereas", "However", "Therefore", "Inasmuch", "Insofar",
    "Month", "Year", "Day", "The", "And", "But", "For", "Nor",
    "Throughout", "Moreover", "Furthermore", "Concerning",
}

# Patronymic extraction: 'X son of Y' or 'X daughter of Y'
PATRONYMIC_RE = re.compile(
    r"\b([A-Z][a-z]{3,25})\s+(?:son|daughter)\s+of\s+([A-Z][a-z]{3,25})\b"
)

# Role words following names: helps classify agent function
ROLE_WORDS_RE = re.compile(
    r"\b(?:tax\s+collector|sitologos|dekaprotos|strategos|praktor|"
    r"donkey.driver|auletes|gymnasiarch|komarch|presbyteros|"
    r"farmer|weaver|soldier|veteran|freedman)\b",
    re.IGNORECASE,
)


def extract_agents(df: pd.DataFrame) -> pd.DataFrame:
    records = []
    for _, row in df.iterrows():
        text = str(row.get("translation_text", ""))
        if not text or text == "nan":
            continue
        for m in PATRONYMIC_RE.finditer(text):
            name   = m.group(1)
            father = m.group(2)
            if name in SKIP_WORDS or father in SKIP_WORDS:
                continue
            # Context window for role detection
            ctx_start = max(0, m.start() - 80)
            ctx_end   = min(len(text), m.end() + 120)
            ctx = text[ctx_start:ctx_end].replace("\n", " ")
            role_m = ROLE_WORDS_RE.search(ctx)
            records.append({
                "doc_id":      row["doc_id"],
                "institution": row.get("institution", ""),
                "date_year":   row.get("date_year_approx"),
                "date_text":   str(row.get("date_text", ""))[:40],
                "genre":       str(row.get("genre", ""))[:60],
                "name":        name,
                "father":      father,
                "role":        role_m.group(0).lower() if role_m else None,
                "context":     ctx[:200],
            })
    return pd.DataFrame(records)


def summarize_agents(mentions: pd.DataFrame) -> pd.DataFrame:
    summary = (
        mentions
        .groupby(["name", "father", "institution"])
        .agg(
            n_docs      = ("doc_id", "nunique"),
            earliest    = ("date_year", "min"),
            latest      = ("date_year", "max"),
            span_years  = ("date_year", lambda x: x.max() - x.min() if x.notna().sum() > 1 else 0),
            roles       = ("role", lambda x: ", ".join(sorted(x.dropna().unique()))),
            doc_ids     = ("doc_id", lambda x: "; ".join(sorted(x.unique())[:8])),
        )
        .reset_index()
        .sort_values("n_docs", ascending=False)
    )
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--institution", default=None,
                        help="Filter to one institution (e.g. 'michigan')")
    args = parser.parse_args()

    print("Loading APIS combined CSV...")
    df = pd.read_csv(PROC_DIR / "apis_combined.csv")
    translated = df[df["has_translation"] == True].copy()

    if args.institution:
        translated = translated[translated["institution"] == args.institution]
        print(f"  Filtered to '{args.institution}': {len(translated):,} docs")
    else:
        print(f"  {len(translated):,} translated documents")

    print("Extracting named agents...")
    mentions = extract_agents(translated)
    print(f"  {len(mentions):,} agent mentions")
    print(f"  {mentions.groupby(['name','father']).ngroups} unique individuals (name+father)")

    summary = summarize_agents(mentions)

    print()
    print("Top individuals by document count:")
    top = summary[summary["n_docs"] >= 3]
    for _, r in top.iterrows():
        span = f"{abs(r['earliest']):.0f}–{abs(r['latest']):.0f} BCE" \
               if r['earliest'] < 0 else f"{r['earliest']:.0f}–{r['latest']:.0f} CE"
        print(f"  {r['name']:18s} son of {r['father']:18s}  {r['n_docs']:2d} docs  "
              f"{span}  [{r['roles'] or 'no role'}]")

    out_m = PROC_DIR / "michigan_agents.csv"
    out_s = PROC_DIR / "michigan_agents_summary.csv"
    mentions.to_csv(out_m, index=False, encoding="utf-8-sig")
    summary.to_csv(out_s, index=False, encoding="utf-8-sig")
    print(f"\n-> {out_m}")
    print(f"-> {out_s}")


if __name__ == "__main__":
    main()
