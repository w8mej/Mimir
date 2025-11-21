
# 🔐 Mimir: Confidential Federated Autoregressive Inference  
*FutureThoughts & Research Continuation Document*  

## Concept  
Mimir enables **multiple mutually distrustful parties** (e.g., hospitals, banks, or agencies) to cooperatively perform **autoregressive (AR) inference** over a shared model **without revealing**:  
- Their **input prompts** or private data.  
- The **model weights** or intermediate activations.  

This prototype demonstrates how **secure multiparty computation (MPC)**, **trusted execution environments (TEEs)**, and **federated inference** can coexist to support privacy-preserving text generation, predictive typing, or risk modeling.

---

## Current Implementation Summary (Strict PoC Features)

### 🔧 Core Privacy & MPC Layer
| Component | Description |
|------------|--------------|
| **Secret Sharing** | Additive replicated shares across three parties. |
| **Beaver Triples** | Precomputed for secure matrix multiplications with **sacrifice checks** and metrics. |
| **Fixed-Point Encoding** | 16-bit scale with signed 64-bit ring arithmetic. |
| **SPDZ-style MACs** | Message authentication codes applied to every open or reveal. |
| **HMAC-DRBG (SP 800-90A)** | Joint coin-tossing with commitments to derive shared randomness. |
| **Constant-Time C Kernels** | CFFI-compiled fixed-point multiplication and matmul ops for timing uniformity. |
| **Chebyshev exp (minimax)** | Degree-6 approximation for exp(x) on [-6, 6] replacing poly-exp; only masked sums are revealed. |
| **Softmax (MAC-verified masked LSE)** | Secure log-sum-exp with no plaintext logits. |

---

### 🧩 Model & Federated Inference
- **Two-layer Transformer** with secure attention and MLP.  
- **Secret-shared KV-cache** persists across steps for AR efficiency.  
- Deterministic **step-by-step generation** over secret-shared tokens.  
- **Tiny tokenizer** for repeatable E2E inference.  

---

### 🔐 Trust & Transport
| Layer | Mechanism |
|--------|-----------|
| **TEE Attestation** | SEV-SNP / TDX quote verification and policy-based measurement admission. |
| **mTLS** | Certificates bound to attested measurements (OID extension). |
| **WireGuard Overlay** | Auto-peering, key rotation, and health-checked tunnels between nodes. |
| **Enclave Boot Path** | KMS decrypt → attested TLS → gRPC secure coordinator startup. |

---

### 🧱 Infrastructure
- **Docker Compose** spins up coordinator, triples service, Prometheus, and Grafana.  
- **Terraform** stacks for:
  - AWS Nitro Enclaves (parent + vsock KMS proxy)  
  - OCI Confidential VMs  
- **GitHub Actions**:
  - Builds & pushes Docker images (GHCR/ECR/OCIR).  
  - Builds Nitro EIFs and uploads to S3.  
  - Generates SBOMs and publishes artifacts.  
- **Prometheus + Grafana** visualize metrics and triple-pool health.  

---

## 📊 Security, Performance & Verification Notes

| Domain | Current State | Future Direction |
|---------|----------------|------------------|
| **Leakage** | Only masked sums revealed; sizes still leak sequence length. | Pad or bucket sequences to equal length. |
| **Integrity** | SPDZ MACs verified on all opens. | Add zero-knowledge range proofs for correctness. |
| **Side Channels** | Timing mitigated via CT loops; Python layers remain variable-time. | Port arithmetic to C / WASM; integrate dudect tests. |
| **Attestation** | Stubs for SNP/TDX verification. | Integrate official AMD & Intel libs + CA chain validation. |
| **Transport** | mTLS and WireGuard functional. | Automate rotation & revocation with Consul / SPIRE. |
| **Scalability** | 3-party prototype. | Extend to N > 3 parties using SPDZ-2k or BMR shares. |
| **Benchmarking** | Synthetic timing harness. | Add end-to-end throughput + latency dashboards. |

---

## 🧭 Next Research Milestones
1. **Federated-MPC Hybrid**: blend secure aggregation (federated style) with MPC runtime to simulate real institutions.  
2. **Differential Privacy on Outputs**: bound leakage by adding noise calibrated to model entropy.  
3. **Homomorphic Fallback**: integrate partial HE (CKKS) for scalar operations.  
4. **Formal Verification**: SMT-based proofs for fixed-point wraparound and MAC soundness.  
5. **Adaptive Key Management**: use distributed KMS / Threshold KMS to seed DRBGs and decrypt enclaves collaboratively.  
6. **Visualization**: entropy maps and leakage bounds rendered in Grafana for educational demonstration.  

---

## 🕓 Roadmap (Projected)

| Quarter | Milestone | Summary |
|----------|------------|----------|
| **Q1 2026** | ✅ Core Mimir Prototype | Fixed-point MPC, Beaver triples, SPDZ MACs, softmax masking, gRPC, enclave boot. |
| **Q2 2026** | 🔒 Secure Federated Extension | Simulate N>3 nodes; add federated aggregation overlay with MPC sampling; test in AWS Nitro + OCI. |
| **Q3 2026** | ⚙️ Constant-Time Kernel Audit | Port MPC arithmetic to C/WASM with dudect testing and constant-time analysis. |
| **Q4 2026** | 🧠 Differential Privacy + Visualization | Integrate entropy-based privacy visualization and DP noise injection. |
| **Q1 2027** | 🧩 Formal Verification | Apply property-based testing and SMT proofs for MPC algebra and fixed-point rounding. |
| **Q2 2027** | 🔗 Distributed KMS / Policy Engine | Add multi-party KMS coordination, CA issuance, and revocation; integrate official SEV-SNP & TDX SDKs. |
| **Q3 2027** | 🌍 Pilot Deployment | Run cross-domain AR inference across sandboxed hospital or finance data clusters. |
| **Q4 2027** | 📜 Publication & Open Release | Release whitepaper, reference implementation, and academic benchmarks. |

---

## ⚠️ Caveats & Ethical Considerations
- This is **not production-secure**; cryptographic routines are for research.  
- Side-channel, timing, and memory-access uniformity need hardened implementations.  
- Attestation verification is **mocked** until tied into vendor SDKs.  
- No PHI/PII data should be used in testing environments.  
- Any deployment to regulated sectors (HIPAA, GLBA, GDPR) requires independent audit.  

---

## 🌐 Vision
*Mimir bridges federated learning and secure computation for real-world AI collaboration.*  
A future version could enable:  
- **Cross-institutional inference** without data sharing.  
- **Verifiable privacy guarantees** through MPC + DP fusion.  
- **Composable trust** between enclaves, MPC nodes, and auditors.  
