# Psilon

**Run any model on any machine.**

Psilon democratizes AI access for consumers. It removes the NVIDIA ecosystem
dependency from AI by porting PyTorch to open, standardized GPU APIs —
**Vulkan**, **DirectX 12**, and **WebGPU** — with performance that aims to
match or exceed CUDA on the same silicon. And with psiCache streaming,
frontier-scale models run *unmodified* on ordinary consumer gaming hardware by
orchestrating VRAM, CPU RAM, and NVMe as a unified cache hierarchy.

Website: **https://stjohnalex.github.io/psilon/**

## The first release: three pillars

### psiTorch — PyTorch on open GPU standards

A highly optimized PyTorch library and backend for Vulkan, DirectX 12, and
WebGPU. It keeps the PyTorch API surface, so existing models and code run
unchanged — `torch.device("vulkan")` works the way you'd expect. On targeted
AI-critical operators, the Vulkan port is often as fast or faster than CUDA on
the same hardware.

### psiCache — stream frontier models on consumer hardware

Streaming an AI model does **not** require quantizing or pruning it to fit in
limited VRAM. psiCache profiles a model at compile time, then adapts at run
time to whatever machine it lands on — streaming arbitrarily large models
through the GPU layer by layer, with prefetch running ahead of compute. The
entire model never needs to be resident in VRAM at once, so frontier models
run in their unmodified entirety on modest hardware. Streaming composes with
quantization when you want more speed — the choice is finally yours.

### Fused Hugging Face libraries

A family of the top Hugging Face AI Python libraries, fused and optimized to
perform better on **CUDA, Vulkan, DX12, and WebGPU** alike. High-overhead
Python paths are replaced with fused native GPU implementations, so the
ecosystem you already use gets faster on every backend — including CUDA.

## Downloads

Signed Windows builds are published on this repository's Releases page:

**https://github.com/stjohnalex/psilon/releases/latest**

Every release includes a `SHA256SUMS.txt` covering all assets — verify your
download before running anything. Mac and Linux builds are planned.

## Semi-opensource

Psilon is developed in an internal repository. Open-source components land
here as they are personally reviewed, and the downloadable binaries are
produced and signed by the internal build system. What you find in this
repository — site, docs, and released source — is everything that has been
deliberately published.

## Contact

- **Business contact**: [Alex St. John on LinkedIn](https://www.linkedin.com/in/alexstjohn/)
- **Demos and deep dives**: [youtube.com/@Playcastio](https://www.youtube.com/@Playcastio)
- **Playcast**: [playcast.io](https://playcast.io)

---

*psiTorch builds on PyTorch and remains compatible with the PyTorch API.
PyTorch is a trademark of The Linux Foundation. Hugging Face is a trademark of
Hugging Face, Inc.*
