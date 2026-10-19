# Contributing

Thanks for your interest in `ke-designated-facility-ems`.

This is a **simulation-first** reference project. Nothing here is deployed, there are no pilots or partners, and every number is simulated unless a source is cited. Please keep contributions consistent with that.

## What helps right now

- **Reproduce the stack on another setup** (other OS, other CPU, `arm64`). Tell us what worked and what did not. `arm64` is untested.
- **Correct a fact or a citation.** Use the "Data correction" issue form and include the source URL and the date you read it.
- **Report a bug** in the compose stack, the seed files, the smoke test or the runbook.
- **Review the docs** (`docs/runbook.md`, `docs/adr/`) for errors, gaps or unclear wording.

## Running and testing locally

Follow `docs/runbook.md`. To check that the stack is healthy, run the smoke test from the repository root:

```bash
sudo bash deploy/smoke-test.sh
```

Exit code 0 means all checks passed, 1 means a check failed, 2 means a usage or configuration problem. The smoke test never asserts simulated values.

## Evidence rules

- Cite a source and a retrieval date for every number, regulation or licence statement. If you cannot, say it is an assumption.
- If two sources disagree, report the conflict instead of picking one.
- Do not commit secrets, credentials or personal data. Settings belong in config files; secrets belong in environment variables.
- Do not claim deployments, pilots, partners, users or certificates.
- Do not copy OpenEMS code into this repository. OpenEMS is run unmodified from upstream images under its own licence.
- Pin versions (images by digest) and seed all randomness.

## Making a change

1. Open an issue first for anything larger than a typo, so we can agree on scope.
2. Keep changes small and focused: one purpose per pull request.
3. Use [Conventional Commits](https://www.conventionalcommits.org/) for messages, for example `docs: fix runbook step 4` or `fix: handle empty log in smoke test`.
4. Explain how you validated the change.

## Out of scope for v0.1

Utility APIs, authentication, multi-site support, real hardware, billing, M-Pesa and a custom dashboard. Such requests will be closed as out of scope for now, not as a judgement on their merit.

## Licence

By contributing you agree that your contribution is licensed under the MIT licence in `LICENSE`.

## Expectations

This is a small project. There is no promised review time. Participation is covered by the [Code of Conduct](CODE_OF_CONDUCT.md); security reports go through the [Security Policy](SECURITY.md).
