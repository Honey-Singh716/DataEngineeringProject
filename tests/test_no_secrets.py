"""
tests/test_no_secrets.py
Scans all tracked files in git for exposed credentials, passwords, and API keys:
1. PASSWORD '...' literals (except documented placeholders)
2. postgresql://user:pass@ connection strings with real credentials
3. gsk_ and sk- API key patterns
4. Known exposed passwords (ReadOnlyPass123, b24cm1030)
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Recognized safe placeholder tokens
SAFE_PLACEHOLDERS = {
    "change_me",
    "your_password",
    "your_host",
    "your_groq_api_key",
    "your_groq_api_key_here",
    "password",
    "pass",
    "secret",
    "valid_pass",
    "strong_secure_password",
    "<password>",
    "<secure_password>",
    "<set in .env>",
    "***",
}

# Regex patterns to catch credentials
RE_PASSWORD_LITERAL = re.compile(r"""(?:PASSWORD|IDENTIFIED\s+BY)\s+['"]([^'"]+)['"]""", re.IGNORECASE)
RE_POSTGRES_URI = re.compile(r"""postgres(?:ql)?(?:\+\w+)?://([^:]+):([^@\s/]+)@""", re.IGNORECASE)
RE_GROQ_KEY = re.compile(r"""\bgsk_[a-zA-Z0-9]{20,}\b""")
RE_OPENAI_KEY = re.compile(r"""\bsk-[a-zA-Z0-9]{20,}\b""")
RE_LEAKED_PW = re.compile(r"""(?:ReadOnlyPass123|b24cm1030)""", re.IGNORECASE)

# Ignored binary and generated file extensions
BINARY_EXTENSIONS = {
    ".docx", ".pdf", ".png", ".jpg", ".jpeg", ".ico", ".svg",
    ".pyc", ".db", ".sqlite", ".dump", ".tar", ".gz", ".zip"
}


def is_placeholder(val: str) -> bool:
    val_clean = val.strip().lower()
    if val_clean in SAFE_PLACEHOLDERS:
        return True
    if (val_clean.startswith("<") and val_clean.endswith(">")) or (val_clean.startswith("{") and val_clean.endswith("}")):
        return True
    if val_clean.startswith(":") or val_clean.startswith("$"):
        return True
    return False


def get_tracked_files() -> list[Path]:
    """Retrieve all files tracked by git."""
    try:
        out = subprocess.check_output(
            ["git", "ls-files"],
            cwd=str(PROJECT_ROOT),
            text=True,
            encoding="utf-8"
        )
        return [PROJECT_ROOT / line.strip() for line in out.splitlines() if line.strip()]
    except Exception as e:
        # Fallback to traversing directory if git command fails
        return [
            p for p in PROJECT_ROOT.rglob("*")
            if p.is_file() and ".git" not in p.parts
        ]


def test_no_hardcoded_secrets_in_tracked_files():
    """Ensure no tracked file contains exposed passwords or secret keys."""
    tracked_files = get_tracked_files()
    violations = []

    for file_path in tracked_files:
        if not file_path.exists():
            continue
        if file_path.suffix.lower() in BINARY_EXTENSIONS:
            continue
        # Self-test exemption: skip this test file itself for regex definitions
        if file_path.name == "test_no_secrets.py":
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for line_no, line in enumerate(content.splitlines(), start=1):
            # 1. Check known leaked passwords
            if RE_LEAKED_PW.search(line):
                violations.append(f"{file_path.relative_to(PROJECT_ROOT)}:{line_no} - Known leaked password pattern found")

            # 2. Check PASSWORD 'literal'
            for match in RE_PASSWORD_LITERAL.finditer(line):
                pw = match.group(1)
                if not is_placeholder(pw):
                    violations.append(f"{file_path.relative_to(PROJECT_ROOT)}:{line_no} - Hardcoded PASSWORD literal '{pw[:4]}***'")

            # 3. Check postgresql://user:pass@
            for match in RE_POSTGRES_URI.finditer(line):
                user, pw = match.group(1), match.group(2)
                if not is_placeholder(pw):
                    violations.append(f"{file_path.relative_to(PROJECT_ROOT)}:{line_no} - Connection URI contains credential for user '{user}'")

            # 4. Check API keys
            if RE_GROQ_KEY.search(line):
                violations.append(f"{file_path.relative_to(PROJECT_ROOT)}:{line_no} - Real Groq API Key pattern found")
            if RE_OPENAI_KEY.search(line):
                violations.append(f"{file_path.relative_to(PROJECT_ROOT)}:{line_no} - Real OpenAI/Standard API Key pattern found")

    assert not violations, (
        f"Found {len(violations)} secret/credential violations in tracked files:\n" +
        "\n".join(violations)
    )
