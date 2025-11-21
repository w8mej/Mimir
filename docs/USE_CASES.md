# Mimir Use Cases

This document outlines the primary use cases for the Mimir project, a Confidential Federated Autoregressive Inference system. It is intended for management review to understand the system's capabilities and workflows.

## Overview

Mimir enables multiple mutually distrustful parties to collaboratively perform inference on a shared machine learning model without revealing their private inputs (prompts) or the model's proprietary weights. It leverages Secure Multiparty Computation (MPC) and Trusted Execution Environments (TEEs) to guarantee privacy and integrity.

## Actors

| Actor | Description |
| :--- | :--- |
| **Client** | The entity initiating an inference request with a private prompt. |
| **Coordinator** | The central service that manages sessions, verifies attestations, and orchestrates the MPC nodes. |
| **MPC Node** | A compute node (running in a TEE) that holds a share of the model and participates in the secure computation. |
| **Administrator** | The individual responsible for deploying the infrastructure and defining security policies. |

## Use Cases

### 1. Secure Autoregressive Inference

**Goal**: Perform text generation on a shared model without exposing the prompt or model weights.

**Actors**: Client, Coordinator, MPC Nodes

**Preconditions**:
- MPC Nodes are registered and attested.
- A session has been created.

**Flow**:
1.  **Submission**: The Client secret-shares their prompt and submits the shares to the MPC Nodes via the Coordinator.
2.  **Computation**: The MPC Nodes collaboratively compute the next token using the shared model and the shared prompt.
    -   *Note*: All operations (matrix multiplications, activations) are performed on encrypted shares.
3.  **Output**: The resulting token is reconstructed and sent back to the Client (or kept shared for the next step).
4.  **Iteration**: Steps 2-3 are repeated for the desired number of tokens.

**Postconditions**:
- The Client receives the generated text.
- No single party learns the full prompt or model weights.

### 2. Confidential Party Registration

**Goal**: Add a new compute node to the network in a secure, verifiable manner.

**Actors**: MPC Node, Coordinator

**Preconditions**:
- The MPC Node is running within a supported TEE (AWS Nitro Enclave or OCI Confidential VM).

**Flow**:
1.  **Attestation**: The MPC Node generates a hardware attestation quote (SEV-SNP or TDX) proving its identity and code integrity.
2.  **Request**: The Node sends a registration request to the Coordinator, including the attestation quote.
3.  **Verification**: The Coordinator verifies the quote against the defined security policy (e.g., checking measurement OIDs).
4.  **Admission**: If valid, the Coordinator issues a short-lived TLS certificate to the Node.

**Postconditions**:
- The MPC Node is authenticated and authorized to participate in MPC sessions.
- Communication channels are secured via mTLS.

### 3. Session Management

**Goal**: Organize MPC computations into isolated sessions.

**Actors**: Client, Coordinator

**Preconditions**:
- Coordinator is running.

**Flow**:
1.  **Creation**: The Client requests a new session, specifying the model and parameters (e.g., ring size).
2.  **Allocation**: The Coordinator allocates resources and assigns MPC Nodes to the session.
3.  **Initialization**: The Coordinator initializes the session state (e.g., triple pools) on the assigned nodes.

**Postconditions**:
- A unique Session ID is generated.
- Resources are reserved for the inference task.

### 4. Infrastructure Deployment

**Goal**: Deploy the secure infrastructure on public cloud providers.

**Actors**: Administrator

**Preconditions**:
- Cloud provider credentials (AWS or OCI) are configured.
- Terraform is installed.

**Flow**:
1.  **Configuration**: The Administrator configures the Terraform variables (region, instance type, etc.).
2.  **Provisioning**: The Administrator runs `terraform apply` to create the resources (VPCs, subnets, Enclaves/VMs).
3.  **Bootstrapping**: The instances boot up, decrypt keys via KMS, and start the MPC services.

**Postconditions**:
- The Mimir network is up and ready to accept connections.

## Non-Functional Requirements

-   **Privacy**: Inputs and weights must remain confidential throughout the computation.
-   **Integrity**: Malicious behavior by any party should be detected (via MACs and Attestation).
-   **Availability**: The system should be resilient to node failures (future work).
