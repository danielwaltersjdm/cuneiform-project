# Pre-Registration Draft
# Behavioral Economics Signals in Ancient Documentary Corpora

**Author:** Daniel Walters, Tulane University
**ORCID:** 0000-0002-0121-7178
**Date:** 2026-04-06 (draft, not yet submitted)
**Target registry:** OSF Registries (osf.io)

---

## 1. Title

Cross-Cultural Behavioral Economics Signals in Ancient Documentary Corpora:
A Computational Analysis of Loss Aversion, Overconfidence, and Intertemporal
Discounting Across Six Corpora (650 BCE – 640 CE)

---

## 2. Research Questions

**Primary:**
1. Do ancient documentary texts exhibit language patterns consistent with behavioral
   economics constructs (loss aversion, overconfidence, intertemporal discounting)?
2. Does the prevalence of these signals vary systematically across document type,
   institutional context, and historical period?

**Secondary:**
3. Are loss-framing signals more prevalent in documents from periods of documented
   economic scarcity or institutional crisis?
4. Do expert advisors (SAA scholars, astrological scribes) show higher overconfidence
   signals than non-expert letter writers in the same corpus?
5. Is there evidence of calibration — defined as co-occurrence of forecast claims and
   failure acknowledgments in the same document?

---

## 3. Hypotheses

All hypotheses are stated in terms of behavioral code rates (% of documents in a
group carrying a signal). All tests are pre-registered before hypothesis testing begins.

**H1 (Loss aversion asymmetry):** The ratio of loss-framing to gain-framing signals
across the combined corpus will be greater than 1.0, consistent with the asymmetric
attention to losses predicted by prospect theory.
*Expected direction: loss > gain.*

**H2 (Expert overconfidence):** SAA astrological scribes (SAA08) and scholar-advisors
(SAA10) will show higher forecast_claim and certainty_claim rates than administrative
letter writers in the same corpus (SAA01, SAA15–21).
*Expected direction: SAA08/SAA10 > administrative volumes.*

**H3 (Calibration rarity):** The calibration signal (forecast AND failed_prediction
in same document) will appear in fewer than 5% of forecast-claim documents,
consistent with motivated reasoning models predicting that agents avoid acknowledging
forecast failures.
*Expected direction: calibration_signal / forecast_claim < 0.05.*

**H4 (Petition loss framing):** The loss-aversion signal rate in petition/complaint
documents will be higher than in non-petition documentary texts within the same corpus
(APIS Michigan).
*Expected direction: petition genre > ostracon/letter genres.*

**H5 (Price-behavior correlation):** In the Babylonian Astronomical Diaries, diary
entries from years when barley prices are in the loss domain (above the 5-year rolling
median) will show higher rates of loss_framing, complaint, and reference_point signals
than entries from gain-domain years.
*Expected direction: loss-domain years show higher behavioral signal rates.*

---

## 4. Corpora and Data Sources

All data is open-access and archived prior to analysis.

| Corpus | Docs | Translated | Period | Source |
|---|---|---|---|---|
| SAA Neo-Assyrian Letters | 3,302 | 3,302 | 911–609 BCE | ORACC (oracc.museum.upenn.edu) |
| Babylonian Astron. Diaries | 404 | 404 | 652 BCE – 61 CE | ADART TEI XML |
| APIS Michigan | 3,582 | 3,283 | 250 BCE – 400 CE | papyri.info |
| APIS Combined | 17,780 | 4,967 | 350 BCE – 640 CE | papyri.info |
| Elephantine ERC | 252 | 235 | 500 BCE – 700 CE | elephantine.smb.museum |
| Deir el-Medina DMD | 4,706 | 4,139 | 1550–1070 BCE | dmd.wepwawet.nl |

**Pre-analysis data freeze:** All corpus files are committed to GitHub
(github.com/danielwaltersjdm/cuneiform-project) with hash `db54a55` prior to hypothesis testing.

---

## 5. Coding Scheme

Behavioral codes are applied via regex pattern matching to English translation text.
All code definitions, patterns, and composite flag logic are documented in
`scripts/code_behavioral.py` (committed prior to analysis).

**22 primary codes** covering loss aversion, overconfidence, intertemporal discounting,
fairness/reciprocity, price/commodity, labor, risk, and institutional/tax language.

**4 composite flags:**
- `be_loss_aversion_signal` = loss_framing OR complaint_petition
- `be_overconfidence_signal` = certainty_claim OR forecast_claim
- `be_calibration_signal` = forecast_claim AND failed_prediction
- `be_economic_core` = price_mention OR commodity_grain OR commodity_money OR loan_credit OR tax_tribute

**Scope limitation:** Regex-based coding captures surface-level lexical patterns;
it does not capture irony, negation ("I am not certain"), or discourse-level framing.
All findings should be interpreted as lower-bound prevalence estimates.

---

## 6. Exclusion Criteria

- Documents with fewer than 20 words of translated text are excluded from analysis.
- Documents marked as literary (poetry, hymns) are excluded from documentary analysis
  but retained in the full dataset.
- Lacunas ([...]) are left in place; regex patterns do not match across lacunas.

---

## 7. Analysis Plan

### 7.1 Descriptive (already complete as of pre-registration)
- Signal prevalence by corpus, volume, and document type
- Loss-to-gain ratio across combined corpus
- Calibration rate = calibration_signal / forecast_claim

### 7.2 Inferential (to be run after pre-registration)

**H1:** One-sample test: loss-to-gain ratio > 1 (binomial or chi-square)
**H2:** Two-proportion z-test: SAA08+SAA10 forecast rate vs. SAA01/15–21 forecast rate
**H3:** One-sample proportion test: calibration_signal / forecast_claim < 0.05
**H4:** Two-proportion z-test: loss_signal in petition genre vs. ostracon genre (Michigan)
**H5:** Wilcoxon rank-sum test: loss_signal rate in loss-domain years vs. gain-domain years

### 7.3 Multiple comparisons
All hypothesis tests use Bonferroni correction (α/5 = 0.01 per test).

---

## 8. Limitations

1. **Translation scope:** Behavioral coding applies only to English translations.
   Corpora with low translation rates (Kanesh: 0.4%, Elephantine: 93%) may have
   non-representative translation selection.

2. **Regex validity:** No inter-rater reliability study; regex codes have not been
   validated against human coding. Future work should include human coding of a
   random sample.

3. **Temporal confounding:** Cross-period and cross-corpus comparisons conflate
   changes in genre conventions, scribal training, and document preservation with
   behavioral differences.

4. **Survival bias:** Administrative documents (the bulk of all corpora) survive at
   higher rates than ephemeral communications; complaint/petition documents may be
   overrepresented relative to their original production rate.

5. **No individual-level data:** With the exception of the Karanis ostraca (Michigan,
   262–312 CE), individual-level panel data is not available. Aggregate rates are
   ecological proxies.

---

## 9. Timeline

- Pre-registration submission: April 2026
- Analysis (inferential): April–May 2026
- Write-up: May–June 2026
- Submission target: Journal of Economic Behavior & Organization or PLOS ONE

---

## 10. Data and Code Availability

All data, scripts, and notebooks are publicly archived at:
- **GitHub:** github.com/danielwaltersjdm/cuneiform-project (CC-BY 4.0 / MIT)
- **OSF:** osf.io (node to be linked at pre-registration)

Original corpora are third-party data (ORACC, papyri.info, DMD, Elephantine ERC)
and are subject to their respective open-access licenses.
