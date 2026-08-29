# FlagOS-Aligned Version Baseline

## Frozen target

`FLAGOS_ALIGNED_BASELINE` is the primary acceptance lane for results intended to be reused by a later FlagOS migration:

| Component | Frozen identity | Official evidence |
|---|---|---|
| FlagOS target | `flagos-ai/vllm-plugin-FL`, `release/0.2` | [README at release/0.2](https://github.com/flagos-ai/vllm-plugin-FL/blob/release/0.2/README.md), branch head `c0c060a6473ad4209c8a141fd463ee9668a6ab79`, queried 2026-08-29 |
| vLLM | `v0.20.2` | FlagOS README links official vLLM `v0.20.2`; `release/0.2` `pyproject.toml` test extra contains `vllm[audio]==0.20.2` |
| vLLM-Ascend | `v0.20.2rc1` | [vLLM-Ascend versioning policy](https://github.com/vllm-project/vllm-ascend/blob/main/docs/source/community/versioning_policy.md), main commit `d4fc06f08ebcc7a934e569dd9f546155d52d375e`, queried 2026-08-29 |
| Python | `>=3.10,<3.12` | vLLM-Ascend compatibility row |
| CANN | `9.0.0` | vLLM-Ascend compatibility row |
| PyTorch / torch_npu | `2.10.0 / 2.10.0` | vLLM-Ascend compatibility row |
| Triton Ascend | `3.2.1` | vLLM-Ascend compatibility row |
| Mooncake | `v0.3.8.post1` | vLLM-Ascend compatibility row |

The compatibility row is the version source of truth. A release or post-release may be used only when official evidence explicitly demonstrates compatibility with vLLM `0.20.2`; do not infer compatibility from a similar version number.

## Dual-track policy

### Track A: `FLAGOS_ALIGNED`

Use vLLM `0.20.2` with vLLM-Ascend `0.20.2rc1`, or an officially documented patch/post release proven compatible with vLLM `0.20.2`. Results in this lane may become the native baseline for a future FlagOS `release/0.2` migration.

### Track B: `LATEST_REFERENCE`

Use a newer vLLM/vLLM-Ascend only when the aligned lane lacks model support, has a known blocker, or a newer implementation is being studied. Every such Result must be marked `NON_FLAGOS_ALIGNED_REFERENCE`. It cannot replace Track A, participate in FlagOS performance acceptance, or be combined with an aligned Result.

If the model is unsupported on `0.20.2rc1`, the aligned status is `FLAGOS_ALIGNED_BASELINE_BLOCKED_MODEL_UNSUPPORTED`; do not silently upgrade the runtime. A newer-only success is evidence of a version/support gap, not an aligned baseline.

## Version identity requirements

Every Task and Result records the runtime tuple, exact repository refs/commits or image digest, Python/CANN/PyTorch/torch_npu/Triton/Mooncake versions, and the track. A changed tuple requires a new Task and Result chain.
