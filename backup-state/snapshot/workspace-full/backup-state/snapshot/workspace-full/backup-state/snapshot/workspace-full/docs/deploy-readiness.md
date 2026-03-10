# Deployment Readiness — Preflight Checklist

Use this checklist before every production deployment using **GitHub + Cloudflare Pages**.

## 1) Repository & Branch Hygiene (GitHub)

- [ ] Default branch is correct (usually `main`) and protected.
- [ ] Deployment branch is explicitly defined (e.g., `main` only).
- [ ] All required status checks are passing (CI/lint/tests/build).
- [ ] No unresolved merge conflicts in the deployment branch.
- [ ] Release PR is reviewed and approved by required reviewers.
- [ ] Commit history is clean (no accidental debug commits, large binaries, or temp files).
- [ ] `.gitignore` includes local env files and build artifacts where appropriate.

## 2) Secrets & Token Hygiene (Security)

- [ ] No secrets in git history (`.env`, API keys, tokens, private keys, service-account JSON).
- [ ] Secret scanning is enabled (GitHub Advanced Security or equivalent scanner).
- [ ] Cloudflare API token is scoped minimally (least privilege; Pages/project-specific if possible).
- [ ] Cloudflare API token has expiration/rotation policy documented.
- [ ] GitHub Actions secrets are used (no plaintext tokens in workflows).
- [ ] Rotated/revoked any leaked or old tokens before deployment.
- [ ] Deploy logs do not print sensitive environment variables.

## 3) Visibility & Access Controls (Private/Public Settings)

- [ ] GitHub repository visibility is intentionally set (`private` or `public`) per policy.
- [ ] Branch protection rules are active (no force push, required reviews/checks).
- [ ] Cloudflare Pages project visibility/access is confirmed per policy.
- [ ] Custom domain DNS records point only to expected Cloudflare endpoints.
- [ ] Preview deployments are limited appropriately (especially for private/internal apps).
- [ ] Team/member access reviewed (remove stale collaborators and over-privileged roles).

## 4) Build & Runtime Configuration

- [ ] Cloudflare Pages build command is correct and reproducible.
- [ ] Output directory is correct (matches framework/build tool output).
- [ ] Node/runtime version is pinned and matches local/CI expectations.
- [ ] Required environment variables are set in Cloudflare (Production + Preview as needed).
- [ ] `NODE_ENV` / environment mode is set correctly for target deployment.
- [ ] Caching strategy is validated (asset hashing, immutable headers for static assets).
- [ ] Redirects/headers config is present and reviewed (`_redirects`, `_headers`, or config files).

## 5) Security Hardening Checks

- [ ] HTTPS enforced; no mixed-content warnings.
- [ ] Security headers configured (at minimum: HSTS, CSP, X-Content-Type-Options, Referrer-Policy, X-Frame-Options/frame-ancestors).
- [ ] CORS policy is explicit and minimal.
- [ ] Error pages do not leak stack traces/internal details.
- [ ] Dependency vulnerabilities checked and triaged (`npm audit`/SCA tool).
- [ ] Third-party scripts are reviewed and trusted; SRI used where feasible.

## 6) QA / Pre-Deploy Validation

- [ ] Fresh install + clean build succeeds locally (`npm ci && npm run build`).
- [ ] Automated tests pass (`npm test` and/or integration/e2e suite).
- [ ] Critical user flows validated on preview deployment.
- [ ] Cross-browser smoke test completed (at least Chromium + one alternate engine).
- [ ] Mobile responsiveness and key breakpoints verified.
- [ ] 404/500/error-state behavior tested.
- [ ] Performance sanity check done (Core Web Vitals/Lighthouse spot check).

## 7) Deploy Execution & Post-Deploy Verification

- [ ] Deployment triggered from approved commit/tag only.
- [ ] Deployment logs reviewed: no warnings/errors ignored.
- [ ] Production URL and custom domain return expected version.
- [ ] Cache purge/revalidation performed if required.
- [ ] Monitoring/analytics/alerts confirm healthy rollout.
- [ ] Rollback path is known and tested (previous good deployment available).

## 8) Sign-off

- [ ] Engineering owner sign-off
- [ ] QA sign-off
- [ ] Security sign-off (if required by policy)
- [ ] Stakeholder/product sign-off

---

## Quick Commands (optional)

```bash
# Check for accidentally tracked env/secrets
git ls-files | grep -E '(\.env|id_rsa|credentials|secret|token|key)'

# Review recent commits before deploy
git log --oneline -n 15

# Verify clean working tree before tagging/release
git status
```
