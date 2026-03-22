from pathlib import Path
import os

from typer.testing import CliRunner

from zenviron.cli import app

runner = CliRunner()


def test_templates_list_has_monorepo() -> None:
    result = runner.invoke(app, ["templates", "list"])
    assert result.exit_code == 0
    assert "monorepo" in result.output
    assert "sql-docker" in result.output


def test_init_renders_and_writes_state(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["init", "Demo Project", "--template", "monorepo", "--target-dir", str(tmp_path)],
    )
    assert result.exit_code == 0

    created = tmp_path / "demo-project"
    assert created.exists()
    assert (created / ".zenviron-state.json").exists()
    assert (created / "README.md").read_text(encoding="utf-8").find("Demo Project") >= 0


def test_conflict_suffix(tmp_path: Path) -> None:
    (tmp_path / "demo").mkdir()
    result = runner.invoke(
        app,
        ["init", "Demo", "--template", "monorepo", "--target-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert (tmp_path / "demo-2").exists()


def test_skills_install_project_mode(tmp_path: Path) -> None:
    dest = tmp_path / ".agents" / "skills" / "monorepo"
    result = runner.invoke(
        app,
        ["skills", "install", "--mode", "project", "--dest", str(dest), "--template", "monorepo"],
    )
    assert result.exit_code == 0
    assert (dest / "SKILL.md").exists()


def test_init_sql_docker_template(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["init", "DB Stack", "--template", "sql-docker", "--target-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    created = tmp_path / "db-stack"
    assert (created / "docker-compose.sql.yml").exists()


def test_template_auto_discovery_without_registry(tmp_path: Path) -> None:
    root = tmp_path / "template"
    skeleton = root / "foo" / "skeleton"
    skeleton.mkdir(parents=True)
    (root / "foo" / "SKILL.md").write_text("# foo skill\n", encoding="utf-8")
    (skeleton / "README.md").write_text("# {{ PROJECT_NAME }}\n", encoding="utf-8")

    old = os.environ.get("ZENVIRON_TEMPLATE_ROOT")
    os.environ["ZENVIRON_TEMPLATE_ROOT"] = str(root)
    try:
        result = runner.invoke(app, ["templates", "list"])
        assert result.exit_code == 0
        assert "foo" in result.output
    finally:
        if old is None:
            del os.environ["ZENVIRON_TEMPLATE_ROOT"]
        else:
            os.environ["ZENVIRON_TEMPLATE_ROOT"] = old
