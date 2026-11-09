"""
Test verification for Issue #7: Broken links detected.
Verifies that all 5 reported broken link errors are fixed:
1. CISA supply chain guide for developers resolves with HTTP 200.
2. CISA/NSA defending CI/CD environments guidance resolves with HTTP 200.
3. README.md does not reference non-existent jeremy_banner.png.
4. checklists/pipeline-security.md uses updated CISA guidance URL.
5. .github/pull_request_template.md points to valid relative CONTRIBUTING.md.
"""

import os
from pathlib import Path
import urllib.error
import urllib.request

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_no_broken_old_cisa_urls():
    old_urls = [
        "https://www.cisa.gov/resources-tools/resources/securing-software-supply-chain-recommended-practices-guide-developers",
        "https://www.cisa.gov/resources-tools/resources/defending-continuous-integrationcontinuous-delivery-cicd-environments",
    ]
    for md_file in [
        REPO_ROOT / "README.md",
        REPO_ROOT / "checklists" / "pipeline-security.md",
    ]:
        content = md_file.read_text(encoding="utf-8")
        for old_url in old_urls:
            assert old_url not in content, f"Found old broken URL {old_url} in {md_file}"


def test_no_missing_banner():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "jeremy_banner.png" not in readme, (
        "README.md still references missing jeremy_banner.png"
    )


def test_pull_request_template_contributing_link():
    template = (REPO_ROOT / ".github" / "pull_request_template.md").read_text(
        encoding="utf-8"
    )
    assert "[CONTRIBUTING.md](../CONTRIBUTING.md)" in template, (
        "PR template must link to ../CONTRIBUTING.md"
    )
    resolved_path = (REPO_ROOT / ".github" / "../CONTRIBUTING.md").resolve()
    assert (
        resolved_path.is_file()
    ), f"Resolved CONTRIBUTING.md does not exist at {resolved_path}"


def test_updated_urls_resolve():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    urls = [
        "https://www.cisa.gov/resources-tools/resources/securing-software-supply-chain-recommended-practices-developers",
        "https://www.cisa.gov/news-events/alerts/2023/06/28/cisa-and-nsa-release-joint-guidance-defending-continuous-integrationcontinuous-delivery-cicd",
    ]
    for url in urls:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            assert (
                resp.status == 200
            ), f"Expected 200 for {url}, got {resp.status}"


if __name__ == "__main__":
    print("Running link tests for Issue #7...")
    test_no_broken_old_cisa_urls()
    print("✓ Old broken CISA URLs removed")
    test_no_missing_banner()
    print("✓ Missing banner reference removed")
    test_pull_request_template_contributing_link()
    print("✓ PR template link to CONTRIBUTING.md verified")
    test_updated_urls_resolve()
    print("✓ New CISA URLs resolve with HTTP 200")
    print("ALL TESTS PASSED!")
