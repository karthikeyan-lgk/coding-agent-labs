#!/usr/bin/env bash
# A tiny repo with one staged change for the pipeline to look at. Recreated on every run.
set -euo pipefail
rm -rf out/repo && mkdir -p out/repo && cd out/repo
git init -q -b main
git config user.email ci@example.invalid && git config user.name "release-bot"
cat > billing.py <<'PY'
def invoice_total(items):
    return round(sum(price * qty for price, qty in items), 2)
PY
printf '# Changelog\n\n' > CHANGELOG.md
git add . && git commit -qm "billing: invoice total"
cat > billing.py <<'PY'
def invoice_total(items, discount=0):
    subtotal = sum(price * qty for price, qty in items)
    # discount is a percentage, e.g. 10 for 10%
    return round(subtotal - subtotal * discount, 2)
PY
git add billing.py
