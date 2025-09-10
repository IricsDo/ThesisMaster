# `start.py` — Argument Guide

This document explains how to use the CLI arguments supported by `start.py`, how the two execution modes work, and which arguments conflict with or disable each other.

---

## 1) Execution Modes

`start.py` supports **two independent modes**. Validation rules are applied based on the chosen mode:

1. **Training mode** (default): runs the full Phase 1 pipeline with up to 4 steps  
   `step1 → step2 → step3 → step4`  
   - You can also enable **make-data only** to run just step1.

2. **Predict-only mode** (`--predict_only`): prepares prediction data (unless skipped) and runs `predict(...)` using an already-trained model. No training or validation occurs.

> When `--predict_only` is on, any training-specific arguments are **ignored** unless explicitly stated otherwise.

---

## 2) Argument Reference

### Summary table

| Argument | Aliases | Type | Required (Training) | Required (Make-Data Only) | Required (Predict-Only) | Default | Notes |
|---|---|---:|:---:|:---:|:---:|---:|---|
| `--predict_only` | `-pred_only` | flag | No | No | – | `False` | Enable predict-only mode. Disables training validations. |
| `--model_path` | `-mp` | str | No | No | **Yes** | `""` | Path to a **model file** (`.pth`/`.pb`) **or a directory** containing the model. |
| `--predict_folder` | `-p` | str | No | No | **Yes** | `""` | Folder containing input data to predict. Tool writes to `<predict_folder>/result`. |
| `--skip_prepare_predict_data` | — | flag | No | No | No | `False` | Skip building `<predict_folder>/result`; it must already exist. |
| `--tensorflow` | `-tf` | flag | Optional | Optional | Optional | `False` | Force TensorFlow backend. Mutually exclusive with `--pytorch`. |
| `--pytorch` | `-pt` | flag | Optional | Optional | Optional | `False` | Force PyTorch backend. Mutually exclusive with `--tensorflow`. |
| `--input_folder` | `-i` | str | **Yes** | **Yes** | No | — | Training input directory for step1. |
| `--output_folder` | `-o` | str | **Yes** | **Yes** | No | — | Output directory for training artifacts and model. |
| `--training_json` | `-trainj` | str | **Yes** | *See note* | No | — | Training configuration (`.json`) used by step2. |
| `--epochs` | `-e` | int | No | No | No | `10000` | Number of training steps/epochs. |
| `--only_make_data` | `-omd` | flag | Optional | — | No | `False` | Runs only **step1** (data preparation), skipping steps 2–4. |
| `--load_phase1_status` | `-lps1` | flag | Optional | Optional | No | `False` | Reuse previously created data if compatible. |
| `--num_of_hidro` | `-noh` | list[str] | **Yes** | **Yes** | No | `[]` | List of atomic systems; e.g. `-noh 4 10 19 28 52 55 58 100 112`. |
| `--min_len_data` | `-mld` | int | Optional | Optional | No | `0` | Minimum sequence length filter for step1. |
| `--verbose` | `-v` | flag | Optional | Optional | Optional | `False` | Verbose logging. |

**Important about `--training_json` when `--only_make_data` is used**:  
- The canonical pipeline does **not** need `--training_json` to execute **only step1**.  
- Depending on your local `start.py` validations, you may still be required to pass a placeholder JSON path when running with `--only_make_data`. If you prefer not to require it, adjust the validations accordingly.

**About `--num_of_hidro`**:  
- It is **required** for **full training** and for **make-data only** (step1).  
- It is **not required** for **predict-only**.

---

## 3) Backend Detection & Conflicts

### Auto-detection
When `--tensorflow` and `--pytorch` are **both omitted** in predict-only mode, the backend is auto-detected from `--model_path`:
- If `--model_path` is a **file**:  
  - `.pth` ⇒ **PyTorch**  
  - `.pb` ⇒ **TensorFlow**
- If `--model_path` is a **directory**:  
  - Prefer canonical file names `graph.pth` / `graph.pb`.  
  - Otherwise, scan the directory (shallow) for `*.pth` / `*.pb`.  
  - If multiple candidates of the **same kind** are found, choose the **most recent** by modified time.  
  - If **both kinds** are found, the run fails with an **explicit error** (you must specify `-pt` or `-tf`).

### Mutual exclusions & precedence
- **`--tensorflow`** and **`--pytorch`** are **mutually exclusive**. If both are set, the run fails.
- If a backend flag is set but the actual model type conflicts (e.g., `.pb` with `--pytorch`), the run fails with a clear error.
- When both flags are omitted, auto-detection decides the backend (predict-only).

---

## 4) Mode Rules (Enable/Disable)

- `--predict_only`:
  - **Enables**: `--model_path`, `--predict_folder`, backend flags or auto-detect, `--skip_prepare_predict_data`, `--verbose`.
  - **Disables/Ignored**: `--input_folder`, `--output_folder`, `--training_json`, `--epochs`, `--only_make_data`, `--load_phase1_status`, `--num_of_hidro`, `--min_len_data`.
- Training mode (no `--predict_only`):
  - **Requires**: `--input_folder`, `--output_folder`, `--training_json`.
  - **`--only_make_data`** runs only **step1** (data creation), skipping steps 2–4.
  - **`--num_of_hidro`** is needed for full 4-step training and for make-data only.

---

## 5) Output Paths & What Gets Written

- **Predict-only**:
  - Input: `--predict_folder` (raw), prepared to `--predict_folder/result` (unless skipped).
  - Output: predictions are written under `--predict_folder/result`.
- **Training**:
  - Input: `--input_folder`, split/organized during step1 into `--output_folder`.
  - Output: models and logs under `--output_folder` (e.g., `graph.pth` / `graph.pb`, plots, logs, etc.).

---

## 6) Example Commands

### 6.1 Full training (4 steps)
```bash
python start.py   -i /data/train_input   -o /data/train_out   -trainj /configs/train_config.json   -noh 4 10 19 28 52 55 58 100 112   -pt   -lps1   -v
```

### 6.2 Make-data only (run step1, skip steps 2–4)
```bash
python start.py   -i /data/train_input   -o /data/train_out   -noh 4 10 19 28 52 55 58 100 112   -omd   -v
```
> If your local validation still enforces `--training_json`, provide a placeholder: `-trainj /configs/dummy.json`.

### 6.3 Predict-only (model **file**, backend auto-detected)
```bash
# PyTorch (.pth)
python start.py   -pred_only   -mp /models/best/graph.pth   -p /data/predict_in   -v

# TensorFlow (.pb)
python start.py   -pred_only   -mp /models/tf/graph.pb   -p /data/predict_in
```

### 6.4 Predict-only (model **directory**, canonical or newest)
```bash
python start.py   -pred_only   -mp /models/best_dir   -p /data/predict_in
```

### 6.5 Predict-only (directory contains both `.pb` and `.pth` → **must** pick one)
```bash
python start.py   -pred_only   -mp /models/mixed   -p /data/predict_in   -pt        # or -tf
```

### 6.6 Predict-only (skip preparing `<predict_folder>/result`)
```bash
python start.py   -pred_only   -mp /models/best/graph.pth   -p /data/predict_in   --skip_prepare_predict_data
```

---

## 7) Common Errors & Quick Fixes

- **Both backends set**:  
  `Please choose either --pytorch or --tensorflow, not both.`  
  → Remove one of `-pt` or `-tf`.

- **Model type conflicts with forced backend**:  
  e.g., `.pb` model with `-pt`.  
  → Use the matching flag or omit both flags to auto-detect.

- **Both `.pb` and `.pth` found in model directory** (predict-only):  
  → Specify either `-pt` or `-tf` to resolve ambiguity.

- **`--skip_prepare_predict_data` used but `<predict_folder>/result` missing**:  
  → Remove the flag or pre-create that folder.

- **Make-data only & `--training_json` validation**:  
  If your local `start.py` still validates `--training_json` even with `-omd`, pass a dummy json or relax that validation in code.

---

## 8) Quick Checklist

- Training full steps: `-i`, `-o`, `-trainj`, `-noh ...`, optionally `-pt`/`-tf`.
- Make-data only: `-i`, `-o`, `-noh ...`, `-omd` (and optionally `-v`).  
  If needed by your local validation, add `-trainj /configs/dummy.json`.
- Predict-only: `-pred_only`, `-mp`, `-p`, optional `-pt`/`-tf` (else auto-detect), optional `--skip_prepare_predict_data`.
