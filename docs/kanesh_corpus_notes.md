# Kanesh (Old Assyrian) Corpus — Download Notes & Research Assessment

## Download Summary

**Date downloaded:** 2026-04-02
**Saved to:** `raw_data/kanesh/`
**Total size:** ~86 MB (63 MB TF + 15 MB ZIP + 7.9 MB ATF)

---

## Files Downloaded

### 1. `cdli_old_assyrian_atf.txt` — 7.9 MB, 319,126 lines
- **Source:** GitHub: Nino-cunei/oldassyrian (sourced from CDLI bulk export)
- **Format:** ATF (ASCII Transliteration Format) — plain text, standard for cuneiform
- **Contents:** 4,775 tablets with full transliterations + metadata headers
- **Metadata per tablet:** primary publication, provenience, period, genre, museum number, CDLI P-number, author
- **Breakdown:**
  - ~1,385 letters
  - ~782 administrative records
  - ~468 legal documents
  - Balance: contracts, school texts, miscellaneous
- **Key signals:** 11,537 mentions of silver (kaspu); 12,884 mentions of weight units (mana/shekel)
- **Translations:** Partial — many tablets have `#tr.en:` lines; others marked "uncertain"

### 2. `Nino-cunei/oldassyrian/` — 63 MB (extracted from `nino-cunei-oldassyrian-complete.zip`)
- **Source:** https://github.com/Nino-cunei/oldassyrian (v0.1, Zenodo DOI: 10.5281/zenodo.3909515)
- **Format:** Text-Fabric (TF) — graph-based annotation format, Python-readable
- **Contents:** Same 4,774 tablets as the ATF file, restructured into per-feature binary annotation files
- **Node counts:** 766,501 signs, ~314,012 words, ~109,860 lines, 4,775 documents = 1,289,143 annotated nodes
- **Feature files include:** `reading.tf`, `translation@en.tf`, `genre.tf`, `subgenre.tf`, `period.tf`, `author.tf`, `pnumber.tf`, `ln.tf`, `atf.tf`, and ~55 others
- **Best for:** Structured Jupyter analysis using the `tf` Python library; enables queries like "all tablets by merchant X mentioning silver"

### 3. `nino-cunei-oldassyrian-complete.zip` — 15 MB (kept as archive backup)

---

## What This Corpus Is

The **Old Assyrian merchant texts from Kültepe/Kanesh** (~1950–1850 BCE) are the commercial archive of Assyrian merchants operating a long-distance trade network between Assur (northern Iraq) and Kanesh (central Anatolia, modern Kültepe, Turkey). Merchants traded primarily in tin, textiles, and silver.

The archive survived because clay tablets were stored in the merchant houses at Kanesh and preserved when the city burned. Most tablets were found by illegal excavation and are now scattered across museums; the CDLI/OATP has been systematically digitizing them.

---

## Research Relevance for Behavioral Economics

### Strongest signals for each research question:

| Behavioral Construct | What to Look For | Evidence in Corpus |
|---|---|---|
| **Loss aversion** | Language of losses vs. gains; asymmetric emotional language in response to bad vs. good outcomes | Letters contain explicit grievance language ("I suffered a loss", "you ruined me"); compare sentiment intensity for gain vs. loss events |
| **Prospect theory** | Risk-taking under different reference points; willingness to accept certain vs. uncertain outcomes | Partnership contracts specify fixed vs. variable returns; some letters discuss accepting a certain lower price vs. waiting |
| **Overconfidence** | Price predictions that systematically miss; stated certainty vs. actual outcomes | Letters contain price expectations ("sell if it reaches X"); compare against administrative records of actual prices |
| **Reference dependence** | Changes in behavior relative to a stated target or expectation | "I expected 10 minas; I received 7" structures appear in letters |

### Key assets:
- **Named, repeated agents:** The same merchant names (Puzur-Assur, Imdi-ilum, etc.) appear across dozens of tablets — essential for individual-level behavioral analysis
- **Eponym dating:** Tablets can be dated to specific Assyrian eponym years, enabling chronological ordering
- **Price data:** Silver prices, textile prices, and exchange rates are explicitly stated
- **Conditional clauses:** "If the price is good, sell; if not, hold" constructions directly encode reference-point reasoning

### Limitations:
- Most texts are in Akkadian transliteration; English translations are partial
- Linking "prediction" tablets to "outcome" tablets requires manual or semi-automated matching
- No single tablet contains both forecast and outcome — cross-tablet linking is needed

---

## Recommended Next Steps

1. **Install Text-Fabric** (`pip install text-fabric`) and explore the TF corpus in a notebook
2. **Extract letter tablets** — filter `genre == "letter"` and build a translations CSV
3. **Extract price mentions** — identify silver/commodity quantity patterns across all genres
4. **Map merchant networks** — link tablets by named sender/recipient for repeated-agent analysis
5. **Build forecast-outcome pairs** — match letters containing price expectations to administrative records

---

## Action Log

| Date | Action | Detail |
|---|---|---|
| 2026-04-02 | Downloaded ATF file | `raw_data/kanesh/cdli_old_assyrian_atf.txt` (7.9 MB) |
| 2026-04-02 | Downloaded TF corpus | `raw_data/kanesh/Nino-cunei/oldassyrian/` (63 MB, via nino-cunei-oldassyrian-complete.zip) |
| 2026-04-02 | Created this notes file | `docs/kanesh_corpus_notes.md` |
