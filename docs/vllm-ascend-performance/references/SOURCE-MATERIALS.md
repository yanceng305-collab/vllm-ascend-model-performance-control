# Source Materials

## User-provided files

The following files were present on the workstation on 2026-08-29. They remain outside the Control repository and were not modified.

| ID | Role | Original path | SHA-256 | Status |
|---|---|---|---|---|
| `SRC-A` | Huawei end-to-end optimization data; candidate Ascend/runtime/workload evidence | `C:\Users\22477\Downloads\共享-华为端到端模型优化数据.xlsx` | `45f2759b85d8a271058c2928c33a3ab7ed70d801b2772dd6b8b4fdbf369ea268` | Received and ingested |
| `SRC-B` | H100 vLLM benchmark reference | `D:\download_web\H100 baseline vllm benchmark_ Qwen,GLM,MiniMax,Hy,DeepSeek.docx` | `25e63fb5d30e7940d7e18e79a6f11852160b3d53c30bf1b3a7a5edd940afe8a6` | Received and ingested |

## Provenance rules

`SRC-A` was temporarily locked by another process during the initial hash attempt; its digest was then computed over the original bytes with shared-read access. Values retain workbook sheet and cell/table anchors. `SRC-B` hash was read successfully; values retain document page/table/paragraph anchors.

## Extracted material

See [H100-REFERENCE-INDEX.md](H100-REFERENCE-INDEX.md) for the 24 extracted H100 cells and [PERFORMANCE-NORMALIZATION-POLICY.md](../methodology/PERFORMANCE-NORMALIZATION-POLICY.md) for target rules. No value is promoted to an accepted baseline until comparability and User approval are recorded.

## Ingestion outcome

`MATERIALS_RECEIVED; NORMALIZATION_INPUTS_INCOMPLETE; NO_EXECUTION_READY`.

The DOCX benchmark contract signals random input 4096/output 1024, max concurrency 64, 256 prompts, `ignore_eos`, and throughput/latency fields. It does not freeze warm-up, repeats, aggregation, request rate, sampling, MTP, or graph/eager policy. The workbook contains sheets `qwen3.6-27B`, `qwen3.6-35B`, `glm5.2 int8`, and `dsv4 flash int8`; its H100 compute row states 989 TFLOPS/device, but precision/dense-sparse/SKU comparability remains unapproved.
