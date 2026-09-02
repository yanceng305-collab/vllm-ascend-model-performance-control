#!/usr/bin/env python3
"""
Pre-Commit Formal Result Validator

Validates Formal Results before commit to prevent transcription errors.
Per Decision D-023: Machine-Verified Formal Result Gate

TRUE END-TO-END FAIL-CLOSED:
- Validates Result against validated Evidence and configs directly
- All required fields must be present and match
- No model fallback or guessing allowed
- Exits with code 1 if any validation fails (blocks commit)
"""

import re
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, Optional, Tuple, List


def load_yaml_config(config_path: Path) -> Dict:
    """Load YAML configuration using yaml.safe_load()"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def validate_normalization_config(config: Dict) -> Tuple[bool, str]:
    """Validate normalization config consistency"""
    try:
        a3 = config['a3']
        h100 = config['h100']
        
        # Verify A3 consistency
        a3_computed = a3['cards'] * a3['tflops_per_card_fp16']
        if a3_computed != a3['total_tflops']:
            return False, f"A3 config inconsistent: {a3['cards']} × {a3['tflops_per_card_fp16']} = {a3_computed}, but total_tflops={a3['total_tflops']}"
        
        # Verify H100 consistency
        h100_computed = h100['cards'] * h100['tflops_per_card_fp8']
        if h100_computed != h100['total_tflops']:
            return False, f"H100 config inconsistent: {h100['cards']} × {h100['tflops_per_card_fp8']} = {h100_computed}, but total_tflops={h100['total_tflops']}"
        
        return True, "Config validation PASS"
    except Exception as e:
        return False, f"Config validation error: {e}"


def extract_result_field(content: str, pattern: str) -> Optional[str]:
    """Extract a field from Result markdown using regex"""
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else None


def extract_float(content: str, pattern: str) -> Optional[float]:
    """Extract a float value from Result markdown"""
    value_str = extract_result_field(content, pattern)
    if value_str:
        value_str = re.sub(r'[^\d.]', '', value_str)
        try:
            return float(value_str)
        except ValueError:
            pass
    return None


def extract_int(content: str, pattern: str) -> Optional[int]:
    """Extract an integer value from Result markdown"""
    value_str = extract_result_field(content, pattern)
    if value_str:
        value_str = re.sub(r'[^\d]', '', value_str)
        try:
            return int(value_str)
        except ValueError:
            pass
    return None


def validate_result(result_path: Path, validated_evidence: Dict,
                   normalization_config: Dict, model_config: Dict, model_name: str) -> Tuple[bool, List[str]]:
    """
    Validate a Formal Result document against validated Evidence and configs.
    TRUE END-TO-END FAIL-CLOSED: Any discrepancy causes validation failure.
    
    Returns: (is_valid, list_of_errors)
    """
    
    if not result_path.exists():
        return False, [f"Result file not found: {result_path}"]
    
    content = result_path.read_text(encoding='utf-8')
    errors = []
    
    # Extract Evidence data
    evidence_runtime = validated_evidence['runtime_identity']
    evidence_provenance = validated_evidence['provenance']
    
    # Determine cell from Result
    cell_name = None
    for cell in validated_evidence['cells'].keys():
        if cell in result_path.name or f'{cell} Baseline' in content:
            cell_name = cell
            break
    
    if not cell_name:
        return False, ["Could not determine cell name from Result"]
    
    if cell_name not in validated_evidence['cells']:
        return False, [f"Cell {cell_name} not found in validated Evidence"]
    
    evidence_cell = validated_evidence['cells'][cell_name]
    
    # === REQUIRED FIELDS EXTRACTION ===
    
    # Runtime identity
    result_vllm = extract_result_field(content, r'\*\*vLLM Version\*\*:\s*`([^`]+)`')
    result_image = extract_result_field(content, r'\*\*Image\*\*:\s*`([^`]+)`')
    result_image_sha = extract_result_field(content, r'\*\*Image SHA256\*\*:\s*`([^`]+)`')
    result_container = extract_result_field(content, r'\*\*Container\*\*:\s*`([^`]+)`')
    
    # Provenance
    result_task_id = extract_result_field(content, r'\*\*Task\*\*:\s*([^\n]+)')
    result_dispatch_sha = extract_result_field(content, r'\*\*DISPATCH_CONTROL_SHA\*\*:\s*`?([a-f0-9]{40})`?')
    result_archive_sha = extract_result_field(content, r'\*\*Archive SHA256\*\*:\s*`([^`]+)`')
    
    # Run values
    result_run2 = extract_float(content, r'\*\*Run 2\*\*:\s*([\d.]+)\s*tok/s')
    result_run3 = extract_float(content, r'\*\*Run 3\*\*:\s*([\d.]+)\s*tok/s')
    result_run4 = extract_float(content, r'\*\*Run 4\*\*:\s*([\d.]+)\s*tok/s')
    
    # Completed/failed counts
    result_run2_completed = extract_int(content, r'Run 2\*\*:.*?completed:\s*(\d+)')
    result_run2_failed = extract_int(content, r'Run 2\*\*:.*?failed:\s*(\d+)')
    result_run3_completed = extract_int(content, r'Run 3\*\*:.*?completed:\s*(\d+)')
    result_run3_failed = extract_int(content, r'Run 3\*\*:.*?failed:\s*(\d+)')
    result_run4_completed = extract_int(content, r'Run 4\*\*:.*?completed:\s*(\d+)')
    result_run4_failed = extract_int(content, r'Run 4\*\*:.*?failed:\s*(\d+)')
    
    # Mean
    result_mean = extract_float(content, r'\*\*Mean \(Run2, Run3, Run4\)\*\*:\s*\*\*([\d.]+)\s*tok/s\*\*')
    
    # Hardware basis
    result_a3_cards = extract_int(content, r'A3/910C.*?(\d+)\s*cards')
    result_a3_per_card = extract_int(content, r'A3/910C.*?cards\s*×\s*(\d+)\s*TFLOPS')
    result_a3_total = extract_int(content, r'A3/910C System:\s*([\d,]+)\s*TFLOPS')
    result_h100_cards = extract_int(content, r'H100.*?(\d+)\s*cards')
    result_h100_per_card = extract_int(content, r'H100.*?cards\s*×\s*(\d+)\s*TFLOPS')
    result_h100_total = extract_int(content, r'H100 System:\s*([\d,]+)\s*TFLOPS')
    
    # H100 reference
    result_h100_ref = extract_float(content, r'\*\*H100 Reference\*\*.*?:\s*([\d.]+)\s*tok/s')
    
    # Achievement
    result_achievement = extract_float(content, r'Achievement.*?=\s*([\d.]+)%')
    
    # === CHECK REQUIRED FIELDS PRESENCE ===
    
    required_fields = {
        'vllm_version': result_vllm,
        'image': result_image,
        'image_sha256': result_image_sha,
        'container': result_container,
        'task_id': result_task_id,
        'dispatch_control_sha': result_dispatch_sha,
        'archive_sha256': result_archive_sha,
        'run2_throughput': result_run2,
        'run3_throughput': result_run3,
        'run4_throughput': result_run4,
        'run2_completed': result_run2_completed,
        'run2_failed': result_run2_failed,
        'run3_completed': result_run3_completed,
        'run3_failed': result_run3_failed,
        'run4_completed': result_run4_completed,
        'run4_failed': result_run4_failed,
        'mean': result_mean,
        'a3_cards': result_a3_cards,
        'a3_per_card': result_a3_per_card,
        'a3_total': result_a3_total,
        'h100_cards': result_h100_cards,
        'h100_per_card': result_h100_per_card,
        'h100_total': result_h100_total,
        'h100_reference': result_h100_ref,
        'achievement': result_achievement,
    }
    
    missing_fields = [field for field, value in required_fields.items() if value is None]
    if missing_fields:
        errors.append(f"Missing required fields: {', '.join(missing_fields)}")
        return False, errors  # Fail immediately on missing fields
    
    # === VALIDATE AGAINST EVIDENCE ===
    
    # 1. Runtime identity
    if result_vllm != evidence_runtime['vllm_version']:
        errors.append(f"vLLM version mismatch: Evidence={evidence_runtime['vllm_version']}, Result={result_vllm}")
    if result_image != evidence_runtime['image']:
        errors.append(f"Image mismatch: Evidence={evidence_runtime['image']}, Result={result_image}")
    if result_image_sha != evidence_runtime['image_sha256']:
        errors.append(f"Image SHA256 mismatch: Evidence={evidence_runtime['image_sha256']}, Result={result_image_sha}")
    if result_container != evidence_runtime['container_name']:
        errors.append(f"Container mismatch: Evidence={evidence_runtime['container_name']}, Result={result_container}")
    
    # 2. Provenance
    if result_task_id != evidence_provenance['task_id']:
        errors.append(f"Task ID mismatch: Evidence={evidence_provenance['task_id']}, Result={result_task_id}")
    if result_dispatch_sha != evidence_provenance['dispatch_control_sha']:
        errors.append(f"DISPATCH_CONTROL_SHA mismatch: Evidence={evidence_provenance['dispatch_control_sha']}, Result={result_dispatch_sha}")
    
    # Archive SHA256
    if validated_evidence.get('archive_sha256') and validated_evidence['archive_sha256'] != "UNKNOWN":
        if result_archive_sha != validated_evidence['archive_sha256']:
            errors.append(f"Archive SHA256 mismatch: Evidence={validated_evidence['archive_sha256']}, Result={result_archive_sha}")
    
    # 3. Run values
    evidence_run2 = evidence_cell['runs']['run2']['throughput']
    evidence_run3 = evidence_cell['runs']['run3']['throughput']
    evidence_run4 = evidence_cell['runs']['run4']['throughput']
    
    if abs(result_run2 - evidence_run2) > 0.01:
        errors.append(f"Run2 throughput mismatch: Evidence={evidence_run2}, Result={result_run2}")
    if abs(result_run3 - evidence_run3) > 0.01:
        errors.append(f"Run3 throughput mismatch: Evidence={evidence_run3}, Result={result_run3}")
    if abs(result_run4 - evidence_run4) > 0.01:
        errors.append(f"Run4 throughput mismatch: Evidence={evidence_run4}, Result={result_run4}")
    
    # 4. Completed/failed counts
    if result_run2_completed != evidence_cell['runs']['run2']['completed']:
        errors.append(f"Run2 completed mismatch: Evidence={evidence_cell['runs']['run2']['completed']}, Result={result_run2_completed}")
    if result_run2_failed != evidence_cell['runs']['run2']['failed']:
        errors.append(f"Run2 failed mismatch: Evidence={evidence_cell['runs']['run2']['failed']}, Result={result_run2_failed}")
    if result_run3_completed != evidence_cell['runs']['run3']['completed']:
        errors.append(f"Run3 completed mismatch: Evidence={evidence_cell['runs']['run3']['completed']}, Result={result_run3_completed}")
    if result_run3_failed != evidence_cell['runs']['run3']['failed']:
        errors.append(f"Run3 failed mismatch: Evidence={evidence_cell['runs']['run3']['failed']}, Result={result_run3_failed}")
    if result_run4_completed != evidence_cell['runs']['run4']['completed']:
        errors.append(f"Run4 completed mismatch: Evidence={evidence_cell['runs']['run4']['completed']}, Result={result_run4_completed}")
    if result_run4_failed != evidence_cell['runs']['run4']['failed']:
        errors.append(f"Run4 failed mismatch: Evidence={evidence_cell['runs']['run4']['failed']}, Result={result_run4_failed}")
    
    # 5. Mean calculation
    recomputed_mean = (evidence_run2 + evidence_run3 + evidence_run4) / 3
    if abs(result_mean - recomputed_mean) > 0.01:
        errors.append(f"Mean calculation error: Recomputed={recomputed_mean:.2f}, Result={result_mean:.2f}")
    
    # === VALIDATE AGAINST CONFIGS ===
    
    # 6. Hardware normalization basis
    if result_a3_cards != normalization_config['a3']['cards']:
        errors.append(f"A3 cards mismatch: Config={normalization_config['a3']['cards']}, Result={result_a3_cards}")
    if result_a3_per_card != normalization_config['a3']['tflops_per_card_fp16']:
        errors.append(f"A3 TFLOPS/card mismatch: Config={normalization_config['a3']['tflops_per_card_fp16']}, Result={result_a3_per_card}")
    if result_a3_total != normalization_config['a3']['total_tflops']:
        errors.append(f"A3 total TFLOPS mismatch: Config={normalization_config['a3']['total_tflops']}, Result={result_a3_total}")
    if result_h100_cards != normalization_config['h100']['cards']:
        errors.append(f"H100 cards mismatch: Config={normalization_config['h100']['cards']}, Result={result_h100_cards}")
    if result_h100_per_card != normalization_config['h100']['tflops_per_card_fp8']:
        errors.append(f"H100 TFLOPS/card mismatch: Config={normalization_config['h100']['tflops_per_card_fp8']}, Result={result_h100_per_card}")
    if result_h100_total != normalization_config['h100']['total_tflops']:
        errors.append(f"H100 total TFLOPS mismatch: Config={normalization_config['h100']['total_tflops']}, Result={result_h100_total}")
    
    # 7. H100 reference (from model config)
    if model_name not in model_config['models']:
        errors.append(f"Model {model_name} not found in model-workload-references.yaml")
        return False, errors
    
    model_data = model_config['models'][model_name]
    h100_ref_expected = None
    for workload_data in model_data['h100_references'].values():
        if workload_data['cell_name'] == cell_name:
            h100_ref_expected = workload_data['throughput_tok_s']
            break
    
    if h100_ref_expected is None:
        errors.append(f"H100 reference for cell {cell_name} not found in model config")
    elif abs(result_h100_ref - h100_ref_expected) > 0.01:
        errors.append(f"H100 reference mismatch: Config={h100_ref_expected}, Result={result_h100_ref}")
    
    # 8. Achievement calculation
    a3_norm = result_mean / result_a3_total
    h100_norm = result_h100_ref / result_h100_total
    recomputed_achievement = (a3_norm / h100_norm) * 100
    
    if abs(recomputed_achievement - result_achievement) > 0.05:
        errors.append(f"Achievement calculation error: Recomputed={recomputed_achievement:.2f}%, Result={result_achievement:.2f}%")
    
    if errors:
        return False, errors
    
    return True, []


def main():
    if len(sys.argv) < 4:
        print("Usage: python validate_result.py <result_file.md> <validated_evidence.json> <model_name>", file=sys.stderr)
        print("Example: python validate_result.py RESULT-*.md validated-evidence.json GLM-5.2-W8A8", file=sys.stderr)
        print("", file=sys.stderr)
        print("model_name must match a key in model-workload-references.yaml", file=sys.stderr)
        print("No fallback or guessing allowed.", file=sys.stderr)
        sys.exit(1)
    
    result_path = Path(sys.argv[1])
    validated_evidence_path = Path(sys.argv[2])
    model_name = sys.argv[3]
    
    # Load validated Evidence
    try:
        with open(validated_evidence_path, 'r', encoding='utf-8') as f:
            validated_evidence = json.load(f)
    except Exception as e:
        print(f"✗ FAIL: Could not load validated Evidence", file=sys.stderr)
        print(f"  FORMAL_RESULT_VALIDATION_FAILED", file=sys.stderr)
        print(f"  Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    if validated_evidence.get('validation_status') != 'PASS':
        print(f"✗ FAIL: Evidence validation did not pass", file=sys.stderr)
        print(f"  FORMAL_RESULT_VALIDATION_FAILED", file=sys.stderr)
        print(f"  Evidence error: {validated_evidence.get('error')}", file=sys.stderr)
        sys.exit(1)
    
    # Load configs
    repo_root = Path(__file__).parent.parent
    norm_config_path = repo_root / 'docs' / 'vllm-ascend-performance' / 'hardware-normalization-config.yaml'
    model_config_path = repo_root / 'docs' / 'vllm-ascend-performance' / 'model-workload-references.yaml'
    
    try:
        normalization_config = load_yaml_config(norm_config_path)
        model_config = load_yaml_config(model_config_path)
    except Exception as e:
        print(f"✗ FAIL: Could not load configs", file=sys.stderr)
        print(f"  FORMAL_RESULT_VALIDATION_FAILED", file=sys.stderr)
        print(f"  Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Validate normalization config
    config_valid, config_msg = validate_normalization_config(normalization_config)
    if not config_valid:
        print(f"✗ FAIL: Normalization config validation failed", file=sys.stderr)
        print(f"  FORMAL_RESULT_VALIDATION_FAILED", file=sys.stderr)
        print(f"  {config_msg}", file=sys.stderr)
        sys.exit(1)
    
    # Check model exists in config
    if model_name not in model_config['models']:
        print(f"✗ FAIL: Unknown model '{model_name}'", file=sys.stderr)
        print(f"  FORMAL_RESULT_VALIDATION_FAILED", file=sys.stderr)
        print(f"  Model not found in model-workload-references.yaml", file=sys.stderr)
        print(f"  Available models: {', '.join(model_config['models'].keys())}", file=sys.stderr)
        sys.exit(1)
    
    # Validate Result
    is_valid, errors = validate_result(result_path, validated_evidence, normalization_config, model_config, model_name)
    
    if is_valid:
        print(f"✓ PASS: {result_path.name}")
        print(f"  All validations passed")
        sys.exit(0)
    else:
        print(f"✗ FAIL: {result_path.name}", file=sys.stderr)
        print(f"  FORMAL_RESULT_VALIDATION_FAILED", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
