# Security Policy

## Scope

This repository is a **simulation-only development stack**. It is not deployed anywhere and must not be exposed to a network you do not control. The policy below reflects that.

## Supported versions

Only the latest commit on `main` is supported. There are no tagged releases yet.

## How to report a vulnerability

Use GitHub's **private vulnerability reporting**: open the repository's **Security** tab and choose **Report a vulnerability**. Please do not open a public issue with exploit details.

If you cannot see that button, open a public issue titled "Security contact request" with **no technical details**, and we will arrange another private route.

## What is in scope

- Secrets, tokens or credentials committed to the repository or its history.
- Ports published beyond loopback (`127.0.0.1`) by the compose stack.
- Flaws in the scripts (for example `deploy/smoke-test.sh`) such as unsafe handling of input or files.
- Unpinned or tampered image references.

## What is not in scope

- The documented OpenEMS default logins (Felix console and UI) on loopback in the development stack. This is a recorded, dev-only exception: see [ADR 0005](docs/adr/0005-dev-only-default-credentials-exception.md).
- Vulnerabilities in upstream OpenEMS, Docker or the operating system. Please report those to their own projects.
- Anything that requires running the stack on a public network contrary to the runbook.

## What to expect

This is a best-effort, volunteer project. There is no bug bounty and no guaranteed response time. We will acknowledge valid reports when we can and credit reporters if they wish.
