# AI-Cyber Intro Certification — Working Context

Context for Claude Code sessions in this repo. Written 2026-08-21.

## What this is

An **introductory** certification course on AI for cybersecurity, taught as a series of
Google Colab notebooks. Asynchronous — students read, run, and modify code in the
notebook itself. Owner/author: Abe Weigant.

Two sister courses build on this one: one covering **LLMs** in depth, one covering
**securing AI** in depth. Modules 6 and 7 preview those while standing on their own.

Condensed from a 15-week outline into 7 modules.

| Module | Title | Status |
|---|---|---|
| 1 | Course Introduction & The Role of AI in Cybersecurity | Done, needs polish |
| 2 | Cyber Threat Landscape, Data Sources, Preprocessing, First ML Model | Done, needs polish |
| 3 | Supervised Machine Learning | Done, needs polish |
| 4 | Unsupervised Learning: Anomaly Detection & Threat Hunting | Done, needs polish |
| 5 | Deep Learning Models for Cybersecurity | **Complete, pending verification** |
| 6 | LLMs + Explainable AI (capstone: LLM-assisted forensic log triage) | Not started |
| 7 | Adversarial Attacks & the Secure AI/ML Lifecycle | Not started |

## Repo layout

This repo is the course's **dataset host**. Notebooks pull data by raw GitHub URL,
which deliberately keeps students off Kaggle API tokens after Module 1.

```
Module1_Intro-2.ipynb            Module 1 notebook (naming is inconsistent across
Student_Module2_.ipynb           the five files -- these are the real filenames)
Student_Module3.ipynb
Module4_Student.ipynb
Module5_Student.ipynb
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

**All five modules are now checked in** (commit `e6843c8`, 2026-08-20). The canonical
copies still live in Google Drive / Colab — these are downloaded snapshots, so re-export
from Colab (File → Download → Download .ipynb) before editing if the Colab copy has moved
ahead. Modules 1–4 are committed with saved outputs; see the student-identifier warning
under Known gaps before pushing anything from Module 4.

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

## Open items

1. **Full end-to-end execution of Module 5 in one pass.** Every section has been run and
   verified individually — the autoencoder and MLP, the DGA CNN and LSTM, the malware CNN
   under both protocols, the phishing model and its diagnostics, and a reference solution
   to the final lab. A single whole-notebook `nbconvert --execute` has not completed end to
   end, purely because the DGA LSTM on ~540k domains is slow on CPU. Worth one clean run in
   Colab on a T4 to confirm cell-to-cell state flows correctly, then save the outputs.
2. **Modules 1–4 polish.** See the summary below.
3. **Modules 6 and 7.** Not started. Design decisions are recorded below.

No estimated numbers remain anywhere in Module 5's prose. Every figure is measured.

## Known gaps in Modules 1–4

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

**Module 1.** Students set up a Kaggle account and API token, then later modules use raw
GitHub URLs instead. Pick one. Also, the `df.columns` output in step 3 already shows `Index`,
which the step 4 rename is supposed to produce — stale outputs from a re-run.

**All of 1–4.** No random seeds, so student output drifts from the numbers in the prose.
The Module 5 setup cell can be copied in as-is.

**All of 1–4.** Module 5 now teaches students to check for duplicates, leakage, imbalance,
and construct validity. Modules 3 and 4 use SMOTE, splits, and the credit card dataset
without those checks. Re-read them as a student who has already learned to audit — anywhere
they could ask "wait, did you check that?" needs either the check or an explanation.

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

- `tensorflow-cpu` from PyPI trains this module's models in minutes on a couple of CPUs.
  **Run every model before shipping it** — both architecture bugs found so far (the unbuilt
  `summary()` and the BatchNorm collapse) were invisible to static review.
- Keras `validation_split` takes the **last n% without shuffling**. On family-ordered data
  like Malimg's native row order, that hands the model a validation set of classes it never
  trained on, and you see ~1% val accuracy that looks like catastrophic overfitting. Shuffle first.
- **Colab MCP bridge — working as of 2026-08-21.** It failed earlier (timed out at 60s,
  twice) because it was configured as `uvx git+https://github.com/googlecolab/colab-mcp`,
  which re-resolves the git ref and rebuilds ~60 packages on every launch and never
  finishes inside the MCP startup window. Fixed by installing it once and pointing the
  config at the resulting binary:

  ```bash
  uv tool install --python 3.13 git+https://github.com/googlecolab/colab-mcp
  claude mcp add --scope local colab-mcp -- ~/.local/bin/colab-mcp   # ~/.claude.json, not committed
  ```

  Update with `uv tool upgrade colab-mcp`. Claude Desktop reads a separate file,
  `~/Library/Application Support/Claude/claude_desktop_config.json`, and points at the
  same binary; Claude Code never reads that file. Restart the client after config changes —
  MCP servers load at startup.

  It is a browser bridge, not an API client. The server opens a localhost WebSocket on an
  ephemeral port with a random token, accepts only `Origin: colab.research.google.com`
  (or `colab.google.com`), one client at a time. Calling its connect tool opens a Colab tab
  carrying `#mcpProxyToken=...&mcpProxyPort=...`; that page dials back and Colab's own
  notebook tools are then proxied in. So a signed-in browser session must be open. Note
  the connect tool hardcodes a blank scratch notebook (`/notebooks/empty.ipynb`) — whether
  the proxied tools can then open `Module5_Student.ipynb` from Drive is not yet tested.
- When editing notebooks programmatically, each element of a cell's `source` list must end
  with `\n` except the last. Splitting on `'\n'` without re-adding them silently concatenates
  every line into one, and the notebook still parses as valid JSON.
