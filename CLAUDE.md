# AI-Cyber Intro Certification — Working Context

Context for Claude Code sessions in this repo. Started 2026-08-21, last updated 2026-09-01.

**Status: all 7 modules built. Modules 1–5 ran end to end on Google Colab on 2026-08-30 with
zero execution errors** — 315 pages of output reviewed. Modules 1–4 reproduced *every* figure
quoted in this file exactly. Module 5's model metrics moved slightly, as designed, and every
one landed inside the ranges its notebook states. Colab PDFs are in `instructor/`.

**Module 7 built 2026-08-30 and Colab-verified 2026-08-31** (adversarial attacks + secure
AI/ML lifecycle). It ran end to end on Colab with **zero execution errors**; the export is
`instructor/Module7_Instructor-new-Colab.pdf` (35 pages). Every attack reproduced in direction,
and every figure landed inside its stated range — including the two that matter most: the
one-character evasion (94% at ≤1 edit, identical to local) and the final lab's *non*-recovery
under adversarial training. Numbers are quoted as directions, not digits: adversarial search is
stochastic, so the drift rule applies with force. Shipped notebook outputs are from the local
run; the Colab PDF is the proof, exactly as for Modules 1–5. **Module 6 (LLMs + XAI) is now the
only module not started.**

**Post-verification edits, same day:** a full audit (every cell of all ten copies) fixed 8
small defects and resolved 13 findings — see `instructor/FIXES.md` for the complete log.
This added cells to every module (checkpoint cells; M3 gained ROC/PR, cross-validation and
feature-importance cells), so **the notebooks are now ahead of the verified Colab run**: the
new cells ship without stored outputs and quote only locally-measured numbers as
approximations. The next Colab pass must execute them and transplant outputs. Also new:
`README.md` (public, the student-facing syllabus) and `instructor/GRADING_RUBRICS.md`
(0/1/2 rubric for all 100+ written questions). **All of the above is committed and pushed** in
both repos as of 2026-09-01.

**Module 6 built 2026-09-01 — and it is the one module not verified by execution.** LLMs +
Explainable AI, 62 cells, 16 coding tasks, 6 write-ups. Its labs require a live model endpoint,
which the authoring environment does not have, so it ships for a first live pass. Read
"Module 6" below before touching it: what *was* verified locally, what was not, and why it
ships without stored outputs.

## What this is

An **introductory** certification course on AI for cybersecurity, taught as a series of Google
Colab notebooks. Asynchronous — students read, run and modify code in the notebook itself.
Owner/author: Abe Weigant. Condensed from a 15-week outline into 7 modules.

Two sister courses build on this one: one on **LLMs** in depth, one on **securing AI** in
depth. Modules 6 and 7 preview those while standing on their own.

| Module | Title | Cells | Status |
|---|---|---|---|
| 1 | Course Introduction & The Role of AI in Cybersecurity | 62 | Rebuilt; Colab-verified 2026-08-30, then edited same day (audit) |
| 2 | Threat Landscape, Data Sources, Preprocessing, First ML Model | 58 | Rebuilt; Colab-verified 2026-08-30, then edited same day (audit) |
| 3 | Supervised Machine Learning | 67 | Rebuilt; Colab-verified 2026-08-30, then edited same day (audit) |
| 4 | Unsupervised Learning: Anomaly Detection & Threat Hunting | 84 | Converted to a lab; Colab-verified 2026-08-30, then edited same day (audit) |
| 5 | Deep Learning Models for Cybersecurity | 92 | Complete; Colab-verified 2026-08-30, then edited same day (audit) |
| 6 | Large Language Models & Explainable AI (capstone: LLM-assisted forensic log triage) | 62 | Built 2026-09-01; **not yet verified against a live endpoint** |
| 7 | Adversarial Attacks & the Secure AI/ML Lifecycle | 31 | Built 2026-08-30; **Colab-verified 2026-08-31** |

Across the five audited modules: **63 coding tasks, 109 written questions.** Module 7 adds 7
attack exercises + a final lab and 6 write-up blocks; Module 6 adds 16 coding tasks and 6
write-up blocks.

## If you are here to evaluate the course

Four things to know before you file findings, so you do not re-report settled questions.

1. **The numbers in "Measured facts" were measured, not estimated.** Every one came from
   executing the code. If you disagree with one, run it — but do not assume it is a typo.
2. **Some omissions are deliberate.** SVMs are *intentionally* absent (reasoning below).
   Hyperparameter tuning and `ImbPipeline` were accidentally dropped in a rebuild and were
   **restored 2026-08-27** as Module 3 Lab D.3. `LearningCurve` (yellowbrick) was replaced on
   purpose by sklearn's `learning_curve`. Check the casualty table before calling a gap.
3. **Exact figures and approximate ones are distinguished on purpose.** Dataset and structural
   facts are quoted exactly because they reproduce exactly. Model metrics are given as `~89%`
   or as ranges because they drift between environments. Prose that says `~0.88` is not vague
   writing; it is the rule below being followed. Flag violations in *either* direction.
4. **Solutions are in a separate private repo** at `instructor/`. The student notebooks
   deliberately contain scaffolds (`# YOUR CODE HERE`) that will not execute standalone. That
   is not a bug. Evaluate the instructor copies for correctness, the student copies for
   pedagogy and for absence of leaked answers.

Two scripts audit this course; both live in `instructor/` and are described under
"How to work on this course".

## Repo layout

This repo is the course's **dataset host** and holds the student-facing notebooks. Notebooks
pull data by raw GitHub URL. **No module uses Kaggle** — removed 2026-08-26.

```
Module1_Student.ipynb .. Module7_Student.ipynb   (no Module 6 gap -- all seven exist)
instructor/                      a SEPARATE PRIVATE git repo -- see below.
                                 gitignored here; it can never be committed to this one.
malimg_64.npz                    9,339 malware byte-images, 64x64 grayscale (22.7 MB)
CEAS_08.parquet                  39,154 labelled emails with full body text (19 MB)
creditcard.csv.zip               credit card fraud (Modules 3, 4 and 5)
dga_websites.csv / legit_websites.csv   DGA vs legitimate domains (Module 5)
Backdoor_Malware.pcap.parquet    IoT flow features, 3,218 rows (Module 5 final lab)
Recon-PortScan.pcap.parquet      IoT flow features, 82,284 rows (Modules 5 and 7)
UNSW_2018_IoT_Botnet_*.csv.zip   unused so far
phishing_dataset1.parquet        112 lexical URL features, 88,647 rows (Modules 1, 2, 3)
Log_Data.csv                     30 rows, toy firewall log (Module 2)
forensic_log.csv                 774 log lines, one week, 8 hosts (Module 6 capstone)
forensic_log_truth.csv           its ground truth: 46 malicious lines, 8 attack stages.
                                 SEPARATE FILE on purpose -- it cannot land in a prompt
                                 by accident. Regenerate both with
                                 instructor/gen_forensic_log.py (byte-reproducible).
```

Every module loads data through a `DATA_URL` constant defined in its setup cell:

```python
DATA_URL = "https://github.com/abramweigant/AI-Cyber-Intro-Cert/raw/refs/heads/main/"
```

**Nothing may hardcode a dataset URL.** Module 4 did until 2026-08-27; if the repo moves, four
modules need one line changed and the fifth would have failed silently.

## Two repos: student here, solutions private

**This repo is PUBLIC.** Answer keys live in a separate private repo,
`abramweigant/AI-Cyber-Intro-Cert-Instructor`, checked out at `instructor/` inside this working
tree as its own independent git repository. `cd instructor` puts you on the private remote; the
parent ignores `instructor/` entirely.

`.gitignore` here guards `instructor/`, `Module5_Instructor.ipynb` and `*.pdf`. **A PDF render
of an instructor notebook carries every solution with it** — that is how the Colab exports must
be moved. Never remove those lines. Colab exports land in the public root by default; move them
to `instructor/` immediately.

Retired originals live in the private repo, never in this one:
`Module1_Intro-2_SUPERSEDED.ipynb`, `Student_Module2__SUPERSEDED.ipynb`,
`Student_Module3_SUPERSEDED.ipynb`. All three remain in this repo's history at `e6843c8`.

## How to work on this course

**The workflow that works** (established on Modules 5 and 1, used for all of them):

1. Edit the **instructor copy** as the master. It holds the solutions and teaching notes.
2. Verify by executing — `nbconvert --to notebook --execute` into a scratch path, or run every
   code cell in order in a fresh namespace.
3. Derive the student copy: replace solution cells with scaffolds, clear outputs on exercise
   cells only, strip the instructor banner from cell 0.
4. Transplant outputs from the verified run into both copies, so teaching cells carry fresh
   output rather than a mix of vintages.
5. **Integrity check.** Markdown must differ **only** at cell 0; code **only** at the exercise
   indices; cell counts must match; and no `INSTRUCTOR SOLUTION` or `TEACHING NOTE` string may
   appear in the student copy. Match those two as *phrases* — the bare word `SOLUTION` also
   matches `resolution` and ordinary prose, and returns four false positives.

Cell counts, both copies (verified 2026-08-30, post-audit; M6 2026-09-01): **M1 62, M2 58,
M3 67, M4 84, M5 92, M6 62, M7 31.** Each module now carries one **checkpoint cell** asserting deterministic dataset
facts at its most error-prone pipeline joint (the drift rule decides what is safe to
assert — dataset facts yes, model metrics never). Keep checkpoints identical in both
copies; they are teaching cells, not exercises.

**The drift rule — the single most useful rule this project has produced.** Structural and
dataset facts reproduce exactly in every environment tested, so quote them exactly. Model
metrics do not, so quote them as approximations or ranges. Identical code restored
EarlyStopping at epoch 10 and 16 on CPU and 30 on a Colab T4; the Malimg naive protocol moved
more than two accuracy points between environments. Both 2026-08-30 Colab runs confirmed the
rule in both directions: Modules 1–4 hit every exact figure, and every Module 5 metric landed
inside its stated range.

**Two audit scripts, both in `instructor/`:**

| script | question it answers |
|---|---|
| `audit_dropped_topics.py old.ipynb new.ipynb` | *What did the rebuild stop teaching?* Terms used ≥3× in the original and 0× in the rebuild. |
| `sweep_artifacts.py nb.ipynb [...]` | *What did the rebuild leave behind?* Orphan prose, undefined names, dead cross-references, draft text, stale tooling. |

Run both on the **instructor** copies. Student scaffolds make the undefined-name check report
every name the student is meant to create, and solution-only code reports as dropped.

**Other checks worth repeating** (not scripted, run manually 2026-08-27/30): duplicate cells
(none in any module), URL liveness (28 distinct URLs), and whether any cell over ~60s streams
progress. Do **not** bother spell-checking against `/usr/share/dict/words`: it returned 294
unknown tokens of which 4 were real.

**Editing notebooks programmatically:** each element of a cell's `source` list must end with
`\n` except the last. Splitting on `'\n'` without re-adding them silently concatenates every
line into one, and the notebook still parses as valid JSON.

## Why each module was rebuilt

Modules 1, 2 and 3 were rebuilt from the dataset up; Module 4 was converted from a
demonstration into a lab; Module 5 was extended. The originals are retired, not deleted — read
this before restoring anything from them.

**Module 1.** It called its data "emails". It was not emails — the columns were URL lexical
features (`NumDots`, `UrlLength`, `AtSymbol`, `IpAddress`) with no sender, subject or body, and
students were told to print "the first 25 emails". Its Kaggle dependency had gone stale:
question 5D asked for `df.tail(400000)` and `df.head(11439)` against 662,591 rows whose label
boundary sits near index 100,011. The rebuild runs on `phishing_dataset1.parquet`.

**Module 2.** It shipped broken — a live `FileNotFoundError` in the load cell with stale output
below it, and five cells referencing `X_train_scaled`, `model`, `y_test` and `X_train` that no
code cell defined, because code lived in markdown for students to copy. Its Kaggle download was
over a gigabyte for one `.head()` call. And its central explanation was impossible: it
attributed a perfect score to the model memorising the attacker's IP `103.27.14.88`, but
`source_ip` is dropped before modelling. It also printed `model.coef_[0]` and called it "the
model's brain" on a three-class problem where `coef_` is `(3, 16)`. The rebuild keeps the
24-row toy log deliberately — you can read every row, and 100% on five test rows is the lesson.

**Module 3.** It could not execute: it loaded `phishing_dataset1.parquet`, then uploaded
`features_at_0.9_threshold_train.parquet`, a file the notebook itself produces thirty cells
later. Its stated premise was false — it promised "terrible recall" on the minority class where
the actual figure is **0.915**. And its prescribed fix was wrong: measured on genuinely
imbalanced data, SMOTE, undersampling and class weighting all make the model six to ten times
worse. **The thesis is inverted in the rebuild**: the module now measures the standard remedies
rather than asserting them, and finds threshold tuning and model choice beat all three.

**Module 4.** Unlike the others it executed correctly and was well seeded. It was converted
because it had **zero student tasks and zero gradable output** — all 21 code cells were
pre-written and the "Analysis & Reflection" headings stated conclusions rather than asking
questions. It now has 14 coding tasks and 8 write-ups. Two curriculum gaps were closed, both
topics named but never taught: **choosing `k`** (the module said this "often requires the Elbow
method or Silhouette analysis", demonstrated neither, and hardcoded k three times) and
**DBSCAN**, absent entirely. DBSCAN doubles as the counterpart to the existing scaling lesson —
Isolation Forest is tree-based and scale-invariant, DBSCAN is distance-based and is not.

**Removed from Module 4 separately:** a Gradio quiz and a self-defeating "Teacher's Decoder
Tool". They opened public `.live` tunnels from a student notebook — a poor pattern to model in
a security course — the links expire after 72 hours, and the saved output contained a real
student identifier and score. Since 2026-08-30 the ten quiz scenarios live
**in the notebook itself** (Module 4 cell 3) as a written activity — no LMS or external
quiz tool exists or is needed. `instructor/module4_knowledge_check_questions.md` is the
answer key.

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

## The organizing idea of Module 6, and how it was verified

**The spine: three things that sound right and are not, and one that is.** Module 5's throughline
is six results that are not what they appear; Module 7's is that there is an optimiser on the
other side. Module 6's is that *fluency is not evidence*, and it is what makes LLMs and
explainability one module rather than two half-modules bolted together.

| section | what you get | can you check it? |
|---|---|---|
| 2 | a detector with a 99.5% score | yes — and it falls to ~72% on ordinary modern email |
| 3 | a model that follows your instructions | no — until an attacker writes instructions into the data |
| 4 | a model's account of its own reasoning | **no.** It is generated text, produced like everything else it says |
| 4 | a SHAP attribution | **yes.** Arithmetic on the model, verified by hand to machine precision |

That last row is the constructive half and the reason the module is not merely cynical. Do not
remove it: "explainability" is not one thing, some explanations are measurements and some are
stories, and the whole module exists to make students able to tell which they are holding.

### What was verified, and what was not

**Module 6 has never run against a real language model.** The design decision recorded below —
live endpoint, no canned-transcript fallback — means the authoring environment cannot execute
its LLM cells. Rather than ship it unexercised, it was verified in three layers:

1. **The classical, SHAP and scoring code was executed for real**, locally, against the real
   datasets. Every number in the "Module 6" measured-facts block below came from running it.
2. **The API client was tested against a mock OpenAI-compatible server**: endpoint discovery
   across both path conventions, model listing, system-prompt and temperature passthrough, 401
   handling, and unreachable-host handling all behave as documented.
3. **The whole notebook was then executed end to end against a context-aware mock endpoint**
   (`nbconvert --execute`, all 62 cells, **zero errors**), with `DATA_URL` pointed at local
   files. That exercises every code path — chunking, JSON extraction, detection scoring,
   grounding, all three plots — so a `NameError`, a bad index or a wrong API shape cannot
   survive. What it cannot tell you is whether the *models* behave as the teaching notes claim.

**So the live pass must do two things**, not one: confirm the module runs, and confirm each
LLM-dependent claim in the direction its teaching note predicts. Those claims are the
zero-shot/few-shot crossover (§2), the injection-vs-capability trend (§3), the rationale/
attribution mismatch (§4), and per-stage triage recall (§5). Every one is stated as a
*direction* in the instructor headers, never as a digit — the drift rule applies with more
force here than anywhere else in the course, because LLM output is not reproducible even at
`temperature=0`, which §1.2 makes students measure for themselves.

**Module 6 ships with no stored outputs, deliberately.** Transplanting the mock run would put
fabricated model replies in front of students in the one module about not trusting fluent
output. Transplant after the first live pass, exactly as for every other module.

### Build discipline

Both copies are generated by `instructor/build_m6.py` from one source of truth. **Edit the
builder, never the notebooks** — it is what makes the integrity invariants hold by
construction (equal cell counts; markdown differs only at cell 0; code only at the 16 exercise
indices; no `INSTRUCTOR SOLUTION` / `TEACHING NOTE` string can reach the student copy). All of
those were re-checked after the build and pass. The artifact sweep returns **2 findings, both
verified false positives**: `device_type_Unknown` and `firewall_rule_Deny` in cell 15, which are
a deliberate callback to Module 2's coefficients and are correctly backticked column names.

The capstone dataset is generated by `instructor/gen_forensic_log.py`, which is deterministic
and was confirmed to reproduce the two shipped CSVs byte-identically.

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
`smote` -> `RandomForestClassifier(n_estimators=50)`, grid over `smote` in
`['passthrough', SMOTE]` and `model__max_depth` in `[None, 10]`, `scoring='f1'`,
`cv=StratifiedKFold(3, shuffle=True, random_state=42)`, `verbose=2`.

| smote | max_depth | mean CV F1 | std | rank |
|---|---|---|---|---|
| passthrough | None | **0.8411** | 0.0138 | 1 |
| passthrough | 10 | 0.8312 | 0.0161 | 2 |
| SMOTE | None | 0.8282 | 0.0161 | 3 |
| SMOTE | 10 | **0.6201** | **0.0716** | 4 |

`best_params_` is `{'model__max_depth': None, 'smote': 'passthrough'}` — the library defaults.
Held-out P 0.941 / R 0.816 / **F1 0.874**, which is *exactly* D.2's 100-tree forest.

**Three results, all negative — say so to students before they think they broke it.** The
search was free to use SMOTE and refused it, applied the correct way inside the pipeline at
every fold; that is what retires the objection that Lab C only beat SMOTE by applying it
crudely, and it is the reason the lab exists. Tuning changed nothing, confirming D.2's
default-vs-default comparison was fair rather than lucky. And the winning **50**-tree forest
ties D.2's **100**-tree forest to three decimals, so doubling the trees bought nothing either.
Direct held-out check on the same forest: no resampling P 0.941 / R 0.816 / F1 0.874, against
SMOTE-in-pipeline P 0.871 / R 0.827 / F1 0.848 — fold-safe SMOTE buys 0.011 recall for 0.070
precision, at double the training time.

**The ranking is identical at 30, 50 and 100 trees** — only the cost changes. That is what
makes the 50-tree search safe.

*Added 2026-08-30 (audit), measured locally at seed 42 — model metrics, quote as approximate:*

| model | ROC AUC | PR AUC (average precision) |
|---|---|---|
| naive logistic regression | 0.9605 | 0.7414 |
| Random Forest (100 trees) | 0.9630 | 0.8734 |

ROC AUC cannot separate the course's worst and best models at 577:1 (0.0025 apart); PR AUC
separates them by 0.13. That contrast is the point of the new ROC/PR cell after Lab C.2 —
preserve it. The new feature-importance cell's facts: V17 / V14 / V12 lead the forest's
`feature_importances_`, top 3 carrying ~44% of the total.

**Grid-search timings, and the mistake worth not repeating.** 65s on 12 cores; **274s on 2**;
Colab's two vCPUs are slower still, so budget **4–8 minutes**. The first version of this lab
used `n_estimators=100` and `verbose=1` and was shipped with the estimate "about two minutes
locally, longer on Colab" — extrapolated from a 12-core machine without ever testing a
constrained one. On Colab it ran 15–25 minutes while printing **one line and then nothing**,
which is indistinguishable from a hang, and it was reported as one. Two fixes: halve the
forest (verified not to change the ranking), and **`verbose=2`, which prints all twelve
`[CV] END` lines as they finish**. Generalise this: any cell over ~60s needs streaming
progress, and any runtime estimate for Colab must come from a core-limited measurement, not
from dividing a fast machine's number by a guess.

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

Colab, 2026-08-30: CNN **89.02% / 0.8846**, LSTM **85.30% / 0.8402**, exercise **0.9029**.
Within a tenth of a point of the local run on all three — but see the drift rule; quote these
as `~89%` / `~85%`, not exactly.

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
- Reference results, **two runs, and this is what drift looks like**:

  | protocol | local | Colab 2026-08-30 | notebook quotes |
  |---|---|---|---|
  | honest — deduplicated, 23 classes | 97.99% / 0.949 | **98.56% / 0.9637** | `~98%` / `~0.95` |
  | naive — as distributed, 25 classes | 94.87% / 0.910 | **95.08% / 0.9143** | `~95%` / `~0.91` |

  `Yuner.A` recall 1.000 in both. The notebook's approximations covered both runs, which is
  the drift rule working as designed — do not replace them with exact figures.
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
- TF-IDF + logistic regression: **99.50% in 7.5s**. The Conv1D model: **~99.6%**.
  Colab 2026-08-30: TF-IDF 99.50% / F1 0.9955 / 7.0s; Conv1D **99.59% / F1 0.9963** / 11.6s;
  majority-class baseline 55.79%. An earlier note here recorded the Conv1D as "99.63%", which
  was its **F1**, not its accuracy. The gap between the two models is a tenth of a point either
  way, which is the section's whole argument.
- First 5 words alone → 95.6%. First 10 → 97.7%. First 20 → 98.5%.
- Top "legitimate" tokens are `python`, `perl`, `postfix`, `list`, `wrote`. 30.0% of benign
  messages contain "mailing list" and 27.4% contain "listinfo", against ~0.1% of malicious.
  The benign class is developer mailing list traffic.

**Module 6 — `CEAS_08.parquet` and `forensic_log.csv`.** Everything below was measured by
execution locally. The sklearn figures are deterministic on a fixed split and reproduced
identically across runs; quote structural facts exactly and model metrics as approximations,
as always.

*Section 2 — the 2008 detector, rebuilt with Module 5's exact split and settings:*

| check | value |
|---|---|
| reproduction of M5's baseline | **99.49%** accuracy, F1 **0.9954**, ~3s |
| split | 31,323 train / 7,831 test (M5's figures, reproduced) |
| top tokens for LEGITIMATE | `wrote` −7.23, `org` −6.52, **`2007` −4.35**, `thanks` −3.74, `python` −3.66, `perl` −2.99 |
| top tokens for MALICIOUS | `com` +7.29, `your` +6.35, `love` +4.94, `replica` +3.80, `watches` +3.21, `cnn` +2.94 |
| `password` coefficient | **−0.847 — evidence the message is LEGITIMATE** |
| `verify` / `account` / `login` | −0.113 / −0.564 / −0.275, all toward legitimate |
| `urgent` / `click` | +0.356 / +0.709 |
| modern probe set (12 phish + 6 benign, hand-written) | **72.2%** accuracy |
| phishing recall on the probe | **8/12 (67%)**; missed the IT-migration, DocuSign, HR-handbook and MFA-disabled lures |
| mean p(malicious) on the 12 phishing mails | **0.577** |
| confidence, CEAS test | mean **0.963**, **40.1%** above 0.99, 2.2% below 0.75 |
| confidence, modern probe | mean **0.677**, **0.0%** above 0.99, **88.9%** below 0.75 |

**The 99.5% model is a 2008-spam-genre detector, and `2007` being among its strongest evidence
for "legitimate" is the cleanest construct-validity failure in the course.** An earlier
hypothesis — that the mailing-list traffic was the culprit, so excluding it would collapse the
score — was **measured and did not survive**: dropping every test message containing "mailing
list" or "listinfo" moves accuracy 99.49% → 99.44%. The shortcut is real; that particular
prediction about it was wrong. Do not reinstate it.

*Section 4 — SHAP, and this is arithmetic, so it must reproduce exactly:*

| check | value |
|---|---|
| base value `w·E[x] + b` | **+0.3873** |
| efficiency, `base + Σφ` vs the logit | agrees to **~1e-16** on every row |
| `shap` LinearExplainer at its DEFAULTS | max diff **6.577e-02**, base value **+0.5239** — it silently subsamples the background to 100 rows |
| `shap` with `Independent(A_train, max_samples=31323)` | max diff **0.000e+00** — exact agreement |
| on the missed IT-migration lure | 33 tokens present, sum φ **−1.8806**; 19,967 absent, sum φ **+1.0072** |
| occlusion ("LIME's core idea") vs exact SHAP | Pearson **0.928**, Spearman **0.894** — and **9 of 33 tokens land on the wrong side of zero** |

**Task 4.3's occlusion result is the one to protect if the section is ever trimmed.** An r of
0.93 is the kind of number that gets an approximation waved through, and it coexists with nine
of thirty-three tokens attributed in the *opposite* direction. The mechanism is that
`TfidfVectorizer` L2-normalises each document, so deleting one word rescales every other
feature and the occlusion score for word A silently absorbs the renormalisation of B..Z. It
generalises to every perturbation explainer: they assume features can be varied independently,
and correlated or normalised features break that quietly.

**More than half the model's evidence comes from words that are not in the email.** Absent
features get φ = −w·E[x], so every 2008 mailing-list word the message fails to contain counts as
evidence *for* maliciousness. The email's own words say legitimate (−1.88) and the missing
vocabulary says malicious (+1.01); they nearly cancel, which is *why* Section 2's confidence
histogram piles up near 0.5. Sections 2 and 4 interlock on this — do not edit one without the
other.

*Section 5 — the capstone log (generated, deterministic, exact):*

| check | value |
|---|---|
| lines / malicious | **774 / 46 (5.9%)** |
| hosts / log sources | 8 / 7 (`cron`, `firewall`, `nginx`, `sshd`, `sudo`, `systemd`, `useradd`) |
| message text | 45,685 chars, ~11.5k tokens — fits a 128k context; chunked at 80 lines (**10 chunks**) anyway |
| intrusion | line_ids **212–260**, 2026-03-11 02:14–03:09, with 3 benign lines interleaved |
| stages | recon 12, enumeration 7, brute_force 14, initial_access 2, persistence 4, lateral_movement 2, collection 1, exfiltration 4 |
| attacker / C2 | `185.243.115.94` / `45.147.230.61` |
| the chain | brute-force `deploy` on vpn01 → `useradd svc_update` + cron C2 → lateral to db01 → `mysqldump` → 4 large transfers out |
| "flag everything" baseline | precision 0.059, recall 1.000, **F1 0.112** |

Two design points to preserve. **Legitimate overnight activity was added on purpose** — nightly
backups, healthchecks, logrotate, including 11–28 MB internal transfers on the intrusion night —
so "it happened at 02:00" and "it was a big transfer" are not free answers. And **most chunks
contain nothing**, which is the point: a model that reports a finding in every chunk produces a
fluent, entirely fictional incident report, which is why Task 5.2 scores false positives and not
just recall.

**Final lab (IoT flows).** 85,502 rows combined; 2,043 exact duplicates (concentrated in
PortScan); 1 row with nulls; no constant columns in the combined set; no feature rows with
contradictory labels. After cleaning: 83,458 rows, 3,215 backdoor / 80,243 portscan (25:1).
**Majority-class baseline accuracy is 96.15%** — a dataset fact, exact. Reference solution
with a tuned threshold: accuracy 95.57%, macro F1 0.691, backdoor F1 0.405, backdoor recall
~0.39. Colab 2026-08-30: threshold 0.5418, accuracy **95.34%**, macro F1 **0.7010**, backdoor
F1 **0.4263**, recall **0.4495**. The notebook states these as ranges (accuracy ~95.1–95.5%,
macro F1 ~0.69–0.71, backdoor F1 ~0.40–0.43, recall ~0.42–0.48) and both runs land inside all
four. The lesson does not depend on the digits: accuracy comes in **below** the do-nothing
baseline while the model catches roughly 40% of backdoor flows the baseline catches none of.

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

### The artifact sweep — a different tool for a different defect

The topic audit answers *what did the rebuild stop teaching?* It cannot answer *what did the
rebuild leave behind?* `instructor/sweep_artifacts.py` does that, over five categories:

| check | what it catches |
|---|---|
| **A. orphan prose** | a backticked identifier in markdown that no code cell defines or uses |
| **B. undefined name** | a name a code cell loads that no earlier cell bound — AST-based, so it sees lambda args and comprehension targets |
| **C. dead xref** | a Module / Section / Lab / Task reference with no matching heading |
| **D. draft text** | TODO, FIXME, "need video", unresolved authoring chatter |
| **E. stale tooling** | Kaggle, Gradio, yellowbrick, `files.upload`, `drive.mount` |

Category A is the one that catches the Module 3 failure mode. Run it on the **instructor**
copies; student scaffolds make category B report every name the student is meant to create.

Findings on 2026-08-30, after the audit edits: **6, all verified false positives** — three real
dataset column names in Module 1 (the code selects them by suffix, so no literal match),
`C2LOP.P` in Module 5 (a real Malimg family, confirmed against `malimg_64.npz`; now cell 64),
Module 5's `drive.mount` (now cell 87), which sits inside a markdown code block as optional
guidance and never executes, and `explorer.exe` in Module 4 cell 3 — a Windows process name
inside a knowledge-check scenario, not code. The sweep gained four category-D patterns on
2026-08-30 (`**Reasoning**:`, `subtask`, `Data Analysis Key Findings`, `Insights or Next
Steps`) after Module 4 was found still carrying its AI-authoring narration; they now guard
against that class of leftover.

**Checks the sweep does not cover, run manually 2026-08-27:** duplicate cells (none in any
module) and URL liveness (28 distinct URLs; see below).

### Fixed 2026-08-27

| defect | where | fix |
|---|---|---|
| dead link, hard 404 | M2 cell 55, DataCamp scikit-learn cheat sheet | replaced with `scikit-learn.org/stable/machine_learning_map.html` |
| **expired TLS certificate** | M3 cell 60, `neptune.ai` | replaced with `scikit-learn.org/stable/modules/compose.html` — students would have hit a browser security warning |
| typo `tequniques` | M2 cell 11 | `techniques` |
| typo `validatate` | M4 cell 1 — **a learning objective** | `validate` |
| typos `Valuble` / `guidence` / `Dr. ismail` | M3 cell 60 | `Valuable` / `guidance` / `Dr. Ismail` |
| hardcoded dataset URL | M4 cell 67 | routed through `DATA_URL` like every other module |

`media.defense.gov` returns 403 to every automated agent (bot protection) and could not be
verified from here. It is the only URL in the course whose state is unknown; check it in a
browser.

**On spell-checking:** `/usr/share/dict/words` is far too thin for this material — it lacks
plurals, contractions and most ordinary technical vocabulary, and returned 294 unknown tokens
of which 4 were real. Useful only with a large allowlist, and only for finding rare one-off
tokens. Do not treat its output as a defect list.

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

## Curriculum decisions and open gaps

**Deliberately absent — do not report these as gaps.**

- **SVMs.** 18 uses in the original Module 3, now one passing mention in Module 1's concept
  list. SVC is slow on 227k rows and the module already compares three families. One scenario
  in the Module 4 knowledge check keeps students able to recognise an SVM as supervised. This
  is a decision, recorded so it stays one.
- **`LearningCurve` (yellowbrick).** Replaced by sklearn's `learning_curve`, which Module 3
  uses.
- **`to_parquet` / persisting a cleaned dataset.** Each rebuilt module loads from `DATA_URL`
  and stands alone.
- **Imputation.** Module 2 covers the same ground.
- **Regression.** Named in Module 1's taxonomy, never practiced. Decided 2026-08-30: every
  security problem in this course is detection/classification, and that is representative of
  the field. Recorded so it stays a decision.
- **The reading-half prose voice.** The expository halves of Modules 1–3 are heavier and more
  textbook-toned than the rebuilt lab halves. Reviewed 2026-08-30 and deliberately left: the
  content is accurate and referenced, and a wholesale rewrite risks vocabulary drops the topic
  audit would then chase. Module 4's narration cells — the actual defects — were rewritten. If
  a full voice pass is ever done, run `audit_dropped_topics.py` before/after per module.
- **Naive Bayes.** Appears in one knowledge-check scenario (which tests paradigm recognition,
  not the algorithm) with an in-notebook gloss saying the course does not teach it.
- **Gradient boosting (XGBoost/LightGBM).** Not taught. Open question rather than settled:
  arguably more industry-relevant than SVMs; the Module 3 bake-off is the natural home if it
  is ever added. One line in the bake-off's write-up could also simply name it.

**Genuinely open.**

1. **Module 6 has never run against a real model.** Everything else about it is verified;
   see its section above for exactly what that means and what the live pass must do.
2. **Malimg at full resolution.** Malimg encodes file size in image height and the 64×64 resize
   destroys it, so `Yuner.A` and `Autorun.K` collapse to one image each. They may be separable
   at full resolution. The raw `malimg_dataset` folder was deleted locally; the notebook flags
   this as unresolved rather than hiding it.
3. **`media.defense.gov` link, Module 1 cell 60.** Returns 403 to every automated agent (bot
   protection) and could not be verified. The only URL in the course whose state is unknown.

**Resolved, listed so they are not re-opened:** Kaggle removed course-wide; Module 2's
impossible source-IP explanation and `coef_[0]` error; Module 3's circular dependency and
inverted thesis; Module 4's draft text, Gradio tunnels, and unreconciled PCA variance claim;
Module 3's missing leakage story (SMOTE before the split reports F1 0.948 against an honest
0.109); hyperparameter tuning and `ImbPipeline` (Lab D.3, 2026-08-27); Pearson vs Spearman
(Lab A.5); a hard-404 DataCamp link and an expired TLS certificate on `neptune.ai`; four typos
including `validatate` in a Module 4 learning objective.

**A correction to an earlier note in this file:** it claimed Modules 3–4 had no random seeds.
That was **wrong about Module 4**, which had twelve `np.random.seed(42)` / `random_state=42`
occurrences and was the best-seeded of the original four.

## Module 7 — built 2026-08-30, decisions and measured facts

**Structure (31 cells):** intro + attack taxonomy + MITRE ATLAS framing → S1 re-arm both
targets (DGA CNN + backdoor MLP) with the model-sync contract assertion → S2 evasion flagship
(DGA char-insertion) → S3 feature-space FGSM + the problem-space caveat → S4 poisoning (trigger
backdoor) → S5 membership inference + model extraction → S6 defence (adversarial training + the
lifecycle table + governance) → final lab (attack & defend the backdoor detector) → module +
course summary. Given cells: setup, both model rebuilds, checkpoint. Scaffolded exercises:
2.1, 3.1, 4.1, 5.1, 5.2, 6.1, final lab.

**Decisions made (record so they stay decisions):**
- **Flagship retargeted from Malimg to the DGA CNN.** The null-byte-append attack on the malware
  CNN needs raw binaries the course cannot distribute; the DGA character-perturbation attack is
  trivially distributable, fully verifiable, and just as visceral. Malimg is kept as a *worked
  explanation* in the summary, not a runnable lab. (Confirmed with Abe 2026-08-30.)
- **M7 rebuilds both targets from public data** rather than requiring the student's saved
  `backdoor_detector.keras` (which is private/gitignored). "Load your own if you kept it" is the
  optional path. This keeps M7 standalone; the contract-assertion cell is the M5/M7 sync guard.
- **Membership inference uses a random-label forced-memorisation construction.** A model trained
  to fit random labels can only memorise, giving a reliable, reproducible loss gap (member ~0.000,
  non-member ~4, MI ~86%). An earlier "small model, real labels, long training" version did *not*
  reliably memorise on this separable task (one full run came back at ~50%/no-leak) — do not
  revert to it. The production model's ~50% (no leak) is kept as the contrast.
- **Synthetic-media / FLUX demo left out** of the core module (mentioned as an optional extension
  only). Adds a heavy dependency for a tangential point.
- **ATLAS technique IDs verified against MITRE, 2026-08-30** (a first build had three wrong).
  Correct mapping: S2 greedy/query-based = **AML.T0043.001 Black-Box Optimization**; S3 FGSM =
  **AML.T0043.000 White-Box Optimization**; S4 = **AML.T0020** + **AML.T0043.004 Insert Backdoor
  Trigger**; S5.1 = **AML.T0024.000 Infer Training Data Membership**; S5.2 = **AML.T0024.002
  Extract ML Model** via **AML.T0040 AI Model Inference API Access**. `AML.T0044` does not exist
  in the ATLAS technique list — do not cite it. Re-verify if ATLAS renumbers.
- **The backdoor threshold is tuned on the test set**, inherited from M5's final lab. Kept
  deliberately (every attack is measured as a fall from that same baseline, so comparisons hold)
  but now **declared in-notebook** rather than passed over. Do not silently "fix" it without
  re-measuring every attack baseline.

**Measured facts (local, seed 42, TF 2.21 — quote as DIRECTIONS, not digits; adversarial search
is stochastic and the final-lab numbers especially move per run):**

| stage | result |
|---|---|
| DGA CNN baseline | ~89% acc, F1 ~0.88 |
| Backdoor MLP baseline | ~95% acc, backdoor recall ~0.43–0.46; contract: input 39 == meta n_features 39 |
| Evasion (DGA flagship) | ~94% of flagged domains flip with **1 inserted char** (a hyphen), 100% within 2; conf 1.00→~0.02 |
| Evasion (FGSM on MLP) | recall ~0.43 → ~0.10 (ε=0.05) → ~0.002 (ε=0.25) |
| Poisoning (trigger `qzx7q`) | 0% control = no effect; **0.5%** of labels → ~96% trigger escape; clean F1 flat (~0.885); 3% → 100% |
| Membership inference | production ~50% (no leak); forced-memorise member loss 0.000 / non-member ~4 → MI ~86% |
| Model extraction | surrogate from 60k query answers (pool = **attacker-collected** held-out domains, never the target's training set) agrees ~90% on unseen domains and inherits the hyphen blind spot. A **synthetic random-string pool reaches only ~66%** — the query distribution matters, which is what makes query monitoring a real defence |
| Adversarial training (DGA) | **like-for-like on the same fixed mid-hyphen attack**: undefended still-flags ~35% → hardened ~100%, for ~0.7–1.4 F1 points. Do NOT use Section 2's greedy ~5% as the 'before' number — different, stronger attack. **Greedy still evades ~95% with a different edit** — the honest limit |
| Final lab (backdoor) | FGSM ε=0.05 cuts recall ~0.43→~0.10; adv-training on ε=0.1 gives **no reliable recovery** (lands ~0.09–0.15, i.e. within noise, sometimes slightly lower) — a deliberate honest-weak-result contrasting with 6.1's clean DGA defence. Single-step feature-space adv-training is known to be brittle; do not quote a recovery figure |

**The flagship's throughline (preserve it):** the DGA model learned "hyphen/structure = legit"
as a proxy — the same construct-validity shortcut M5 Section 5 exposed — and a single hyphen
walks through it. The evasion is not generic noise; it attacks the gap between what the model
was *named* to do and what it *learned* to do. Keep that connection explicit; it is what makes
M7 the payoff of the whole course rather than a bolt-on.

**Colab verification — DONE 2026-08-31, zero errors.** Local vs Colab, showing the drift rule
working as designed (dataset/structural facts exact, model metrics inside range):

| check | local | Colab | notebook quotes |
|---|---|---|---|
| DGA CNN | 89.00% / F1 0.8828 | 88.98% / 0.8825 | `~89%` / `~0.88` |
| contract, discrete features | 39==39, 11 of 39 | 39==39, 11 of 39 | **exact both runs** |
| evasion ≤1 / ≤2 edits | 94% / 100% | 94% / 100% | **identical** |
| backdoor clean recall | 0.434 | 0.449 | ~0.43–0.46 |
| FGSM ε=0.05 / 0.25 | 0.103 / 0.002 | 0.118 / 0.025 | ~0.10–0.14 / near zero |
| poisoning 0% / 0.5% escape | 0% / 96% | 0% / 96% | **control exact** |
| membership inference | 50.4% / 85.8% | 50.4% / 85.8% | ~50% / ~86% |
| extraction: collected / synthetic | 90.6% / 66.3% | 90.5% / 69.2% | ~90% / ~66–69% |
| 6.1 like-for-like | 35% → 100%, cost 0.7 | 34% → 100%, cost 0.6 | ~34–35% → ~100% |
| final lab hardened @ε=0.05 | 0.090 (vs 0.103) | 0.087 (vs 0.118) | no reliable recovery |

**The most important confirmation:** the final lab's hardened model came out *below* the
undefended one on Colab too (0.087 vs 0.118). Had the original "adversarial training restores
most of it" claim shipped, Colab would have contradicted the notebook in front of students.
The streaming-progress fixes also worked — the `[1/3]…[3/3]` poisoning lines and the
per-epoch DGA output are visible in the PDF.

**Colab pins TensorFlow 2.20.0** against the local 2.21.0; no compatibility issues surfaced.

## Modules 6 and 7 design decisions (both now BUILT — kept for the model roster and the record)

**Module 6 — BUILT 2026-09-01.** See "The organizing idea of Module 6" above for the spine,
the verification status and the build discipline. The design below was followed; five things
were settled *during* the build and are recorded here so they stay settled:

1. **No `openai` SDK — plain `requests`.** Zero install on Colab, one fewer version-drift
   surface, and it puts the bearer token visibly on the wire, which is the point Section 1.1
   is making. Students write the client themselves; it is six lines.
2. **The endpoint path is discovered, not assumed.** Open WebUI serves
   `/api/chat/completions`; a plain OpenAI-compatible gateway serves `/v1/chat/completions`.
   Both are "OpenAI-compatible", and guessing wrong yields a 404 indistinguishable from a dead
   server. `discover_endpoint()` probes both and is given to students rather than assigned.
3. **`gemma3:27b` stays the capstone model; `qwen3.8:27b` was not adopted.** Its 262K context
   would buy nothing here — the capstone log is ~11.5k tokens and *deliberately* chunked at 80
   lines, because chunking is the lesson. Revisit only if a future capstone needs a log that
   genuinely does not fit 128K. This also avoids depending on Ollama ≥0.32.
4. **`phi4:latest` is used, exactly as the roster note proposed**, as the middle data point in
   the prompt-injection demo. Three models across 3B → 14B → 27B make "capability is itself a
   security control" a measured trend rather than a two-point anecdote.
5. **First module in the course to `pip install` anything** (`shap`, in the Section 4 cell that
   needs it, guarded by a try/except so it installs only when absent). Everything else runs on
   what Colab already ships. If the live pass finds `shap` fragile on Colab's pinned numpy, the
   fallback is already in the notebook: Task 4.1 derives the exact values by hand and does not
   need the library at all.

Abe hosts models locally behind Open WebUI (OpenAI-compatible API, publicly routable), with a
dedicated "google colab user" API key.

| use | model | why |
|---|---|---|
| workhorse (few-shot phishing, most exercises) | `qwen3:8b` | best instruction-following per parameter; serves concurrent students. Disable thinking mode for classification labs (`/no_think`) or output is slow and hard to parse |
| capstone log triage | `gemma3:27b` | 128k context; logs are long |
| prompt-injection demo | `llama3.2:3b` **and** `gemma3:27b` | same payload against both — the small model folds, the large one usually resists. The contrast is the lesson: model capability is itself a security control |
| XAI section | `gpt-oss:20b` | exposes reasoning traces; compare its stated reasoning against SHAP attributions on the same email. Plausible is not faithful |

Read **both** the base URL and the key from Colab secrets (`OPENWEBUI_BASE_URL`,
`OPENWEBUI_API_KEY`), never hardcode — the URL too, because the homelab may move (the `DATA_URL`
lesson) and a routable URL + key in a notebook a student later publishes is the exact leak the
course preaches against. Rotate per cohort and rate-limit; scope the key server-side to just the
course models. **Decided 2026-08-30, and honoured in the build: M6 labs require the live endpoint — no
canned-transcript fallback.** A student whose endpoint is down cannot complete the module
offline; accept that or revisit. This is why **M6 could not be verified from the authoring
environment**, and what the three-layer mock verification described above was doing instead.
The notebook's connectivity-check cell lists what the server actually serves and names any of
the five required tags that are missing, so the live pass confirms the roster automatically.

**Full Ollama roster, as of 2026-08-31.** All four models the design above depends on are still
served, so the plan stands unchanged. Read the "notes" column as a *throughput tier*, because
that is what decides whether a model can face a class of concurrent asynchronous students:

| model | size | tier / note |
|---|---|---|
| `llama4:scout` | 67 GB | 109B MoE, **heavy CPU-offload, ~5-15 tok/s** |
| `qwen3:32b` | 20 GB | dense all-rounder, partial offload |
| `qwen3-coder:30b` | 18 GB | agentic coding MoE |
| `qwen3.8:27b` | 17 GB | dense multimodal, **262K ctx**, needs Ollama ≥0.32 |
| `gemma3:27b` | 17 GB | all-rounder — **capstone model** |
| `gpt-oss:20b` | 13 GB | MoE, reasoning traces — **XAI section** |
| `phi4:latest` | 9.1 GB | 14B, **fits VRAM** (fully GPU-resident) |
| `qwen2.5-coder:14b` | 9.0 GB | FIM coding, recommended serve model |
| `qwen2.5-coder:7b-instruct-q8_0` | 8.1 GB | coding, q8 |
| `qwen3:8b` | 5.2 GB | fast all-rounder — **workhorse** |
| `llama3.1:8b` | 4.9 GB | fast general |
| `qwen2.5-coder:7b` | 4.7 GB | FIM coding |
| `phi4-mini:latest` | 2.5 GB | fast small |
| `llama3.2:3b` | 2.0 GB | fast — **prompt-injection "folds" model** |

Three consequences for M6, to settle before authoring rather than during:

1. **`llama4:scout` is disqualified, and that is a decision.** At ~5-15 tok/s a single capstone
   log-triage response takes minutes, and concurrent students would collapse it. Do not reach for
   it because it is the biggest model on the list.
2. **`phi4:latest` is the interesting new arrival** — 14B that *fits VRAM*, so it is fully
   GPU-resident and the best throughput-per-capability on the roster. Two uses: a faster
   workhorse alternative to `qwen3:8b` if concurrency measurement says so, and a **middle data
   point in the prompt-injection demo**. Three models across a capability range (3B folds → 14B →
   27B resists) turns "model capability is itself a security control" from a two-point anecdote
   into a measured trend. Worth doing if the endpoint can take the load.
3. **`qwen3.8:27b` is a capstone candidate** at 262K context against `gemma3:27b`'s 128K — more
   log per prompt, which is exactly the capstone's constraint. But it **needs Ollama ≥0.32**, so
   confirm the container version before depending on it; otherwise stay on `gemma3:27b`. A/B the
   two during the verification pass.

Coding models (`qwen3-coder:30b`, the `qwen2.5-coder:*` family) are not relevant to M6's content,
which is security *text*, not code generation.

Also available and unused: FLUX.2 dev, FLUX.1 schnell, SDXL, Z-Image Turbo. Left out of M7's core
build (see below); available if a synthetic-media social-engineering demo is ever wanted.

**Module 7 — BUILT 2026-08-30. See the "Module 7 — built" section above for the full structure,
decisions and measured facts.** The design intent recorded here originally proposed the malware
CNN as the flagship target (append null bytes → byte layout shifts → texture smears). That was
**changed during the build**: the attack needs raw binaries the course cannot distribute, so the
runnable flagship is the DGA character-perturbation attack instead, with Malimg kept as a worked
explanation. The M3/M5-in-sync requirement is enforced by a contract-assertion cell in M7 S1
(loads the model, asserts input width == the saved meta's feature count). Weeks 14/15 were
collapsed into the one module as planned.

## Environment notes

**Local is for authoring; Colab is the proof.** The local stack is ahead of what Colab pins, so
anything a published number depends on needs a confirming Colab run. This is not pedantry — the
BatchNorm collapse below was invisible until the model actually ran. All five modules are
portable: no `files.upload`, no Kaggle, no absolute paths. Module 5's only Colab-ism is
`display()`, plus an optional `drive.mount` snippet inside a markdown block that never executes.

**Colab runtime is roughly 2 vCPUs and slower per core than an Apple Silicon laptop.** Estimate
Colab cost from a *core-limited* measurement, never by dividing a fast machine's number by a
guess. Module 3's Lab D.3 shipped as "about two minutes" from a 12-core measurement and took
15–25 minutes on Colab. Any cell over ~60s needs streaming progress (`verbose=2`, per-epoch
output) or it is indistinguishable from a hang — and will be reported as one.

**TensorFlow on Apple Silicon: use `tensorflow`, not `tensorflow-cpu`.** `tensorflow-cpu` has
never published a macOS arm64 wheel in any release — verified against the PyPI release index,
2026-08-21. Plain `tensorflow` does, and 2.20/2.21 include cp313. **Run every model before
shipping it**: both architecture bugs found so far (an unbuilt `summary()` and the BatchNorm
collapse) were invisible to static review.

**Keras `validation_split` takes the last n% without shuffling.** On family-ordered data like
Malimg's native row order that hands the model a validation set of classes it never trained on,
and you see ~1% val accuracy that looks like catastrophic overfitting. Shuffle first.

**Local Jupyter + MCP is the working setup for driving notebooks** — `datalayer/jupyter-mcp-server`,
actively maintained, 18 tools.

```bash
uv venv --python 3.13 ~/.venvs/aicyber
uv pip install --python ~/.venvs/aicyber/bin/python \
  jupyterlab jupyter-collaboration jupyter-mcp-tools ipykernel \
  tensorflow scikit-learn pandas numpy pyarrow matplotlib seaborn imbalanced-learn scipy
~/.venvs/aicyber/bin/python -m ipykernel install --user --name aicyber \
  --display-name "Python (AI-Cyber)"
uv tool install --python 3.13 "jupyter-mcp-server>=1.5.0"

# token via env so it stays out of `ps`; loopback only -- the upstream README's
# `--ip 0.0.0.0` would expose the kernel, and a Jupyter token is arbitrary code execution
env JUPYTER_TOKEN="$(cat ~/.venvs/aicyber/.jupyter_token)" nohup \
  ~/.venvs/aicyber/bin/jupyter lab --port 8888 --ip 127.0.0.1 --no-browser \
  --ServerApp.root_dir="$HOME/AI-Cyber-Intro-Cert" > ~/.venvs/aicyber/jupyter.log 2>&1 &
```

Token at `~/.venvs/aicyber/.jupyter_token` (mode 600). MCP registered at local scope in
`~/.claude.json` with `JUPYTER_URL` / `CODE_SANDBOX_URL` set to **`http://127.0.0.1:8888`, not
`localhost`** — the server binds IPv4 only and `localhost` can resolve to `::1`. The venv lives
outside the repo on purpose: the remote is public. Verified stack: **pandas 3.0.5 / numpy 2.5.2
/ TensorFlow 2.21.0 / scikit-learn 1.9.0 / imbalanced-learn 0.14.2 / Python 3.13.14**.

**Colab MCP bridge (`googlecolab/colab-mcp`) — abandoned 2026-08-21. Do not retry it.** The
Colab page connects, authenticates, and is dropped in the same second, reproducibly. Ruled out
by direct test: token, origin allowlist, port reachability on both address families, stale
cookies, orphaned servers, missing runtime, wrong tab. Upstream is stale (last commit
2026-04-01) with five unresolved reports: #43, #54, #81, #84, #100. **The decisive point:**
`SCRATCH_PATH` is hardcoded to `/notebooks/empty.ipynb` and discussion #80 confirms it cannot
attach to an existing notebook — even working perfectly it would open a blank scratchpad, never
a module from Drive. It could not have done the job it was being fixed for.

Two findings worth keeping. **A genuine dual-stack bug, still unreported upstream:**
`websockets.serve(host="localhost", port=0)` opens one socket per address family, each getting
its *own* ephemeral port, while only `sockets[0]`'s port is advertised in the URL fragment — so
the advertised port is unreachable over the other family (observed `[::1]:64298` +
`127.0.0.1:64299`). A local patch is applied at
`~/.local/share/uv/tools/colab-mcp/lib/python3.13/site-packages/colab_mcp/websocket_server.py`,
original saved beside it as `.orig`; `uv tool upgrade` will overwrite it. And **Safari can never
work** here: it refuses to treat `ws://localhost` as a secure context and blocks the dial-back
as mixed content. Chrome and Firefox exempt localhost.
