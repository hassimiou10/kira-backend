#!/bin/bash

API_URL="${1:-https://api.kira-app.com}"

echo "════════════════════════════════════════"
echo "  Vérification déploiement KIRA"
echo "  URL : $API_URL"
echo "════════════════════════════════════════"

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'

pass() { echo -e "${GREEN}✅ $1${NC}"; }
fail() { echo -e "${RED}❌ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }

ERRORS=0

echo ""
echo "1. Health Check..."
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/health/")
[ "$HEALTH" = "200" ] && pass "Health check OK" || { fail "Health check: HTTP $HEALTH"; ERRORS=$((ERRORS+1)); }

echo ""
echo "2. Plans de paiement..."
PLANS=$(curl -s "$API_URL/api/payments/plans/" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('data',[])))" 2>/dev/null)
[ "${PLANS:-0}" -ge "3" ] && pass "$PLANS plans disponibles" || fail "Plans: $PLANS"

echo ""
echo "3. Documentation..."
SWAGGER=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/docs/")
[ "$SWAGGER" = "200" ] && pass "Swagger OK" || warn "Swagger: HTTP $SWAGGER"

echo ""
echo "════════════════════════════════════════"
if [ "$ERRORS" -eq 0 ]; then
  echo -e "${GREEN}  🎉 KIRA est opérationnel !${NC}"
else
  echo -e "${RED}  ⚠️  $ERRORS erreur(s) détectée(s)${NC}"
fi
echo "  API  : $API_URL/api/"
echo "  Docs : $API_URL/api/docs/"
echo "════════════════════════════════════════"

exit $ERRORS