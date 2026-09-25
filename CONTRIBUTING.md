# Contributing

Thanks for helping improve this roadmap. It gets better with more eyes on it, and corrections are as valuable as additions.

---

## The most valuable contributions

Ranked by how much they help, not by how much work they are:

1. **Fixing something wrong** — an outdated version number, a superseded standard, a claim that is no longer true. These are the highest-value PRs and they are usually one line.
2. **Fixing a broken link** — link rot is constant.
3. **Adding a genuinely excellent resource** — see the bar below.
4. **Improving an explanation** — if a section confused you, it confuses others. Say so, or rewrite it.
5. **Adding a working example** — a policy, a pipeline snippet, a checklist item that caught something real.
6. **Translations** — open an issue first so we can agree on structure.

---

## The bar for adding a resource

A resource gets added if it meets **all** of these:

- [ ] **Directly relevant** to a DevSecOps engineer's actual work
- [ ] **High quality** — you have personally read, watched, or used it
- [ ] **Current** — not describing a tool version or standard that has moved on
- [ ] **Accessible** — free preferred; paid resources must be clearly marked and genuinely worth it
- [ ] **Not redundant** — it teaches something the existing entries do not

A resource is **rejected** if:

- ❌ It is an affiliate link, or your own commercial product without disclosure
- ❌ It is vendor marketing dressed as education (a "guide" that ends in a demo request)
- ❌ It is SEO content that restates the OWASP Top 10 with no added insight
- ❌ It is a certification mill or a paid bootcamp promising employment
- ❌ It requires an account merely to see whether it is useful

> **Disclosure rule:** if you have any commercial relationship with a resource you are adding — you work there, you get paid for referrals, it is your own product — say so in the PR description. Disclosed conflicts are usually fine. Undisclosed ones get the PR closed.

---

## Style

Match the surrounding text.

- **Explain why, not just what.** "Use cosign to sign images" is less useful than "signing proves provenance; the value is entirely in verifying it at admission."
- **Be specific.** Name tools, versions, standards, and CVEs. Vague advice helps nobody.
- **Be honest about trade-offs.** No tool is universally best. Say what something is bad at.
- **Keep the resource format consistent:**
  ```markdown
  - [Resource name](https://url) — short reason it is worth your time <sup>FREE</sup>
  ```
  Tags: `FREE`, `PAID`, `OSS`, `BOOK`, or combinations like `FREE BOOK`.
- **No hype.** "Revolutionary", "game-changing", and "military-grade" all get edited out.
- **British or American spelling both fine** — just be internally consistent within a file.

---

## Making a change

```bash
# 1. Fork and clone
git clone https://github.com/YOUR-USERNAME/DevSecOps-Roadmap.git
cd DevSecOps-Roadmap

# 2. Branch
git checkout -b add-runtime-security-resource

# 3. Make the change

# 4. If you touched the diagrams, regenerate them
python3 assets/generate_diagrams.py --png

# 5. Check your links resolve
#    (CI does this too, but catching it locally is faster)
lychee --no-progress README.md

# 6. Commit and open a PR
git commit -m "Add Falco custom rule authoring guide to section 17"
```

### PR description

Tell us:
- **What** you changed
- **Why** it improves the roadmap
- **Whether** you have any commercial relationship with anything you added

One-line PRs need one-line descriptions. Do not over-formalise.

---

## What needs discussion first

Open an issue before you write the code for:

- **Structural changes** — reordering phases, adding or removing a numbered step
- **New top-level directories**
- **Removing an existing resource** — say why; there may be a reason it is there
- **Translations** — worth coordinating so they do not fragment

Everything else: just open the PR.

---

## Reporting an error

You do not need to fix it yourself. Open an issue with:

- What is wrong
- Where (file and section)
- What it should say, if you know

A well-written issue is a real contribution.

---

## Regenerating the diagrams

The diagrams are generated from data structures in `assets/generate_diagrams.py` — do not hand-edit the SVG files, your changes will be overwritten.

```bash
python3 assets/generate_diagrams.py          # SVG only
python3 assets/generate_diagrams.py --png    # SVG + PNG (needs Chrome or ImageMagick)
```

Edit the `ROADMAP`, `PIPELINE`, or `LANDSCAPE` structures at the top of the file, then re-run. No dependencies beyond the Python standard library.

---

## Code of conduct

Be decent to each other. Assume good faith. Disagree about technical substance freely; do not make it personal.

Security is a field with a lot of gatekeeping and a lot of people pretending to know more than they do. This repo is explicitly for people who are learning. Answers like "just read the RFC" or "if you have to ask, you're not ready" are not welcome here.

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## Licence

By contributing, you agree that your contributions are licensed under the [Apache License 2.0](LICENSE), the same as the rest of the project.
