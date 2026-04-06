# Project State

_Last updated: 2026-04-06_

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
- [x] Downloaded papyri.info DDB EpiDoc XML: P.Zen (77), P.Oxy (3,451), P.Mich (818), P.Eleph (35), T.Vindol (523), P.Ness (176)
- [x] Downloaded APIS institutional XML: 29 institutions, 17,780 docs, 4,967 translated (28%)
  - Michigan: 3,582 docs, 3,283 translated (92%) — primary behavioral corpus
  - Chicago: 253 docs, 100% translated
  - Berkeley: 1,665 docs, 492 translated
  - Berenike: 261 docs, 205 translated
  - Combined: `processed_data/papyri/apis_combined.csv`
- [x] Built `scripts/fetch_papyri.py` — DDB EpiDoc + APIS XML downloader
- [x] Built `scripts/parse_epidoc.py` — parses DDB transcription + APIS institutional records
- [x] Built `notebooks/02_papyri_economic_eda.ipynb` — papyri economic signal EDA
  - 48% of translated docs have economic content
  - 519 payment, 349 grain/wheat, 308 tax/receipt, 60 complaint/loss, 76 loan/debt, 52 interest docs
- [x] Built `scripts/fetch_dmd.py` — DMD scraper (Deir el-Medina, 4,706 records)
- [x] Built `scripts/fetch_elephantine.py` — Elephantine TEI-XML downloader (252 records)
- [x] Added P.Babatha, P.Dura, P.Cair.Zen, P.Iand.Zen to fetch_papyri.py

## In Progress

- [ ] DMD download: ~522/4,706 records (~11%)
- [ ] Elephantine download: ~175/252 records (~69%)
- [ ] P.Babatha, P.Dura, P.Iand.Zen downloads (small collections, <200 files each)

## Blocked

- [ ] Kanesh behavioral analysis — blocked on translation coverage (6/1,385 letters translated)
- [ ] Ur III / OB behavioral analysis — ATF downloaded but mostly untranslated; need ARCHIBAB
- [ ] Nuzi Archives — HARD (2,335 CDLI tablets, 1 translation, no bulk digital source)
- [ ] Amarna Letters — HARD (ORACC projects are empty shells, English ed. Moran 1992 print-only)
- [ ] Turin Strike Papyrus — HARD (English translation still in preparation on TPOP)

## Planned (Not Started)

- [ ] Parse DMD records → `processed_data/deir_el_medina/dmd_records.csv`
- [ ] Parse Elephantine records → `processed_data/elephantine/elephantine_records.csv`
- [ ] Parse P.Babatha, P.Dura, P.Iand.Zen via parse_epidoc.py
- [ ] ARCHIBAB translations for Old Babylonian — decision pending (scraper needed)
- [ ] LLM-assisted behavioral coding of economic papyri (60 complaint/loss docs, 76 loan docs)
- [ ] Price series extraction from grain/commodity papyri
- [ ] Interest rate extraction from loan documents
- [ ] Named-agent network analysis (Michigan tax receipt corpus)
- [ ] Behavioral coding scheme for Kanesh letters
