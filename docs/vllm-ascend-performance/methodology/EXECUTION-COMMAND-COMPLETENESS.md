# Execution Command Completeness Policy

From Stage 1 onward, every formal Task that permits A3PerfRunner to perform a server operation must contain complete, directly executable commands. Abstract instructions such as “pull image”, “create container”, “launch model”, “run smoke test”, “run benchmark”, or “optimize and retest” are insufficient without the actual command, resolved identity, paths, parameters, logging, readiness checks, and cleanup.

## Required command coverage

- **Stage 1 Runtime Preparation:** exact image/tag/digest, `docker pull` if approved, complete `docker run`, fixed container name, mounts/devices, preparation commands, and post-create verification.
- **Stage 2 Model Launch / Load:** exact container, model path, environment, vLLM command, TP/DP/EP, quantization, model length, cache/MTP/graph/eager settings, ports, served name, log path, readiness check, stop and cleanup.
- **Stage 3 Functional Smoke:** exact endpoint, request/API command, model name, prompt, output requirement, timeout, expected HTTP/result criteria, evidence capture, and cleanup.
- **Stage 4 Performance Baseline:** complete `vllm bench serve` command for each cell, including backend, base URL, endpoint, model/tokenizer, dataset, input/output lengths, prompts, concurrency, request rate, sampling, `ignore_eos`, warm-up, repeats, aggregation, timeout, and raw output path. Every 1K/4K/16K/64K cell must have a resolved command or deterministic generator.
- **Stage 5 Optimization / Retest:** changed parameters, preserved baseline identity, complete retest command, and new Task/Result identity; never overwrite a Stage 4 Result.
- **Stage 6 Formal Acceptance:** no server command required; PerfControl reviews immutable Result/Evidence.

**Model-specific note**: GLM-5.2-W8A8 frozen commands are in `models/glm-5.2-w8a8/RUNBOOK.md` and `scripts/` (per D-019).

All command-bearing Tasks must bind exact Control SHA, Task/prompt path, runtime track, and Evidence path. Stateful actions remain separately authorized by User.
