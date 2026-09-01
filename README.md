# vLLM-Ascend Model Performance Control

Public Control repository for auditable native vLLM-Ascend correctness and performance baselines on Ascend hardware. Accepted baselines are intended to be referenced by later FlagOS migration projects; this repository does not contain FlagOS adaptation code.

## Current Status

**BOOTSTRAPPED / GLM-5.2-W8A8 USER-VERIFIED BASELINE ESTABLISHED**

**GLM-5.2-W8A8**: User-verified baseline on vLLM 0.24 established. 64K baseline measured at 927.45 tok/s (48.01% achievement vs 80% target). Frozen baseline artifacts and scripts available. Optimization work in progress.

**DeepSeek-V4-Flash / MiniMax-M3**: Stage 0A discovery awaiting User dispatch.

## Agent Roles

- **PerfControl** (formerly Codex1): Control repo, planning, methodology, Task/prompt authoring, Result review, Acceptance, status governance
- **A3PerfRunner** (formerly Codex2): A3 server execution, Evidence collection, Result reporting

See [AGENTS.md](AGENTS.md) and Decision D-018.

## Navigation

- [Agent Roles](AGENTS.md)
- [Project README](docs/vllm-ascend-performance/README.md)
- [Status](docs/vllm-ascend-performance/STATUS.md)
- [Plan](docs/vllm-ascend-performance/PLAN.md)
- [Decisions](docs/vllm-ascend-performance/DECISIONS.md)
- [Repository and Evidence Rules](docs/vllm-ascend-performance/REPOSITORY-AND-EVIDENCE-RULES.md)

### Methodology
- [Benchmark Contract](docs/vllm-ascend-performance/methodology/BENCHMARK-CONTRACT.md)
- [Normalization Policy](docs/vllm-ascend-performance/methodology/PERFORMANCE-NORMALIZATION-POLICY.md)
- [FlagOS-Aligned Version Baseline](docs/vllm-ascend-performance/methodology/VERSION-BASELINE.md)
- [Comparison Classes](docs/vllm-ascend-performance/methodology/COMPARISON-CLASSES.md)
- [Server Fact Acquisition](docs/vllm-ascend-performance/methodology/SERVER-FACT-ACQUISITION.md)
- [ChatGPT Review and Handoff](docs/vllm-ascend-performance/methodology/CHATGPT-REVIEW-AND-HANDOFF.md)
- [Workspace and Evidence Paths](docs/vllm-ascend-performance/methodology/WORKSPACE-AND-EVIDENCE-PATHS.md)
- [Single-A3 Container Contract](docs/vllm-ascend-performance/methodology/SINGLE-A3-CONTAINER-CONTRACT.md)
- [Execution Command Completeness](docs/vllm-ascend-performance/methodology/EXECUTION-COMMAND-COMPLETENESS.md)
- [Model Hash Policy](docs/vllm-ascend-performance/methodology/MODEL-HASH-POLICY.md)
- [Image Identity Evidence](docs/vllm-ascend-performance/methodology/IMAGE-IDENTITY-EVIDENCE.md)

### Reference Materials
- [Source Materials](docs/vllm-ascend-performance/references/SOURCE-MATERIALS.md)
- [H100 Reference Index](docs/vllm-ascend-performance/references/H100-REFERENCE-INDEX.md)

### Models
- [GLM-5.2-W8A8](docs/vllm-ascend-performance/models/glm-5.2-w8a8/STATUS.md) — **User-verified baseline, 64K@48.01%**
  - [Baseline](docs/vllm-ascend-performance/models/glm-5.2-w8a8/BASELINE.md)
  - [Runbook](docs/vllm-ascend-performance/models/glm-5.2-w8a8/RUNBOOK.md)
  - [H100 Reference](docs/vllm-ascend-performance/models/glm-5.2-w8a8/H100-REFERENCE.md)
  - [Ascend Targets](docs/vllm-ascend-performance/models/glm-5.2-w8a8/ASCEND-TARGETS.md)
  - [Results](docs/vllm-ascend-performance/models/glm-5.2-w8a8/results/INDEX.md)
- [DeepSeek-V4-Pro-W8A8](docs/vllm-ascend-performance/models/deepseek-v4-pro-w8a8/STATUS.md) — Multi-node candidate
- [DeepSeek-V4-Flash-W8A8](docs/vllm-ascend-performance/models/deepseek-v4-flash-w8a8/STATUS.md) — Pending Stage 0A
- [MiniMax-M3](docs/vllm-ascend-performance/models/minimax-m3/STATUS.md) — Pending Stage 0A

### Tasks
- [Stage 0A Environment Discovery Task](docs/vllm-ascend-performance/tasks/VLLM-ASCEND-STAGE0A-ENVIRONMENT-DISCOVERY.md)
- [Stage 0A A3PerfRunner Prompt](docs/vllm-ascend-performance/tasks/CODEX2-VLLM-ASCEND-STAGE0A-DISPATCH-PROMPT.md)
- [Stage 0B Model Discovery Task](docs/vllm-ascend-performance/tasks/VLLM-ASCEND-STAGE0B-MODEL-DISCOVERY.md)

## Lifecycle

```text
User Decision -> PerfControl Formal Task -> explicit User dispatch
-> A3PerfRunner server Evidence -> immutable Result
-> PerfControl Formal Review -> ACCEPTED / REJECTED / NEEDS-FOLLOWUP
```

An accepted result freezes model identity, quantization, runtime/image, versions, CANN/PyTorch stack, hardware, parallelism, launch configuration, benchmark cells, raw metrics, normalized targets, and Evidence pointers.

## Current Model Scope

**Project Model Pool:** GLM-5.2-W8A8, DeepSeek-V4-Flash-W8A8, DeepSeek-V4-Pro-W8A8, MiniMax-M3.

**Current Single-A3 candidates:** GLM-5.2-W8A8, DeepSeek-V4-Flash-W8A8, MiniMax-M3 on one Ascend A3/910C server (8 cards / 16 NPU chips). DeepSeek-V4-Pro-W8A8 remains a `MULTI_NODE_CANDIDATE / NOT_SINGLE_A3_CANDIDATE` and is not part of the current Stage 0 execution scope.

## GLM-5.2-W8A8 Execution Mode

**USER-VERIFIED KNOWN-GOOD BASELINE** (Decision D-019): GLM uses frozen User-verified baseline artifacts (vLLM 0.24, TP16, graph mode, container/launch commands, benchmark scripts). Stage 0 discovery is not required for GLM baseline performance work. Execution mode: Fast Preflight → Run Frozen Commands → Evidence → Result → Optimization.

Stage 0 capability is retained for new servers, new hardware, unknown runtimes, and unverified models (DeepSeek, MiniMax).
