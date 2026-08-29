# H100 Reference Index

Status: `INGESTED`; cells are source records, not accepted targets.

All extracted cells use output 1,024 tokens, concurrency 64, and 256 prompts. The DOCX environment is H100 80GB, CUDA 13.0, driver 580.105.08. Qwen uses TP2; GLM, MiniMax, and Hy3 use TP16 over two nodes; DeepSeek-V4-Flash uses TP8.

| Cell ID | Model | Input/Output | H100 devices | Precision / quantization | Output tok/s | Total tok/s | Mean TTFT ms | Mean TPOT ms | Mean ITL ms |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|
| `SRC-B-Q27-1K` | Qwen3.6-27B | 1024/1024 | 2 | BF16 | 2913.08 | 5826.17 | 1385.91 | 20.62 | 20.62 |
| `SRC-B-Q27-4K` | Qwen3.6-27B | 4096/1024 | 2 | BF16 | 1912.11 | 9560.56 | 2987.64 | 30.52 | 30.52 |
| `SRC-B-Q27-16K` | Qwen3.6-27B | 16384/1024 | 2 | BF16 | 779.76 | 13255.88 | 9399.54 | 72.67 | 72.67 |
| `SRC-B-Q27-64K` | Qwen3.6-27B | 65536/1024 | 2 | BF16 | 187.08 | 12160.18 | 228539.06 | 93.26 | 93.27 |
| `SRC-B-Q35-1K` | Qwen3.6-35B-A3B | 1024/1024 | 2 | BF16 | 4067.21 | 8134.42 | 518.55 | 15.23 | 15.23 |
| `SRC-B-Q35-4K` | Qwen3.6-35B-A3B | 4096/1024 | 2 | BF16 | 3352.01 | 16760.05 | 1034.79 | 18.06 | 18.06 |
| `SRC-B-Q35-16K` | Qwen3.6-35B-A3B | 16384/1024 | 2 | BF16 | 1856.27 | 31556.53 | 3435.45 | 30.97 | 30.97 |
| `SRC-B-Q35-64K` | Qwen3.6-35B-A3B | 65536/1024 | 2 | BF16 | 567.73 | 36902.29 | 32828.42 | 77.58 | 77.58 |
| `SRC-B-GLM-1K` | GLM-5.2-FP8 | 1024/1024 | 16 | FP8 DOCX; INT8 XLSX | 1344.35 | 2688.71 | 1222.68 | 46.42 | 46.42 |
| `SRC-B-GLM-4K` | GLM-5.2-FP8 | 4096/1024 | 16 | FP8 DOCX; INT8 XLSX | 812.69 | 4063.45 | 6640.72 | 69.09 | 69.09 |
| `SRC-B-GLM-16K` | GLM-5.2-FP8 | 16384/1024 | 16 | FP8 DOCX; INT8 XLSX | 257.62 | 4379.60 | 163707.95 | 65.78 | 65.78 |
| `SRC-B-GLM-64K` | GLM-5.2-FP8 | 65536/1024 | 16 | FP8 DOCX; INT8 XLSX | 77.76 | 5054.66 | 703337.80 | 42.32 | 42.36 |
| `SRC-B-M3-1K` | MiniMax-M3 | 1024/1024 | 16 | UNKNOWN | 2013.91 | 4027.81 | 918.29 | 30.89 | 30.89 |
| `SRC-B-M3-4K` | MiniMax-M3 | 4096/1024 | 16 | UNKNOWN | 1111.07 | 5555.33 | 22637.12 | 30.09 | 30.09 |
| `SRC-B-M3-16K` | MiniMax-M3 | 16384/1024 | 16 | UNKNOWN | 408.16 | 6938.76 | 121379.09 | 20.72 | 20.72 |
| `SRC-B-M3-64K` | MiniMax-M3 | 65536/1024 | 16 | UNKNOWN | 121.79 | 7916.13 | 458673.65 | 13.88 | 13.97 |
| `SRC-B-HY3-1K` | Hy3 | 1024/1024 | 16 | UNKNOWN | 1928.11 | 3856.21 | 802.74 | 32.42 | 32.42 |
| `SRC-B-HY3-4K` | Hy3 | 4096/1024 | 16 | UNKNOWN | 1569.37 | 7846.86 | 1687.93 | 39.07 | 39.07 |
| `SRC-B-HY3-16K` | Hy3 | 16384/1024 | 16 | UNKNOWN | 718.89 | 12221.18 | 24980.78 | 59.63 | 59.63 |
| `SRC-B-HY3-64K` | Hy3 | 65536/1024 | 16 | UNKNOWN | 197.78 | 12855.93 | 240859.07 | 56.22 | 56.23 |
| `SRC-B-DSF-1K` | DeepSeek-V4-Flash | 1024/1024 | 8 | UNKNOWN; FP8 KV cache noted | 3328.89 | 6657.78 | 922.84 | 18.33 | 18.33 |
| `SRC-B-DSF-4K` | DeepSeek-V4-Flash | 4096/1024 | 8 | UNKNOWN; FP8 KV cache noted | 2530.45 | 12652.27 | 1962.80 | 23.35 | 23.35 |
| `SRC-B-DSF-16K` | DeepSeek-V4-Flash | 16384/1024 | 8 | UNKNOWN; FP8 KV cache noted | 1272.43 | 21631.27 | 6156.29 | 44.15 | 44.15 |
| `SRC-B-DSF-64K` | DeepSeek-V4-Flash | 65536/1024 | 8 | UNKNOWN; FP8 KV cache noted | 392.51 | 25513.34 | 24677.61 | 138.33 | 138.57 |

## Computation inputs

The XLSX states 989 TFLOPS/device for H100, with totals 1,978 (Qwen, 2 cards), 15,824 (GLM, 16 cards), and 7,912 (DeepSeek Flash, 8 cards). This basis is not approved as comparable because precision, dense/sparse mode, and H100 SKU (PCIe/SXM) are not frozen. No Ascend SKU, card count, comparable compute, or dense/sparse basis is supplied. Therefore no normalized Ascend target is calculated.

## Comparability

GLM is `NOT COMPARABLE` pending FP8-versus-INT8 identity resolution. DeepSeek-V4-Flash is pending exact model quantization resolution. DeepSeek-V4-Pro has no H100 reference cell and is `NOT COMPARABLE`. Any future cell must also freeze request rate, sampling, EOS/cache assumptions, MTP, graph/eager mode, benchmark tool/version, repetitions/statistic, and metric gate class.
