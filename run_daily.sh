#!/usr/bin/env bash
set -euo pipefail

REPO="/home/siyu/git/BOC-Currency-Crawler"
PY="$REPO/.venv/bin/python"

cd "$REPO"

"$PY" "$REPO/boc_eur_cny_spot.py" fetch
"$PY" "$REPO/boc_eur_cny_spot.py" plot

/usr/bin/git add .
if /usr/bin/git diff --cached --quiet; then
    echo "No changes to commit."
else
    /usr/bin/git commit -m "Update BOC EUR/CNY data $(date '+%F %T')"
    /usr/bin/git push
fi

LAST_RATE="$(tail -n 1 "$REPO/boc_eur_spot.txt" | cut -f2-)"
PLOT_FILE="$REPO/eur_spot_trend.png"
NOW="$(date '+%F %T')"

CAPTION="✅ BOC EUR/CNY daily update
Time: ${NOW}
Latest record:
${LAST_RATE}"

curl -sS -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendPhoto" \
  -F "chat_id=${CHAT_ID}" \
  -F "photo=@${PLOT_FILE}" \
  --form-string "caption=${CAPTION}"
