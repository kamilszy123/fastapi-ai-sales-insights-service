#!/bin/bash
INPUT=$(cat)

if ! command -v jq >/dev/null 2>&1; then
  echo "protect-files.sh: jq is required but missing. Blocking until fixed." >&2
  exit 2
fi

FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

PROTECTED_PATTERNS=(".env" "package-lock.json" ".git/")

for pattern in "${PROTECTED_PATTERNS[@]}"; do
  if [[ "$FILE_PATH" == *"$pattern"* ]] || [[ "$COMMAND" == *"$pattern"* ]]; then
    echo "Blocked: matches protected pattern '$pattern'" >&2
    exit 2
  fi
done

exit 0