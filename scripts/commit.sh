#!/usr/bin/env bash
# Commit thay doi trang thai/bai va day len, thu lai neu bi xung dot.
set -u
msg="${1:-cap nhat}"
git config user.name "anshin-bot"
git config user.email "anshin-bot@users.noreply.github.com"
git add -A posts state queue nhat-ky-chu-de.md 2>/dev/null
git diff --cached --quiet && { echo "khong co thay doi"; exit 0; }
git commit -q -m "$msg"
for i in 1 2 3 4 5; do
  git pull -q --rebase -X theirs origin "${GITHUB_REF_NAME:-main}" && git push -q origin HEAD:"${GITHUB_REF_NAME:-main}" && exit 0
  sleep $((i * 3))
done
echo "day len that bai" >&2; exit 1
