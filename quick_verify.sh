#!/bin/bash
# Quick Post-Release Verification Script
# Szybkie sprawdzenie czy landing page jest zsynchronizowana z release

set -e

REPO="ai-fresh/ccgate"
LANDING_PAGE="https://ai-fresh.github.io/ccgate/"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}🚀 Quick Release Verification${NC}"
echo -e "${BLUE}================================${NC}\n"

# 1. Get latest release version
echo "📡 Pobieranie najnowszego release..."
LATEST_TAG=$(gh api repos/${REPO}/releases/latest --jq '.tag_name')
LATEST_VERSION=${LATEST_TAG#v}  # Remove 'v' prefix

echo -e "${GREEN}✓${NC} Najnowszy release: ${GREEN}${LATEST_TAG}${NC}\n"

# 2. Check if landing page has the latest version
echo "🔍 Sprawdzanie landing page..."
PAGE_CONTENT=$(curl -s "$LANDING_PAGE")

# Check JSON-LD version
JSON_LD_VERSION=$(echo "$PAGE_CONTENT" | grep -o '"softwareVersion": "[^"]*"' | head -1 | cut -d'"' -f4)

if [ "$JSON_LD_VERSION" = "$LATEST_VERSION" ]; then
    echo -e "${GREEN}✓${NC} JSON-LD wersja: ${GREEN}${JSON_LD_VERSION}${NC}"
else
    echo -e "${RED}✗${NC} JSON-LD wersja: ${RED}${JSON_LD_VERSION}${NC} (oczekiwano: ${YELLOW}${LATEST_VERSION}${NC})"
    echo -e "${YELLOW}  → Uwaga: Może być OK jeśli JavaScript aktualizuje dynamicznie${NC}"
fi

# Check download links
PKG_LINK=$(echo "$PAGE_CONTENT" | grep -o 'href="[^"]*\.pkg"' | head -1 | cut -d'"' -f2)
if echo "$PKG_LINK" | grep -q "$LATEST_VERSION"; then
    echo -e "${GREEN}✓${NC} PKG link: zawiera wersję ${LATEST_VERSION}"
else
    echo -e "${YELLOW}⚠${NC} PKG link: ${PKG_LINK}"
fi

# 3. Test download asset availability
echo -e "\n📦 Sprawdzanie dostępności plików..."
ASSETS=$(gh api repos/${REPO}/releases/latest --jq '.assets[] | "\(.name) \(.browser_download_url)"')

while IFS= read -r line; do
    NAME=$(echo "$line" | awk '{print $1}')
    URL=$(echo "$line" | awk '{print $2}')

    HTTP_CODE=$(curl -sI "$URL" | grep -E "^HTTP" | awk '{print $2}')

    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
        echo -e "${GREEN}✓${NC} ${NAME} (HTTP ${HTTP_CODE})"
    else
        echo -e "${RED}✗${NC} ${NAME} (HTTP ${HTTP_CODE})"
    fi
done <<< "$ASSETS"

# 4. Check SEO files
echo -e "\n🔍 Sprawdzanie plików SEO..."
for file in sitemap.xml robots.txt llms.txt; do
    HTTP_CODE=$(curl -sI "${LANDING_PAGE}${file}" | grep -E "^HTTP" | awk '{print $2}')

    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✓${NC} ${file}"
    else
        echo -e "${RED}✗${NC} ${file} (HTTP ${HTTP_CODE})"
    fi
done

# 5. Check GitHub Pages status
echo -e "\n🌐 Sprawdzanie GitHub Pages..."
PAGES_STATUS=$(gh api repos/${REPO}/pages --jq '.status')

if [ "$PAGES_STATUS" = "built" ]; then
    echo -e "${GREEN}✓${NC} GitHub Pages: ${PAGES_STATUS}"
else
    echo -e "${YELLOW}⚠${NC} GitHub Pages: ${PAGES_STATUS}"
fi

# 6. Check critical links
echo -e "\n🔗 Sprawdzanie kluczowych linków..."
for url in \
    "https://github.com/${REPO}" \
    "https://github.com/${REPO}/releases/latest" \
    "https://github.com/${REPO}/issues"; do

    HTTP_CODE=$(curl -sI "$url" | grep -E "^HTTP" | awk '{print $2}')

    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
        echo -e "${GREEN}✓${NC} $(basename $url): HTTP ${HTTP_CODE}"
    else
        echo -e "${RED}✗${NC} $(basename $url): HTTP ${HTTP_CODE}"
    fi
done

echo -e "\n${BLUE}================================${NC}"
echo -e "${GREEN}✅ Weryfikacja zakończona!${NC}"
echo -e "${BLUE}================================${NC}\n"

echo "💡 Dla pełnych testów uruchom: python3 test_release.py"
