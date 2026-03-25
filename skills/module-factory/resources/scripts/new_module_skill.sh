#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <module-slug> [root-dir]"
  echo "Example: $0 auth-login"
  exit 1
fi

MODULE_SLUG="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_SKILL_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
if [[ $# -eq 2 ]]; then
  ROOT_DIR="$(cd "$2" && pwd)"
else
  ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../" && pwd)"
fi

TARGET_SKILL_DIR="$ROOT_DIR/skills/module-${MODULE_SLUG}"
TEMPLATE_DIR="$SOURCE_SKILL_DIR/resources/module-template"
SPEC_TEMPLATE_DIR="$SOURCE_SKILL_DIR/resources/spec-template"

if [[ -e "$TARGET_SKILL_DIR" ]]; then
  echo "Target already exists: $TARGET_SKILL_DIR"
  exit 1
fi

mkdir -p "$TARGET_SKILL_DIR/resources/module" \
  "$TARGET_SKILL_DIR/resources/spec" \
  "$TARGET_SKILL_DIR/resources/scripts" \
  "$TARGET_SKILL_DIR/resources/reports"

cp "$SOURCE_SKILL_DIR/SKILL.md" "$TARGET_SKILL_DIR/SKILL.md"
cp "$SOURCE_SKILL_DIR/VERSION.md" "$TARGET_SKILL_DIR/VERSION.md"
cp -R "$TEMPLATE_DIR/." "$TARGET_SKILL_DIR/resources/module/"
cp -R "$SPEC_TEMPLATE_DIR/." "$TARGET_SKILL_DIR/resources/spec/"
cp "$SOURCE_SKILL_DIR/resources/scripts/validate_gate.sh" "$TARGET_SKILL_DIR/resources/scripts/validate_gate.sh"
cp "$SOURCE_SKILL_DIR/resources/scripts/import_module.sh" "$TARGET_SKILL_DIR/resources/scripts/import_module.sh"
chmod +x "$TARGET_SKILL_DIR/resources/scripts/validate_gate.sh" "$TARGET_SKILL_DIR/resources/scripts/import_module.sh"

sed -i.bak "s/^name: module-factory$/name: module-${MODULE_SLUG}/" "$TARGET_SKILL_DIR/SKILL.md"
sed -i.bak "s/^# module-factory$/# module-${MODULE_SLUG}/" "$TARGET_SKILL_DIR/SKILL.md"
sed -i.bak "s/module-<slug>/module-${MODULE_SLUG}/g" "$TARGET_SKILL_DIR/SKILL.md"
rm -f "$TARGET_SKILL_DIR/SKILL.md.bak"

sed -i.bak "s/name = \"module-name\"/name = \"module-${MODULE_SLUG}\"/" "$TARGET_SKILL_DIR/resources/spec/module.manifest.toml"
rm -f "$TARGET_SKILL_DIR/resources/spec/module.manifest.toml.bak"

echo "Created module skill at: $TARGET_SKILL_DIR"
echo "Next:"
echo "  1) Fill resources/module/* with feature code"
echo "  2) Update resources/spec/*"
echo "  3) Run resources/scripts/validate_gate.sh"
