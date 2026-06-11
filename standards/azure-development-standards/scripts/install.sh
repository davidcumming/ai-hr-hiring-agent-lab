#!/usr/bin/env bash
#
# install.sh — sync the canonical GenTech skill packages and agent role files
#              into the locations Claude Code and Codex actually scan.
#
# Usage:
#   scripts/install.sh <target-project-dir> [--copy]
#
#   <target-project-dir>   The consuming project repo to install into (required).
#   --copy                 Use rsync copy instead of symlinks (default: symlink).
#                          Use --copy when symlinks are undesirable (e.g. Windows,
#                          or you want a frozen vendored snapshot).
#
# What it does (idempotent):
#   Canonical source (this standards repo):
#     Skills/.agents/skills/   ->  the 33 skill packages
#     agents/                  ->  the agent role files
#
#   Installed into the target so both tools auto-discover them:
#     <target>/.agents/skills/   (Codex scans .agents/skills/ at repo root)
#     <target>/.claude/skills/   (Claude Code scans .claude/skills/)
#     <target>/.claude/agents/   (Claude Code scans .claude/agents/)
#
#   The same skill set is installed to both skills/ locations; the agent role
#   files go to .claude/agents/ (Codex reads role files as attached prompts and
#   does not require a fixed scan dir for them).
#
# Notes:
#   - Idempotent: re-running refreshes symlinks / re-syncs files in place.
#   - Prints every link / sync it performs.
#   - Non-destructive to unrelated files in the target.
#   - The hidden canonical source folder (Skills/.agents/skills/) is invisible in
#     Finder and Obsidian; a proposal to un-hide it is recorded as ADR-0005 under
#     Initial_Documentation/adr/. This script is the interim bridge until then.
#
set -euo pipefail

# --- resolve paths ----------------------------------------------------------

# Standards-repo root = parent of this script's directory.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SKILLS_SRC="$SOURCE_ROOT/Skills/.agents/skills"
AGENTS_SRC="$SOURCE_ROOT/agents"

# --- parse args -------------------------------------------------------------

MODE="symlink"
TARGET=""

for arg in "$@"; do
  case "$arg" in
    --copy) MODE="copy" ;;
    -h|--help)
      sed -n '2,30p' "$0"   # print the usage header above
      exit 0
      ;;
    *)
      if [[ -z "$TARGET" ]]; then
        TARGET="$arg"
      else
        echo "error: unexpected argument: $arg" >&2
        exit 2
      fi
      ;;
  esac
done

if [[ -z "$TARGET" ]]; then
  echo "error: target project directory is required" >&2
  echo "usage: scripts/install.sh <target-project-dir> [--copy]" >&2
  exit 2
fi

if [[ ! -d "$TARGET" ]]; then
  echo "error: target is not a directory: $TARGET" >&2
  exit 2
fi
TARGET="$(cd "$TARGET" && pwd)"

# Sanity-check the canonical source actually exists.
for d in "$SKILLS_SRC" "$AGENTS_SRC"; do
  if [[ ! -d "$d" ]]; then
    echo "error: canonical source missing: $d" >&2
    exit 1
  fi
done

echo "Installing GenTech skills + agent roles"
echo "  source: $SOURCE_ROOT"
echo "  target: $TARGET"
echo "  mode:   $MODE"
echo

# --- helpers ----------------------------------------------------------------

# link_or_copy <src-dir> <dest-dir>
# Mirrors the *contents* of src-dir into dest-dir (one entry per child).
link_or_copy() {
  local src="$1" dest="$2"
  mkdir -p "$dest"
  local entry name
  for entry in "$src"/*; do
    [[ -e "$entry" ]] || continue          # empty-glob guard
    name="$(basename "$entry")"
    local out="$dest/$name"
    if [[ "$MODE" == "symlink" ]]; then
      # Idempotent: replace any existing link/dir at the destination name.
      rm -rf "$out"
      ln -s "$entry" "$out"
      echo "  link  $out -> $entry"
    else
      rsync -a --delete "$entry/" "$out/" 2>/dev/null || rsync -a "$entry" "$dest/"
      echo "  sync  $out"
    fi
  done
}

# --- install skills (both scan locations) -----------------------------------

echo "Skills -> .agents/skills/ (Codex)"
link_or_copy "$SKILLS_SRC" "$TARGET/.agents/skills"
echo

echo "Skills -> .claude/skills/ (Claude Code)"
link_or_copy "$SKILLS_SRC" "$TARGET/.claude/skills"
echo

# --- install agent roles (Claude Code scan location) ------------------------

echo "Agent roles -> .claude/agents/ (Claude Code)"
link_or_copy "$AGENTS_SRC" "$TARGET/.claude/agents"
echo

echo "Done. Re-run any time to refresh; the operation is idempotent."
