# ADR-004: HIPAA Compliance Architecture

**Status:** Accepted
**Date:** 2026-04-01
**Deciders:** SunShift Architecture Team

---

## Context

SunShift's target market includes three healthcare-adjacent segments in Tampa Bay:

- **Dental practices** (avg 3–8 employees)
- **Chiropractic clinics** (avg 2–6 employees)
- **Independent medical billing offices** (avg 5–15 employees)

User research (N=47 SMB interviews) shows healthcare contacts have the highest
willingness-to-pay: **$300–500/month** vs. $99–199/month for law or accounting firms.
Healthcare is also the segment most acutely aware of hurricane risk — patient records,
billing data, and scheduling systems are all subject to HIPAA, and a disaster that
destroys on-prem records without a compliant backup triggers both HIPAA breach
notification obligations and potential fines.

### Regulatory Stakes

HIPAA violation fines under HHS Office for Civil Rights (OCR):
- Unknowing violation: **$100–$50,000 per violation**
- Reasonable cause: **$1,000–$100,000 per violation**
- Willful neglect (corrected): **$10,000–$250,000 per violation**
- Willful neglect (uncorrected): **$50,000–$1,900,000 per violation**

A single breach event involving a covered entity (CE) using SunShift could trigger
multi-violation findings if the infrastructure is non-compliant. SunShift must be able
to serve as a HIPAA-compliant Business Associate (BA) with a valid Business Associate
Agreement (BAA) in place.

### Options Considered

| Option | Description | HIPAA-Viable | Cost |
|---|---|---|---|
| No encryption, shared KMS | S3 default encryption, no per-customer keys | No | Minimal |
| AWS-managed keys only | SSE-S3 or SSE-KMS with AWS-managed keys | Borderline | Low |
| **Triple encryption + CMK (chosen)** | AES-256 at rest + TLS 1.3 in transit + client-side AES-256-GCM | Yes | ~$1/key/month |
| HSM-based key management | CloudHSM per customer | Yes (over-engineered) | $1,500/month |

CloudHSM is designed for financial institutions and enterprises; it is economically
unviable at SMB pricing. The triple-encryption + CMK path provides genuine HIPAA
compliance at a cost that fits within the $300–500/month pricing tier.

---

## Decision

We implement **triple encryption with per-customer Customer Master Keys (CMKs)**, plus
immutable audit logging and IAM least-privilege access control.

### Encryption Architecture

| Layer | Method | Key Management | Where Enforced |
|---|---|---|---|
| At rest (S3) | AES-256 via AWS KMS SSE-KMS | Per-customer CMK (~$1/key/mo) | S3 bucket policy requires SSE-KMS |
| In transit | TLS 1.3 | AWS Certificate Manager (auto-renew) | ALB + API Gateway enforce TLS minimum |
| Client-side (agent) | AES-256-GCM | Agent-managed, customer master key | On-prem Python agent encrypts before upload |

Client-side encryption means that data leaving the customer's premises is already
encrypted with a key only the customer controls. AWS never receives plaintext ePHI.
Even a KMS key compromise at the cloud layer does not expose the underlying data.

### Audit Logging

HIPAA requires audit controls (§164.312(b)). SunShift implements:

- **S3 Object Lock (WORM):** Audit logs written to a dedicated S3 bucket with
  Object Lock in Compliance mode, 7-year retention (meets HIPAA minimum of 6 years
  for business records)
- **CloudTrail:** All AWS API calls logged to a separate account-level trail with
  S3 data event logging enabled for ePHI buckets
- **Application audit log:** Every data access, encryption operation, and key rotation
  event is written to a structured JSON log with ISO 8601 timestamps and actor identity

Log schema:
```json
{
  "timestamp": "2026-04-01T14:23:11Z",
  "event_type": "DATA_UPLOAD",
  "actor": "agent:customer-id-abc123",
  "resource": "s3://sunshift-hipaa-prod/abc123/backup-20260401.enc",
  "encryption_key_id": "arn:aws:kms:us-east-2:123456789:key/...",
  "result": "SUCCESS",
  "bytes_transferred": 2147483648
}
```

### IAM Least-Privilege

- Each customer's on-prem agent receives a dedicated IAM role with S3 permissions
  scoped to only their bucket prefix (`s3:PutObject`, `s3:GetObject` on
  `arn:aws:s3:::sunshift-hipaa-prod/{customer-id}/*`)
- No cross-customer bucket access is possible at the IAM policy level
- KMS key policy restricts decryption to the customer's IAM role only
- No wildcard (`*`) resource policies exist in any HIPAA-tier IAM document

### BAA

AWS offers a HIPAA BAA covering S3, KMS, Lambda, CloudTrail, and CloudWatch Logs
in us-east-2. SunShift signs this BAA at the AWS account level before onboarding any
healthcare customer. SunShift in turn executes a BAA with each healthcare customer
before their data touches SunShift infrastructure.

---

## Consequences

### Positive

- **Unlocks highest-WTP segment:** Healthcare customers at $300–500/month represent
  3–5x the revenue per customer vs. general SMB tier
- **Genuine compliance:** Triple encryption + CMK + WORM audit logs satisfies all five
  HIPAA Security Rule safeguard categories
- **Competitive barrier:** Most SMB-focused backup solutions do not offer per-customer
  CMK isolation; this is a defensible differentiator
- **Insurance-grade audit trail:** Object Lock WORM logs provide evidence in the event
  of OCR audit or customer-side breach investigation

### Negative

- **Operational complexity:** Per-customer CMK provisioning adds an onboarding step
  that must be automated (Terraform module). Manual provisioning does not scale.
- **KMS cost:** At $1/key/month, a 100-customer healthcare cohort adds $100/month in
  KMS key charges. This must be factored into healthcare tier pricing.
- **Key rotation responsibility:** HIPAA recommends annual key rotation. Automated
  rotation via KMS annual rotation policy is enabled by default; customer must be
  notified of rotation events (triggers re-encryption of at-rest data).
- **Client-side encryption complexity:** The on-prem Python agent must correctly
  implement AES-256-GCM with authenticated encryption. Any implementation error in the
  agent could silently corrupt data before upload. Mitigation: NIST-validated
  cryptography library (`cryptography` Python package, FIPS 140-2 validated backend).

### Risks

| Risk | Mitigation |
|---|---|
| Customer loses their master key | Key escrow option: customer can deposit key recovery material in AWS Secrets Manager under their own account |
| OCR audit demands log integrity proof | S3 Object Lock Compliance mode prevents log deletion even by root account |
| Agent sends plaintext due to encryption bug | Integration test suite validates ciphertext is never plaintext; automated check on upload |
| BAA not in place before data transfer | Onboarding workflow gates data transfer behind BAA signature confirmation |

### Accepted Tradeoffs

We accept the $100/month KMS overhead at scale and the per-customer CMK provisioning
complexity because the healthcare segment's $300–500/month WTP more than offsets these
costs, and because shipping a non-compliant product into the HIPAA segment is not an
option — the liability exposure dwarfs the operational cost of doing it correctly.
