#!/usr/bin/env python3
"""Check that a Codex Skill directory is reasonably safe to publish to GitHub.

This is a lightweight local check, not a complete secret scanner or legal
review. It checks the repository shape, obvious scaffold placeholders,
machine-specific paths, suspicious credential patterns, binary/archive leaks,
and Python syntax without importing third-party packages.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_FILES = (
    "SKILL.md",
    "README.md",
    "LICENSE",
    ".gitignore",
    "agents/openai.yaml",
    "assets/CodexProjectProfile.template.md",
    "assets/TOOLCHAIN_PROFILE.template.md",
    "assets/AvatarAudit.template.md",
    "references/evidence-and-authorization.md",
    "references/toolchain-mcp.md",
    "references/avatar-workflows.md",
    "references/blender-handoff.md",
    "references/modification-lessons.md",
    "references/plugin-update-workflow.md",
    "scripts/scan_unity_avatar.py",
    "scripts/read_mcp_sse.py",
    "scripts/check_github_ready.py",
)

TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".yaml",
    ".yml",
    ".toml",
    ".txt",
    ".json",
}

SUSPICIOUS_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private_key_block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("bearer_token", re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{20,}")),
    ("github_token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b")),
    ("github_pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("openai_like_key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{15,}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b")),
)

MACHINE_PATH_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "user_absolute_path",
        re.compile(r"(?i)\b[A-Z]:\\Users\\(?!<user>)[^\s`\"'<>]+"),
    ),
    (
        "private_project_path",
        re.compile(
            r"(?i)\b[A-Z]:\\(?:sucai|下载|BaiduNetdiskDownload|tengxun|xwechat_files|CodexSandboxOffline)\\[^\s`\"'<>]+"
        ),
    ),
)

FORBIDDEN_DIR_NAMES = {
    "library",
    "temp",
    "logs",
    "obj",
    "build",
    "builds",
    "__pycache__",
}

FORBIDDEN_SUFFIXES = {".zip", ".7z", ".rar", ".unitypackage", ".blend", ".fbx"}


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def add_issue(issues: list[dict[str, str]], severity: str, code: str, message: str, path: str = "") -> None:
    item = {"severity": severity, "code": code, "message": message}
    if path:
        item["path"] = path
    issues.append(item)


def read_text(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in data:
        return None
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace")


def check_required_files(root: Path, issues: list[dict[str, str]]) -> None:
    for item in REQUIRED_FILES:
        path = root / item
        if not path.is_file():
            add_issue(issues, "error", "missing_required_file", f"缺少必要文件：{item}", item)


def check_skill_frontmatter(root: Path, issues: list[dict[str, str]]) -> None:
    path = root / "SKILL.md"
    text = read_text(path)
    if text is None:
        return
    if not text.startswith("---"):
        add_issue(issues, "error", "frontmatter_missing", "SKILL.md 没有以 YAML frontmatter 开始。", "SKILL.md")
        return
    end = text.find("\n---", 3)
    if end < 0:
        add_issue(issues, "error", "frontmatter_unclosed", "SKILL.md 的 YAML frontmatter 没有闭合。", "SKILL.md")
        return
    front = text[3:end]
    name = re.search(r"(?m)^name:\s*([^\s]+)\s*$", front)
    description = re.search(r"(?m)^description:\s*(.+?)\s*$", front)
    if not name or name.group(1) != "vrchat-avatar-workbench":
        add_issue(issues, "error", "skill_name_invalid", "Skill name 必须是 vrchat-avatar-workbench。", "SKILL.md")
    if not description or "TODO" in description.group(1):
        add_issue(issues, "error", "skill_description_invalid", "Skill description 缺失或仍是 TODO。", "SKILL.md")


def check_nested_skill_roots(root: Path, issues: list[dict[str, str]]) -> None:
    for path in root.rglob("SKILL.md"):
        if path == root / "SKILL.md":
            continue
        add_issue(issues, "error", "nested_skill_root", "发现额外的嵌套 SKILL.md，可能导致安装多嵌套一层。", rel(path, root))


def check_forbidden_entries(root: Path, issues: list[dict[str, str]]) -> None:
    for path in root.rglob("*"):
        if path == root:
            continue
        relative_parts = {part.casefold() for part in path.relative_to(root).parts}
        if relative_parts & FORBIDDEN_DIR_NAMES:
            # .git is intentionally allowed; only report user-content/cache dirs.
            if ".git" not in relative_parts:
                add_issue(issues, "error", "forbidden_entry", "Skill 仓库不应包含 Unity 工程/缓存目录。", rel(path, root))
                continue
        if path.is_file() and path.suffix.casefold() in FORBIDDEN_SUFFIXES:
            add_issue(issues, "error", "forbidden_binary", "Skill 仓库不应包含模型、归档或 UnityPackage。", rel(path, root))


def check_text_content(root: Path, issues: list[dict[str, str]]) -> None:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.casefold() not in TEXT_SUFFIXES:
            continue
        if ".git" in path.relative_to(root).parts:
            continue
        # The checker necessarily contains the patterns it is looking for.
        if path.resolve() == Path(__file__).resolve():
            continue
        text = read_text(path)
        if text is None:
            continue
        if re.search(r"(?i)\[TODO|TODO:\s*", text):
            add_issue(issues, "error", "scaffold_placeholder", "发现未完成的 TODO 占位符。", rel(path, root))
        for code, pattern in MACHINE_PATH_PATTERNS:
            match = pattern.search(text)
            if match:
                add_issue(issues, "error", code, f"发现可能属于个人电脑的绝对路径：{match.group(0)}", rel(path, root))
        for code, pattern in SUSPICIOUS_PATTERNS:
            if pattern.search(text):
                add_issue(issues, "error", code, "发现疑似凭据或私钥模式；请移除后再发布。", rel(path, root))


def check_python_syntax(root: Path, issues: list[dict[str, str]]) -> None:
    for path in (root / "scripts").glob("*.py"):
        text = read_text(path)
        if text is None:
            add_issue(issues, "error", "script_unreadable", "Python 脚本无法按 UTF-8 读取。", rel(path, root))
            continue
        try:
            ast.parse(text, filename=str(path))
        except SyntaxError as exc:
            add_issue(issues, "error", "python_syntax", f"Python 语法错误：{exc.msg}（line {exc.lineno}）。", rel(path, root))


def check_openai_yaml_shape(root: Path, issues: list[dict[str, str]]) -> None:
    path = root / "agents" / "openai.yaml"
    text = read_text(path)
    if text is None:
        return
    for key in ("interface:", "display_name:", "short_description:", "default_prompt:", "policy:", "allow_implicit_invocation:"):
        if key not in text:
            add_issue(issues, "error", "openai_yaml_field_missing", f"agents/openai.yaml 缺少字段：{key}", rel(path, root))
    if "$vrchat-avatar-workbench" not in text:
        add_issue(issues, "error", "default_prompt_missing_skill", "default_prompt 没有显式提及 $vrchat-avatar-workbench。", rel(path, root))


def build_report(root: Path) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    check_required_files(root, issues)
    check_skill_frontmatter(root, issues)
    check_nested_skill_roots(root, issues)
    check_forbidden_entries(root, issues)
    check_text_content(root, issues)
    check_python_syntax(root, issues)
    check_openai_yaml_shape(root, issues)
    issues.sort(key=lambda item: (item["severity"], item["code"], item.get("path", "")))
    errors = sum(item["severity"] == "error" for item in issues)
    warnings = sum(item["severity"] == "warning" for item in issues)
    return {
        "schema_version": "github-ready-check/1",
        "root": str(root),
        "ready": errors == 0,
        "error_count": errors,
        "warning_count": warnings,
        "issues": issues,
        "checks": {
            "required_files": True,
            "frontmatter": True,
            "nested_skill_root": True,
            "forbidden_entries": True,
            "text_patterns": True,
            "python_ast": True,
            "openai_yaml_shape": True,
        },
        "note": "This is a lightweight publication check, not a complete secret scanner or legal review.",
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Skill/repository root")
    parser.add_argument("--pretty", action="store_true", help="Indent JSON output")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"Root does not exist: {root}"}, ensure_ascii=False), file=sys.stderr)
        return 2
    report = build_report(root)
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
