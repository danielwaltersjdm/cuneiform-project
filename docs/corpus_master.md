# Master Corpus Target List

_Source: `docs/corpus_survey.md` (65 corpora surveyed)_
_Last updated: 2026-04-06_

This document is the working download and analysis plan. It lists every corpus worth targeting, their download status, and digital home. The survey document is the reference; this is the action list.

---

## Download Status Key

- **DONE** — downloaded and parsed
- **QUEUE** — should be downloaded; freely available
- **PARTIAL** — partially available; download what's accessible
- **HARD** — behind paywall or physical archives only; note options
- **SKIP** — undeciphered, inaccessible, or signal too low

---

## Tier 1 — Highest Behavioral Signal

These are the priority downloads. All have explicit price/forecast data, named recurring agents, or complaint/loss framing.

| # | Corpus | Signal | Status | Digital Home |
|---|---|---|---|---|
| 1.5 | Old Assyrian / Kanesh (c. 1950–1750 BCE) | Highest | **DONE** | CDLI ATF + Nino-cunei TF |
| 1.12 | Neo-Assyrian SAA Letters (c. 911–609 BCE) | High | **DONE** (SAA01,05,15–19,21) | https://oracc.museum.upenn.edu/saao/ |
| 1.13 | SAA Oracle/Forecast Volumes: SAA04, SAA08, SAA09, SAA10 | Highest (forecast) | **DONE** | SAA04: 348 texts; SAA08: 566; SAA09: 8; SAA10: 387. Parsed into `processed_data/neo_assyrian/letters_translations.csv` |
| 1.15 | Babylonian Astronomical Diaries (c. 652 BCE – 61 CE) | Highest (price series) | **DONE** | adart1–3 downloaded; 404 translated entries → `processed_data/babylonian_diaries/diary_translations.csv`. adart5/6 had no downloadable files. |
| 2.8 | Roman Egypt Papyri / Oxyrhynchus (30 BCE – 640 CE) | Highest (scale) | **DONE** | 3,451 DDB EpiDoc XML files → `raw_data/papyri/p.oxy/`; parsed → `processed_data/papyri/p.oxy_parsed.csv`. APIS: michigan (822 docs, 98% translated), chicago (100%), columbia (797, metadata-only), + 27 more institutions → `processed_data/papyri/apis_combined.csv` (9,419 docs, 24.7% translated) |
| 1.3 | Ur III Administrative Archives (c. 2112–2004 BCE) | High (institutional) | **DONE** | 110,984 catalogue entries + 77,531 ATF blocks → `raw_data/cdli_bulk/ur3_atf.txt` + `processed_data/cdli_bulk/cdli_cat_ur3.csv`. Note: mostly untranslated (transliterations only). |
| 1.7 | Old Babylonian: Sippar, Larsa (c. 2000–1600 BCE) | High (loans, prices) | **DONE** | 66,236 catalogue entries + 13,527 ATF blocks → `raw_data/cdli_bulk/old_babylonian_atf.txt` + `processed_data/cdli_bulk/cdli_cat_old_babylonian.csv`. Mostly untranslated; ARCHIBAB translations still to source separately. |
| 1.9 | Nuzi Archives (c. 1500–1350 BCE) | High (individual) | **QUEUE** | https://cdli.earth |
| 2.4 | Deir el-Medina Ostraca and Papyri (c. 1550–1070 BCE) | High (labor/loss) | **QUEUE** | https://dmd.wepwawet.nl/ |
| 5.1 | Pompeii Wax Tablets: Sulpicii Archive (1st century CE) | High (risk/credit) | **HARD** | Trismegistos; academic editions only |
| 5.9 | Karanis Papyri (c. 1st–4th century CE) | High (community) | **DONE** | Included in APIS michigan (822 docs, P.Mich series); also P.Mich EpiDoc → `raw_data/papyri/p.mich/` (818 files) |

---

## Tier 2 — High Behavioral Signal

Strong evidence of one or more bias types; download once Tier 1 is complete.

| # | Corpus | Signal | Status | Digital Home |
|---|---|---|---|---|
| 1.14 | Neo-Babylonian: Murashû and Egibi (c. 700–400 BCE) | High (loans, 5-gen) | **PARTIAL** | https://www.achemenet.com (Egibi); Penn Museum (Murashû) |
| 2.7 | Zenon Archive (c. 259–229 BCE) | High (single agent) | **DONE** | 77 DDB EpiDoc XML → `raw_data/papyri/p.zen.pestm/`; parsed → `processed_data/papyri/p.zen.pestm_parsed.csv`. Translation coverage via APIS columbia (metadata-only) and HGV IDs outside downloaded range; full translations accessible via DDB |
| 5.3 | Roman Dacia Wax Tablets — Alburnus Maior (131–167 CE) | High (risk-sharing) | **PARTIAL** | https://www.eagle-network.eu |
| 6.1 | Chinese Oracle Bones (Shang, c. 1250–1050 BCE) | High (forecast) | **HARD** | YOD database (subscription); Tencent 3D corpus |
| 2.2 | Heqanakht Letters (c. 2002 BCE) | Med-high (loss framing) | **QUEUE** | https://libmma.contentdm.oclc.org/digital/collection/p15324coll10/id/177421/ |
| 2.5 | Turin Strike Papyrus (c. 1157 BCE) | Med-high (loss aversion) | **QUEUE** | https://collezionepapiri.museoegizio.it/en-GB/document/131/ |
| 2.6 | Elephantine Papyri (Aramaic, c. 495–399 BCE) | Med-high (loans) | **QUEUE** | https://elephantine.smb.museum/ |
| 3.1 | Amarna Letters (c. 1360–1332 BCE) | Med-high (diplomacy/loss) | **QUEUE** | https://oracc.museum.upenn.edu (search: Amarna) |
| 3.5 | Babatha Archive (c. 93–135 CE) | Med-high (legal/loss) | **HARD** | NLI Israel; academic editions |
| 3.13 | Palmyrene Texts / Palmyra Tariff (1st–3rd CE) | Med-high (price schedule) | **PARTIAL** | https://search.library.wisc.edu/digital/AWPAIPColl |
| 4.2 | Classical Greek Inscriptions (maritime loans) | Medium (credit risk) | **QUEUE** | https://inscriptions.packhum.org/ |
| 4.4 | Greek/Demotic Ostraca from Roman Egypt | Medium (tax compliance) | **QUEUE** | https://papyri.info |
| 5.2 | Vindolanda Tablets (c. 85–130 CE) | Medium (prices/complaints) | **DONE** | 523 DDB EpiDoc XML → `raw_data/papyri/t.vindol/`; parsed → `processed_data/papyri/t.vindol_parsed.csv` |
| 5.4 | Dura-Europos Documents (c. 100–256 CE) | Med-high (military finance) | **QUEUE** | https://papyri.info (P.Dura texts) |
| 5.6 | Nessana Papyri (c. 500–700 CE) | Medium (cross-regional) | **DONE** | 176 DDB EpiDoc XML → `raw_data/papyri/p.ness/`; parsed → `processed_data/papyri/p.ness_parsed.csv` |
| 5.7 | Petra Papyri (c. 537–593 CE) | Med-high (family archive) | **HARD** | ACOR publication; Trismegistos metadata |
| 1.6 | Mari Archives (c. 1800–1760 BCE) | Med-high (prophetic) | **HARD** | https://archibab.fr (partial); ARM series only |

---

## Tier 3 — Medium or Supplementary Signal

Download opportunistically or only if Tier 1–2 analysis reveals a gap.

| # | Corpus | Signal | Status | Notes |
|---|---|---|---|---|
| 1.1 | Late Uruk Administrative Tablets (c. 3350–2900 BCE) | Low (price baseline) | **QUEUE** | https://cdli.earth |
| 1.2 | Early Dynastic Lagash/Girsu (c. 2600–2350 BCE) | Low-med | **QUEUE** | https://cdli.earth |
| 1.4 | Ebla Archives (c. 2400–2300 BCE) | Med (institutional) | **PARTIAL** | http://ebda.cnr.it/ |
| 1.10 | Ugarit Economic Archives (c. 1400–1185 BCE) | Medium | **QUEUE** | https://cdli.earth |
| 1.11 | Middle Assyrian Archives (c. 1400–1050 BCE) | Low-med | **QUEUE** | https://oracc.museum.upenn.edu/tcma/ |
| 1.17 | Seleucid/Hellenistic Babylonian (c. 330–63 BCE) | Med-high (loans) | **PARTIAL** | https://oracc.museum.upenn.edu/hbtin/ |
| 1.18 | Hittite Archives — Hattusa (c. 1650–1180 BCE) | Medium (treaties/omens) | **PARTIAL** | https://www.hethport.uni-wuerzburg.de/HPM/ |
| 1.20 | Urartian Inscriptions (c. 860–590 BCE) | Low-med | **QUEUE** | https://www.en.ag.geschichte.uni-muenchen.de/research/ecut/ |
| 2.1 | Abusir Papyri (c. 2400 BCE) | Low-med | **PARTIAL** | https://cegu.ff.cuni.cz |
| 2.3 | Lahun/Kahun Papyri (c. 1850 BCE) | Medium | **QUEUE** | https://www.ucl.ac.uk/museums-static/digitalegypt/ |
| 3.3 | Samaria Ostraca (c. 786–746 BCE) | Low | **HARD** | Istanbul Archaeological Museum; academic |
| 3.4 | Lachish Letters (c. 587 BCE) | Low | **QUEUE** | https://www.britishmuseum.org/collection |
| 3.7 | Arad Ostraca (c. 600 BCE) | Low-med | **HARD** | Israel Museum; no open-access portal |
| 3.8 | Phoenician/Punic Inscriptions | Low-med (tariffs) | **PARTIAL** | http://cip.cchs.csic.es/ |
| 3.9 | Saqqara Aramaic Papyri (c. 475–400 BCE) | Low | **HARD** | Academic editions only |
| 3.10 | Wadi Daliyeh Papyri (c. 375–335 BCE) | Low-med | **HARD** | DJD XXVIII; CAL bibliography |
| 3.11 | Nabataean Papyri | Low | **QUEUE** | https://diconab.huma-num.fr/ |
| 3.12 | Murabba'at Documents (1st–2nd CE) | Low-med | **HARD** | DJD II; academic only |
| 3.14 | Aramaic Papyri from Bactria (c. 353–324 BCE) | Low-med | **HARD** | Khalili Collections; Naveh/Shaked 2012 |
| 4.1 | Linear B Tablets (c. 1450–1200 BCE) | Low | **QUEUE** | https://damos.hum.uio.no/ |
| 5.5 | Herculaneum Papyri (before 79 CE) | Low (monitor) | **QUEUE** | https://scrollprize.org/ |
| 5.8 | Ravenna Papyri (5th–7th CE) | Low-med | **PARTIAL** | Trismegistos; Manchester Digital Collections |
| 6.3 | Tebtunis Papyri (c. 250 BCE – 300 CE) | Medium | **QUEUE** | https://papyri.info; APIS UC Berkeley |
| 6.4 | Dead Sea Scrolls — Economic Documents | Low-med | **PARTIAL** | https://www.deadseascrolls.org.il/ |

---

## Skip (Undeciphered or No Signal)

| # | Corpus | Reason |
|---|---|---|
| 1.8 | Middle Babylonian / Kassite | <10% published; low signal currently |
| 1.16 | Persepolis Fortification Tablets | <15% published; access restricted |
| 1.19 | Proto-Elamite Tablets | Undeciphered |
| 3.2 | Ugaritic Archives | Duplicate of 1.10 |
| 3.6 | Bar Kokhba Letters | Military crisis; low standard-bias signal |
| 4.3 | Hellenistic Papyri | Covered by 2.7 and 2.8 |
| 4.5 | Linear A | Undeciphered |
| 4.6 | Cypro-Minoan | Undeciphered |
| 6.2 | Persepolis Treasury Tablets | Duplicate of 1.16 |

---

## Download Queue Order (Tier 1, free corpora first)

1. ~~SAA04, SAA08, SAA09, SAA10~~ ✓ DONE — 1,309 texts parsed into `processed_data/neo_assyrian/letters_translations.csv`
2. ~~Babylonian Astronomical Diaries~~ ✓ DONE — adart1–3; 404 translated entries → `processed_data/babylonian_diaries/diary_translations.csv`
3. ~~Ur III~~ ✓ DONE — 77,531 ATF blocks → `raw_data/cdli_bulk/ur3_atf.txt`; 110,984 catalogue entries → `processed_data/cdli_bulk/cdli_cat_ur3.csv`
4. ~~Old Babylonian ATF~~ ✓ DONE — 13,527 ATF blocks → `raw_data/cdli_bulk/old_babylonian_atf.txt`; 66,236 catalogue entries — **ARCHIBAB translations still to source**
5. Deir el-Medina — DMD database (frame-based; needs custom scraper)
6. Amarna Letters — not in CDLI as translated; academic editions only (Moran 1992)
7. ~~Zenon Archive~~ ✓ DONE — 77 DDB EpiDoc files; no inline translations (HGV range issue)
8. ~~Roman Egypt / Oxyrhynchus~~ ✓ DONE — 3,451 DDB EpiDoc files across 72 volumes
9. ~~Karanis Papyri~~ ✓ DONE — covered by APIS michigan (822 docs, 98% translated)
10. ~~Remaining free Tier 2 (Vindolanda, Nessana, Elephantine)~~ ✓ DONE — all downloaded via papyri.info
11. ~~APIS institutional collections~~ ✓ DONE — 9,419 docs from 29 institutions → `processed_data/papyri/apis_combined.csv`
12. Next: Deir el-Medina scraper; then behavioral analysis of papyri + APIS data

## Also downloaded (supporting infrastructure)
- Full CDLI ATF corpus: `raw_data/cdli_bulk/cdliatf_unblocked.atf` (83 MB, 3.5M lines)
- Full CDLI catalogue: `raw_data/cdli_bulk/cdli_cat.csv` (148 MB, 353,283 tablets)
