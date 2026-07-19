# VerifyAI Investigation Report

**Job ID:** test-job-12345
**Verdict:** FRAUDULENT
**Trust Score:** 24.0
**Confidence:** 33.1
**Recommended Action:** Delete and block.

## Reasoning Tree
- **Threat Agent** [CRITICAL]: Domain paypa1-security-update.xyz. attempts to imitate a known brand.
- **Threat Agent** [CRITICAL]: Upfront fee request (job scam indicator).
- **Source Agent** [HIGH]: Domain uses a TLD often associated with spam/fraud.
- **Source Agent** [HIGH]: Domain uses insecure HTTP connection.
- **Evidence Agent** [POSITIVE]: Contains structured contact info or numerical data.
- **Decision Agent (Veto)** [CRITICAL]: Automatic Veto Applied due to critical threat: Domain paypa1-security-update.xyz. attempts to imitate a known brand.
