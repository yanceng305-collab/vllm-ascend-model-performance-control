# Git Hooks Setup for Machine-Verified Formal Result Gate

## Overview

Per Decision D-023, pre-commit hooks validate Formal Results before commit to prevent transcription errors.

## One-Time Setup

Run this command once to enable the pre-commit hook:

```bash
git config core.hooksPath .githooks
```

This configures Git to use hooks from `.githooks/` directory instead of the default `.git/hooks/`.

## What the Hook Does

When you `git commit`, the pre-commit hook automatically:

1. Detects if any `RESULT-*.md` files are being committed
2. Checks that `validated-evidence.json` exists in repo root
3. Runs `validate_result.py` on each Result file
4. Compares Result against validated Evidence and configs
5. **BLOCKS commit** if validation fails with `FORMAL_RESULT_VALIDATION_FAILED`

## Validation Checks

The hook verifies:
- ✓ Evidence runtime == Result runtime
- ✓ Raw Run2/3/4 values == Result values  
- ✓ Recomputed mean == Result mean
- ✓ Normalization basis == hardware-normalization-config.yaml
- ✓ Recomputed achievement == Result achievement
- ✓ DISPATCH_CONTROL_SHA == Evidence
- ✓ H100 reference == model-workload-references.yaml
- ✓ All required fields present

## Workflow

### Before Committing Results

1. **Validate Evidence first**:
   ```bash
   python scripts/validate_evidence.py ./evidence-temp/run-XXXXXX 1K 4K 16K 64K > validated-evidence.json
   ```

2. **Generate Results** (using validated Evidence):
   ```bash
   python scripts/generate_result.py validated-evidence.json GLM-5.2-W8A8 1K <sha256> "<location>" > RESULT-1K.md
   # Repeat for 4K, 16K, 64K
   ```

3. **Review and edit** (AI adds analysis, Formal Review rationale, Next Steps only)

4. **Commit** (hook validates automatically):
   ```bash
   git add RESULT-*.md validated-evidence.json
   git commit -m "Add machine-verified Results"
   ```

5. **If validation fails**: Fix errors, re-generate if needed, try commit again

6. **If validation passes**: Commit succeeds, proceed with push

## Platform Notes

- **Linux/macOS**: Uses `.githooks/pre-commit` (bash script)
- **Windows**: Uses `.githooks/pre-commit.bat` (batch script)

Git automatically selects the correct hook based on platform.

## Bypassing Hook (NOT RECOMMENDED)

To bypass validation (emergency only, violates D-023):
```bash
git commit --no-verify
```

**WARNING**: This defeats the Machine-Verified Gate and may allow transcription errors into the repository. Only use in exceptional circumstances with explicit approval.

## Troubleshooting

### Hook not running

Check hook path configuration:
```bash
git config core.hooksPath
```

Should output: `.githooks`

If not set, run setup command again:
```bash
git config core.hooksPath .githooks
```

### Validation errors

Common issues:
1. `validated-evidence.json not found` → Run `validate_evidence.py` first
2. `Runtime version mismatch` → Evidence and Result have different runtime identity
3. `Mean calculation error` → Result mean doesn't match recomputed value from Evidence
4. `Achievement calculation error` → Achievement % doesn't match recomputed value

Fix: Re-generate Results using `generate_result.py` (which auto-generates factual fields correctly).

### Permission denied (Linux/macOS)

Make hook executable:
```bash
chmod +x .githooks/pre-commit
```

## Testing the Hook

Create a test commit with a Result file to verify hook runs:

```bash
# Stage a Result file
git add docs/vllm-ascend-performance/models/glm-5.2-w8a8/results/RESULT-*.md

# Attempt commit (hook should validate)
git commit -m "Test hook"

# You should see validation output
```

If no validation output appears, check hook setup.

---

**Decision Reference**: D-023 Machine-Verified Formal Result Gate
