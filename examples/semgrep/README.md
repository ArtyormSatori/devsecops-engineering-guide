# Custom Semgrep rules

**Writing rules is the highest-value SAST skill there is.** Almost everyone runs somebody else's rules; very few people write their own, and the bugs that actually get exploited in your application are the ones only your rules can find.

The reason is structural. A registry rule can spot `eval(userInput)` because that pattern is wrong in every codebase on earth. It cannot spot a query missing your tenancy filter, because correct and incorrect code are **syntactically identical** — the only difference is a convention that exists in your team's heads. That gap is where broken access control lives, and broken access control is the most common serious vulnerability class in real applications.

This directory is a working example of closing that gap: rules, test cases for both directions, and CI that runs them.

```bash
semgrep --test --config rules/                 # run the tests (11 cases, all passing)
semgrep --config rules/ path/to/your/code      # run against real code
semgrep --config rules/ --sarif -o results.sarif .
```

---

## What is here

| File | |
|---|---|
| [`rules/python-security.yaml`](rules/python-security.yaml) | 6 Python rules |
| [`rules/python-security.py`](rules/python-security.py) | Test cases for them |
| [`rules/javascript-security.yaml`](rules/javascript-security.yaml) | 5 JavaScript/TypeScript rules |
| [`rules/javascript-security.js`](rules/javascript-security.js) | Test cases for them |

| Rule | Catches |
|---|---|
| `orm-query-missing-tenant-scope` · `js-mongo-query-missing-tenant-scope` | Multi-tenant data leaks through unscoped queries |
| `jwt-signature-not-verified` · `js-jwt-decoded-without-verification` | Tokens trusted without checking the signature |
| `tls-verification-disabled` · `js-tls-verification-disabled` | Debug workarounds that shipped |
| `subprocess-shell-true-with-interpolation` · `js-command-injection-via-interpolation` | Command injection |
| `secret-passed-as-cli-argument` | Credentials visible in `ps` and audit logs |
| `unsafe-deserialisation` | Pickle/YAML loading as remote code execution |
| `js-timing-unsafe-secret-comparison` | Signature comparison that leaks the signature |

---

## How the tests work

Semgrep pairs a rule file with a test file of the same basename in the same directory — `python-security.yaml` with `python-security.py`. Annotations sit on the line immediately above the code:

| Annotation | Meaning |
|---|---|
| `ruleid: <id>` | This line **must** be flagged — guards against false negatives |
| `ok: <id>` | This line must **not** be flagged — guards against false positives |
| `todoruleid: <id>` | Known gap, does not fail the build |
| `todook: <id>` | Known false positive, does not fail the build |

**Write the `ok` cases first.** A rule with only positive tests is a rule that flags everything and passes its own test suite — and the first person to hit twenty false positives will turn it off for the whole organisation. The negative cases are what make a rule deployable.

---

## Writing your own

The workflow that produces useful rules, in order:

1. **Start from a real bug.** A rule written from an incident, a code review comment, or a post-mortem finds real problems. A rule written from a blog post finds test fixtures.
2. **Write the failing test first**, then make the rule catch it.
3. **Write the passing test**, then make the rule stop flagging it. This step is where most of the design work happens.
4. **Run it against a large open-source codebase in your language** and read every hit. Measure the false positive rate before you inflict it on anyone.
5. **Ship at the right severity.** `WARNING` and a comment, not `ERROR` and a blocked merge, until the rate is known.

Useful mechanics:

- `pattern-not-regex` — the cheap way to express "unless it mentions the tenant column". Crude, but it works, and it is honest about being a convention check.
- `metavariable-regex` — match on a *name*, e.g. only variables ending in `token` or `secret`.
- `metavariable-pattern` — match on the *structure* of what a metavariable captured.
- `pattern-inside` / `pattern-not-inside` — scope a rule to a decorator, a class, or a handler.
- `taint` mode — for source-to-sink dataflow when a syntactic pattern is not enough.
- `semgrep --dump-ast --lang python file.py` — when a pattern will not match, look at what Semgrep actually sees.

> Ship five rules with a measured false positive rate. Not fifty with an unmeasured one. The second option produces exactly one outcome: `# nosemgrep` everywhere.

## Tuning the two tenant-scoping rules

They ship at `LOW` confidence deliberately, because they are the only rules here that depend on your codebase's conventions rather than on a language feature. Before enabling them:

1. Change the `pattern-not-regex` to your actual scoping column (`tenant_id`, `workspace_id`, `account_id` — whatever yours is).
2. Add your ORM's real call shapes to the `pattern-either` block.
3. Run against your codebase and count the hits. If there are hundreds, the right fix is usually **not** a better rule — it is a scoped session or repository layer that makes the unsafe query hard to write, plus a rule that flags the raw session when someone bypasses it.

That last point generalises. The best outcome of writing a rule is often discovering an API that would make the rule unnecessary.

---

## Running in CI

Rules in this directory are tested on every PR by [`.github/workflows/validate-examples.yml`](../../.github/workflows/validate-examples.yml). If you take one thing from this example, take that: **your rules are code, and untested code rots.**

For scanning an application rather than testing rules:

```yaml
- name: Semgrep
  run: |
    semgrep scan \
      --config ./semgrep-rules \
      --config p/default \
      --sarif --output semgrep.sarif \
      --baseline-commit "$(git merge-base origin/main HEAD)"
```

`--baseline-commit` is the flag that makes adoption survivable: it reports only findings **introduced by this PR**, so you can turn the rules on today rather than after a six-month backlog cleanup. Upload the SARIF to one aggregation point rather than reading it in the job log.

---

## See also

- [P3 in the projects list](../../projects/README.md) — the portfolio version of this, with a measured false positive rate
- [`checklists/secure-code-review.md`](../../checklists/secure-code-review.md) — what to look for by hand
- [Semgrep rule syntax](https://semgrep.dev/docs/writing-rules/rule-syntax) · [Testing rules](https://semgrep.dev/docs/writing-rules/testing-rules) · [semgrep-rules](https://github.com/semgrep/semgrep-rules) for prior art
