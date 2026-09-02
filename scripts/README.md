# Evidence Validation and Result Generation Scripts

## Overview

Per Decision D-023 (Machine-Verified Formal Result Gate), these scripts eliminate AI transcription errors in Formal Results by auto-extracting factual fields from Evidence and machine-computing normalization/achievement values.

## Scripts

### 1. `validate_evidence.py` - Evidence Validation and Extraction

**Purpose**: Validates Evidence bundle integrity and extracts machine-readable facts.

**Usage**:
```bash
python scripts/validate_evidence.py <evidence_directory> [cell1 cell2 ...]
```

**Example**:
```bash
python scripts/validate_evidence.py ./evidence-temp/run-20260902-140958 1K 4K 16K 64K > validated-evidence.json
```

**Output**: JSON with auto-extracted:
- Runtime identity (container, image, vLLM version)
- DISPATCH_CONTROL_SHA and Task ID
- Run2/Run3/Run4 throughput values
- Completed/failed counts
- Machine-computed Mean(Run2, Run3, Run4)

---

### 2. `generate_result.py` - Formal Result Generator

**Purpose**: Generates Formal Result markdown from validated Evidence with all factual fields auto-generated.

**Usage**:
```bash
python scripts/generate_result.py <validated_evidence.json> <cell_name> <h100_reference>
```

**Example**:
```bash
python scripts/generate_result.py validated-evidence.json 1K 2688.71 > RESULT-GLM52-W8A8-1K-BASELINE.md
```

**Auto-Generated Fields**:
- Runtime identity
- DISPATCH_CONTROL_SHA
- Run2/Run3/Run4 raw values
- Mean throughput
- Hardware normalization basis (from `hardware-normalization-config.yaml`)
- Achievement percentage

**AI Authoring Limited To**: Analysis, Formal Review rationale, Next Steps

---

### 3. `validate_result.py` - Pre-Commit Result Validator

**Purpose**: Validates Formal Results before commit to block transcription errors.

**Usage**:
```bash
python scripts/validate_result.py <result_file.md>
```

**Example**:
```bash
python scripts/validate_result.py docs/vllm-ascend-performance/models/glm-5.2-w8a8/results/RESULT-GLM52-W8A8-1K-BASELINE.md
```

**Validates**:
- Evidence runtime == Result runtime
- Raw Run2/Run3/Run4 values == Result values
- Recomputed mean == Result mean
- Normalization basis == `hardware-normalization-config.yaml`
- Recomputed achievement == Result achievement
- DISPATCH_CONTROL_SHA == Evidence provenance

**Exit Codes**:
- 0: Validation PASS
- 1: Validation FAIL (`FORMAL_RESULT_VALIDATION_FAILED`)

**On Failure**: Blocks commit. Investigate and correct errors.

---

## Normalization Configuration

**File**: `docs/vllm-ascend-performance/hardware-normalization-config.yaml`

**Purpose**: Authoritative machine-readable hardware compute basis per Decision D-024 (supersedes the A3 compute-basis portion of D-020).

**Contents**:
- A3/910C: 8 cards × 752 TFLOPS FP16 = 6016 TFLOPS
- H100: 16 cards × 989 TFLOPS FP8 = 15824 TFLOPS
- Target achievement: 80%

**Usage**: All Result generators and validators MUST load values from this file. Manual transcription is prohibited.

---

## Workflow

### PerfControl Formal Result Creation Workflow

1. **Download Evidence**:
   ```bash
   gh release download evidence-test-glm52-run-20260902-140958 --pattern "GLM52-W8A8-BASELINE-EVIDENCE-*.tar.gz"
   ```

2. **Verify SHA256**:
   ```bash
   sha256sum GLM52-W8A8-BASELINE-EVIDENCE-*.tar.gz
   # Compare with Runner-provided expected SHA256
   ```

3. **Extract Evidence**:
   ```bash
   tar -xzf GLM52-W8A8-BASELINE-EVIDENCE-*.tar.gz
   ```

4. **Validate Evidence**:
   ```bash
   python scripts/validate_evidence.py ./run-20260902-140958 1K 4K 16K 64K > validated-evidence.json
   ```

5. **Generate Results** (one per cell):
   ```bash
   python scripts/generate_result.py validated-evidence.json 1K 2688.71 > RESULT-GLM52-W8A8-1K-BASELINE.md
   python scripts/generate_result.py validated-evidence.json 4K 4063.45 > RESULT-GLM52-W8A8-4K-BASELINE.md
   python scripts/generate_result.py validated-evidence.json 16K 4379.60 > RESULT-GLM52-W8A8-16K-BASELINE.md
   python scripts/generate_result.py validated-evidence.json 64K 5054.66 > RESULT-GLM52-W8A8-64K-BASELINE.md
   ```

6. **AI Review**: Edit generated Results to add analysis, Formal Review rationale, Next Steps. **Do not modify factual fields**.

7. **Validate Results**:
   ```bash
   python scripts/validate_result.py RESULT-GLM52-W8A8-1K-BASELINE.md
   python scripts/validate_result.py RESULT-GLM52-W8A8-4K-BASELINE.md
   python scripts/validate_result.py RESULT-GLM52-W8A8-16K-BASELINE.md
   python scripts/validate_result.py RESULT-GLM52-W8A8-64K-BASELINE.md
   ```

8. **If Validation PASS**: Commit and push.

9. **If Validation FAIL**: `FORMAL_RESULT_VALIDATION_FAILED`. Investigate error. Do NOT commit until corrected.

---

## Prohibited Actions

Per Decision D-023, AI agents are **prohibited** from manually filling these factual fields:
- Runtime/image identity
- DISPATCH_CONTROL_SHA
- Run2/Run3/Run4 raw values
- Completed/failed counts
- Mean(Run2, Run3, Run4)
- Evidence archive SHA256
- Hardware normalization basis
- Normalized throughput calculations
- Achievement percentage

**All factual fields MUST be auto-generated by scripts.**

---

## Benefits

1. **Eliminates AI transcription errors**: Runtime identity, calculation rounding, normalization basis errors are prevented.
2. **Full precision calculations**: Mean and achievement computed with full precision, not from two-decimal display values.
3. **Authoritative normalization source**: Single source of truth (`hardware-normalization-config.yaml`).
4. **Pre-commit gate**: Validation failures block commits before errors enter the repository.
5. **Reusable for all models**: GLM, DeepSeek, MiniMax, and future models use the same validated workflow.

---

## Decision Reference

- **D-020**: Hardware compute basis and normalization policy (historical; A3 compute-basis portion superseded by D-024)
- **D-023**: Machine-Verified Formal Result Gate (this workflow)
- **D-024**: GLM-5.2-W8A8 A3/910C hardware compute basis correction (active basis 752 × 8 = 6016)
