# Project State

_Last updated: 2026-04-06_

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
- [x] Built `scripts/parse_atf.py` → `processed_data/kanesh/kanesh_tablets.csv` (6,614 tablets)
- [x] Created `docs/corpus_master.md` — master download target list (65 corpora, tiered by signal strength)
- [x] Downloaded SAA04, SAA08, SAA09, SAA10 (oracle/forecast volumes); parsed 1,309 texts
- [x] Downloaded Babylonian Astronomical Diaries adart1–3; parsed 404 translated entries
- [x] Downloaded full CDLI ATF corpus (83 MB, 3.5M lines) and catalogue (148 MB, 353,283 tablets)
- [x] Extracted Ur III subset: 77,531 ATF blocks + 110,984 catalogue entries
- [x] Extracted Old Babylonian subset: 13,527 ATF blocks + 66,236 catalogue entries
- [x] Downloaded papyri.info DDB EpiDoc XML: P.Zen (77), P.Oxy (3,451), P.Mich (818), P.Eleph (35), T.Vindol (523), P.Ness (176)
- [x] Downloaded APIS institutional XML from 29 institutions: 9,419 total docs, 2,326 with English translation
  - High translation coverage: michigan (98%), chicago (100%), oslo (89%), wisconsin (89%), berenike (79%)
  - No translation (metadata only): columbia, oxford-ipap, yale, duke, britmus, fordham
  - Combined into `processed_data/papyri/apis_combined.csv`
- [x] Built `scripts/fetch_papyri.py` — downloads DDB EpiDoc + APIS XML from papyri/idp.data GitHub repo
- [x] Built `scripts/parse_epidoc.py` — parses both DDB transcription files and APIS institutional records

## In Progress

- [ ] Corpus acquisition — see `docs/corpus_master.md` for full queue
  - Next: Deir el-Medina (DMD scraper needed)
- [ ] Translation gap for Kanesh (6 Letter tablets with translations out of 1,385 letters)
  - Option A: LLM-based translation of Akkadian transliterations
  - Option B: Source ARCHIBAB translations (also needed for Old Babylonian)

## Blocked

- [ ] Kanesh behavioral analysis — blocked on translation coverage
- [ ] Ur III / OB behavioral analysis — ATF downloaded but mostly untranslated; need ARCHIBAB or LLM
- [ ] Forecast-outcome matching — blocked on translation coverage

## Planned (Not Started)

- [ ] Build `scripts/kanesh/parse_atf.py` → `processed_data/kanesh/kanesh_tablets.csv`
- [ ] LLM-assisted coding of letters for: price predictions, confidence level, gain/loss framing, conditional clauses
- [ ] Sentiment asymmetry analysis (loss vs. gain language)
- [ ] Conditional clause extraction and prospect-theory framing test
- [ ] Price expectation vs. outcome matching (overconfidence/calibration test)
- [ ] Merchant network analysis (named agents across multiple tablets)
- [ ] Download SAA04, SAA08, SAA09, SAA10 (oracle/astrological volumes) as secondary corpus
