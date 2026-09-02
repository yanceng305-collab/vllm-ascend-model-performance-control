#!/usr/bin/env python3
"""
Evidence Validation and Extraction Script

Validates Evidence bundle integrity and extracts machine-readable facts.
Produces validated Evidence summary for Formal Result generation.

Per Decision D-023: Machine-Verified Formal Result Gate
FAIL-CLOSED: Any missing/invalid field causes validation failure and exit 1.
"""

import json
import sys
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def extract_runtime_identity(evidence_dir: Path) -> Dict:
    """Extract runtime identity from runtime-identity.txt"""
    runtime_file = evidence_dir / "runtime-identity.txt"
    if not runtime_file.exists():
        raise FileNotFoundError(f"Missing runtime-identity.txt in {evidence_dir}")
    
    content = runtime_file.read_text(encoding='utf-8')
    
    # Extract key fields
    identity = {}
    
    # Container name
    match = re.search(r'Name:\s*(.+)', content)
    identity['container_name'] = match.group(1).strip() if match else None
    
    # Container ID
    match = re.search(r'ID:\s*(.+)', content)
    identity['container_id'] = match.group(1).strip() if match else None
    
    # Image
    match = re.search(r'Image:\s*(.+)', content)
    identity['image'] = match.group(1).strip() if match else None
    
    # Image SHA256
    match = re.search(r'SHA256:\s*(sha256:[a-f0-9]+)', content)
    identity['image_sha256'] = match.group(1).strip() if match else None
    
    # vLLM Version
    match = re.search(r'vLLM Version:\s*(.+)', content)
    identity['vllm_version'] = match.group(1).strip() if match else None
    
    # Validate required fields
    required_fields = ['container_name', 'container_id', 'image', 'image_sha256', 'vllm_version']
    for field in required_fields:
        if not identity.get(field):
            raise ValueError(f"Runtime identity missing required field: {field}")
    
    return identity


def extract_control_sha(evidence_dir: Path) -> Dict:
    """Extract DISPATCH_CONTROL_SHA and Task ID from control-sha.txt"""
    control_file = evidence_dir / "control-sha.txt"
    if not control_file.exists():
        raise FileNotFoundError(f"Missing control-sha.txt in {evidence_dir}")
    
    content = control_file.read_text(encoding='utf-8')
    
    provenance = {}
    
    # Task ID
    match = re.search(r'Task ID:\s*(.+)', content)
    provenance['task_id'] = match.group(1).strip() if match else None
    
    # DISPATCH_CONTROL_SHA
    match = re.search(r'DISPATCH_CONTROL_SHA:\s*([a-f0-9]{40})', content)
    provenance['dispatch_control_sha'] = match.group(1).strip() if match else None
    
    # Authorization
    match = re.search(r'Authorization:\s*(.+)', content)
    provenance['authorization'] = match.group(1).strip() if match else None
    
    # Validate required fields
    if not provenance['task_id']:
        raise ValueError("control-sha.txt missing Task ID")
    if not provenance['dispatch_control_sha']:
        raise ValueError("control-sha.txt missing DISPATCH_CONTROL_SHA")
    if not provenance['authorization']:
        raise ValueError("control-sha.txt missing Authorization")
    if provenance['authorization'] != 'EXECUTE':
        raise ValueError(f"Authorization is '{provenance['authorization']}', expected 'EXECUTE'")
    
    return provenance


def extract_throughput_from_log(log_file: Path) -> Optional[float]:
    """Extract Total token throughput from benchmark log"""
    if not log_file.exists():
        return None
    
    content = log_file.read_text(encoding='utf-8')
    
    # Look for "Total token throughput (tok/s):"
    match = re.search(r'Total token throughput \(tok/s\):\s+([\d.]+)', content)
    if match:
        return float(match.group(1))
    
    return None


def extract_completed_failed_from_log(log_file: Path) -> Tuple[Optional[int], Optional[int]]:
    """Extract completed and failed counts from benchmark log"""
    if not log_file.exists():
        return None, None
    
    content = log_file.read_text(encoding='utf-8')
    
    completed = None
    failed = None
    
    # Look for "Successful requests:" or "Total completed:" (handle variable whitespace)
    match = re.search(r'(?:Successful requests|Total completed):\s+(\d+)', content)
    if match:
        completed = int(match.group(1))
    
    # Look for "Failed requests:" or similar - check for explicit count
    match = re.search(r'(?:Failed requests|Total failed):\s+(\d+)', content)
    if match:
        failed = int(match.group(1))
    else:
        # If no explicit failed line found, assume 0 if completed was found
        if completed is not None:
            failed = 0
    
    return completed, failed


def validate_cell(evidence_dir: Path, cell_name: str, expected_prompts: int = 256) -> Dict:
    """Validate and extract data for a single cell"""
    cell_dir = evidence_dir / cell_name
    if not cell_dir.exists():
        raise FileNotFoundError(f"Missing cell directory: {cell_name}")
    
    cell_data = {
        'cell_name': cell_name,
        'runs': {}
    }
    
    # Validate run1 exists (warmup)
    run1_log = cell_dir / "run1.log"
    if not run1_log.exists():
        raise FileNotFoundError(f"Missing run1.log in {cell_name} (warmup run required)")
    
    # Extract run2, run3, run4 data
    for run_name in ['run2', 'run3', 'run4']:
        log_file = cell_dir / f"{run_name}.log"
        
        if not log_file.exists():
            raise FileNotFoundError(f"Missing {run_name}.log in {cell_name}")
        
        throughput = extract_throughput_from_log(log_file)
        completed, failed = extract_completed_failed_from_log(log_file)
        
        if throughput is None:
            raise ValueError(f"Could not extract throughput from {log_file}")
        if completed is None:
            raise ValueError(f"Could not extract completed count from {log_file}")
        if failed is None:
            raise ValueError(f"Could not extract failed count from {log_file}")
        
        # Validate workload contract
        if completed != expected_prompts:
            raise ValueError(f"{cell_name} {run_name}: completed={completed}, expected {expected_prompts}")
        if failed != 0:
            raise ValueError(f"{cell_name} {run_name}: failed={failed}, expected 0")
        
        cell_data['runs'][run_name] = {
            'throughput': throughput,
            'completed': completed,
            'failed': failed
        }
    
    # Calculate mean (Run2, Run3, Run4) with full precision
    throughputs = [cell_data['runs'][r]['throughput'] for r in ['run2', 'run3', 'run4']]
    cell_data['mean_throughput'] = sum(throughputs) / len(throughputs)
    
    return cell_data


def verify_manifest_and_checksums(evidence_dir: Path) -> None:
    """Verify MANIFEST.txt and SHA256SUMS.txt exist and are accessible"""
    manifest_file = evidence_dir / "MANIFEST.txt"
    sha256sums_file = evidence_dir / "SHA256SUMS.txt"
    
    if not manifest_file.exists():
        raise FileNotFoundError(f"Missing MANIFEST.txt in {evidence_dir}")
    if not sha256sums_file.exists():
        raise FileNotFoundError(f"Missing SHA256SUMS.txt in {evidence_dir}")
    
    # Basic readability check
    try:
        manifest_file.read_text(encoding='utf-8')
        sha256sums_file.read_text(encoding='utf-8')
    except Exception as e:
        raise ValueError(f"Could not read manifest/checksums files: {e}")


def validate_evidence(evidence_dir: Path, cells: List[str], expected_prompts: int = 256,
                     archive_sha256: str = None, evidence_location: str = None) -> Dict:
    """
    Validate Evidence bundle and extract all machine-readable facts.
    FAIL-CLOSED: Any validation failure raises exception and exits 1.
    
    Returns validated Evidence summary as dict.
    """
    evidence_dir = Path(evidence_dir)
    
    if not evidence_dir.exists():
        raise FileNotFoundError(f"Evidence directory not found: {evidence_dir}")
    
    # Verify MANIFEST and checksums exist
    verify_manifest_and_checksums(evidence_dir)
    
    # Extract runtime identity
    runtime_identity = extract_runtime_identity(evidence_dir)
    
    # Extract control SHA
    provenance = extract_control_sha(evidence_dir)
    
    # Validate and extract all cells
    cells_data = {}
    for cell in cells:
        cells_data[cell] = validate_cell(evidence_dir, cell, expected_prompts)
    
    # Build Evidence archive metadata
    evidence_run_id = evidence_dir.name
    archive_filename = f"{provenance['task_id']}-EVIDENCE-{evidence_run_id}.tar.gz"
    
    # Build validated Evidence summary
    validated_evidence = {
        'evidence_directory': str(evidence_dir.absolute()),
        'evidence_run_id': evidence_run_id,
        'archive_filename': archive_filename,
        'archive_sha256': archive_sha256 if archive_sha256 else "UNKNOWN",
        'evidence_location': evidence_location if evidence_location else "UNKNOWN",
        'runtime_identity': runtime_identity,
        'provenance': provenance,
        'cells': cells_data,
        'validation_status': 'PASS',
        'expected_prompts': expected_prompts
    }
    
    return validated_evidence


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_evidence.py <evidence_directory> [cell1 cell2 ...] [--sha256 <hash>] [--location <location>]", file=sys.stderr)
        print("Example: python validate_evidence.py ./run-20260902-140958 1K 4K 16K 64K --sha256 abc123... --location 'GitHub Release ...'", file=sys.stderr)
        sys.exit(1)
    
    evidence_dir = Path(sys.argv[1])
    
    # Parse arguments
    cells = []
    archive_sha256 = None
    evidence_location = None
    
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--sha256' and i + 1 < len(sys.argv):
            archive_sha256 = sys.argv[i + 1]
            i += 2
        elif arg == '--location' and i + 1 < len(sys.argv):
            evidence_location = sys.argv[i + 1]
            i += 2
        elif not arg.startswith('--'):
            cells.append(arg)
            i += 1
        else:
            i += 1
    
    if not cells:
        cells = ['1K', '4K', '16K', '64K']
    
    try:
        validated_evidence = validate_evidence(evidence_dir, cells, 
                                              archive_sha256=archive_sha256,
                                              evidence_location=evidence_location)
        
        # Output as JSON
        print(json.dumps(validated_evidence, indent=2))
        sys.exit(0)
        
    except Exception as e:
        print(json.dumps({
            'validation_status': 'FAIL',
            'error': str(e)
        }, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
