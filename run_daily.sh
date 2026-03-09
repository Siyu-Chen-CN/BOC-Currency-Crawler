#!/usr/bin/env bash
set -euo pipefail

REPO="/home/siyu/git/BOC-Currency-Crawler"
PY="$REPO/.venv/bin/python"

cd "$REPO"

# 1. 抓取最新汇率
"$PY" "$REPO/boc_eur_cny_spot.py" fetch

# 2. 画图
"$PY" "$REPO/boc_eur_cny_spot.py" plot

# 3. 提交到 Git
/usr/bin/git add .

# 没有变更就退出，不报错
if /usr/bin/git diff --cached --quiet; then
    echo "No changes to commit."
    exit 0
fi

/usr/bin/git commit -m "Update BOC EUR/CNY data $(date '+%F %T')"

/usr/bin/git push
