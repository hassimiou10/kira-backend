#!/bin/bash

DOMAIN="${1:-kira-app.com}"
API_DOMAIN="api.${DOMAIN}"

echo "════════════════════════════════════════"
echo "  Vérification DNS & SSL — $DOMAIN"
echo "════════════════════════════════════════"

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'

pass() { echo -e "${GREEN}✅ $1${NC}"; }
fail() { echo -e "${RED}❌ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }

echo ""
echo "1. DNS..."
API_IP=$(dig +short CNAME "$API_DOMAIN" 2>/dev/null | head -1)
ROOT_IP=$(dig +short A "$DOMAIN" 2>/dev/null | head -1)
[ -n "$API_IP" ] && pass "api.$DOMAIN → $API_IP" || fail "api.$DOMAIN non résolu"
[ -n "$ROOT_IP" ] && pass "$DOMAIN → $ROOT_IP" || fail "$DOMAIN non résolu"

echo ""
echo "2. SSL..."
check_ssl() {
  local host=$1
  CERT=$(echo | openssl s_client -connect "$host:443" -servername "$host" 2>/dev/null \
    | openssl x509 -noout -dates 2>/dev/null)
  [ $? -eq 0 ] && pass "$host → SSL valide" || fail "$host → SSL invalide"
}
check_ssl "$API_DOMAIN"
check_ssl "$DOMAIN"

echo ""
echo "3. HTTPS Redirect..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "http://$DOMAIN" 2>/dev/null)
[ "$HTTP_STATUS" = "301" ] || [ "$HTTP_STATUS" = "302" ] && \
  pass "HTTP → HTTPS ($HTTP_STATUS)" || warn "Redirect: $HTTP_STATUS"

echo ""
echo "4. API Health..."
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "https://$API_DOMAIN/api/health/")
[ "$HEALTH" = "200" ] && pass "Health check OK" || fail "Health: $HEALTH"

echo ""
echo "════════════════════════════════════════"
echo -e "${GREEN}  🌐 Vérification terminée${NC}"
echo "  Site  : https://$DOMAIN"
echo "  API   : https://$API_DOMAIN/api/"
echo "  Docs  : https://$API_DOMAIN/api/docs/"
echo "════════════════════════════════════════"