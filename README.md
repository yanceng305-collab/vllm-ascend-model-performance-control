# vLLM-Ascend Model Performance Control

Public Control repository for auditable native vLLM-Ascend correctness and performance baselines on Ascend hardware. Accepted baselines are intended to be referenced by later FlagOS migration projects; this repository does not contain FlagOS adaptation code.

## Current status

**BOOTSTRAPPED / MATERIALS RECEIVED; NORMALIZATION INPUTS INCOMPLETE / NO EXECUTION READY**

No A3/NPU test has been run. No model/runtime/hardware identity is frozen yet.

## Navigation

- [Project README](docs/vllm-ascend-performance/README.md)
- [Status](docs/vllm-ascend-performance/STATUS.md)
- [Plan](docs/vllm-ascend-performance/PLAN.md)
- [Decisions](docs/vllm-ascend-performance/DECISIONS.md)
- [Repository and Evidence Rules](docs/vllm-ascend-performance/REPOSITORY-AND-EVIDENCE-RULES.md)
- [Benchmark Contract](docs/vllm-ascend-performance/methodology/BENCHMARK-CONTRACT.md)
- [Normalization Policy](docs/vllm-ascend-performance/methodology/PERFORMANCE-NORMALIZATION-POLICY.md)
- [FlagOS-Aligned Version Baseline](docs/vllm-ascend-performance/methodology/VERSION-BASELINE.md)
- [Comparison Classes](docs/vllm-ascend-performance/methodology/COMPARISON-CLASSES.md)
- [Stage 0 Server Fact Acquisition](docs/vllm-ascend-performance/methodology/SERVER-FACT-ACQUISITION.md)
- [ChatGPT Review and Handoff](docs/vllm-ascend-performance/methodology/CHATGPT-REVIEW-AND-HANDOFF.md)
- [Stage 0 Codex2 Task](docs/vllm-ascend-performance/tasks/VLLM-ASCEND-STAGE0-SERVER-FACT-ACQUISITION.md)
- [Source Materials](docs/vllm-ascend-performance/references/SOURCE-MATERIALS.md)
- [H100 Reference Index](docs/vllm-ascend-performance/references/H100-REFERENCE-INDEX.md)
- [GLM-5.2-W8A8](docs/vllm-ascend-performance/models/glm-5.2-w8a8/STATUS.md)
- [DeepSeek-V4-Pro-W8A8](docs/vllm-ascend-performance/models/deepseek-v4-pro-w8a8/STATUS.md)
- [DeepSeek-V4-Flash-W8A8](docs/vllm-ascend-performance/models/deepseek-v4-flash-w8a8/STATUS.md)
- [MiniMax-M3](docs/vllm-ascend-performance/models/minimax-m3/STATUS.md)

## Lifecycle

```text
User Decision -> Codex1 Formal Task -> explicit User dispatch
-> Codex2 server Evidence -> immutable Result
-> Codex1 Formal Review -> ACCEPTED / REJECTED / NEEDS-FOLLOWUP
```

An accepted result freezes model identity, quantization, runtime/image, versions, CANN/PyTorch stack, hardware, parallelism, launch configuration, benchmark cells, raw metrics, normalized targets, and Evidence pointers.

## Current model scope

**Project Model Pool:** GLM-5.2-W8A8, DeepSeek-V4-Flash-W8A8, DeepSeek-V4-Pro-W8A8, MiniMax-M3.

**Current Single-A3 candidates:** GLM-5.2-W8A8, DeepSeek-V4-Flash-W8A8, MiniMax-M3 on one Ascend A3/910C server (8 cards / 16 NPU chips). DeepSeek-V4-Pro-W8A8 remains a `MULTI_NODE_CANDIDATE / NOT_SINGLE_A3_CANDIDATE` and is not part of the current Stage 0 execution scope.
