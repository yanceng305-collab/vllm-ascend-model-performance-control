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
| Max concurrency | 64 | requests |
| Num prompts | 256 | prompts |
| **Total token throughput** | **2688.71** | **tok/s** |
| Output token throughput | 1344.35 | tok/s |
| Mean TTFT | 1222.68 | ms |
| P99 TTFT | 3152.29 | ms |
| Mean TPOT | 46.42 | ms |

**H100 normalized throughput** (1K cell):
```
2688.71 tok/s / 16 cards / 989 TFLOPS/card = 0.169913 tok/s per TFLOPS
```

### SRC-B-GLM-4K (4096 input)

| Metric | Value | Unit |
|---|---|---|
| Input tokens | 4096 | tokens |
| Output tokens | 1024 | tokens |
| Max concurrency | 64 | requests |
| Num prompts | 256 | prompts |
| **Total token throughput** | **4063.45** | **tok/s** |
| Output token throughput | 812.69 | tok/s |
| Mean TTFT | 6640.72 | ms |
| P99 TTFT | 29472.86 | ms |
| Mean TPOT | 69.09 | ms |

**H100 normalized throughput** (4K cell):
```
4063.45 tok/s / 16 cards / 989 TFLOPS/card = 0.256790 tok/s per TFLOPS
```

### SRC-B-GLM-16K (16384 input)

| Metric | Value | Unit |
|---|---|---|
| Input tokens | 16384 | tokens |
| Output tokens | 1024 | tokens |
| Max concurrency | 64 | requests |
| Num prompts | 256 | prompts |
| **Total token throughput** | **4379.60** | **tok/s** |
| Output token throughput | 257.62 | tok/s |
| Mean TTFT | 163707.95 | ms |
| P99 TTFT | 227645.14 | ms |
| Mean TPOT | 65.78 | ms |

**H100 normalized throughput** (16K cell):
```
4379.60 tok/s / 16 cards / 989 TFLOPS/card = 0.276769 tok/s per TFLOPS
```

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

- All four cells (1K/4K/16K/64K) extracted from User-provided XLSX file (sheet: "推理glm5.2 int8", column: "NV-H100原生-fp8")
- Source ingestion date: 2026-09-02
- H100 configuration: 16 cards, FP8 precision, 989 TFLOPS per card
- See Decision D-020 for compute basis and normalization policy
- See `references/SOURCE-MATERIALS.md` for original source hash and ingestion record
