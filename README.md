# AI for Cybersecurity — Introductory Certification

An introductory certification course on applying machine learning and AI to cybersecurity,
taught as a series of Jupyter notebooks you run on your issued lab VM. Asynchronous: you read,
run, and modify the code yourself, and every module ends with written analysis you submit for
grading.

**Author:** Abe Weigant

## How the course works

Each module is one notebook. Open it in **VS Code** on your lab VM, run cells top to bottom,
and complete the coding tasks (`# YOUR CODE HERE`) and written questions (`[insert response]`)
as you meet them. Every dataset downloads automatically from this repository — no accounts and
no manual uploads. Checkpoint cells are placed after error-prone steps; if one passes, your
pipeline state matches the reference and you can continue with confidence.

### One-time setup

From a terminal in this folder on your VM:

```bash
./setup.sh
```

That creates a `.venv`, installs everything the course needs, registers a Jupyter kernel called
**Python (AI-Cyber)**, and checks that the datasets are reachable. Then in VS Code: open this
folder, open `Module1_Student.ipynb`, and pick that kernel from the selector in the top right.

Re-running `setup.sh` is safe.

One habit the course will insist on from day one: **a good-looking number is a claim, not a
result.** Every module contains at least one number that is not what it appears to be, and
learning to find out why is the skill being certified.

## The modules

| # | Module | Focus | Est. time |
|---|---|---|---|
| 1 | Course Introduction & The Role of AI in Cybersecurity | AI/ML/DL foundations; your first dataset audit — finding missing values that are not marked missing | 3–4 h |
| 2 | Threat Landscape, Data Sources, Preprocessing, First ML Model | Kill Chain & MITRE ATT&CK; cleaning a broken log; your first classifier, and why its perfect score is a symptom | 4–5 h |
| 3 | Supervised Machine Learning | EDA and correlation as interrogation; the accuracy trap; measuring (not assuming) the standard fixes for class imbalance; model comparison and fold-safe tuning | 5–6 h |
| 4 | Unsupervised Learning: Anomaly Detection & Threat Hunting | Scaling, PCA, K-Means, DBSCAN, hierarchical clustering, Isolation Forests; evaluating without ground truth | 4–5 h |
| 5 | Deep Learning Models for Cybersecurity | Autoencoders, MLPs, 1D/2D CNNs, LSTMs, embeddings — and auditing your own evaluation at every step | 6–8 h |
| 6 | Large Language Models & Explainable AI | Calling an LLM over an API; phishing triage against the model you built in Module 5; prompt injection; SHAP derived from first principles; capstone: LLM-assisted forensic log triage | 5–6 h |
| 7 | Adversarial Attacks & the Secure AI/ML Lifecycle | Attacking the DGA and backdoor detectors **you** built in Module 5 — evasion, poisoning, membership inference, model extraction — then defending them and threat-modelling the lifecycle with MITRE ATLAS | 5–6 h |

Time estimates include the written questions. A few cells are long-running by design and say so
where they appear — the Module 3 grid search and Module 5's networks each take several minutes.
**Your VM has no GPU and does not need one**: every model in the course is sized to train on
CPU. Long cells print progress while they work, so if output is still appearing, nothing is
wrong. Module 6 is paced by the shared model server rather than by your VM.

**Module 6 is the one module you cannot complete offline.** It needs a live language-model
model server on the range. `setup.sh` writes a `.env` file in this folder holding its address;
confirm `LLM_BASE_URL` matches what your instructor gives you and restart the notebook kernel.
The server needs no password from you — Section 1 explains why, and what you would write in a
report if you found a service like it on a real engagement.

Modules 6 and 7 preview two sister courses — one on LLMs in depth, one on securing AI
systems in depth — while standing on their own.

**Keep your Module 5 final-lab artifacts** (`backdoor_detector.keras` and its threshold
JSON). Module 7 attacks the same model and architecture; it rebuilds them from the public data
so it stands alone, and your saved copy is the optional path.

## Prerequisites

- Comfortable reading and writing basic Python.
- Introductory security concepts help but are reviewed where needed.
- No prior machine learning experience is assumed.
- Your issued lab VM, with VS Code and its Python + Jupyter extensions.
- Module 6 additionally needs the range's model server reachable from your VM.

## Datasets

All hosted in this repository and loaded by URL from each notebook's setup cell:

| file | contents | used in |
|---|---|---|
| `phishing_dataset1.parquet` | 88,647 URLs × 111 lexical/host features | Modules 1, 2, 3 |
| `Log_Data.csv` | 30-row toy firewall log (deliberately broken) | Module 2 |
| `creditcard.csv.zip` | 284,807 card transactions, 492 fraudulent | Modules 3, 4, 5 |
| `dga_websites.csv` / `legit_websites.csv` | ~675k generated vs. legitimate domains | Module 5 |
| `malimg_64.npz` | 9,339 malware binaries rendered as 64×64 grayscale images | Module 5 |
| `CEAS_08.parquet` | 39,154 labelled emails with full body text | Module 5 |
| `Backdoor_Malware.pcap.parquet` / `Recon-PortScan.pcap.parquet` | IoT network flow records | Module 5 final lab, Module 7 |
| `forensic_log.csv` / `forensic_log_truth.csv` | One week of server logs (774 lines) with a multi-stage intrusion planted inside, and its ground truth | Module 6 capstone |

## Completion

Each module is assessed on its coding tasks and written responses. The written questions
carry the weight: they ask you to predict before you run, argue from the numbers your own
notebook produced, and defend trade-offs — not to restate definitions. Grading rubrics are
maintained by the instructor.
