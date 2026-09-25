# Security Policy

This repository contains documentation, checklists, and example configurations. It is not a running service, so the realistic issue classes are different from a typical software project.

## What to report

Please open an issue, or contact the maintainer privately via GitHub, for:

- **A link to a malicious or compromised resource.** Report this privately and urgently — a bad link in a widely-read roadmap is a real supply chain risk.
- **An example configuration that is insecure.** These files get copied into real pipelines. If one of them teaches a bad practice, that is a genuine bug and worth reporting.
- **Advice that is actively harmful** rather than merely outdated.

## What is not a vulnerability here

- A tool mentioned in the roadmap has a CVE — report that to the tool's maintainers
- A resource is outdated — open a normal issue or PR
- You disagree with a recommendation — open an issue, that is a healthy discussion

## Reporting privately

Use GitHub's [private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability) on this repository, or contact the maintainer through their GitHub profile.

Please include what the issue is, where it is, and why it matters. We will acknowledge within a few days.

## Example configurations

Everything under `examples/` is illustrative and intended to be reviewed and adapted, not copied blindly into production. Pins go stale, registry paths are placeholders, and policies need tuning for your environment. The README in that directory says the same thing more loudly.
