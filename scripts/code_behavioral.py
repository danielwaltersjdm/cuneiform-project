"""
code_behavioral.py

Applies behavioral economics coding scheme to translated ancient documents.
Tags each document with binary flags for behavioral constructs.

Input:  any CSV with a 'translation_text' column (APIS, Elephantine, DMD, SAA, ADsD)
Output: same CSV with additional coding columns

Usage:
  python scripts/code_behavioral.py --input processed_data/papyri/apis_combined.csv
  python scripts/code_behavioral.py --input processed_data/elephantine/elephantine_records.csv
  python scripts/code_behavioral.py --input processed_data/deir_el_medina/dmd_records.csv
  python scripts/code_behavioral.py --all    # process all known corpora
"""

import argparse
import re
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent

# ---------------------------------------------------------------------------
# Behavioral coding scheme
# ---------------------------------------------------------------------------
# Each entry: (column_name, regex_pattern)
# column_name will be prefixed with "be_"

BEHAVIORAL_CODES = {
    # ---- LOSS AVERSION / PROSPECT THEORY ----
    # Explicit framing of outcomes as losses vs. gains
    "loss_framing": (
        r"\bloss(?:es)?\b|\blosing\b|\blost\b|\bdamage[sd]?\b|\bdestruct|\bdetri"
        r"|\binjur|\bsuffer(?:ed|ing)?\b|\bworse(?:ned)?\b|\bshortfall\b|\bdeficit\b"
        r"|\bsuffer(?:ing)? loss\b"
    ),
    "gain_framing": (
        r"\bgain[sd]?\b|\bprofit[s]?\b|\bbenef[it]|\badvantage\b|\bsurplus\b"
        r"|\bexcess\b|\bmore than expected\b|\bincrease[sd]?\b"
    ),
    "reference_point": (
        r"\bexpected\b|\bused to\b|\baccustomed\b|\bformer(?:ly)?\b|\bprevious(?:ly)?\b"
        r"|\busual(?:ly)?\b|\bcustom(?:ary)?\b|\bnormal(?:ly)?\b|\boriginal(?:ly)?\b"
        r"|\bas (?:before|agreed|promised|arranged|stipulated)\b"
    ),
    "complaint_petition": (
        r"\bcomplaint[s]?\b|\bcomplain(?:ing|ed)?\b|\bpetition[s]?\b|\bpetition(?:ing|ed)?\b"
        r"|\bappeal[s]?\b|\bprotest[s]?\b|\bgrievance[s]?\b|\bwrong(?:ed|ful)?\b"
        r"|\bunjust\b|\billegal\b|\bunlawful\b"
    ),

    # ---- OVERCONFIDENCE / OPTIMISM ----
    "certainty_claim": (
        r"\bcertain(?:ly)?\b|\bsurely\b|\bwithout doubt\b|\bno doubt\b|\bassuredly\b"
        r"|\bdefinitely\b|\bwill certainly\b|\bwill surely\b|\bI know\b|\bI am sure\b"
    ),
    "forecast_claim": (
        r"\bwill (?:arrive|come|pay|deliver|send|be)\b|\bshall\b|\bexpect[s]?\b"
        r"|\bpromise[sd]?\b|\bguarantee[sd]?\b|\bpledge[sd]?\b"
    ),
    "failed_prediction": (
        r"\bdid not arrive\b|\bdid not come\b|\bdid not pay\b|\bdid not deliver\b"
        r"|\bnot as expected\b|\bnot as promised\b|\bfailed to\b|\bcontrary to\b"
        r"|\bunexpectedly\b|\bsurpris(?:ed|ingly)\b"
    ),

    # ---- INTERTEMPORAL DISCOUNTING / HYPERBOLIC ----
    "interest_rate": (
        r"\binterest\b|\busury\b|\brate\b(?= of)|\bpercent\b|\bmonthly\b(?= payment)"
        r"|\bper month\b|\bper year\b|\bannual(?:ly)?\b"
    ),
    "loan_credit": (
        r"\bloan[s]?\b|\blend(?:ing|er|ers)?\b|\bborrow(?:ed|ing)?\b|\bcredit\b"
        r"|\bdebtor[s]?\b|\bcreditor[s]?\b|\bdebt[s]?\b|\bowe[sd]?\b|\bowing\b"
    ),
    "deferred_payment": (
        r"\bdue (?:in|on|by|within)\b|\bwhen .{1,30} arrives?\b|\bafter .{1,20} days?\b"
        r"|\bwithin .{1,15} days?\b|\bby the time\b|\buntil\b|\bdelay\b|\boverdue\b"
        r"|\bpayment .{1,20} later\b"
    ),

    # ---- FAIRNESS / RECIPROCITY ----
    "fairness_claim": (
        r"\bfair(?:ly|ness)?\b|\bunfair\b|\bequal\b|\binequal|\bjust(?:ice)?\b"
        r"|\bunjust\b|\bdeserv(?:e[sd]?|ing)\b|\brightful(?:ly)?\b|\bdue (?:to|me|him|her|us|you)\b"
    ),
    "reciprocity": (
        r"\bin return\b|\bin exchange\b|\brecipro|\brepay\b|\bcompensate\b"
        r"|\breward[ed]?\b|\breturn the favor\b|\bin kind\b"
    ),

    # ---- PRICE / COMMODITY DATA ----
    "price_mention": (
        r"\bprice[sd]?\b|\bworth\b|\bvalue[sd]?\b|\bcost[sd]?\b|\brate\b"
        r"|\bsell(?:ing)? (?:price|for)\b|\bbought? (?:at|for)\b|\bpurchased? (?:at|for)\b"
    ),
    "commodity_grain": (
        r"\bartaba[e]?\b|\bgrain\b|\bwheat\b|\bbarley\b|\bspelt\b"
        r"|\bsesame\b|\bpulse[s]?\b|\blegum"
    ),
    "commodity_money": (
        r"\bdrachm[ae]?i?\b|\btalent[s]?\b|\bdenarii\b|\bsesterc|\bsilver\b|\bgold\b"
        r"|\bdeben\b|\bkite\b|\bcopper\b|\bshek(?:el|el)s?\b|\bmina[es]?\b"
    ),

    # ---- LABOR / EFFORT ----
    "labor_absence": (
        r"\bdid not (?:work|come|appear|report)\b|\bwas absent\b|\babsence\b"
        r"|\bdid not bring\b|\bstrike\b|\brefus(?:ed|ing) to work\b|\bidle\b"
    ),
    "wage_payment": (
        r"\bwage[s]?\b|\bsalary\b|\bpay(?:ment)? (?:for|of) (?:work|labor|service)\b"
        r"|\bhired?\b|\bworkman\b|\blabourer\b|\bslave[s]?\b"
    ),

    # ---- RISK / UNCERTAINTY ----
    "risk_mention": (
        r"\brisk[s]?\b|\bdanger[s]?\b|\bhazard\b|\buncertain\b|\bchance\b"
        r"|\bloss (?:at sea|in transit|by theft)\b|\bperil\b"
    ),
    "contract_formal": (
        r"\bcontract[s]?\b|\bagreement[s]?\b|\bstipulat|\baccording to the\b"
        r"|\bas agreed\b|\bhereby\b|\bwitness(?:es)?\b|\bseal(?:ed)?\b|\bsigned\b"
    ),

    # ---- TAX / INSTITUTIONAL ----
    "tax_tribute": (
        r"\btax(?:es)?\b|\btribute\b|\breceipt[s]?\b|\barithmesis\b|\btelonion\b"
        r"|\bcustom[s]? (?:duty|duties)\b|\bimpost\b|\blevy\b"
    ),
}


# ---------------------------------------------------------------------------
# Apply coding
# ---------------------------------------------------------------------------

def code_corpus(df: pd.DataFrame, text_col: str = "translation_text") -> pd.DataFrame:
    """Add behavioral coding columns to df. Returns df with new columns."""
    t = df[text_col].fillna("").astype(str)

    for label, pattern in BEHAVIORAL_CODES.items():
        col = f"be_{label}"
        df[col] = t.str.contains(pattern, case=False, regex=True)

    # Derived composite flags
    df["be_loss_aversion_signal"] = df["be_loss_framing"] | df["be_complaint_petition"]
    df["be_overconfidence_signal"] = df["be_certainty_claim"] | df["be_forecast_claim"]
    df["be_calibration_signal"]   = df["be_forecast_claim"] & df["be_failed_prediction"]
    df["be_economic_core"]        = (
        df["be_price_mention"] | df["be_commodity_grain"] | df["be_commodity_money"] |
        df["be_loan_credit"]   | df["be_tax_tribute"]
    )
    return df


def summarize(df: pd.DataFrame, label: str) -> None:
    be_cols = [c for c in df.columns if c.startswith("be_")]
    print(f"\n=== {label} ({len(df):,} docs) ===")
    for col in be_cols:
        n = df[col].sum()
        if n > 0:
            print(f"  {col:35s}: {n:5,}  ({100*n/len(df):.1f}%)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

CORPORA = {
    "apis_combined":  "processed_data/papyri/apis_combined.csv",
    "elephantine":    "processed_data/elephantine/elephantine_records.csv",
    "dmd":            "processed_data/deir_el_medina/dmd_records.csv",
    "saa":            "processed_data/neo_assyrian/letters_translations.csv",
    "diaries":        "processed_data/babylonian_diaries/diary_translations.csv",
}

TEXT_COLS = {
    "apis_combined":  "translation_text",
    "elephantine":    "translation_text",
    "dmd":            "contents",
    "saa":            "translation",
    "diaries":        "translation",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Path to input CSV")
    parser.add_argument("--text-col", default="translation_text",
                        help="Column name for text content")
    parser.add_argument("--all", action="store_true", help="Process all known corpora")
    args = parser.parse_args()

    if args.all:
        for name, path in CORPORA.items():
            full_path = PROJECT_ROOT / path
            if not full_path.exists():
                print(f"Skipping {name} (not found: {path})")
                continue
            df = pd.read_csv(full_path)
            text_col = TEXT_COLS.get(name, "translation_text")
            if text_col not in df.columns:
                print(f"Skipping {name} (column '{text_col}' not found)")
                continue
            df = code_corpus(df, text_col)
            out = full_path.parent / f"{full_path.stem}_coded.csv"
            df.to_csv(out, index=False, encoding="utf-8-sig")
            summarize(df, name)
            print(f"  -> {out}")
        return

    if not args.input:
        parser.print_help()
        return

    input_path = Path(args.input)
    df = pd.read_csv(input_path)
    df = code_corpus(df, args.text_col)
    out = input_path.parent / f"{input_path.stem}_coded.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")
    summarize(df, input_path.stem)
    print(f"\n-> {out}")


if __name__ == "__main__":
    main()
