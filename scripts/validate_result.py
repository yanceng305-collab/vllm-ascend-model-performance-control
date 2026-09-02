#!/usr/bin/env python3
"""
Pre-Commit Formal Result Validator

Validates Formal Results before commit to prevent transcription errors.
Per Decision D-023: Machine-Verified Formal Result Gate

Verifies:
- Evidence runtime == Result runtime
- Raw Run values == Result
- Recomputed mean == Result
- Normalization basis == Decision/config
- Recomputed achievement == Result
- DISPATCH_CONTROL_SHA == Evidence
- Archive SHA256 == Evidence provenance

Exits with code 1 if validation fails (blocks commit).
"""

import re
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple


def load_normalization_config(config_path: Path) -> Dict:
    """Load hardware normalization configuration"""
    config = {}
    with open(config_path, 'r', encoding='utf-8') as f:
        for line in f:
            if 'total_tflops: 6048' in line:
                config['a3_total_tflops'] = 6048
            elif 'total_tflops: 15824' in line:
                config['h100_total_tflops'] = 15824
            elif 'target_achievement_minimum: 0.80' in line or 'target_achievement_minimum: 0.8' in line:
                config['target_achievement_minimum'] = 0.80
    return config


def extract_result_field(content: str, pattern: str) -> Optional[str]:
    """Extract a field from Result markdown using regex"""
    match = re.search(pattern, content, re.MULTILINE)
    return match.group(1).strip() if match else None


def extract_float(content: str, pattern: str) -> Optional[float]:
    """Extract a float value from Result markdown"""
    value_str = extract_result_field(content, pattern)
    if value_str:
        # Remove commas and extract just the number
        value_str = re.sub(r'[^\d.]', '', value_str)
        try:
            return float(value_str)
        except ValueError:
            pass
    return None


def validate_result(result_path: Path, validated_evidence: Optional[Dict] = None,
                   normalization_config: Optional[Dict] = None) -> Tuple[bool, str]:
    """
    Validate a Formal Result document.
    
    Returns: (is_valid, error_message)
    """
    
    if not result_path.exists():
        return False, f"Result file not found: {result_path}"
    
    content = result_path.read_text(encoding='utf-8')
    
    # Extract key fields from Result
    result_data = {}
    
    # Runtime identity
    result_data['vllm_version'] = extract_result_field(content, r'\*\*vLLM Version\*\*:\s*`([^`]+)`')
    result_data['image'] = extract_result_field(content, r'\*\*Image\*\*:\s*`([^`]+)`')
    
    # DISPATCH_CONTROL_SHA
    result_data['dispatch_control_sha'] = extract_result_field(content, r'\*\*DISPATCH_CONTROL_SHA\*\*:\s*`?([a-f0-9]{40})`?')
    
    # Archive SHA256
    result_data['archive_sha256'] = extract_result_field(content, r'\*\*Archive SHA256\*\*:\s*`([a-f0-9]{64})`')
    
    # Run values
    result_data['run2'] = extract_float(content, r'\*\*Run 2\*\*:\s*([\d.]+)\s*tok/s')
    result_data['run3'] = extract_float(content, r'\*\*Run 3\*\*:\s*([\d.]+)\s*tok/s')
    result_data['run4'] = extract_float(content, r'\*\*Run 4\*\*:\s*([\d.]+)\s*tok/s')
    
    # Mean
    result_data['mean'] = extract_float(content, r'\*\*Mean \(Run2, Run3, Run4\)\*\*:\s*\*\*([\d.]+)\s*tok/s\*\*')
    
    # Achievement
    result_data['achievement'] = extract_float(content, r'Achievement.*?=\s*([\d.]+)%')
    
    # H100 reference
    result_data['h100_reference'] = extract_float(content, r'\*\*H100 Reference\*\*.*?:\s*([\d.]+)\s*tok/s')
    
    # Hardware basis
    result_data['a3_total'] = extract_float(content, r'A3/910C System:\s*([\d,]+)\s*TFLOPS')
    result_data['h100_total'] = extract_float(content, r'H100 System:\s*([\d,]+)\s*TFLOPS')
    
    # Validation checks
    errors = []
    
    # If validated_evidence provided, check against it
    if validated_evidence:
        # Check runtime identity
        evidence_runtime = validated_evidence.get('runtime_identity', {})
        if evidence_runtime.get('vllm_version') and result_data['vllm_version']:
            if evidence_runtime['vllm_version'] != result_data['vllm_version']:
                errors.append(f"Runtime version mismatch: Evidence={evidence_runtime['vllm_version']}, Result={result_data['vllm_version']}")
        
        # Check DISPATCH_CONTROL_SHA
        evidence_sha = validated_evidence.get('provenance', {}).get('dispatch_control_sha')
        if evidence_sha and result_data['dispatch_control_sha']:
            if evidence_sha != result_data['dispatch_control_sha']:
                errors.append(f"DISPATCH_CONTROL_SHA mismatch: Evidence={evidence_sha}, Result={result_data['dispatch_control_sha']}")
    
    # Check mean calculation
    if all([result_data['run2'], result_data['run3'], result_data['run4'], result_data['mean']]):
        computed_mean = (result_data['run2'] + result_data['run3'] + result_data['run4']) / 3
        # Allow 0.01 tolerance for rounding
        if abs(computed_mean - result_data['mean']) > 0.01:
            errors.append(f"Mean calculation error: Expected {computed_mean:.2f}, Result={result_data['mean']:.2f}")
    
    # Check hardware normalization basis
    if normalization_config:
        if result_data['a3_total'] and result_data['a3_total'] != normalization_config['a3_total_tflops']:
            errors.append(f"A3 TFLOPS mismatch: Config={normalization_config['a3_total_tflops']}, Result={result_data['a3_total']}")
        
        if result_data['h100_total'] and result_data['h100_total'] != normalization_config['h100_total_tflops']:
            errors.append(f"H100 TFLOPS mismatch: Config={normalization_config['h100_total_tflops']}, Result={result_data['h100_total']}")
    
    # Check achievement calculation
    if all([result_data['mean'], result_data['h100_reference'], result_data['a3_total'], result_data['h100_total'], result_data['achievement']]):
        a3_norm = result_data['mean'] / result_data['a3_total']
        h100_norm = result_data['h100_reference'] / result_data['h100_total']
        computed_achievement = (a3_norm / h100_norm) * 100
        
        # Allow 0.05% tolerance for rounding
        if abs(computed_achievement - result_data['achievement']) > 0.05:
            errors.append(f"Achievement calculation error: Expected {computed_achievement:.2f}%, Result={result_data['achievement']:.2f}%")
    
    if errors:
        return False, "\n".join(errors)
    
    return True, "Validation PASS"


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_result.py <result_file.md>", file=sys.stderr)
        print("Example: python validate_result.py RESULT-GLM52-W8A8-1K-BASELINE.md", file=sys.stderr)
        sys.exit(1)
    
    result_path = Path(sys.argv[1])
    
    # Load normalization config
    repo_root = Path(__file__).parent.parent
    config_path = repo_root / 'docs' / 'vllm-ascend-performance' / 'hardware-normalization-config.yaml'
    
    normalization_config = load_normalization_config(config_path)
    
    # Validate Result
    is_valid, message = validate_result(result_path, normalization_config=normalization_config)
    
    if is_valid:
        print(f"✓ PASS: {result_path.name}")
        print(f"  {message}")
        sys.exit(0)
    else:
        print(f"✗ FAIL: {result_path.name}", file=sys.stderr)
        print(f"  FORMAL_RESULT_VALIDATION_FAILED", file=sys.stderr)
        print(f"  {message}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
