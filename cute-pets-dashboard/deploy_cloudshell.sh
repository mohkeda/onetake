#!/usr/bin/env bash
# Build and deploy the Firebase version of the dashboard from Google Cloud Shell.
# Usage (inside a clone of this repo):  bash cute-pets-dashboard/deploy_cloudshell.sh EDITOR_EMAIL [VIEWER_EMAILS_COMMA_SEPARATED] [PROJECT_ID]
# The web config is fetched from Firebase at run time, so nothing project-specific is stored in the repo.
set -euo pipefail
EMAIL="${1:?editor e-mail required}"
VIEWERS="${2:-}"
PROJECT="${3:-cutepets-monthly-report}"
cd "$(dirname "$0")"

if ! firebase projects:list >/dev/null 2>&1; then
  echo ">> Firebase CLI is not signed in. Follow the link, approve, and paste the code back here."
  firebase login --no-localhost
fi

echo ">> Fetching web app config for $PROJECT"
firebase apps:sdkconfig WEB --project "$PROJECT" > /tmp/sdkconfig.txt
python3 - <<'PY'
import json, re
t = open('/tmp/sdkconfig.txt').read()
m = re.search(r'\{.*\}', t, re.S)
s = m.group(0)
try:
    cfg = json.loads(s)
except Exception:
    s2 = re.sub(r'([{,]\s*)([A-Za-z_]\w*)\s*:', r'\1"\2":', s)
    s2 = re.sub(r',\s*}', '}', s2)
    cfg = json.loads(s2)
keep = {k: cfg[k] for k in ("apiKey", "authDomain", "projectId", "storageBucket", "messagingSenderId", "appId") if k in cfg}
json.dump(keep, open('firebase-config.json', 'w'), indent=2)
print("config:", keep["projectId"], keep["appId"])
PY

sed -i "s/'OWNER@gmail.com'/'$EMAIL'/" firebase/firestore.rules
if [ -n "$VIEWERS" ]; then
  LIST=$(echo "$VIEWERS" | tr 'A-Z' 'a-z' | sed "s/[[:space:]]//g; s/,/','/g")
  sed -i "s/editors().concat(\[\])/editors().concat(['$LIST'])/" firebase/firestore.rules
fi
grep -n "function editors\|function viewers" firebase/firestore.rules
python3 build_firebase.py index.html firebase firebase-config.json

cd firebase
firebase deploy --project "$PROJECT" --non-interactive
git -C .. checkout -- firebase/firestore.rules firebase/public/index.html 2>/dev/null || true
echo ">> Done: https://$PROJECT.web.app"
