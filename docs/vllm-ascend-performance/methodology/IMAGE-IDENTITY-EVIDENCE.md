# vLLM-Ascend 0.20.2rc1 Image Identity Evidence

Public GitHub facts queried 2026-08-29:

- Release: https://github.com/vllm-project/vllm-ascend/releases/tag/v0.20.2rc1
- Tag commit: `367b8e62da799870a7476ce34f5f7658589a8aad`
- Official image workflow: https://github.com/vllm-project/vllm-ascend/blob/v0.20.2rc1/.github/workflows/schedule_image_build_and_push.yaml
- Workflow defines A3 carriers `Dockerfile.a3` (Ubuntu) and `Dockerfile.a3.openEuler` (openEuler), with suffixes `a3` and `a3-openeuler`; tag-triggered publishing uses the release version pattern.
- Repository root at the tag contains `Dockerfile.a3`, `Dockerfile.a3.openEuler`, `Dockerfile`, and `Dockerfile.openEuler`.
- Release notes state the matched vLLM baseline is 0.20.2 and the aligned CANN/Triton/PyTorch/torch_npu tuple is 9.0.0 / 3.2.1 / 2.10.0 / 2.10.0.

The public release API exposes no image asset or digest for this tag. Therefore no final image tag/digest is frozen by this Control revision. Stage 0A must inspect local image inventory and host compatibility. Final Stage 1 image selection requires the official carrier evidence above plus server evidence; if no directly usable aligned A3 image exists, record `NO_DIRECT_ALIGNED_IMAGE` and create a separate authorized preparation Task rather than silently switching versions.
