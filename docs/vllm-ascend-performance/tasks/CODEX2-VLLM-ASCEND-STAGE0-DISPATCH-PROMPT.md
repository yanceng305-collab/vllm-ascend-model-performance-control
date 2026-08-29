# Codex2 Dispatch Prompt: Stage 0 Server Fact Acquisition

You are Codex2 executing `VLLM-ASCEND-STAGE0-SERVER-FACT-ACQUISITION` for Control repo `https://github.com/yanceng305-collab/vllm-ascend-model-performance-control`.

## Control binding and drift gate

- Task ID: `VLLM-ASCEND-STAGE0-SERVER-FACT-ACQUISITION`
- Task path: `docs/vllm-ascend-performance/tasks/VLLM-ASCEND-STAGE0-SERVER-FACT-ACQUISITION.md`
- Prompt path: `docs/vllm-ascend-performance/tasks/CODEX2-VLLM-ASCEND-STAGE0-DISPATCH-PROMPT.md`
- Control baseline before this revision: `17672b16f665f74ff6ad45ab344a8054fc75dc9b` (lineage anchor; the exact prompt artifact is the committed file at the current Control SHA verified below)
- Prompt artifact commit: the commit returned by `git log -1 --format=%H -- docs/vllm-ascend-performance/tasks/CODEX2-VLLM-ASCEND-STAGE0-DISPATCH-PROMPT.md` after fetching `main`; this is the prompt's authoritative Control SHA.
- Formal artifact rule: this Markdown file committed in the Control repo is the authoritative handoff; terminal text is not a substitute.

At execution start, live query or fetch the Control repo and verify the current `main` HEAD, this prompt path, and the Task path. The current HEAD is the prompt's Control binding; record it as `CONTROL_SHA_VERIFIED` in Evidence and the immutable Result. Confirm that the prompt and Task still have the same scope and safety boundary. If the checked-out files differ from this committed artifact, or a newer HEAD changes the Task/prompt scope, report drift and STOP; do not silently execute an old artifact. The pre-revision SHA above is only the lineage anchor and must not be used as the execution SHA.

This prompt is dispatch-ready but is not authorization by itself. Execute only after the User explicitly dispatches this exact committed prompt and Task. Then execute only the read-only, non-destructive discovery below. Do not run a model service or benchmark. Do not install, uninstall, upgrade, rebuild, pull, modify, or delete anything.

## Scope and lane

Hardware target: one Ascend A3/910C server with 8 cards / 16 NPU chips.

Models in scope: `glm-5.2-w8a8`, `deepseek-v4-flash-w8a8`, and `minimax-m3`.

`deepseek-v4-pro-w8a8` remains a project-pool `MULTI_NODE_CANDIDATE / NOT_SINGLE_A3_CANDIDATE` and is explicitly out of scope for this run.

Target lane: `FLAGOS_ALIGNED`, defined by FlagOS `release/0.2`, vLLM `0.20.2`, vLLM-Ascend `0.20.2rc1`, Python >=3.10,<3.12, CANN 9.0.0, PyTorch/torch_npu 2.10.0/2.10.0, Triton Ascend 3.2.1, Mooncake v0.3.8.post1. Newer versions, if observed, are facts only and must be labeled `LATEST_REFERENCE / NON_FLAGOS_ALIGNED_REFERENCE`.

## Allowed probes

Read files/configs; query `npu-smi`, `docker inspect`, package/version metadata, Python read-only imports/introspection, model directories and hashes, vLLM/vLLM-Ascend registries, architecture recognition, device/topology/HBM/network/OS/kernel/HCCL facts, and supported launch flags. Capture exact commands, timestamps, stdout/stderr, and exit codes.

## Required answers

For hardware/runtime: SKU, NPU count, driver, firmware, HBM, topology, OS/kernel, Python, CANN, torch, torch_npu, vLLM, vLLM-Ascend, Triton Ascend, HCCL, Mooncake, image/container ID/digest, and whether the exact aligned tuple exists.

For each in-scope model: actual path, config, architecture, revision/SHA, file hashes, quantization method/config, dtype, KV-cache dtype, tokenizer, availability, registry recognition, import/module/source origins, exact capability errors, and supported TP/DP/EP/launch flags discoverable without launching. For MiniMax-M3 explicitly determine whether the actual downloaded variant is BF16, W8A8, or another quantization and whether static 16-NPU capacity is plausible from read-only facts.

Assign one status per in-scope model: `READY`, `BLOCKED_RUNTIME`, `BLOCKED_MODEL_SUPPORT`, `BLOCKED_QUANTIZATION`, `BLOCKED_MISSING_MODEL`, or `BLOCKED_UNKNOWN`. State the next eligible stage and distinguish server facts from User decisions. Do not assign a Stage 0 disposition to DeepSeek-V4-Pro.

## Prohibited

No package or system changes, no driver/CANN changes, no model edits, no image pull/rebuild/commit, no service launch, no benchmark, and no long-running workload. Stop and report if a requested fact requires a prohibited action.

## Evidence root and run ID

First inspect read-only whether a project evidence workspace already exists. If one is clearly discoverable, use it and record the path-selection evidence. Otherwise use `/tmp/vllm-ascend-model-performance-control/evidence`. Generate the run ID automatically at execution start as a UTC timestamp in `YYYYMMDDTHHMMSSZ` form. Create the run directory under `VLLM-ASCEND-STAGE0-SERVER-FACT-ACQUISITION/YYYYMMDDTHHMMSSZ`, replacing the final component with the generated timestamp, without overwriting another run. Do not ask the User to choose or replace a path or ID.

## Evidence and immutable Result

The run directory must contain a manifest, verified Control SHA, exact commands, timestamps, logs, inventories, probes, and checksums. Publish one immutable `RESULT-*.md` to the Control repo after execution. Do not include credentials or secrets. Do not rewrite the Result after publication; use a supplement for corrections. Do not create a performance Result or claim PASS/FAIL.
