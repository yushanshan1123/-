#!/usr/bin/env bash
set -euo pipefail

TOKEN="$1"
REPO_URL="https://github.com/yushanshan1123/-.git"
WORKDIR="/home/ubuntu/.openclaw/workspace"
PUSHDIR="/home/ubuntu/.openclaw/workspace/.tmp_github_push"

rm -rf "$PUSHDIR"
mkdir -p "$PUSHDIR"

# Export a clean copy of the project (exclude local-only dirs)
cd "$WORKDIR"

tar --exclude='./.git' --exclude='./dist' --exclude='./memory' --exclude='*/__pycache__' \
  --exclude='./.agents' --exclude='./.agent' --exclude='./binance-skills-hub' --exclude='./.openclaw' \
  --exclude='./*.sqlite3' --exclude='./trade_review_records.json' \
  -czf "$PUSHDIR/src.tar.gz" .

cd "$PUSHDIR"
tar -xzf src.tar.gz
rm src.tar.gz

# Init git repo
rm -rf .git
git init -q

git add -A

git commit -q -m "Contest demo: contract calmness checker" || true

# Push using token without echoing it in parent process output
git branch -M main

git remote add origin "https://x-access-token:${TOKEN}@github.com/yushanshan1123/-.git"

git push -u -f origin main -q

echo "PUSH_OK"
