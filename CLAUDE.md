# Cuneiform Project — Project Knowledge

## Research Goal

Analyze ancient cuneiform tablet data for evidence of behavioral biases: overconfidence, loss aversion, prospect theory effects, and related judgment biases. Primary focus is the Old Assyrian Kanesh merchant corpus (~1950–1850 BCE).

## Architecture

```
raw_data/
  neo_assyrian/       SAA TEI XML corpora (8 volumes, ORACC)
  kanesh/             Old Assyrian merchant texts (CDLI/Nino-cunei)
processed_data/
  neo_assyrian/       Parsed CSVs from SAA corpus
  kanesh/             (empty — awaiting parse_atf.py)
outputs/
  neo_assyrian/       Charts from EDA notebook
  kanesh/             (empty)
notebooks/            Jupyter analysis notebooks
scripts/              Python ETL scripts
docs/                 Reference notes and corpus documentation
```

## Corpora

### Neo-Assyrian SAA Letters (`raw_data/neo_assyrian/`)
- 8 SAA volumes (SAA01, 05, 15–19, 21), TEI XML format from ORACC
- 1,993 letters, ~209,940 tokens, all with English translations
- Processed into: `letters_translations.csv`, `text_summary.csv`, `numerical_estimates.csv`, `neo_assyrian_letters_tokens.csv`
- **Assessment:** Royal correspondence — poorly suited for behavioral analysis. Numbers are mostly troop counts and distances, not forecasts or prices.

### Old Assyrian Kanesh Corpus (`raw_data/kanesh/`)
- Source: Nino-cunei/oldassyrian v0.1 (Zenodo DOI: 10.5281/zenodo.3909515), derived from CDLI
- 4,775 tablets: ~1,385 letters, ~782 administrative, ~468 legal
- Two formats: `cdli_old_assyrian_atf.txt` (7.9 MB ATF) + `Nino-cunei/oldassyrian/tf/` (63 MB Text-Fabric)
- **Only 67 tablets have English translations** in the ATF file — the rest are transliteration-only (Akkadian)
- 11,500+ silver mentions, 12,800+ weight-unit mentions; rich price/transaction data
- **Assessment:** Primary target for behavioral analysis. Named repeated agents, explicit price expectations, conditional clauses, loan/debt records.

## Key Conventions

- Scripts use `Path(__file__).parent.parent` as project root — all data paths are relative to that
- All scripts accept `--project` and `--output` CLI args for targeted runs
- ORACC XML parsing uses `recover=True` (lxml) to handle invalid xml:id colons in ORACC output
- ATF format: metadata block per tablet, transliteration lines, `#tr.en:` for English translations
- Text-Fabric corpus queryable via `pip install text-fabric` + `tf` Python library

## Key Assumptions

- The **translation gap** (67/4,775 tablets translated) is the binding constraint for behavioral analysis
- Linking forecast letters to outcome records requires cross-document matching by merchant name + eponym date + commodity — non-trivial
- Behavioral signals most tractable: (1) conditional clause framing, (2) sentiment asymmetry in gain vs. loss letters, (3) price expectation vs. outcome matching where translations exist
- Machine translation of Akkadian transliterations via LLM is the highest-leverage next step

## Python Environment

- `venv/` at project root; activate with `venv/Scripts/activate`
- Python executable: `venv/Scripts/python.exe`
- Key deps: pandas, lxml, tqdm, beautifulsoup4, requests, matplotlib, seaborn, jupyter
