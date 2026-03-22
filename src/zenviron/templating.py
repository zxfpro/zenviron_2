from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*([A-Z_]+)\s*\}\}")


@dataclass(frozen=True)
class TemplateStatus:
    name: str
    path: Path
    status: str
    message: str


@dataclass(frozen=True)
class InitResult:
    project_name: str
    module_name: str
    repo_slug: str
    target_dir: Path


def discover_templates(template_root: Path) -> list[TemplateStatus]:
    if not template_root.exists():
        return []

    items: list[TemplateStatus] = []
    for path in sorted(template_root.iterdir()):
        if not path.is_dir():
            continue

        skeleton = path / "skeleton"
        skill = path / "SKILL.md"
        if not skeleton.exists():
            items.append(TemplateStatus(path.name, path, "error", "missing skeleton/"))
            continue

        unclosed = _find_unclosed_placeholders(skeleton)
        if unclosed:
            items.append(TemplateStatus(path.name, path, "error", f"unclosed placeholders in {unclosed[0]}"))
            continue

        if not skill.exists():
            items.append(TemplateStatus(path.name, path, "warn", "missing SKILL.md"))
            continue

        items.append(TemplateStatus(path.name, path, "ok", "healthy"))

    return items


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9\-\s_]", "", name).strip().lower()
    slug = slug.replace("_", "-")
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug or "project"


def module_name_from_slug(slug: str) -> str:
    return slug.replace("-", "_")


def resolve_local_target(base_dir: Path, desired_slug: str) -> Path:
    first = base_dir / desired_slug
    if not first.exists():
        return first

    for i in range(2, 22):
        candidate = base_dir / f"{desired_slug}-{i}"
        if not candidate.exists():
            return candidate

    return base_dir / f"{desired_slug}-{datetime.now().strftime('%Y%m%d-%H%M')}"


def github_name_candidates(slug: str) -> list[str]:
    return [
        slug,
        f"{slug}-app",
        f"{slug}-monorepo",
        f"{slug}-{datetime.now().strftime('%Y%m%d')}",
    ]


def render_project(template_dir: Path, destination: Path, variables: dict[str, str]) -> None:
    destination.mkdir(parents=True, exist_ok=True)

    for src in template_dir.rglob("*"):
        rel = src.relative_to(template_dir)
        dst = destination / rel
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            continue

        if _is_text_file(src):
            content = src.read_text(encoding="utf-8")
            for key, value in variables.items():
                content = content.replace(f"{{{{ {key} }}}}", value)
                content = content.replace(f"{{{{{key}}}}}", value)
            dst.write_text(content, encoding="utf-8")
        else:
            dst.write_bytes(src.read_bytes())


def write_state_file(root: Path, result: InitResult) -> None:
    payload = {
        "display_name": result.project_name,
        "repo_slug": result.repo_slug,
        "module_name": result.module_name,
        "target_dir": str(result.target_dir),
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    (root / ".zenviron-state.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _is_text_file(path: Path) -> bool:
    return path.suffix.lower() in {
        ".md",
        ".txt",
        ".toml",
        ".json",
        ".yml",
        ".yaml",
        ".py",
        ".sh",
        ".env",
        ".gitignore",
    }


def _find_unclosed_placeholders(root: Path) -> list[Path]:
    bad: list[Path] = []
    for file in root.rglob("*"):
        if file.is_dir() or not _is_text_file(file):
            continue
        content = file.read_text(encoding="utf-8")
        opens = content.count("{{")
        closes = content.count("}}")
        if opens != closes:
            bad.append(file)
            continue
        for token in re.findall(r"\{\{(.*?)\}\}", content):
            if token.strip() and not PLACEHOLDER_PATTERN.match(f"{{{{{token}}}}}"):
                bad.append(file)
                break
    return bad
