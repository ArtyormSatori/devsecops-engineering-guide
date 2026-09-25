#!/usr/bin/env python3
"""
Generate the DevSecOps Roadmap diagrams (SVG + PNG).

Usage:
    python3 assets/generate_diagrams.py          # writes SVG files
    python3 assets/generate_diagrams.py --png    # also renders PNG via headless Chrome

Everything is data-driven: edit the ROADMAP / PIPELINE / LANDSCAPE structures
below and re-run. No external Python dependencies.
"""

from __future__ import annotations

import argparse
import html
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- palette ---

BG = "#0a1018"
PANEL = "#111c2b"
CARD = "#16233a"
CARD_EDGE = "#22334f"
INK = "#f1f5f9"
INK_DIM = "#94a3b8"
INK_FAINT = "#64748b"
CHIP_BG = "#1e2f4a"

FONT = "DejaVu Sans, Inter, Segoe UI, Helvetica Neue, Arial, sans-serif"
MONO = "DejaVu Sans Mono, JetBrains Mono, Consolas, monospace"

# ---------------------------------------------------------------- content ---

ROADMAP = [
    {
        "phase": "PHASE 0",
        "name": "Foundations",
        "tag": "You cannot secure a system you cannot operate",
        "color": "#38bdf8",
        "steps": [
            {
                "n": 1,
                "title": ["Git & Version", "Control Hygiene"],
                "bullets": ["Signed commits & tags", "Branch protection rules",
                            "CODEOWNERS as authz", "Secret removal + rotation"],
                "chips": ["git", "gitsign", "pre-commit"],
            },
            {
                "n": 2,
                "title": ["Programming for", "Automation"],
                "bullets": ["Python or Go, deeply", "Bash is non-negotiable",
                            "SARIF / SBOM parsing", "Build your own tooling"],
                "chips": ["Python", "Go", "Bash"],
            },
            {
                "n": 3,
                "title": ["Linux, Systems", "& Hardening"],
                "bullets": ["Namespaces & cgroups", "Capabilities, seccomp",
                            "AppArmor / SELinux", "CIS Benchmarks"],
                "chips": ["Lynis", "OpenSCAP", "auditd"],
            },
            {
                "n": 4,
                "title": ["Networking &", "Applied Crypto"],
                "bullets": ["TLS 1.3, PKI, mTLS", "DNS, HTTP, CORS",
                            "Zero Trust (800-207)", "Post-quantum readiness"],
                "chips": ["Wireshark", "openssl", "mkcert"],
            },
            {
                "n": 5,
                "title": ["Security", "Fundamentals"],
                "bullets": ["CIA triad, AAA, risk", "AuthN vs AuthZ, OIDC",
                            "CWE vs CVE vs CAPEC", "Attacker's mindset"],
                "chips": ["MITRE ATT&CK", "OWASP", "CWE Top 25"],
            },
        ],
    },
    {
        "phase": "PHASE 1",
        "name": "The Delivery System",
        "tag": "Build the thing you are going to secure",
        "color": "#34d399",
        "steps": [
            {
                "n": 6,
                "title": ["Containers &", "Image Security"],
                "bullets": ["Distroless, non-root", "Deploy by digest",
                            "Drop capabilities", "Container escapes"],
                "chips": ["Trivy", "Syft", "Hadolint"],
            },
            {
                "n": 7,
                "title": ["Kubernetes", "Security"],
                "bullets": ["RBAC without cluster-admin", "Pod Security Standards",
                            "Admission control", "Default-deny NetworkPolicy"],
                "chips": ["Kyverno", "kube-bench", "Kubescape"],
            },
            {
                "n": 8,
                "title": ["IaC & Policy", "as Code"],
                "bullets": ["Terraform / OpenTofu", "Gate on plan, not source",
                            "Secure golden modules", "Expiring exceptions"],
                "chips": ["Checkov", "OPA", "KICS"],
            },
            {
                "n": 9,
                "title": ["CI/CD", "Engineering"],
                "bullets": ["Ephemeral runners", "GitOps pull-based deploys",
                            "Hermetic builds", "Fast feedback < 10 min"],
                "chips": ["Actions", "Argo CD", "Tekton"],
            },
            {
                "n": 10,
                "title": ["Cloud Platforms", "& Cloud Security"],
                "bullets": ["IAM is the perimeter", "CSPM / CIEM / CNAPP",
                            "IMDSv2, no static keys", "Landing zones & SCPs"],
                "chips": ["Prowler", "ScoutSuite", "Custodian"],
            },
        ],
    },
    {
        "phase": "PHASE 2",
        "name": "Shift Left",
        "tag": "Minutes in review, or a weekend in production",
        "color": "#fbbf24",
        "steps": [
            {
                "n": 11,
                "title": ["Secure Coding &", "OWASP Top 10:2025"],
                "bullets": ["A01 Broken Access Control", "A03 Supply Chain Failures",
                            "ASVS 5.0 requirements", "API Top 10 / BOLA"],
                "chips": ["ASVS 5.0", "Cheat Sheets", "WSTG"],
            },
            {
                "n": 12,
                "title": ["Threat", "Modeling"],
                "bullets": ["STRIDE, PASTA, LINDDUN", "Trust boundaries first",
                            "Threat models as code", "Insecure design is unscannable"],
                "chips": ["Threat Dragon", "pytm", "threagile"],
            },
            {
                "n": 13,
                "title": ["Security Testing:", "SAST · SCA · DAST"],
                "bullets": ["Know each tool's blind spot", "Fail on new, warn on old",
                            "Write custom rules", "Reachability analysis"],
                "chips": ["Semgrep", "CodeQL", "ZAP"],
            },
            {
                "n": 14,
                "title": ["Secrets &", "Workload Identity"],
                "bullets": ["Ladder: static -> dynamic", "OIDC federation in CI",
                            "SPIFFE/SPIRE identity", "Rotate first, investigate second"],
                "chips": ["Vault", "OpenBao", "SOPS"],
            },
        ],
    },
    {
        "phase": "PHASE 3",
        "name": "Supply Chain & Pipeline Integrity",
        "tag": "A03:2025 - the defining topic of the field",
        "color": "#f472b6",
        "steps": [
            {
                "n": 15,
                "title": ["Software Supply", "Chain Security"],
                "bullets": ["SBOM: CycloneDX / SPDX", "SLSA v1.2 build levels",
                            "Sigstore keyless signing", "VEX to cut the noise",
                            "Verify at admission"],
                "chips": ["cosign", "in-toto", "Dependency-Track", "Scorecard"],
            },
            {
                "n": 16,
                "title": ["Hardening the", "Pipeline Itself"],
                "bullets": ["OWASP CI/CD Top 10", "Pin actions to SHAs",
                            "Poisoned Pipeline Execution", "Least-privilege tokens",
                            "Restrict runner egress"],
                "chips": ["zizmor", "Poutine", "Harden-Runner", "actionlint"],
            },
        ],
    },
    {
        "phase": "PHASE 4",
        "name": "Runtime",
        "tag": "Prevention fails - plan for it",
        "color": "#fb923c",
        "steps": [
            {
                "n": 17,
                "title": ["Runtime Security &", "Detection Engineering"],
                "bullets": ["eBPF visibility", "Detections as tested code",
                            "Map coverage to ATT&CK", "Drift = incident",
                            "Tune for signal"],
                "chips": ["Falco", "Tetragon", "Tracee", "Sigma"],
            },
            {
                "n": 18,
                "title": ["Incident Response", "for Cloud-Native"],
                "bullets": ["Isolate, do not kill the pod", "Ephemeral forensics",
                            "Revoke sessions, rotate keys", "Blameless post-mortems",
                            "Rehearsed runbooks"],
                "chips": ["NIST 800-61r3", "Atomic Red Team", "tabletops"],
            },
        ],
    },
    {
        "phase": "PHASE 5",
        "name": "Scale & Govern",
        "tag": "The technical work is the easy half",
        "color": "#a78bfa",
        "steps": [
            {
                "n": 19,
                "title": ["Vulnerability", "Management at Scale"],
                "bullets": ["KEV + EPSS beat CVSS", "Reachability & exposure",
                            "Measure MTTR, not counts", "Bulk fixes over one-by-one"],
                "chips": ["EPSS", "KEV", "OpenVEX"],
            },
            {
                "n": 20,
                "title": ["Compliance as", "Code & Governance"],
                "bullets": ["NIST SSDF 800-218", "ISO 27001 / SOC 2 / PCI",
                            "EU CRA: Sep 26 / Dec 27", "Evidence from pipelines"],
                "chips": ["OSCAL", "InSpec", "SAMM"],
            },
            {
                "n": 21,
                "title": ["AI & LLM", "Security"],
                "bullets": ["OWASP LLM Top 10 (2025)", "Agentic Top 10 (2026)",
                            "Prompt injection, agency", "Model supply chain, AI-BOM"],
                "chips": ["garak", "PyRIT", "ModelScan"],
            },
            {
                "n": 22,
                "title": ["Culture, Metrics", "& Maturity"],
                "bullets": ["Security champions", "Paved roads over gates",
                            "MTTR, coverage, escape rate", "DSOMM self-assessment"],
                "chips": ["DSOMM", "SAMM", "DORA"],
            },
        ],
    },
]

PIPELINE = [
    {
        "title": "CODE",
        "sub": "developer laptop",
        "color": "#38bdf8",
        "items": ["IDE security plugins", "pre-commit hooks", "gitleaks scan",
                  "Secure coding standards", "Threat model in repo"],
    },
    {
        "title": "COMMIT / PR",
        "sub": "< 10 minutes",
        "color": "#34d399",
        "items": ["Secret scanning", "SAST (diff-aware)", "SCA + license check",
                  "IaC misconfig scan", "Workflow audit (zizmor)", "Signed commits"],
    },
    {
        "title": "BUILD",
        "sub": "hermetic + attested",
        "color": "#fbbf24",
        "items": ["Pinned dependencies", "Reproducible build", "SBOM generation",
                  "Image vulnerability scan", "Sign with cosign", "SLSA provenance"],
    },
    {
        "title": "ADMISSION",
        "sub": "the enforcement point",
        "color": "#f472b6",
        "items": ["Verify signature", "Verify provenance", "Policy as code",
                  "Pod Security Standards", "Block :latest / privileged"],
    },
    {
        "title": "RUNTIME",
        "sub": "prevention fails",
        "color": "#fb923c",
        "items": ["DAST / API testing", "eBPF runtime detection", "Drift detection",
                  "CSPM / KSPM posture", "Network policy enforcement"],
    },
    {
        "title": "MANAGE",
        "sub": "close the loop",
        "color": "#a78bfa",
        "items": ["ASPM aggregation", "Dedupe across tools", "KEV / EPSS triage",
                  "SLA tracking (MTTR)", "Feed back to developers"],
    },
]

LANDSCAPE = [
    ("SAST", "#38bdf8", ["Semgrep", "CodeQL", "SonarQube", "Bandit", "gosec"]),
    ("SCA", "#38bdf8", ["Trivy", "Grype", "OSV-Scanner", "Dependency-Track"]),
    ("Secrets scanning", "#38bdf8", ["Gitleaks", "TruffleHog", "detect-secrets"]),
    ("DAST / API", "#34d399", ["OWASP ZAP", "Nuclei", "Schemathesis", "Akto"]),
    ("Fuzzing", "#34d399", ["OSS-Fuzz", "AFL++", "Atheris", "restler"]),
    ("Container", "#fbbf24", ["Trivy", "Grype", "Dockle", "Hadolint", "Clair"]),
    ("Kubernetes", "#fbbf24", ["Kubescape", "kube-bench", "Trivy Operator", "Polaris"]),
    ("IaC", "#fbbf24", ["Checkov", "KICS", "Terrascan", "Trivy config"]),
    ("Policy as code", "#f472b6", ["Kyverno", "OPA / Gatekeeper", "Conftest", "Cedar"]),
    ("Supply chain", "#f472b6", ["cosign", "Syft", "in-toto", "Scorecard", "GUAC"]),
    ("Secrets mgmt", "#f472b6", ["Vault", "OpenBao", "SOPS", "ESO", "SPIRE"]),
    ("Runtime", "#fb923c", ["Falco", "Tetragon", "Tracee", "Wazuh"]),
    ("CSPM / CNAPP", "#fb923c", ["Prowler", "ScoutSuite", "Cloud Custodian", "Steampipe"]),
    ("CI/CD security", "#a78bfa", ["zizmor", "Poutine", "actionlint", "Harden-Runner"]),
    ("ASPM", "#a78bfa", ["DefectDojo", "Faraday"]),
    ("Threat modeling", "#a78bfa", ["Threat Dragon", "pytm", "threagile"]),
    ("AI / LLM security", "#f87171", ["garak", "PyRIT", "ModelScan", "NeMo Guardrails"]),
    ("Vuln intelligence", "#f87171", ["OSV.dev", "EPSS", "CISA KEV", "OpenVEX"]),
]

# ------------------------------------------------------------- svg helpers --


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def text(x, y, content, size=16, fill=INK, weight="normal", anchor="start",
         family=FONT, spacing=None, opacity=None):
    attrs = [
        f'x="{x}"', f'y="{y}"',
        f'font-family="{family}"', f'font-size="{size}"',
        f'font-weight="{weight}"', f'fill="{fill}"',
    ]
    if anchor != "start":
        attrs.append(f'text-anchor="{anchor}"')
    if spacing:
        attrs.append(f'letter-spacing="{spacing}"')
    if opacity:
        attrs.append(f'opacity="{opacity}"')
    return f'<text {" ".join(attrs)}>{esc(content)}</text>'


def rect(x, y, w, h, fill, rx=14, stroke=None, sw=1, opacity=None):
    attrs = [f'x="{x}"', f'y="{y}"', f'width="{w}"', f'height="{h}"',
             f'rx="{rx}"', f'fill="{fill}"']
    if stroke:
        attrs += [f'stroke="{stroke}"', f'stroke-width="{sw}"']
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return f'<rect {" ".join(attrs)}/>'


def chip(x, y, label, color, size=12):
    w = len(label) * (size * 0.62) + 18
    h = size * 1.5 + 4
    out = [rect(x, y, round(w, 1), round(h, 1), CHIP_BG, rx=h / 2,
                stroke=color, sw=1, opacity=0.95)]
    out.append(text(x + w / 2, y + h * 0.7 + 0.6, label, size=size, fill=color,
                    anchor="middle", family=MONO))
    return "".join(out), w


def svg_document(width, height, body, defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="{FONT}">\n'
        f'<defs>{defs}</defs>\n'
        f'{rect(0, 0, width, height, BG, rx=0)}\n'
        f'{body}\n</svg>\n'
    )


# ------------------------------------------------------------ roadmap svg ---

def build_roadmap() -> str:
    W = 1960
    MARGIN = 46
    COLS = 5
    GAP = 26
    CARD_W = (W - 2 * MARGIN - (COLS - 1) * GAP) // COLS   # 350
    HEADER_H = 250
    PHASE_HEAD_H = 74
    PHASE_GAP = 34

    def card_height(step):
        return 122 + len(step["bullets"]) * 25 + 36

    # Pre-compute total height
    y = HEADER_H
    for phase in ROADMAP:
        rows = [phase["steps"][i:i + COLS] for i in range(0, len(phase["steps"]), COLS)]
        y += PHASE_HEAD_H
        for row in rows:
            y += max(card_height(s) for s in row) + 18
        y += PHASE_GAP
    H = y + 96

    b = []

    # --- header -------------------------------------------------------------
    b.append(rect(0, 0, W, HEADER_H - 24, PANEL, rx=0))
    b.append(f'<rect x="0" y="{HEADER_H - 28}" width="{W}" height="4" fill="url(#hdr)"/>')
    b.append(text(MARGIN, 88, "DevSecOps Roadmap", size=60, weight="bold", fill=INK))
    b.append(text(MARGIN, 138, "2026", size=46, weight="bold", fill="#38bdf8"))
    b.append(text(MARGIN + 148, 138,
                  "22 steps  ·  6 phases  ·  foundations to governance",
                  size=22, fill=INK_DIM))
    b.append(text(MARGIN, 176,
                  "Ship fast without shipping vulnerabilities. Security as an automated, "
                  "measurable property of the delivery pipeline",
                  size=19, fill=INK_FAINT))

    # legend
    lx = MARGIN
    for phase in ROADMAP:
        b.append(rect(lx, 196, 13, 13, phase["color"], rx=3))
        b.append(text(lx + 21, 207, f'{phase["phase"]} · {phase["name"]}',
                      size=14, fill=INK_DIM))
        lx += 26 + len(f'{phase["phase"]} · {phase["name"]}') * 7.6

    b.append(text(W - MARGIN, 92, "github.com/siddhantbhattarai101", size=18,
                  fill=INK_FAINT, anchor="end", family=MONO))
    b.append(text(W - MARGIN, 118, "/DevSecOps-Roadmap", size=18,
                  fill="#38bdf8", anchor="end", family=MONO))

    # --- phases -------------------------------------------------------------
    y = HEADER_H
    for phase in ROADMAP:
        color = phase["color"]

        # phase header bar
        b.append(rect(MARGIN, y, W - 2 * MARGIN, 54, PANEL, rx=12,
                      stroke=CARD_EDGE, sw=1))
        b.append(rect(MARGIN, y, 6, 54, color, rx=3))
        b.append(text(MARGIN + 24, y + 34, phase["phase"], size=17, weight="bold",
                      fill=color, family=MONO, spacing="1.5"))
        b.append(text(MARGIN + 132, y + 35, phase["name"], size=25, weight="bold",
                      fill=INK))
        b.append(text(W - MARGIN - 22, y + 34, phase["tag"], size=16,
                      fill=INK_FAINT, anchor="end"))
        y += PHASE_HEAD_H

        rows = [phase["steps"][i:i + COLS]
                for i in range(0, len(phase["steps"]), COLS)]
        for row in rows:
            row_h = max(card_height(s) for s in row)
            # centre rows that do not fill all columns
            row_w = len(row) * CARD_W + (len(row) - 1) * GAP
            offset = MARGIN + (W - 2 * MARGIN - row_w) // 2
            for i, step in enumerate(row):
                x = offset + i * (CARD_W + GAP)
                b.append(build_card(x, y, CARD_W, row_h, step, color))
            y += row_h + 18
        y += PHASE_GAP

    # --- footer -------------------------------------------------------------
    b.append(rect(MARGIN, H - 74, W - 2 * MARGIN, 1, CARD_EDGE, rx=0))
    b.append(text(MARGIN, H - 40,
                  "Concepts and threat models outlast tools. Learn why a control exists "
                  "before you learn which vendor sells it.",
                  size=16, fill=INK_FAINT))
    b.append(text(W - MARGIN, H - 40, "Apache-2.0  ·  contributions welcome",
                  size=15, fill=INK_FAINT, anchor="end"))

    defs = (
        '<linearGradient id="hdr" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0%" stop-color="#38bdf8"/>'
        '<stop offset="20%" stop-color="#34d399"/>'
        '<stop offset="40%" stop-color="#fbbf24"/>'
        '<stop offset="60%" stop-color="#f472b6"/>'
        '<stop offset="80%" stop-color="#fb923c"/>'
        '<stop offset="100%" stop-color="#a78bfa"/>'
        '</linearGradient>'
    )
    return svg_document(W, H, "\n".join(b), defs)


def build_card(x, y, w, h, step, color) -> str:
    b = [rect(x, y, w, h, CARD, rx=16, stroke=CARD_EDGE, sw=1.5)]
    b.append(rect(x, y, w, 4, color, rx=2))

    # number badge
    b.append(f'<circle cx="{x + 34}" cy="{y + 40}" r="19" fill="{color}" opacity="0.15"/>')
    b.append(f'<circle cx="{x + 34}" cy="{y + 40}" r="19" fill="none" '
             f'stroke="{color}" stroke-width="1.5"/>')
    b.append(text(x + 34, y + 46, step["n"], size=17, weight="bold", fill=color,
                  anchor="middle", family=MONO))

    # title (1-2 lines)
    ty = y + 36 if len(step["title"]) > 1 else y + 46
    for line in step["title"]:
        b.append(text(x + 64, ty, line, size=19, weight="bold", fill=INK))
        ty += 23

    # bullets
    by = y + 100
    for bullet in step["bullets"]:
        b.append(f'<circle cx="{x + 24}" cy="{by - 5}" r="2.8" fill="{color}" opacity="0.85"/>')
        b.append(text(x + 36, by, bullet, size=15, fill=INK_DIM))
        by += 25

    # tool chips
    cx, cy = x + 18, y + h - 36
    for label in step["chips"]:
        markup, cw = chip(cx, cy, label, color, size=13)
        if cx + cw > x + w - 14:
            break
        b.append(markup)
        cx += cw + 7

    return "".join(b)


# ----------------------------------------------------------- pipeline svg ---

def build_pipeline() -> str:
    # Laid out 3-across / 2-down rather than 6-across so the text stays
    # legible when GitHub scales the image into a ~850px README column.
    W = 1200
    MARGIN = 44
    HEADER_H = 168
    COLS = 3
    GAP = 22
    ROW_GAP = 34
    COL_W = (W - 2 * MARGIN - (COLS - 1) * GAP) // COLS
    BODY_H = 186 + max(len(s["items"]) for s in PIPELINE) * 30 + 18
    ROWS = (len(PIPELINE) + COLS - 1) // COLS
    H = HEADER_H + ROWS * BODY_H + (ROWS - 1) * ROW_GAP + 196

    b = []
    b.append(rect(0, 0, W, HEADER_H - 26, PANEL, rx=0))
    b.append(f'<rect x="0" y="{HEADER_H - 30}" width="{W}" height="4" fill="url(#hdr)"/>')
    b.append(text(MARGIN, 70, "The DevSecOps Pipeline", size=42, weight="bold", fill=INK))
    b.append(text(MARGIN, 104,
                  "Where every security control belongs in the delivery lifecycle",
                  size=19, fill=INK_DIM))
    b.append(text(MARGIN, 132, "shift left  ·  sign everything  ·  verify at admission",
                  size=16, fill="#38bdf8", family=MONO))

    y0 = HEADER_H + 16
    for i, stage in enumerate(PIPELINE):
        col, row = i % COLS, i // COLS
        x = MARGIN + col * (COL_W + GAP)
        y = y0 + row * (BODY_H + ROW_GAP)
        color = stage["color"]

        b.append(rect(x, y, COL_W, BODY_H, CARD, rx=16, stroke=CARD_EDGE, sw=1.5))
        b.append(rect(x, y, COL_W, 5, color, rx=2))

        b.append(f'<circle cx="{x + COL_W / 2}" cy="{y + 54}" r="25" '
                 f'fill="{color}" opacity="0.16"/>')
        b.append(f'<circle cx="{x + COL_W / 2}" cy="{y + 54}" r="25" fill="none" '
                 f'stroke="{color}" stroke-width="1.5"/>')
        b.append(text(x + COL_W / 2, y + 62, f"{i + 1}", size=21, weight="bold",
                      fill=color, anchor="middle", family=MONO))

        b.append(text(x + COL_W / 2, y + 110, stage["title"], size=23, weight="bold",
                      fill=INK, anchor="middle", spacing="1"))
        b.append(text(x + COL_W / 2, y + 136, stage["sub"], size=16,
                      fill=INK_FAINT, anchor="middle"))
        b.append(rect(x + 34, y + 154, COL_W - 68, 1, CARD_EDGE, rx=0))

        iy = y + 190
        for item in stage["items"]:
            b.append(f'<circle cx="{x + 28}" cy="{iy - 5}" r="3.2" fill="{color}"/>')
            b.append(text(x + 42, iy, item, size=17, fill=INK_DIM))
            iy += 30

        # arrow to the next stage, wrapping at the end of a row
        ay = y + BODY_H / 2
        if col < COLS - 1 and i < len(PIPELINE) - 1:
            ax = x + COL_W + 4
            b.append(f'<path d="M {ax} {ay} l 12 0 M {ax + 7} {ay - 5} l 6 5 '
                     f'l -6 5" stroke="{INK_FAINT}" stroke-width="2.2" fill="none" '
                     f'stroke-linecap="round" stroke-linejoin="round"/>')
        elif col == COLS - 1 and i < len(PIPELINE) - 1:
            # wrap: right edge of this row down to the left edge of the next
            wy = y + BODY_H + ROW_GAP / 2
            b.append(f'<path d="M {x + COL_W / 2} {y + BODY_H} L {x + COL_W / 2} {wy} '
                     f'L {MARGIN + COL_W / 2} {wy} L {MARGIN + COL_W / 2} {y + BODY_H + ROW_GAP}" '
                     f'stroke="{INK_FAINT}" stroke-width="2.2" fill="none" '
                     f'stroke-linejoin="round"/>')
            b.append(f'<path d="M {MARGIN + COL_W / 2 - 5} {y + BODY_H + ROW_GAP - 8} '
                     f'l 5 8 l 5 -8" stroke="{INK_FAINT}" stroke-width="2.2" fill="none" '
                     f'stroke-linecap="round" stroke-linejoin="round"/>')

    # feedback loop from the last card back to the first
    last_y = y0 + (ROWS - 1) * (BODY_H + ROW_GAP) + BODY_H
    fy = last_y + 46
    x0 = MARGIN + ((len(PIPELINE) - 1) % COLS) * (COL_W + GAP) + COL_W / 2
    x1 = MARGIN + COL_W / 2
    b.append(f'<path d="M {x0} {last_y} L {x0} {fy} L {x1 - 60} {fy}" '
             f'stroke="#a78bfa" stroke-width="2.2" fill="none" stroke-dasharray="7 6" '
             f'stroke-linejoin="round"/>')
    b.append(f'<path d="M {x1 - 52} {fy - 5} l -8 5 l 8 5" stroke="#a78bfa" '
             f'stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    b.append(text(W - MARGIN, fy + 32,
                  "findings, SBOMs and telemetry flow back to developers",
                  size=17, fill="#a78bfa", anchor="end"))

    b.append(rect(MARGIN, H - 92, W - 2 * MARGIN, 1, CARD_EDGE, rx=0))
    b.append(text(MARGIN, H - 58,
                  "Rule of thumb: fail the build on NEW findings, warn on the backlog.",
                  size=17, fill=INK_FAINT))
    b.append(text(MARGIN, H - 30,
                  "Every gate needs a documented, auditable bypass.",
                  size=17, fill=INK_FAINT))

    defs = (
        '<linearGradient id="hdr" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0%" stop-color="#38bdf8"/>'
        '<stop offset="20%" stop-color="#34d399"/>'
        '<stop offset="40%" stop-color="#fbbf24"/>'
        '<stop offset="60%" stop-color="#f472b6"/>'
        '<stop offset="80%" stop-color="#fb923c"/>'
        '<stop offset="100%" stop-color="#a78bfa"/>'
        '</linearGradient>'
    )
    return svg_document(W, H, "\n".join(b), defs)


# ---------------------------------------------------------- landscape svg ---

def build_landscape() -> str:
    # Two columns rather than three, so the tool chips stay readable inline.
    W = 1150
    MARGIN = 44
    HEADER_H = 146
    COLS = 2
    GAP = 22
    CHIP_SIZE = 15
    CARD_W = (W - 2 * MARGIN - (COLS - 1) * GAP) // COLS

    def chip_w(tool):
        return len(tool) * (CHIP_SIZE * 0.62) + 18

    def chip_rows(tools):
        """How many wrapped chip rows this category needs."""
        rows, x = 1, 0.0
        for tool in tools:
            cw = chip_w(tool)
            if x and x + cw > CARD_W - 38:
                rows += 1
                x = 0.0
            x += cw + 8
        return rows

    CARD_H = 48 + max(chip_rows(t) for _, _, t in LANDSCAPE) * 33 + 14
    ROWS = (len(LANDSCAPE) + COLS - 1) // COLS
    H = HEADER_H + ROWS * (CARD_H + GAP) + 96

    b = []
    b.append(rect(0, 0, W, HEADER_H - 26, PANEL, rx=0))
    b.append(f'<rect x="0" y="{HEADER_H - 30}" width="{W}" height="4" fill="url(#hdr)"/>')
    b.append(text(MARGIN, 64, "The 2026 Open Source Toolchain", size=36,
                  weight="bold", fill=INK))
    b.append(text(MARGIN, 98,
                  "Pick ONE per category and learn it properly. Breadth here is a trap.",
                  size=19, fill=INK_DIM))

    y = HEADER_H
    for idx, (category, color, tools) in enumerate(LANDSCAPE):
        col = idx % COLS
        row = idx // COLS
        x = MARGIN + col * (CARD_W + GAP)
        cy = y + row * (CARD_H + GAP)

        b.append(rect(x, cy, CARD_W, CARD_H, CARD, rx=14, stroke=CARD_EDGE, sw=1.5))
        b.append(rect(x, cy, 5, CARD_H, color, rx=2))
        b.append(text(x + 24, cy + 36, category, size=21, weight="bold", fill=INK))

        chip_x, chip_y = x + 22, cy + 58
        for tool in tools:
            cw = chip_w(tool)
            if chip_x > x + 22 and chip_x + cw > x + CARD_W - 16:
                chip_x = x + 22
                chip_y += 33
            if chip_y > cy + CARD_H - 28:
                break
            markup, cw = chip(chip_x, chip_y, tool, color, size=CHIP_SIZE)
            b.append(markup)
            chip_x += cw + 8

    b.append(text(MARGIN, H - 42,
                  "Commercial equivalents exist for every category. The concepts transfer;",
                  size=16, fill=INK_FAINT))
    b.append(text(MARGIN, H - 20,
                  "the vendors matter less than they would like you to believe.",
                  size=16, fill=INK_FAINT))

    defs = (
        '<linearGradient id="hdr" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0%" stop-color="#38bdf8"/>'
        '<stop offset="50%" stop-color="#f472b6"/>'
        '<stop offset="100%" stop-color="#a78bfa"/>'
        '</linearGradient>'
    )
    return svg_document(W, H, "\n".join(b), defs)


# --------------------------------------------------------------- rendering --

def render_png(svg_path: str, png_path: str, scale: float = 1.5) -> bool:
    """Render SVG -> PNG using headless Chrome (falls back to ImageMagick)."""
    import re

    with open(svg_path, encoding="utf-8") as fh:
        svg = fh.read()
    m = re.search(r'width="(\d+)" height="(\d+)"', svg)
    if not m:
        return False
    w, h = int(m.group(1)), int(m.group(2))

    chrome = next((c for c in ("google-chrome", "chromium", "chromium-browser")
                   if shutil.which(c)), None)
    if chrome:
        with tempfile.TemporaryDirectory() as tmp:
            page = os.path.join(tmp, "page.html")
            with open(page, "w", encoding="utf-8") as fh:
                fh.write(f'<!doctype html><meta charset="utf-8">'
                         f'<style>html,body{{margin:0;padding:0;background:{BG};}}'
                         f'svg{{display:block;}}</style>{svg}')
            cmd = [
                chrome, "--headless", "--disable-gpu", "--no-sandbox",
                "--hide-scrollbars", "--default-background-color=00000000",
                f"--force-device-scale-factor={scale}",
                f"--window-size={w},{h}",
                f"--screenshot={png_path}",
                f"--user-data-dir={os.path.join(tmp, 'profile')}",
                f"file://{page}",
            ]
            res = subprocess.run(cmd, capture_output=True, timeout=180)
            if os.path.exists(png_path) and os.path.getsize(png_path) > 5000:
                return True
            sys.stderr.write(res.stderr.decode()[-800:] + "\n")

    if shutil.which("magick") or shutil.which("convert"):
        tool = "magick" if shutil.which("magick") else "convert"
        subprocess.run([tool, "-density", "144", "-background", BG,
                        svg_path, png_path], check=False, timeout=180)
        return os.path.exists(png_path)
    return False


DIAGRAMS = {
    "devsecops-roadmap": build_roadmap,
    "devsecops-pipeline": build_pipeline,
    "devsecops-toolchain": build_landscape,
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--png", action="store_true", help="also render PNG files")
    ap.add_argument("--scale", type=float, default=1.5, help="PNG device scale factor")
    ap.add_argument("--out", default=HERE, help="output directory")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    for name, builder in DIAGRAMS.items():
        svg_path = os.path.join(args.out, f"{name}.svg")
        with open(svg_path, "w", encoding="utf-8") as fh:
            fh.write(builder())
        print(f"  wrote {svg_path}")

        if args.png:
            png_path = os.path.join(args.out, f"{name}.png")
            if render_png(svg_path, png_path, args.scale):
                size = os.path.getsize(png_path) / 1024
                print(f"  wrote {png_path}  ({size:.0f} KB)")
            else:
                print(f"  !! failed to render {png_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
