from __future__ import annotations

from pathlib import Path
import shutil
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_FACTORY_SCRIPT = REPO_ROOT / "skills" / "module-factory" / "resources" / "scripts" / "new_module_skill.sh"
GATE_SCRIPT = REPO_ROOT / "skills" / "module-factory" / "resources" / "scripts" / "validate_gate.sh"


def test_new_module_skill_scaffolds_expected_layout(tmp_path: Path) -> None:
    rc = subprocess.run(
        ["bash", str(MODULE_FACTORY_SCRIPT), "auth-login", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert rc.returncode == 0, rc.stderr

    created = tmp_path / "skills" / "module-auth-login"
    assert (created / "SKILL.md").exists()
    assert (created / "VERSION.md").exists()
    assert (created / "resources" / "module").exists()
    assert (created / "resources" / "spec" / "INTEGRATION.md").exists()
    assert (created / "resources" / "spec" / "USAGE.md").exists()
    assert (created / "resources" / "scripts" / "validate_gate.sh").exists()
    assert (created / "resources" / "scripts" / "import_module.sh").exists()


def test_validate_gate_fails_without_e2e(tmp_path: Path) -> None:
    rc = subprocess.run(
        ["bash", str(MODULE_FACTORY_SCRIPT), "auth-login", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert rc.returncode == 0, rc.stderr

    created = tmp_path / "skills" / "module-auth-login"
    e2e_file = created / "resources" / "spec" / "E2E.md"
    shutil.move(str(e2e_file), str(e2e_file) + ".bak")

    gate = subprocess.run(
        ["bash", str(GATE_SCRIPT), str(created)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert gate.returncode != 0
    assert "missing required file" in gate.stdout.lower()
