# Project State

_Last updated: 2026-04-06 (Session 3)_

## Done

- [x] Downloaded 8 SAA Neo-Assyrian letter volumes from ORACC (TEI XML, ~38 MB)
- [x] Parsed all SAA letters into `letters_translations.csv` (3,302 texts across 12 volumes)
- [x] Parsed transliterations into `neo_assyrian_letters_tokens.csv` (209,940 tokens)
- [x] Extracted 2,476 numerical estimates into `numerical_estimates.csv`
- [x] Built EDA notebook (`01_explore_corpus.ipynb`) for SAA corpus
- [x] Downloaded Old Assyrian Kanesh corpus (ATF + Text-Fabric, ~86 MB)
- [x] Reorganized folder structure into `neo_assyrian/` and `kanesh/` subfolders
- [x] Built `scripts/parse_atf.py` → `processed_data/kanesh/kanesh_tablets.csv` (6,614 tablets)
- [x] Created `docs/corpus_master.md` — master download target list (65 corpora, tiered by signal strength)
- [x] Downloaded Babylonian Astronomical Diaries adart1–3; parsed 404 translated entries
- [x] Downloaded full CDLI ATF corpus (83 MB, 3.5M lines) + catalogue (148 MB, 353,283 tablets)
- [x] Extracted CDLI period subsets: Ur III (77,531 ATF + 110,984 catalogue), OB (13,527 + 66,236), OA (6,452), NB (15,633)
- [x] Downloaded papyri.info DDB EpiDoc XML: P.Zen (77), P.Oxy (3,451), P.Mich (818), P.Eleph (35), T.Vindol (523), P.Ness (176), P.Babatha (28), P.Dura (139), P.Cair.Zen (5), P.Iand.Zen (82)
- [x] Downloaded APIS institutional XML: 29 institutions, 17,780 docs, 4,967 translated (28%)
  - Michigan: 3,582 docs, 3,283 translated (92%) — primary behavioral corpus
  - Combined: `processed_data/papyri/apis_combined.csv`
- [x] Built `scripts/fetch_papyri.py`, `scripts/parse_epidoc.py`
- [x] Built `notebooks/02_papyri_economic_eda.ipynb` — papyri EDA (48% economic, 60 complaint/loss docs)
- [x] **Deir el-Medina DMD: 4,706 records downloaded and parsed**
  - 3,936 ostraca, 344 papyri, 4,139 with contents
  - `processed_data/deir_el_medina/dmd_records.csv` + `_coded.csv`
  - Top coded signals: 753 economic core (16%), 408 grain (8.7%), 284 wage (6%), 75 labor absence
- [x] **Elephantine ERC: 252 records downloaded and parsed (235 translated, 93%)**
  - `processed_data/elephantine/elephantine_records.csv` + `_coded.csv`
- [x] **Behavioral coding applied to all 5 corpora** (`scripts/code_behavioral.py`)
  - apis_combined, elephantine, dmd, saa (letters), babylonian_diaries
  - 22 behavioral codes + 4 composite flags
- [x] **`scripts/extract_diary_prices.py`** — 664 commodity price observations extracted
  - `processed_data/babylonian_diaries/diary_prices.csv`
  - Barley: 127 obs, 567–75 BCE; also dates, mustard, cress, sesame
- [x] **`notebooks/03_saa_overconfidence_analysis.ipynb`** — SAA overconfidence/calibration
  - 26.1% overconfidence signal; 11 calibration documents; loss-to-gain framing ratio by volume
- [x] **`notebooks/04_babylonian_diaries_prices.ipynb`** — price series analysis
  - Volatility analysis (CV), shock detection, co-movement correlations, reference-point framing

## Blocked

- [ ] Kanesh behavioral analysis — blocked on translation coverage (6/1,385 letters translated)
- [ ] Ur III / OB behavioral analysis — ATF downloaded but mostly untranslated; need ARCHIBAB
- [ ] Nuzi Archives — HARD (2,335 CDLI tablets, 1 translation, no bulk digital source)
- [ ] Amarna Letters — HARD (ORACC projects are empty shells; Moran 1992 print-only)
- [ ] Turin Strike Papyrus — HARD (English translation in preparation)
- [ ] ARCHIBAB (Neo-Babylonian/Murashû/Egibi) — HARD (French only, account required)

## Next Priorities

1. **Run notebooks 03 and 04** to generate output charts → `outputs/` directory
2. **APIS interest rate extraction** — 52 docs with interest mentions in Michigan corpus
3. **Named-agent network** — Michigan tax receipts, recurring individuals
4. **Price–behavior linkage** — correlate diary price shocks with SAA letter loss-framing dates
5. **Pre-registration** — draft OSF pre-reg for behavioral coding analysis (before hypothesis testing)
6. **Tier 2 free downloads** — Heqanakht, Turin Strike (if available), classical Greek inscriptions
