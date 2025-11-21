
# SECURITY / THREAT MODEL (MVP)

## Goals
- Demonstrate confidential inference workflows for autoregressive models.
- Preserve *input* and *model* privacy under honest-but-curious assumptions while enabling token-by-token generation.
- Provide hooks for auditability and future attestation.

## Assumptions
- **Honest-but-curious 3PC**: at most 1 colluding party among 3.
- Nodes run in controlled environments; containers provide namespacing but no strong isolation.
- RNGs are cryptographically strong when upgraded (current MVP uses NumPy RNGs).

## Assets
- **Inputs**: prompts/token IDs
- **Parameters**: model weights
- **Intermediates**: attention scores, activations, KV-cache
- **Outputs**: generated tokens

## Current MVP posture
- Secret sharing (replicated) for tensors and weights.
- Some intermediate opens for practicality (attention scores, V-context, softmax normalizer).
- KV cache stored **publicly** for demo. (Upgrade path: keep K/V secret-shared.)
- Transport security is not implemented in code (gRPC insecure channels for local dev).
- Prometheus metrics are non-sensitive counters/histograms only.

## Potential risks
- Information leakage via opened intermediates.
- Side channels through timing/size patterns if deployed cross-tenant.
- RNG predictability for sampling variants.

## Upgrade path
- Replace opens with masked reveals + Beaver-based secure matmuls for QKᵀ and AV.
- MACed shares (SPDZ) for malicious security; sacrifice checks for triples.
- mTLS between nodes + optional WireGuard overlay; pin container digests.
- Remote attestation (AMD SEV-SNP / Intel TDX) with quote verification in Coordinator.
- Differential Privacy at logits layer; configurable ε, clipping.
- Secret-shared KV cache with per-step garbage collection and transcript hashing.
