from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Optional

import typer

from zenviron.templating import (
    InitResult,
    discover_templates,
    github_name_candidates,
    module_name_from_slug,
    render_project,
    resolve_local_target,
    slugify,
    write_state_file,
)

app = typer.Typer(help="Zenviron CLI for AI-ready project templates and skills")
templates_app = typer.Typer(help="Manage template discovery")
skills_app = typer.Typer(help="Install skills into project or user scope")
app.add_typer(templates_app, name="templates")
app.add_typer(skills_app, name="skills")


def _template_root() -> Path:
    env_path = os.getenv("ZENVIRON_TEMPLATE_ROOT")
    if env_path:
        return Path(env_path).expanduser().resolve()
    return Path(__file__).resolve().parents[2] / "template"


@templates_app.command("list")
def list_templates() -> None:
    """List auto-discovered templates with health checks."""
    root = _template_root()
    templates = discover_templates(root)
    if not templates:
        typer.echo(f"No templates found under {root}")
        raise typer.Exit(code=1)

    for item in templates:
        typer.echo(f"{item.name}\t{item.status}\t{item.message}")


@app.command()
def init(
    project_name: str = typer.Argument(..., help="Human friendly project name"),
    template: str = typer.Option("monorepo", "--template", help="Template name under template/<name>"),
    target_dir: Path = typer.Option(Path.cwd(), "--target-dir", help="Directory where project is created"),
    with_skills: bool = typer.Option(True, "--with-skills/--without-skills", help="Copy template skill folder into .agents/skills"),
) -> None:
    """Create a new project from template skeleton."""
    template_dir = _template_root() / template
    skeleton_dir = template_dir / "skeleton"
    if not skeleton_dir.exists():
        typer.echo(f"Template '{template}' invalid: missing skeleton/ at {skeleton_dir}")
        raise typer.Exit(code=1)

    repo_slug = slugify(project_name)
    module_name = module_name_from_slug(repo_slug)

    base_dir = target_dir.expanduser().resolve()
    final_target = resolve_local_target(base_dir, repo_slug)

    variables = {
        "PROJECT_NAME": project_name,
        "MODULE_NAME": module_name,
        "REPO_SLUG": final_target.name,
    }
    render_project(skeleton_dir, final_target, variables)

    if with_skills:
        skill_file = template_dir / "SKILL.md"
        if skill_file.exists():
            skills_dest = final_target / ".agents" / "skills" / template
            skills_dest.mkdir(parents=True, exist_ok=True)
            shutil.copy2(skill_file, skills_dest / "SKILL.md")

    result = InitResult(
        project_name=project_name,
        module_name=module_name,
        repo_slug=final_target.name,
        target_dir=final_target,
    )
    write_state_file(final_target, result)

    readme = final_target / "README.md"
    if readme.exists():
        readme_text = readme.read_text(encoding="utf-8")
        readme_text += f"\n\n## Repository Name Candidates\n{', '.join(github_name_candidates(final_target.name))}\n"
        readme.write_text(readme_text, encoding="utf-8")

    typer.echo(f"Created project at {final_target}")


@skills_app.command("install")
def install_skills(
    mode: str = typer.Option("project", "--mode", help="project or user"),
    dest: Optional[Path] = typer.Option(None, "--dest", help="Target path for skills installation"),
    template: str = typer.Option("monorepo", "--template", help="Template skill source"),
) -> None:
    """Install skills from template into target location."""
    if mode not in {"project", "user"}:
        typer.echo("--mode must be one of: project, user")
        raise typer.Exit(code=1)

    template_dir = _template_root() / template
    skill_src = template_dir / "SKILL.md"
    if not skill_src.exists():
        typer.echo(f"Missing SKILL.md in template: {template}")
        raise typer.Exit(code=1)

    if dest is None:
        if mode == "project":
            dest = Path.cwd() / ".agents" / "skills" / template
        else:
            home = Path(os.getenv("CODEX_HOME", Path.home() / ".codex"))
            dest = home / "skills" / template

    final_dest = dest.expanduser().resolve()
    final_dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(skill_src, final_dest / "SKILL.md")
    typer.echo(f"Installed skill into {final_dest}")


@app.command()
def doctor() -> None:
    """Basic environment checks."""
    checks = {
        "template_root_exists": _template_root().exists(),
        "codex_home": str(Path(os.getenv("CODEX_HOME", Path.home() / ".codex")).expanduser()),
        "cwd": str(Path.cwd()),
    }
    for key, value in checks.items():
        typer.echo(f"{key}: {value}")


if __name__ == "__main__":
    app()
