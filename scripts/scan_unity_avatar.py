#!/usr/bin/env python3
"""Read-only static baseline scanner for a VRChat Unity avatar project.

The scanner deliberately avoids parsing Unity's complete multi-document YAML.
It indexes GUIDs, searches targeted serialized markers, audits package paths, and
emits a stable JSON report suitable for follow-up semantic inspection.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "vrchat-avatar-baseline/1"
TEXT_EXTENSIONS = {
    ".anim",
    ".asset",
    ".controller",
    ".json",
    ".mat",
    ".overridecontroller",
    ".prefab",
    ".unity",
}
SKIP_DIRS = {"Library", "Logs", "Obj", "Temp", "UserSettings", ".git"}
MARKERS = {
    "descriptor_fields": ("customExpressions:", "expressionParameters:", "baseAnimationLayers:"),
    "avatar_descriptor_type": ("VRCAvatarDescriptor",),
    "modular_avatar": ("nadena.dev.modular-avatar", "ModularAvatar"),
    "vrcfury": ("VRCFury", "vrcfury"),
    "physbones": ("VRCPhysBone", "VRCPhysBoneCollider", "PhysBone"),
    "contacts": ("VRCContact", "ContactReceiver", "ContactSender"),
    "animator": ("AnimatorController", "m_Controller", "m_AnimatorController"),
}
PACKAGE_HINTS = {
    "com.vrchat.avatars": "vrchat_sdk_avatars",
    "com.vrchat.base": "vrchat_sdk_base",
    "nadena.dev.modular-avatar": "modular_avatar",
    "nadena.dev.ndmf": "ndmf",
    "com.anatawa12.avatar-optimizer": "avatar_optimizer",
    "vrchat.blackstartx.gesture-manager": "gesture_manager",
    "com.coplaydev.unity-mcp": "mcp_for_unity",
}


def read_text(path: Path, limit: int | None = None) -> str:
    """Read UTF-8 text without changing the source file."""

    try:
        with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
            if limit is None:
                return handle.read()
            return handle.read(limit)
    except OSError:
        return ""


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def iter_files(root: Path, suffixes: set[str] | None = None) -> Iterable[Path]:
    """Yield sorted files while skipping Unity caches and VCS metadata."""

    if not root.exists():
        return
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if suffixes is not None and path.suffix.lower() not in suffixes:
            continue
        yield path


def parse_json_file(path: Path) -> tuple[Any | None, str | None]:
    if not path.exists():
        return None, "missing"
    try:
        return json.loads(read_text(path)), None
    except json.JSONDecodeError as exc:
        return None, f"invalid_json:{exc.msg}"


def add_diagnostic(
    diagnostics: list[dict[str, Any]],
    severity: str,
    code: str,
    message_zh: str,
    evidence: list[str] | None = None,
    layer: str = "source_static",
) -> None:
    diagnostics.append(
        {
            "severity": severity,
            "code": code,
            "message_zh": message_zh,
            "evidence": sorted(set(evidence or [])),
            "evidence_layer": layer,
        }
    )


def parse_project_version(project_root: Path, diagnostics: list[dict[str, Any]]) -> dict[str, Any]:
    path = project_root / "ProjectSettings" / "ProjectVersion.txt"
    text = read_text(path)
    match = re.search(r"^m_EditorVersion:\s*(\S+)", text, re.MULTILINE)
    version = match.group(1) if match else None
    if not path.exists():
        add_diagnostic(diagnostics, "error", "missing_project_version", "缺少 Unity ProjectVersion.txt。", [relative(path, project_root)])
    elif not version:
        add_diagnostic(diagnostics, "warning", "unity_version_unresolved", "无法从 ProjectVersion.txt 解析 Unity 版本。", [relative(path, project_root)])
    return {"path": relative(path, project_root), "version": version}


def package_path_from_lock(package_id: str, record: dict[str, Any]) -> Path | None:
    version = str(record.get("version", ""))
    if version.startswith("file:"):
        return Path(version[5:].replace("/", "\\"))
    if record.get("source") == "embedded":
        return Path(package_id)
    return None


def audit_packages(project_root: Path, diagnostics: list[dict[str, Any]]) -> dict[str, Any]:
    packages_dir = project_root / "Packages"
    manifest_path = packages_dir / "manifest.json"
    lock_path = packages_dir / "packages-lock.json"
    vpm_path = packages_dir / "vpm-manifest.json"
    manifest, manifest_error = parse_json_file(manifest_path)
    lock, lock_error = parse_json_file(lock_path)
    vpm, vpm_error = parse_json_file(vpm_path)

    if manifest_error == "missing":
        add_diagnostic(diagnostics, "error", "missing_manifest", "缺少 Packages/manifest.json。", [relative(manifest_path, project_root)])
    elif manifest_error:
        add_diagnostic(diagnostics, "error", "invalid_manifest", "Packages/manifest.json 不是有效 JSON。", [relative(manifest_path, project_root)])
    if lock_error not in (None, "missing"):
        add_diagnostic(diagnostics, "warning", "invalid_packages_lock", "packages-lock.json 无法解析，包版本审计不完整。", [relative(lock_path, project_root)])

    manifest_deps = (manifest or {}).get("dependencies", {}) if isinstance(manifest, dict) else {}
    lock_deps = (lock or {}).get("dependencies", {}) if isinstance(lock, dict) else {}
    if not isinstance(manifest_deps, dict):
        manifest_deps = {}
    if not isinstance(lock_deps, dict):
        lock_deps = {}

    package_ids = sorted(set(manifest_deps) | set(lock_deps))
    packages: list[dict[str, Any]] = []
    for package_id in package_ids:
        lock_record = lock_deps.get(package_id, {})
        if not isinstance(lock_record, dict):
            lock_record = {}
        local_relative = package_path_from_lock(package_id, lock_record)
        local_package_json = None
        local_exists = None
        if local_relative is not None:
            local_path = packages_dir / local_relative
            local_package_json = local_path / "package.json"
            local_exists = local_path.exists()
            if not local_exists:
                add_diagnostic(
                    diagnostics,
                    "warning",
                    "missing_local_package",
                    f"本地包路径不存在：{package_id}。",
                    [relative(local_path, project_root), relative(lock_path, project_root)],
                )

        package_json, package_json_error = parse_json_file(local_package_json) if local_package_json else (None, None)
        packages.append(
            {
                "id": package_id,
                "category": PACKAGE_HINTS.get(package_id),
                "manifest_version": manifest_deps.get(package_id),
                "lock_version": lock_record.get("version"),
                "lock_source": lock_record.get("source"),
                "lock_depth": lock_record.get("depth"),
                "local_path": relative(packages_dir / local_relative, project_root) if local_relative else None,
                "local_exists": local_exists,
                "package_json_version": (package_json or {}).get("version") if isinstance(package_json, dict) else None,
                "package_json_error": package_json_error,
            }
        )

    manifest_text = read_text(manifest_path)
    external_paths = sorted(set(re.findall(r"(?i)(?:file:)?([a-z]:[/\\][^\"\s,}]+)", manifest_text)))
    if external_paths:
        add_diagnostic(
            diagnostics,
            "warning",
            "external_absolute_package_path",
            "Manifest 含外部绝对包路径，工程可复现性受影响。",
            [relative(manifest_path, project_root)] + external_paths,
        )

    return {
        "manifest": relative(manifest_path, project_root),
        "lock": relative(lock_path, project_root) if lock_path.exists() else None,
        "vpm_manifest": relative(vpm_path, project_root) if vpm_error != "missing" else None,
        "vpm_manifest_status": "valid" if isinstance(vpm, dict) else (vpm_error or "absent"),
        "packages": packages,
    }


def build_guid_index(project_root: Path) -> dict[str, str]:
    index: dict[str, str] = {}
    assets = project_root / "Assets"
    for meta in iter_files(assets, {".meta"}):
        match = re.search(r"^guid:\s*([0-9a-f]{32})\s*$", read_text(meta, 4096), re.MULTILINE | re.IGNORECASE)
        if match:
            index.setdefault(match.group(1).lower(), relative(meta.with_suffix(""), project_root))
    return index


def marker_counts(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for group, needles in MARKERS.items():
        count = sum(text.count(needle) for needle in needles)
        if count:
            counts[group] = count
    return counts


def find_asset_candidates(
    project_root: Path,
    avatar_roots: list[str],
    guid_index: dict[str, str],
) -> dict[str, Any]:
    assets = project_root / "Assets"
    scenes: list[str] = []
    candidates: list[dict[str, Any]] = []
    root_hits: list[dict[str, Any]] = []
    root_patterns = (
        ("m_Name", re.compile(r"^\s*m_Name:\s*(.+?)\s*$", re.MULTILINE)),
        ("serialized_value", re.compile(r"^\s*value:\s*(.+?)\s*$", re.MULTILINE)),
    )
    requested_lower = [value.casefold() for value in avatar_roots]
    for path in iter_files(assets, TEXT_EXTENSIONS):
        rel = relative(path, project_root)
        if path.suffix.lower() == ".unity":
            scenes.append(rel)
        if path.suffix.lower() not in {".unity", ".prefab", ".asset"}:
            continue
        text = read_text(path)
        counts = marker_counts(text)
        name_hits: list[dict[str, str]] = []
        for field_name, pattern in root_patterns:
            for match in pattern.finditer(text):
                name = match.group(1).strip()
                if name and name.casefold() in requested_lower:
                    name_hits.append({"asset": rel, "name": name, "source_field": field_name})
        requested_name_hits = sorted({item["name"] for item in name_hits})
        root_hits.extend(name_hits)
        score = (counts.get("descriptor_fields", 0) * 3) + sum(counts.get(key, 0) for key in ("modular_avatar", "vrcfury", "physbones", "contacts"))
        if requested_name_hits:
            score += 2
        if score == 0:
            continue
        refs = sorted(set(match.group(1).lower() for match in re.finditer(r"\bguid:\s*([0-9a-f]{32})\b", text, re.IGNORECASE)))
        candidates.append(
            {
                "asset": rel,
                "kind": path.suffix.lower().lstrip("."),
                "score": score,
                "marker_counts": counts,
                "requested_root_name_hits": requested_name_hits,
                "referenced_guids": [{"guid": guid, "asset": guid_index.get(guid)} for guid in refs],
            }
        )
    candidates.sort(key=lambda item: (-item["score"], item["asset"]))
    return {
        "scene_files": sorted(scenes),
        "descriptor_candidates": candidates[:100],
        "root_name_hits": sorted(root_hits, key=lambda item: (item["name"].casefold(), item["asset"])),
        "guid_index_size": len(guid_index),
    }


def inspect_logs(project_root: Path, diagnostics: list[dict[str, Any]]) -> dict[str, Any]:
    log_root = project_root / "Logs"
    patterns = {
        "compile_error": re.compile(r"(?i)\berror\s+CS\d+\b|script compilation failed|compilation failed"),
        "sdk_patcher": re.compile(r"(?i)sdk\s*patcher"),
    }
    hits: dict[str, list[dict[str, Any]]] = {key: [] for key in patterns}
    for path in iter_files(log_root, {".log", ".txt"}):
        text = read_text(path, 256 * 1024)
        for kind, pattern in patterns.items():
            lines = [line.strip() for line in text.splitlines() if pattern.search(line)]
            if lines:
                hits[kind].append({"file": relative(path, project_root), "sample": lines[:10], "count": len(lines)})
                code = "compile_errors_in_logs" if kind == "compile_error" else "sdk_patcher_warning"
                message = "日志中发现编译错误，后续 Unity/MCP/构建检查可能不可靠。" if kind == "compile_error" else "日志中出现 SDK Patcher 相关信息，需确认是否为旧版或阻断性警告。"
                add_diagnostic(diagnostics, "warning", code, message, [relative(path, project_root)])
    return hits


def runtime_gates(project_root: Path, package_report: dict[str, Any]) -> dict[str, Any]:
    unity_lock = project_root / "Temp" / "UnityLockfile"
    has_mcp = any(package.get("category") == "mcp_for_unity" for package in package_report["packages"])
    return {
        "unity_lockfile_present": unity_lock.exists(),
        "mcp_package_detected": has_mcp,
        "mcp_ready_for_tools": "not_checked",
        "mcp_snapshot_freshness": "not_checked",
        "unity_running_as_admin": "not_checked",
        "semantic_inspection_allowed": False,
        "note_zh": "静态扫描器不会探测管理员权限、MCP 新鲜度或 Unity 进程；需用实时语义检查单独确认。",
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    project_root = Path(args.project).expanduser().resolve()
    if not project_root.is_dir():
        raise FileNotFoundError(f"Project root does not exist: {project_root}")
    if args.json_out:
        output_path = args.json_out.expanduser().resolve()
        try:
            output_path.relative_to(project_root)
        except ValueError:
            pass
        else:
            raise ValueError("--json-out must be outside the Unity project to preserve read-only scope")
    diagnostics: list[dict[str, Any]] = []
    required_dirs = {name: (project_root / name).is_dir() for name in ("Assets", "Packages", "ProjectSettings")}
    for name, present in required_dirs.items():
        if not present:
            add_diagnostic(diagnostics, "error", f"missing_{name.lower()}", f"工程根缺少 {name}/。", [name])
    git_present = (project_root / ".git").exists()
    if not git_present:
        add_diagnostic(diagnostics, "warning", "git_not_detected", "工程根未发现 Git 元数据，修改前需要显式备份。", [".git"])

    version = parse_project_version(project_root, diagnostics)
    packages = audit_packages(project_root, diagnostics)
    guid_index = build_guid_index(project_root)
    assets = find_asset_candidates(project_root, args.avatar_root, guid_index)
    logs = inspect_logs(project_root, diagnostics)

    requested_scene = args.scene.replace("\\", "/") if args.scene else None
    scene_exists = None
    if requested_scene:
        scene_path = project_root / Path(requested_scene)
        scene_exists = scene_path.is_file()
        if not scene_exists:
            add_diagnostic(diagnostics, "warning", "requested_scene_not_found", f"指定场景不存在：{requested_scene}。", [requested_scene])

    if not assets["descriptor_candidates"]:
        add_diagnostic(diagnostics, "warning", "avatar_descriptor_not_located", "静态扫描未定位到明显的 AvatarDescriptor 候选；需要检查序列化脚本 GUID 或使用 Unity 语义检查。", ["Assets/"])

    diagnostics.sort(key=lambda item: (item["severity"], item["code"], item["evidence"]))
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": "scan_unity_avatar", "version": "1.0", "read_only": True},
        "project": {
            "root": str(project_root),
            "required_directories": required_dirs,
            "git_present": git_present,
            "unity": version,
            "requested_scene": {"path": requested_scene, "exists": scene_exists},
            "requested_avatar_roots": args.avatar_root,
        },
        "packages": packages,
        "assets": assets,
        "logs": logs,
        "runtime_gates": runtime_gates(project_root, packages),
        "diagnostics": diagnostics,
        "scope": {
            "writes_performed": False,
            "upload_attempted": False,
            "csharp_executed": False,
        },
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="Unity project root")
    parser.add_argument("--scene", help="Expected scene path relative to project root")
    parser.add_argument("--avatar-root", action="append", default=[], help="Avatar root name to prioritize; repeatable")
    parser.add_argument("--json-out", type=Path, help="Optional report path outside the project")
    parser.add_argument("--pretty", action="store_true", help="Indent JSON output")
    parser.add_argument("--fail-on", choices=("none", "warning", "error"), default="none")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        report = build_report(args)
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(json.dumps({"schema_version": SCHEMA_VERSION, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    indent = 2 if args.pretty else None
    output = json.dumps(report, ensure_ascii=False, indent=indent, sort_keys=True) + "\n"
    if args.json_out:
        output_path = args.json_out.expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(output)
    if args.fail_on != "none":
        rank = {"warning": 1, "error": 2}
        threshold = rank[args.fail_on]
        if any(rank.get(item["severity"], 0) >= threshold for item in report["diagnostics"]):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
