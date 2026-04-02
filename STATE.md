# Project State

_Last updated: 2026-04-02_

## Done

- [x] Downloaded 8 SAA Neo-Assyrian letter volumes from ORACC (TEI XML, ~38 MB)
- [x] Parsed all 1,993 SAA letters into `letters_translations.csv`
- [x] Parsed transliterations into `neo_assyrian_letters_tokens.csv` (209,940 tokens)
- [x] Extracted 2,476 numerical estimates into `numerical_estimates.csv`
- [x] Built EDA notebook (`01_explore_corpus.ipynb`) for SAA corpus
- [x] Downloaded Old Assyrian Kanesh corpus (ATF + Text-Fabric, ~86 MB)
- [x] Reorganized folder structure into `neo_assyrian/` and `kanesh/` subfolders
- [x] Updated all script and notebook paths after reorganization
- [x] Evaluated SAA corpus for behavioral research suitability (verdict: poor fit)
- [x] Evaluated Kanesh corpus for behavioral research suitability (verdict: strong fit)
- [x] Reviewed 10 example financial transactions from translated Kanesh tablets
- [x] Created `docs/kanesh_corpus_notes.md`

## In Progress

- [ ] Deciding how to solve the translation gap (67/4,775 Kanesh tablets translated)
  - Option A: LLM-based translation of Akkadian transliterations
  - Option B: Source additional translations from ARCHIBAB or published corpora

## Blocked

- [ ] `scripts/kanesh/parse_atf.py` — not yet built; needed before any Kanesh analysis
- [ ] Kanesh behavioral analysis — blocked on translation coverage
- [ ] Forecast-outcome matching — blocked on parse_atf.py and translation coverage

## Planned (Not Started)

- [ ] Build `scripts/kanesh/parse_atf.py` → `processed_data/kanesh/kanesh_tablets.csv`
- [ ] LLM-assisted coding of letters for: price predictions, confidence level, gain/loss framing, conditional clauses
- [ ] Sentiment asymmetry analysis (loss vs. gain language)
- [ ] Conditional clause extraction and prospect-theory framing test
- [ ] Price expectation vs. outcome matching (overconfidence/calibration test)
- [ ] Merchant network analysis (named agents across multiple tablets)
- [ ] Download SAA04, SAA08, SAA09, SAA10 (oracle/astrological volumes) as secondary corpus
