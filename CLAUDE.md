# AI-Cyber Intro Certification — Working Context

Context for Claude Code sessions in this repo. Written 2026-08-21, last updated 2026-08-26.

## What this is

An **introductory** certification course on AI for cybersecurity, taught as a series of
Google Colab notebooks. Asynchronous — students read, run, and modify code in the
notebook itself. Owner/author: Abe Weigant.

Two sister courses build on this one: one covering **LLMs** in depth, one covering
**securing AI** in depth. Modules 6 and 7 preview those while standing on their own.

Condensed from a 15-week outline into 7 modules.

| Module | Title | Status |
|---|---|---|
| 1 | Course Introduction & The Role of AI in Cybersecurity | **Rebuilt 2026-08-26, verified on Colab** |
| 2 | Cyber Threat Landscape, Data Sources, Preprocessing, First ML Model | **Rebuilt 2026-08-26, verified locally** |
| 3 | Supervised Machine Learning | **Rebuilt 2026-08-26, verified locally** |
| 4 | Unsupervised Learning: Anomaly Detection & Threat Hunting | **Rebuilt 2026-08-26, verified locally** |
| 5 | Deep Learning Models for Cybersecurity | **Complete, verified on Colab 2026-08-26** |
| 6 | LLMs + Explainable AI (capstone: LLM-assisted forensic log triage) | Not started |
| 7 | Adversarial Attacks & the Secure AI/ML Lifecycle | Not started |

## Repo layout

This repo is the course's **dataset host** and holds the student-facing notebooks.
Notebooks pull data by raw GitHub URL. **No module uses Kaggle any more** — Module 1's
account/API-token onboarding was removed on 2026-08-26.

```
Module1_Student.ipynb            rebuilt 2026-08-26 (see below)
Module2_Student.ipynb            rebuilt 2026-08-26 (see below)
Module3_Student.ipynb            rebuilt 2026-08-26 (see below)
Module4_Student.ipynb            rebuilt 2026-08-26 (see below)
Module5_Student.ipynb
instructor/                      a SEPARATE PRIVATE git repo -- see "Two repos" below.
                                 gitignored here; it can never be committed to this one.
malimg_64.npz                    9,339 malware byte-images, 64x64 grayscale (22.7 MB)
CEAS_08.parquet                  39,154 labelled emails with full body text (19 MB)
creditcard.csv.zip               credit card fraud (Modules 4 and 5)
dga_websites.csv / legit_websites.csv   DGA vs legitimate domains (Module 5)
Backdoor_Malware.pcap.parquet    IoT flow features, 3,218 rows (Module 5 final lab)
Recon-PortScan.pcap.parquet      IoT flow features, 82,284 rows (Module 5 final lab)
UNSW_2018_IoT_Botnet_*.csv.zip   unused so far
phishing_dataset1.parquet        112 lexical URL features, 88,647 rows
Log_Data.csv                     30 rows, toy firewall log (Module 2)
```

Notebooks reference data via a `DATA_URL` constant defined in the module's setup cell:

```python
DATA_URL = "https://github.com/abramweigant/AI-Cyber-Intro-Cert/raw/refs/heads/main/"
```

**All five modules are checked in.** The canonical copies still live in Google Drive /
Colab — these are downloaded snapshots, so re-export from Colab before editing if the Colab
copy has moved ahead. Modules 2–4 are committed with saved outputs; see the
student-identifier warning under Known gaps before pushing anything from Module 4.

## Two repos: student here, solutions private

**This repo is PUBLIC.** Answer keys live in a separate private repo,
`abramweigant/AI-Cyber-Intro-Cert-Instructor`, checked out at `instructor/` inside this
working tree as its own independent git repository. `cd instructor` puts you on the private
remote; the parent directory ignores `instructor/` entirely.

`.gitignore` here guards `instructor/`, `Module5_Instructor.ipynb`, and `*.pdf` — a PDF
render of an instructor notebook carries every solution with it, which is how the Module 5
and Module 1 Colab exports had to be moved. Never remove those lines.

**Workflow that works, established on Modules 5 and 1:**

1. Edit the **instructor copy** as the master. It holds the solutions and teaching notes.
2. Verify by executing — `nbconvert --to notebook --execute` into a scratch path.
3. Derive the student copy from the master: replace solution cells with scaffolds, clear
   outputs on exercise cells only, strip the instructor banner from cell 0.
4. Transplant outputs from the verified run into both copies so teaching cells carry fresh
   output rather than a mix of vintages.
5. Integrity check: markdown must differ **only** at cell 0, code **only** at the exercise
   indices, and no `INSTRUCTOR`/`TEACHING NOTE` string may appear in the student copy.

Cell counts, both copies (verified 2026-08-27): Module 1 is 61, Module 2 is 57, Module 3 is
61, Module 4 is 83, Module 5 is 91. The check above is what guarantees they stayed in step.
The leak check must match `INSTRUCTOR SOLUTION` and `TEACHING NOTE` as phrases -- matching the
bare word `SOLUTION` also hits `resolution` and ordinary prose, and returns four false
positives.

Retired originals live in the private repo, never in this one:
`Module1_Intro-2_SUPERSEDED.ipynb`, `Student_Module2__SUPERSEDED.ipynb`,
`Student_Module3_SUPERSEDED.ipynb`. All three are still in this repo's history at `e6843c8`.

## Module 1 rebuild (2026-08-26)

The original `Module1_Intro-2.ipynb` is **retired** — archived in the private repo as
`Module1_Intro-2_SUPERSEDED.ipynb`, still in this repo's history at `e6843c8`. Do not
restore it without reading why it was replaced:

- **It called its data "emails". It was not emails.** The columns were URL lexical features
  (`NumDots`, `UrlLength`, `AtSymbol`, `IpAddress`) with no sender, subject or body. Students
  were told to print "the first 25 emails" and export `first_100_emails.csv`, then met real
  email data in Module 5.
- **Its Kaggle dependency had already gone stale.** Question 5D asked for `df.tail(400000)`
  and `df.head(11439)` against 662,591 rows whose label boundary sits near index 100,011.
  Those numbers matched an earlier version of the download and demonstrated nothing.

The rebuild runs on `phishing_dataset1.parquet`, already hosted here.

## Module 2 rebuild (2026-08-26)

`Student_Module2_.ipynb` is retired for three reasons, all verified:

- **It shipped broken.** A live `FileNotFoundError` in the load cell, with stale output in
  the cell below it. It also could not run top to bottom at all — code lived in markdown for
  students to copy, so five cells referenced `X_train_scaled`, `model`, `y_test` and
  `X_train` that no code cell defined.
- **Its Kaggle download was over a gigabyte for one `.head()` call.** A 183 MB zip extracting
  to `iot23_combined_new.csv` at 903 MB plus a 170 MB file, used in exactly one cell and never
  referenced again.
- **Its central explanation was impossible.** It attributed the perfect score to the model
  memorising the attacker's IP `103.27.14.88`. All seven brute-force rows do share that IP,
  but `source_ip` is dropped before modelling. It also printed `model.coef_[0]` and called it
  "the model's brain" on a three-class problem, where `coef_` is `(3, 16)`.

The rebuild keeps the 24-row toy log for Lab 1 **deliberately** — you can read every row, and
the perfect 100% on five test rows is the memorisation lesson. Lab 2 is new and runs on
`phishing_dataset1.parquet`, so Module 1 audits that dataset and Module 2 acts on the audit.

## Module 3 rebuild (2026-08-26)

`Student_Module3.ipynb` is retired. Three reasons, all verified:

- **It could not execute.** It loaded `phishing_dataset1.parquet`, then uploaded
  `features_at_0.9_threshold_train.parquet` — a file the notebook itself produces thirty
  cells later. Circular. Cell 32's saved output shows 18,070 rows × 73 columns, a derived
  subset that is not in the repo and whose class balance is *inverted* relative to the
  source. The SMOTE lab carried no outputs while three cells below analysed its results.
- **Its stated premise was false.** It told students the naive model would show "terrible
  recall" on the minority class. Actual minority recall on that dataset is **0.915** — 34.6%
  is mild imbalance, and the accuracy trap does not occur.
- **Its prescribed fix was wrong.** Measured on genuinely imbalanced data, SMOTE,
  undersampling and class weighting all make the model six to ten times worse.

**The thesis is inverted in the rebuild, and this is the important part.** The module now
measures the standard remedies rather than asserting them, and finds that threshold tuning
and model choice beat all three. See the measured facts below before editing anything here.

## Module 4 rebuild (2026-08-26)

Module 4 was **not** rebuilt from scratch — unlike 1, 2 and 3 it executed correctly, was
properly seeded, and its final lab was methodologically sound. It was converted from a
**demonstration into a lab**, because it had zero student tasks and zero gradable output:
all 21 code cells were pre-written, and the "Analysis & Reflection" headings stated
conclusions rather than asking questions. It now has 14 coding tasks and 8 write-ups.

Two curriculum gaps closed, both cases of a topic named but never taught:

- **Choosing `k`.** The module said selecting k "often requires the Elbow method or Silhouette
  analysis", demonstrated neither, and hardcoded k three times. Task 4.2 derives it — inertia
  falls 2,591,319 → 665,602 at k=3 then flattens, silhouette peaks at k=3 (0.857).
- **DBSCAN** was absent entirely. Task 4.3 adds it, and it doubles as the counterpart to the
  existing scaling lesson: Isolation Forest is tree-based and scale-invariant, DBSCAN is
  distance-based and is not.

Also fixed: the "Cost of Hunting" draft text, the unreconciled PCA variance claim, a
cross-reference to the wrong section, and a bare URL pasted as markdown. The Gradio quiz and
its self-defeating decoder cell were removed separately — knowledge checks now live in the
external quiz tool, with the questions preserved privately as
`module4_knowledge_check_questions.md`.

## The organizing idea of Module 5

Not planned — it emerged from auditing the existing material, and it now structures
the module and sets up Module 7. Every section contains a result that is not what it
appears to be, and each one fails by a **different mechanism**:

| where | the number looked like | what was actually happening |
|---|---|---|
| Section 2 | F1 collapsed to 0.14 | Threshold artifact from `class_weight`, not a model failure |
| Section 2 | Autoencoder beats Isolation Forest | Its threshold was picked using test labels; the baseline got no such help |
| Section 3 | ~0.89 F1 on DGA detection | 55.3% of the test set had been memorized during training |
| Section 4 | 96–99% on a standard benchmark | 15% duplicate validation images + two families that are the same picture |
| Section 5 | 99.6% phishing detection | Model separated mailing-list posts from 2008 spam — not phishing |
| Final lab | 96.1% accuracy is trivially achievable | Majority-class baseline beats the trained model while catching zero backdoors |

If you edit Module 5, preserve this throughline. It is the module's spine and the
on-ramp to Module 7.

## Measured facts — do not re-derive, do not contradict

All of these were measured by actually running the code, not estimated.

**Module 1 — `phishing_dataset1.parquet` (88,647 rows, 111 features + label).**
Every figure below reproduced **identically** on local pandas 3.0.5 and Colab pandas 2.2.3.
They are dataset properties, not model outputs, so unlike Module 5's metrics they do not
drift and may be quoted exactly.

| check | value |
|---|---|
| `isnull().sum().sum()` | **0** — and it is wrong |
| feature columns containing `-1` sentinels | **66 of 111** |
| rows with `-1` across all 19 `_params` columns | **81,225 (91.6%)** |
| rows with `-1` across all 17 `_directory` and all 17 `_file` columns | **47,509 each** |
| `qty_params` mean | **−0.76** — an impossible average for a count; this is the tell |
| `params_length` mean, with / without sentinels | **5.27 / 73.93** (14× error) |
| exact duplicate rows | **1,438** |
| rows sharing a feature vector | 1,937 |
| feature vectors carrying **both** labels | **6** (13 rows, 0.015%) |
| constant columns | **13**, every one a `_domain` punctuation count |
| class balance | 30,647 phishing / 58,000 legitimate (**34.6%**) |
| column families | `_url` 20, `_domain` 19, `_directory` 17, `_file` 17, `_params` 19, other 20 |

The three sentinel families switch off **as blocks**, because the sentinel encodes a
structural fact about the URL (no query string, no path) rather than a measurement failure.
The network-lookup columns (`time_domain_activation`, `ttl_hostname`, `domain_spf`,
`qty_ip_resolved`, `url_google_index`, …) carry `-1` for a different reason — the lookup was
attempted and failed. Same value, different meaning; the module makes students argue about
that distinction.

**Module 2 — `Log_Data.csv` (30 rows) and `phishing_dataset1.parquet`.**
Deterministic; reproduce exactly.

| check | value |
|---|---|
| toy log cleaning | 30 → 28 (dedupe) → 27 (corrupt timestamp) → 25 (dropna) → **24** (port > 65535) |
| toy log after cleaning | 0 nulls, `firewall_rule` collapses to **Allow 12 / Deny 12** |
| toy log classes | Benign 12, Brute Force 7, Scan 5 |
| toy model | 19 train / **5 test** rows, accuracy **1.00** — only multiples of 20% are reachable |
| `model.coef_` shape | **(3, 16)** — one row per class, not one vector |
| real drivers | `device_type_Unknown` → Brute Force, `device_type_IoT Device` → Scan, `firewall_rule_Deny` → both |
| URL dataset after cleanup | 13 constant columns and 1,438 duplicates dropped → **87,209 rows** |
| logistic regression on URLs | **93.35%** accuracy, **F1 0.9057**, vs a **65.03%** majority baseline |
| dropping the 13 dead columns | changes accuracy by **exactly zero** — zero-variance columns scale to zeros |
| leaving the 1,438 duplicates in | **93.14% / ~0.902** — slightly *worse*, not better |

That last pair is the module's payoff and contradicts what students predict. It is also the
earliest statement of Module 5's thesis: the magnitude of a data defect is an empirical
question, not something you can reason out.

**Module 3 — `phishing_dataset1.parquet` and `creditcard.csv.zip`.** Deterministic.

*Lab A, the sentinel finding (the strongest result in the course):*

| check | value |
|---|---|
| after Module 1's cleanup | 87,209 rows × 99 columns |
| features tying at 0.744 correlation with the label | **8**, agreeing to three decimals |
| `qty_dollar_file` distinct values | **exactly 2** — `-1` (46,323 rows) and `0` (40,886) |
| binary "has a file part" indicator vs label | **r = 0.7446** — same as the column itself |
| phishing rate, URLs with **no** path | **1.6%** |
| phishing rate, URLs **with** a path | **72.8%** |
| feature pairs at \|r\| ≥ 0.95 | **246** (15 at exactly 1.00) |
| pruning survivors | 66 @ 0.95, 58 @ 0.9, 50 @ 0.8, 41 @ 0.7 |

The dataset's single strongest predictor is *whether the URL has a path at all* — almost
certainly an artifact of how the two classes were harvested, not a property of phishing.
This is why Module 2's 93.35% came so easily. Do not remove this finding; it is the module's
spine and the earliest construct-validity lesson in the course.

*Labs B–D, credit card fraud (492 frauds in 284,807 rows, 0.173%, about 577:1):*

| approach | precision | recall | F1 |
|---|---|---|---|
| naive logistic regression | 0.827 | 0.633 | **0.717** |
| + SMOTE | 0.058 | 0.918 | **0.109** |
| + random undersampling | 0.038 | 0.918 | **0.074** |
| + `class_weight='balanced'` | 0.061 | 0.918 | **0.114** |
| naive + tuned threshold (0.153) | 0.735 | 0.765 | **0.750** |
| Decision Tree (depth 6) | 0.895 | 0.786 | **0.837** |
| **Random Forest, no resampling** | 0.941 | 0.816 | **0.874** |
| *SMOTE before the split (leaky)* | *0.974* | *0.924* | *0.948* |

*Lab D.3, added 2026-08-27 — fold-safe grid search.* `ImbPipeline` of `StandardScaler` ->
`smote` -> `RandomForestClassifier(n_estimators=100)`, grid over `smote` in
`['passthrough', SMOTE]` and `model__max_depth` in `[None, 10]`, `scoring='f1'`,
`cv=StratifiedKFold(3, shuffle=True, random_state=42)`. 12 fits, 124s locally.

| smote | max_depth | mean CV F1 | std | rank |
|---|---|---|---|---|
| passthrough | None | **0.8455** | 0.0215 | 1 |
| passthrough | 10 | 0.8435 | 0.0171 | 2 |
| SMOTE | None | 0.8352 | 0.0200 | 3 |
| SMOTE | 10 | **0.6122** | **0.0666** | 4 |

`best_params_` is `{'model__max_depth': None, 'smote': 'passthrough'}` — the library defaults.
Held-out P 0.941 / R 0.816 / **F1 0.874**, *identical* to D.2's untuned forest.

**Two results, and both are negative — say so to students before they think they broke it.**
The search was free to use SMOTE and refused it, applied the correct way inside the pipeline at
every fold. That is what retires the objection that Lab C only beat SMOTE by applying it
crudely, and it is the reason the lab exists. And tuning changed nothing, which confirms D.2's
default-vs-default comparison was fair rather than lucky. Direct held-out check on the same
forest: no resampling P 0.941 / R 0.816 / F1 0.874, against SMOTE-in-pipeline P 0.871 / R 0.827
/ F1 0.848 — fold-safe SMOTE buys 0.011 recall for 0.070 precision, at double the training time.

The leaky run's tell is not its F1 but its test set: **113,726 rows at 50% fraud**, larger
than the dataset it came from. Learning curves: `max_depth=2` gives train 0.792 / val 0.761
(underfit); `max_depth=None` gives train **1.000** / val 0.732 (memorised).

**Module 4 — synthetic data plus `creditcard.csv.zip`.** Seeded; deterministic.

| check | value |
|---|---|
| PCA on 20 noisy dimensions | PC1 **10.55%**, PC2 **6.13%**, total **16.68%** |
| noise floor (if all 20 dims were noise) | **5.0%** per component |
| separation on PC1 | Cohen's *d* = **3.76**; AUC **0.994** (one raw feature: 0.715) |
| elbow / silhouette on session data | inertia 2,591,319 → **665,602** at k=3, then flat; silhouette peaks **0.857** at k=3 |
| DBSCAN, scaled, eps=0.3 | **3 clusters, 4 noise points** — recovers k=3 untold |
| DBSCAN, unscaled | needs eps ≈ 30–60 for the same result |
| silhouette, predicted-normal points | **0.930** |
| extrinsic check on injected anomalies | P 0.82, R 0.90, **F1 0.86** |
| final lab, Isolation Forest on test | P 0.31, R 0.34, **F1 0.32** |
| contamination sweep | 0.1% → R 0.26/P 0.39 … 5% → R 0.87/P 0.03 |

**The 16.68% is not a failure and the module now says why**: PC1 is at double the noise floor,
carries an effect size of 3.76, and reaches AUC 0.994 alone. Explained variance measures
retained *spread*, not retained *usefulness*.

**Cross-module comparison on the credit-card data** — the closing section of Module 4 depends
on these, so keep them in step:

| module | approach | labels in training? | fraud F1 |
|---|---|---|---|
| 3 | Logistic Regression | yes | ~0.72 |
| 3 | + tuned threshold | yes | ~0.75 |
| 3 | Random Forest | yes | **~0.87** |
| 4 | Isolation Forest | **no** | **~0.32** |

**DGA (Section 3).** The original notebook oversampled with `replace=True` *before*
`train_test_split`, creating 248,032 duplicate rows out of 675,000 and putting **55.3%**
of test domains into training. The step was never needed: the two source files are
337,500 and 337,398 rows, already balanced to within 0.03%. Fixed by deduplicating and
splitting first, and fitting the tokenizer on training data only. After the fix:
674,837 unique domains, 539,869 train / 134,968 test, **zero** train/test overlap.

Post-fix reference numbers, three epochs each on the corrected split:

| model | test accuracy | test F1 | train time | inference on 135k |
|---|---|---|---|---|
| 1D CNN | 88.95% | 0.8820 | 51s | 8.5s |
| LSTM | 85.20% | 0.8378 | 264s | 23.2s |
| exercise reference (4 epochs) | 91.25% | 0.9086 | 166s | 10.3s |

Note the leak barely moved the score — the leaky pipeline gave 0.8885 (CNN) and 0.8423
(LSTM) against 0.8820 and 0.8378 corrected. That is because these models are **underfit**
relative to 675k domains at three epochs, so they had little capacity to exploit the
duplicates. The notebook says this explicitly rather than implying the leak was harmless:
the cost of the leak was never the size of the number, it was that the number was
*uncheckable*. More epochs or a wider network would open the gap.

The Section 3 exercise target of F1 > 0.90 **still stands post-fix**, but it is tight —
the reference solution clears it at 0.9086. Do not raise it.

**Malimg (Section 4).**
- The distributed train/validation split shares **15.4%** of validation images with training.
- `Yuner.A` (800 samples) and `Autorun.K` (106) each reduce to **one** distinct image at
  64×64 — and those two images are effectively the same picture: mean absolute difference
  **0.097** on a 0–255 scale, versus a median inter-family centroid distance of **27.43**.
  About 280× closer than a typical family pair. The 25-class task is unsolvable at this
  resolution. Both families are dropped → 23 classes, 7,978 distinct images.
- **Open question:** Malimg encodes file size in image height and our 64×64 resize destroys
  it. These two families may be separable at full resolution. The raw `malimg_dataset`
  folder has been deleted locally, so this is flagged in the notebook as unresolved.
- Reference results — honest protocol: **97.99% accuracy, 0.949 macro F1**. Naive protocol
  (as distributed, 25 classes): **94.87%, 0.910**, with `Yuner.A` recall 1.000 and
  `Autorun.K` recall 0.000.
- The naive protocol scores **lower**, which is the opposite of the intuitive prediction.
  Leakage helps; the impossible class costs more. The exercise is built around that surprise.
- **`BatchNormalization` at Keras' default momentum of 0.99 destroys this model** — 96%
  train accuracy, **11.7%** test accuracy, because the moving statistics never converge at
  85 steps/epoch. momentum=0.90 fixes it; removing BatchNorm entirely is equally accurate
  and twice as fast. It is removed. Do not add it back.

**CEAS_08 (Section 5).**
- 39,154 rows, 21,842 malicious / 17,312 legitimate. All bodies distinct — no duplication leakage.
- 2,405 senders appear more than once; 2,400 are label-pure, covering **43%** of rows.
  Sender domains cover 52%. **But adding the sender to the model changes accuracy by only
  +0.1%**, and neither model degrades on unseen senders — the body signal already saturates.
  The exercise is built on that gap between a real audit finding and its actual impact.
- TF-IDF + logistic regression: **99.50% in 7.5s**. The Conv1D model: **99.63% in ~84s**.
- First 5 words alone → 95.6%. First 10 → 97.7%. First 20 → 98.5%.
- Top "legitimate" tokens are `python`, `perl`, `postfix`, `list`, `wrote`. 30.0% of benign
  messages contain "mailing list" and 27.4% contain "listinfo", against ~0.1% of malicious.
  The benign class is developer mailing list traffic.

**Final lab (IoT flows).** 85,502 rows combined; 2,043 exact duplicates (concentrated in
PortScan); 1 row with nulls; no constant columns in the combined set; no feature rows with
contradictory labels. After cleaning: 83,458 rows, 3,215 backdoor / 80,243 portscan (25:1).
**Majority-class baseline accuracy is 96.15%.** Reference solution with a tuned threshold:
accuracy 95.57%, macro F1 0.691, backdoor F1 0.405, backdoor recall ~0.39.

## Content lost in the rebuilds — READ BEFORE REBUILDING ANYTHING ELSE

Modules 1, 2 and 3 were rebuilt from the dataset up: decide what the module *should* teach,
then write it. That produced better modules and **silently dropped topics the originals
taught**. Where the old content happened to align with the new spine it survived; where it did
not, it vanished without anyone deciding it should.

**The rule this produced:** a rebuild must be *diffed* against the original, topic by topic,
and every dropped topic must be an explicit decision. Deleting a note-to-self is not the same
as deleting the subject it was about — an author's note is evidence a topic was
**under-explained**, not evidence it was unwanted.

### The audit, and two ways to run it wrong

Tokenize both notebooks, count terms appearing **>=3x in the original and 0x in the rebuild**,
across three vocabularies: dotted API calls (`df.info`), CamelCase classes (`GridSearchCV`),
and prose words. Script: `instructor/audit_dropped_topics.py old.ipynb new.ipynb`. About a second per module.

Two mistakes cost a full re-run on 2026-08-27, both of which silently *hide* real drops behind
noise:

1. **Diff the instructor copies, not the student copies.** The student copy has scaffolds where
   solutions were, so every term that lives only in solution code reports as dropped. The
   student-copy run returned 32 false positives on Module 4 alone and buried the one real hit.
2. **Strip base64 before tokenizing.** Module 1's original embeds images in markdown source.
   Undstripped, the top 65 "dropped CamelCase terms" are JPEG fragments and the signal is gone.

### A second failure mode: the explanation outlives the lab

Module 3's rebuild dropped the tuning lab but **kept its two explanatory markdown cells**, which
survived verbatim as cells 51 and 52 (original 83 and 84). They referenced `grid_search.fit()`
and `best_estimator_` — the only occurrences of either string in the module — with no code
anywhere defining them, and cell 52's worked example asserted that SMOTE inside a pipeline
teaches the model to recognise the minority class, which Lab C had already measured as false.

A term-frequency audit **cannot** find this: the vocabulary is present, so nothing reports as
dropped. It shows up only by asking of each explanation, *what code does this describe?* Both
cells were rewritten on 2026-08-27 when Lab D.3 restored the machinery they had been left
explaining.

### Coverage — all five modules audited 2026-08-27

Originals for Modules 1–3 are the retired copies in this private repo; for Modules 4 and 5 they
are the pre-rebuild state at public commit `514550c`.

| module | verdict |
|---|---|
| 1 | **clean** — only `kaggle` (deliberate) and three typos the rebuild fixed (`phising`, `bellow`, `corrolation`) |
| 2 | **clean** — hits were renaming (`df` -> `log`/`clean`/`urls`) and spelling (`memorizes` -> `memorisation`) |
| 3 | **three real drops**, below |
| 4 | **clean** — Gradio quiz removed deliberately, all 10 scenarios preserved in `module4_knowledge_check_questions.md`; supervised/unsupervised framing fully intact (`supervised` 61->61, `unsupervised` 43->44, `zero-day` 7->8, `ground truth` 9->10; only the word *paradigm* fell out of use) |
| 5 | **clean** — sole hit is `todo`, from author notes |

Modules 4 and 5 had never been audited before this date. They were edited rather than rebuilt,
and that was assumed to be safe. It happened to be true; it was not checked.

### Known casualties — all in Module 3

| topic | original | rebuilds | status |
|---|---|---|---|
| Pearson vs **Spearman** correlation | 17 | 19 | **restored 2026-08-27** as Lab A.5 |
| **`ImbPipeline`** (`imblearn.pipeline`) | 17 | 4 | **restored 2026-08-27** as Module 3 Lab D.3 |
| **`GridSearchCV`** / hyperparameter tuning | 11 | 5 | **restored 2026-08-27**, same lab |
| **SVC / SVMs** | 18 | 1 (M1 concept list) | **still missing** |
| `LearningCurve` (yellowbrick) | 4 | 0 | intentional — replaced by sklearn `learning_curve`, present in M3 |
| `to_parquet` (persist the cleaned dataset) | 3 | 0 | acceptable — each rebuilt module now loads from `DATA_URL` and stands alone |
| imputation | 3 | 0 | acceptable — Module 2 covers the same ground |

Visualization and interpretability were checked for systemic loss and **grew**: `plt.` calls
135 -> 147 course-wide, `coef_` 3 -> 8 (Module 2 now teaches it correctly). Module 3's own
histogram/heatmap count fell but was replaced, not removed.

### `ImbPipeline` + `GridSearchCV` were one casualty, not two — restored 2026-08-27

They were a single two-part lab: *diagnose with learning curves inside an `ImbPipeline`, then
tune with `GridSearchCV` respecting that same pipeline.* The rebuild kept the learning curves
and dropped the pipeline and the tuning.

That leaves a **coherent hole, and it is the most important thing in this section.** Module 3
now proves that SMOTE before the split leaks (F1 0.948 against an honest 0.109) and teaches the
manual fix — split first. `ImbPipeline` is the *production-standard* fix: it exists precisely so
resampling happens inside each CV fold and cannot leak. Students learn the failure mode and the
hand-rolled remedy, but never meet the tool the field actually uses to prevent it. The module
argues for measurement over assertion and then omits the mechanism that makes measurement safe
under cross-validation.

**Both halves went back together**, as Lab D.3 — see the measured facts below. Restoring
`GridSearchCV` alone would have reintroduced tuning without the fold-safety that made the
original lab correct.

**SVMs stay out — this is now a decision, not an accident.** SVC is slow on 227k rows, the
module already compares three families, and one scenario in the Module 4 knowledge check keeps
students able to recognise an SVM as supervised. Say so in the module rather than leaving the
silence.

Module 3's learning objectives were rewritten from the new content and therefore do **not**
promise any of the three, so nothing inside the module is broken. That was luck, not diligence.

## Open items

1. **~~Full end-to-end execution of Module 5.~~ Done.** Ran clean three times — twice
   locally (7 minutes, 41/41 cells) and once on a Colab T4 under TensorFlow 2.20. Zero
   execution errors. Module 1 likewise ran clean locally and on Colab.
2. **~~Modules 2–4 polish.~~ Done 2026-08-26/27** — all three rebuilt, assessment normalised
   across all five modules, Module 4's mixed voice fixed.
3. **Colab confirmation runs for Modules 2, 3 and 4.** The last gate before the course ships.
   Modules 1 and 5 are confirmed. Expect 2 and 3 to hold (they assert mostly dataset facts,
   and Module 1's numbers reproduced identically across the pandas 2 -> 3 boundary) and
   Module 4's Isolation Forest metrics to move slightly.
4. **~~Restore the `ImbPipeline` + `GridSearchCV` lab to Module 3.~~ Done 2026-08-27** as
   Lab D.3. Module 3 is now 61 cells and runs clean end to end in 170s locally.
5. **Modules 6 and 7.** Not started. Design decisions are recorded below.

**On quoting numbers.** Module 5's prose gives model metrics as approximations
(`~89%`, `~0.88`) and ranges, because they drift: identical code restored EarlyStopping
epoch 10 and 16 on CPU and 30 on a Colab T4, and the Malimg naive protocol moved more than
two accuracy points between environments. Structural and dataset facts are quoted exactly,
because they reproduce exactly in every environment tested. Keep that distinction when
editing — it is the single most useful rule this project has produced.

## Known gaps

**Module 4, highest priority.** The "Interpretation: The Cost of Hunting" cell contains
unedited draft text in student-facing material:

> False Positives (Top-Right of 'Normal' column? No, actually Bottom-Left): Wait, let's
> read the matrix carefully:

**Module 4.** The Knowledge Check and "Teacher's Decoder Tool" launch Gradio with a public
`.live` share URL. Those links expire after 72 hours (the saved output is already dead), the
saved output contains a real student identifier and score, and opening a public tunnel from
a student notebook is a poor pattern to model in a security course. Consider `ipywidgets`
or moving the check into the LMS.

**Module 4.** The high-dimensional PCA demo retains only 16.68% of variance across PC1 and
PC2 while the prose claims clear separation. The separation is probably real (the attack
class has a 0.9 mean shift on all 20 dimensions) but it needs a sentence explaining why low
retained variance is not automatically a failure.

**~~Module 1.~~ Resolved 2026-08-26** — Kaggle onboarding removed, the stale `Index`
rename sequence gone, the whole lab rebuilt. See "Module 1 rebuild" above.

**~~Module 2.~~ Resolved 2026-08-26** — Kaggle gone, both labs rebuilt, the impossible
source-IP explanation and the `coef_[0]` error fixed. See "Module 2 rebuild" above.

**~~Module 3.~~ Resolved 2026-08-26** — rebuilt, renamed, thesis inverted on measurement.
See "Module 3 rebuild" above.

**~~Module 4.~~ Resolved 2026-08-26** — converted to a lab, both curriculum gaps closed,
draft text and PCA claim fixed. See "Module 4 rebuild" above.

**Correction to an earlier note in this file:** it claimed Modules 3–4 had no random seeds.
That was **wrong about Module 4**, which had twelve `np.random.seed(42)` / `random_state=42`
occurrences throughout and was the best-seeded of the original four.

**~~Module 3 will need a leakage story that actually bites.~~ Delivered.** SMOTE before the
split reports F1 0.948 against an honest 0.109 — roughly ninefold. Module 2's promise stands.

## Module 6 and 7 design decisions

**Module 6 — LLMs + XAI, capstone = LLM-assisted forensic log triage.**
Abe hosts models locally behind Open WebUI (OpenAI-compatible API, publicly routable),
with a dedicated "google colab user" API key. Model assignments:

| use | model | why |
|---|---|---|
| workhorse (few-shot phishing, most exercises) | `qwen3:8b` | best instruction-following per parameter; serves concurrent students. Disable thinking mode for classification labs (`/no_think`) or output is slow and hard to parse |
| capstone log triage | `gemma3:27b` | 128k context; logs are long |
| prompt-injection demo | `llama3.2:3b` **and** `gemma3:27b` | run the same payload against both — the small model folds, the large one usually resists. The contrast is the lesson: model capability is itself a security control |
| XAI section | `gpt-oss:20b` | exposes reasoning traces; compare its stated reasoning against SHAP attributions on the same email. Plausible is not faithful |

Read base URL and key from Colab secrets, never hardcode. Rotate per cohort and rate-limit —
assume a student eventually publishes a notebook containing the key.

Also available and unused: FLUX.2 dev, FLUX.1 schnell, SDXL, Z-Image Turbo. Week 14 of the
original outline lists "fake media" under deceptive techniques, so one of these could drive a
short Module 7 demo on synthetic media for social engineering.

**Module 7 — adversarial attacks and the secure AI/ML lifecycle.**
Attacks the students' *own* models from Modules 3 and 5, rather than fresh toy models. The
hook: the model you were proud of in week 5 breaks in ten lines. The Section 4 malware CNN is
the best target — it reads file layout, and appending null bytes shifts every subsequent byte
without changing behavior. This means M3/M5 model definitions must stay in sync with M7.

Weeks 14 and 15 of the original outline overlap heavily (both list poisoning, model inversion,
and threat modeling), so collapsing them into one module loses nothing.

## Environment notes

- **On Apple Silicon use `tensorflow`, not `tensorflow-cpu`.** `tensorflow-cpu` has never
  published a macOS arm64 wheel in any release — verified against the PyPI release index on
  2026-08-21. Plain `tensorflow` does, and 2.20/2.21 include cp313. An earlier note here
  recommended `tensorflow-cpu`; that must have been a Linux or x86 machine, and it cannot
  resolve on this one. Either way it trains this module's models in minutes on CPU.
  **Run every model before shipping it** — both architecture bugs found so far (the unbuilt
  `summary()` and the BatchNorm collapse) were invisible to static review.
- Keras `validation_split` takes the **last n% without shuffling**. On family-ordered data
  like Malimg's native row order, that hands the model a validation set of classes it never
  trained on, and you see ~1% val accuracy that looks like catastrophic overfitting. Shuffle first.
- **Colab MCP bridge (`googlecolab/colab-mcp`) — abandoned 2026-08-21. Do not retry it.**
  The Colab page connects to the local WebSocket, authenticates, and is then dropped by
  Colab in the same second, reproducibly (six times). Ruled out by direct test, not by
  argument: token (an unauthenticated probe gets a logged 401, real attempts do not),
  origin allowlist, port reachability on both address families, stale cached tokens
  (cookies cleared), orphaned servers (killed, single process on the machine), missing
  runtime (tested with and without a kernel), and wrong-tab (URL checked against the live
  token). Upstream is stale — last commit 2026-04-01 — with five unresolved discussions
  reporting connection failures: #43, #54, #81, #84, #100. Maintainers do not accept PRs
  and route everything to Discussions.

  **The decisive point:** `SCRATCH_PATH` is hardcoded to `/notebooks/empty.ipynb`, and
  discussion #80 confirms it cannot attach to an existing notebook. Even fully working it
  would open a blank scratchpad, never `Module5_Student.ipynb` from Drive. It could not
  have done the job it was being fixed for.

  Two real findings worth keeping. **A genuine dual-stack bug**, still unreported upstream:
  `websockets.serve(host="localhost", port=0)` opens one socket per address family and each
  gets its *own* ephemeral port, while only `sockets[0]`'s port is advertised in the URL
  fragment — so the advertised port is unreachable over the other family. Observed as
  `[::1]:64298` + `127.0.0.1:64299`. A local patch (pick one free port, bind both families
  to it) is applied at
  `~/.local/share/uv/tools/colab-mcp/lib/python3.13/site-packages/colab_mcp/websocket_server.py`,
  original saved beside it as `.orig`. `uv tool upgrade` will overwrite it. And **Safari
  cannot ever work** as the browser here: it refuses to treat `ws://localhost` as a secure
  context and blocks the dial-back as mixed content. Chrome and Firefox exempt localhost.

- **Local Jupyter + MCP is the working setup for driving notebooks (as of 2026-08-21).**
  `datalayer/jupyter-mcp-server` — actively maintained, 18 tools (`use_notebook`,
  `read_notebook`, `insert_cell`, `edit_cell_source`, `execute_cell`, `read_cell`,
  `move_cell`, `execute_code`, ...).

  ```bash
  uv venv --python 3.13 ~/.venvs/aicyber
  uv pip install --python ~/.venvs/aicyber/bin/python \
    jupyterlab jupyter-collaboration jupyter-mcp-tools ipykernel \
    tensorflow scikit-learn pandas numpy pyarrow matplotlib seaborn imbalanced-learn scipy
  ~/.venvs/aicyber/bin/python -m ipykernel install --user --name aicyber \
    --display-name "Python (AI-Cyber)"
  uv tool install --python 3.13 "jupyter-mcp-server>=1.5.0"
  ```

  Start the server (token via env so it stays out of `ps` output; loopback only — the
  upstream README's `--ip 0.0.0.0` would expose the kernel to the network, and a Jupyter
  token is arbitrary code execution):

  ```bash
  env JUPYTER_TOKEN="$(cat ~/.venvs/aicyber/.jupyter_token)" nohup \
    ~/.venvs/aicyber/bin/jupyter lab --port 8888 --ip 127.0.0.1 --no-browser \
    --ServerApp.root_dir="$HOME/AI-Cyber-Intro-Cert" > ~/.venvs/aicyber/jupyter.log 2>&1 &
  ```

  Token lives at `~/.venvs/aicyber/.jupyter_token` (mode 600). The MCP server is registered
  at local scope in `~/.claude.json` (not committed) with `JUPYTER_URL` /
  `CODE_SANDBOX_URL` set to **`http://127.0.0.1:8888`, not `localhost`** — the Jupyter
  server binds IPv4 only, and `localhost` can resolve to `::1`. The venv lives outside the
  repo on purpose: the remote is public.

  Verified on this stack (2026-08-21): `csv.zip`, `parquet`, and `npz` all load, stratified
  split + `StandardScaler` work, and both a functional autoencoder and a `Sequential` model
  with `class_weight` train — under **pandas 3.0.5 / numpy 2.5.2 / TensorFlow 2.21.0 /
  scikit-learn 1.9.0 / Python 3.13.14**.

- **Local and Colab are different environments — treat local as authoring, not as proof.**
  The versions above are ahead of what Colab pins. Anything a published number depends on
  still needs one confirming Colab run. This is not pedantry: the BatchNorm collapse was
  invisible until the model actually ran. Note also that Modules 1-3 contain `google.colab`
  and `files.upload` cells (the Kaggle-token onboarding) that fail locally by design;
  Module 5 is fully portable, its only Colab-ism being `display()`.
- When editing notebooks programmatically, each element of a cell's `source` list must end
  with `\n` except the last. Splitting on `'\n'` without re-adding them silently concatenates
  every line into one, and the notebook still parses as valid JSON.
