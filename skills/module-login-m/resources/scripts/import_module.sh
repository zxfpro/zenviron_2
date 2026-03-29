#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="${1:-}"
TARGET_DIR="${2:-}"

if [[ -z "$SKILL_DIR" || -z "$TARGET_DIR" ]]; then
  echo "Usage: $0 <module-skill-dir> <target-project-dir>"
  exit 1
fi

MODULE_SRC="$SKILL_DIR/resources/module"
SPEC_DIR="$SKILL_DIR/resources/spec"
REPORT_DIR="$SKILL_DIR/resources/reports"

if [[ ! -d "$MODULE_SRC" ]]; then
  echo "Missing module source directory: $MODULE_SRC"
  exit 1
fi

mkdir -p "$TARGET_DIR" "$REPORT_DIR"
timestamp="$(date +%Y%m%d-%H%M%S)"
report="$REPORT_DIR/import-${timestamp}.md"

echo "# Module Import Report" > "$report"
echo "" >> "$report"
echo "- Skill dir: \`$SKILL_DIR\`" >> "$report"
echo "- Target dir: \`$TARGET_DIR\`" >> "$report"
echo "- Time: \`$timestamp\`" >> "$report"
echo "" >> "$report"
echo "## Copy Summary" >> "$report"

# Direct-copy strategy with micro-adjust friendly safe mode: do not overwrite existing files.
rsync -a --ignore-existing "$MODULE_SRC"/ "$TARGET_DIR"/

echo "- Copied payload from \`resources/module/\`" >> "$report"
echo "- Existing files preserved (ignore-existing)" >> "$report"
echo "" >> "$report"
echo "## Next Steps" >> "$report"
echo "1. Follow \`$SPEC_DIR/INTEGRATION.md\` for integration touchpoints." >> "$report"
echo "2. Follow \`$SPEC_DIR/USAGE.md\` for run and verify steps." >> "$report"
echo "3. Apply micro-adjustments only at integration boundaries." >> "$report"

echo "Import finished. Report: $report"
