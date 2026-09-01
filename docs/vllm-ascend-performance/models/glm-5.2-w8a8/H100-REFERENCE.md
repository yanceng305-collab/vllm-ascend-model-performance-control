# GLM-5.2-W8A8 H100 Reference

## Source Identity

Four source cells extracted from User-provided materials (XLSX/DOCX):
- `SRC-B-GLM-1K`: 1024 input tokens
- `SRC-B-GLM-4K`: 4096 input tokens
- `SRC-B-GLM-16K`: 16384 input tokens
- `SRC-B-GLM-64K`: 65536 input tokens

**Precision note**: DOCX identifies GLM-5.2-FP8 while XLSX sheet is labeled `glm5.2 int8`. User has approved these cells as `ENGINEERING_REFERENCE` for GLM-5.2-W8A8 comparison (Decision D-020). The precision difference (H100 FP8 vs A3 W8A8) is acknowledged and recorded as comparison class `ENGINEERING_REFERENCE`.

## H100 Configuration

- **Hardware**: 16 × H100
- **Precision**: FP8
- **Compute basis**: 989 TFLOPS per card @ FP8
- **System compute**: 16 × 989 = 15824 TFLOPS

## H100 Reference Cells

### SRC-B-GLM-1K (1024 input)

| Metric | Value | Unit |
|---|---|---|
| Input tokens | 1024 | tokens |
| Output tokens | 1024 | tokens |
| Total token throughput | TBD | tok/s |

(User source material extraction pending or available in SOURCE-MATERIALS.md)

### SRC-B-GLM-4K (4096 input)

| Metric | Value | Unit |
|---|---|---|
| Input tokens | 4096 | tokens |
| Output tokens | 1024 | tokens |
| Total token throughput | TBD | tok/s |

### SRC-B-GLM-16K (16384 input)

| Metric | Value | Unit |
|---|---|---|
| Input tokens | 16384 | tokens |
| Output tokens | 1024 | tokens |
| Total token throughput | TBD | tok/s |

### SRC-B-GLM-64K (65536 input)

| Metric | Value | Unit |
|---|---|---|
| Input tokens | 65536 | tokens |
| Output tokens | 1024 | tokens |
| Max concurrency | 64 | requests |
| Num prompts | 256 | prompts |
| **Total token throughput** | **5054.66** | **tok/s** |
| Mean TPOT | 42.32 | ms |

**H100 normalized throughput** (64K cell):
```
5054.66 tok/s / 16 cards / 989 TFLOPS/card = 0.319431 tok/s per TFLOPS
```

## Comparison Class

**ENGINEERING_REFERENCE**: H100 uses FP8 precision, A3 uses W8A8 quantization. Precision differs but both are INT8-class quantization. Hardware compute basis is unified per Decision D-020 for normalized comparison.

## Notes

- Full extraction of 1K/4K/16K cells from User source materials may be completed separately
- 64K cell is used as primary reference for current baseline Result
- See Decision D-020 for compute basis and normalization policy
- See `references/SOURCE-MATERIALS.md` for original source hash and ingestion record
