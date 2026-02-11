#!/usr/bin/env python3
"""
Post-Release Validation Tests for CC Gate Landing Page
Weryfikuje czy strona jest zsynchronizowana z najnowszym release'em.

Usage:
    python3 test_release.py
    python3 test_release.py --version 2.8.2  # Test specific version
"""

import requests
import json
import re
import sys
from typing import Dict, Optional
from urllib.parse import urlparse

# Configuration
REPO_OWNER = "ai-fresh"
REPO_NAME = "ccgate"
LANDING_PAGE = f"https://{REPO_OWNER}.github.io/{REPO_NAME}/"
GITHUB_API = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(name: str, passed: bool, message: str = ""):
    """Pretty print test result"""
    status = f"{Colors.GREEN}✓{Colors.RESET}" if passed else f"{Colors.RED}✗{Colors.RESET}"
    print(f"{status} {name}")
    if message:
        indent = "  "
        print(f"{indent}{Colors.YELLOW}→{Colors.RESET} {message}")

def get_latest_release() -> Dict:
    """Fetch latest release from GitHub API"""
    response = requests.get(f"{GITHUB_API}/releases/latest")
    response.raise_for_status()
    return response.json()

def get_landing_page_content() -> str:
    """Fetch landing page HTML"""
    response = requests.get(LANDING_PAGE)
    response.raise_for_status()
    return response.text

def extract_json_ld(html: str) -> Optional[Dict]:
    """Extract JSON-LD structured data from HTML"""
    match = re.search(r'<script type="application/ld\+json">\s*({.*?})\s*</script>', html, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    return None

def test_latest_version_in_json_ld(html: str, expected_version: str) -> bool:
    """Test 1: Weryfikacja wersji w JSON-LD structured data"""
    json_ld = extract_json_ld(html)

    if not json_ld:
        print_test("JSON-LD structured data exists", False, "Nie znaleziono JSON-LD")
        return False

    version = json_ld.get("softwareVersion", "").lstrip("v")
    expected = expected_version.lstrip("v")

    passed = version == expected
    message = f"Znaleziono: {version}, Oczekiwano: {expected}" if not passed else f"Wersja: {version}"
    print_test("JSON-LD ma najnowszą wersję", passed, message)
    return passed

def test_download_links(html: str, expected_version: str) -> bool:
    """Test 2: Weryfikacja czy linki do pobrania wskazują na najnowszą wersję"""
    expected = expected_version.lstrip("v")

    # Find all download links
    pkg_links = re.findall(r'href="([^"]*\.pkg)"', html)
    dmg_links = re.findall(r'href="([^"]*\.dmg)"', html)

    all_passed = True

    for link in pkg_links:
        if f"v{expected}" in link or f"{expected}" in link:
            print_test(f"PKG link ma wersję {expected}", True, link)
        else:
            print_test(f"PKG link ma starą wersję", False, link)
            all_passed = False

    for link in dmg_links:
        if f"v{expected}" in link or f"{expected}" in link:
            print_test(f"DMG link ma wersję {expected}", True, link)
        else:
            print_test(f"DMG link ma starą wersję", False, link)
            all_passed = False

    if not pkg_links and not dmg_links:
        print_test("Znaleziono linki do pobrania", False, "Brak linków .pkg/.dmg")
        return False

    return all_passed

def test_download_assets_accessible(release_data: Dict) -> bool:
    """Test 3: Weryfikacja czy pliki są dostępne do pobrania (bez pobierania całości)"""
    assets = release_data.get("assets", [])

    if not assets:
        print_test("Release ma załączone pliki", False, "Brak assets w release")
        return False

    all_passed = True
    for asset in assets:
        name = asset["name"]
        url = asset["browser_download_url"]

        # HEAD request to check if file exists (nie pobiera całego pliku)
        response = requests.head(url, allow_redirects=True)
        passed = response.status_code == 200

        if passed:
            size_mb = asset["size"] / (1024 * 1024)
            print_test(f"Asset dostępny: {name}", True, f"{size_mb:.1f} MB")
        else:
            print_test(f"Asset niedostępny: {name}", False, f"HTTP {response.status_code}")
            all_passed = False

    return all_passed

def test_seo_files_exist() -> bool:
    """Test 4: Weryfikacja plików SEO"""
    files = {
        "sitemap.xml": f"{LANDING_PAGE}sitemap.xml",
        "robots.txt": f"{LANDING_PAGE}robots.txt",
        "llms.txt": f"{LANDING_PAGE}llms.txt",
    }

    all_passed = True
    for name, url in files.items():
        response = requests.get(url)
        passed = response.status_code == 200

        if passed:
            size = len(response.content)
            print_test(f"SEO file: {name}", True, f"{size} bytes")
        else:
            print_test(f"SEO file: {name}", False, f"HTTP {response.status_code}")
            all_passed = False

    return all_passed

def test_og_image_exists() -> bool:
    """Test 5: Weryfikacja OG image dla social media"""
    html = get_landing_page_content()

    # Extract OG image URL
    match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
    if not match:
        print_test("OG image meta tag exists", False, "Nie znaleziono og:image")
        return False

    og_image_url = match.group(1)
    response = requests.head(og_image_url, allow_redirects=True)
    passed = response.status_code == 200

    if passed:
        print_test("OG image dostępny", True, og_image_url)
    else:
        print_test("OG image niedostępny", False, f"HTTP {response.status_code}: {og_image_url}")

    return passed

def test_canonical_url(html: str) -> bool:
    """Test 6: Weryfikacja canonical URL"""
    match = re.search(r'<link rel="canonical" href="([^"]+)"', html)

    if not match:
        print_test("Canonical URL exists", False, "Nie znaleziono canonical link")
        return False

    canonical = match.group(1)
    expected = LANDING_PAGE
    passed = canonical == expected

    message = f"Canonical: {canonical}" if passed else f"Znaleziono: {canonical}, Oczekiwano: {expected}"
    print_test("Canonical URL jest poprawny", passed, message)
    return passed

def test_dynamic_update_script(html: str) -> bool:
    """Test 7: Weryfikacja czy jest skrypt dynamicznego updateu"""
    has_fetch = "fetch(API_URL)" in html or "api.github.com/repos" in html
    has_update = "softwareVersion" in html and "downloadUrl" in html

    passed = has_fetch and has_update
    message = "Skrypt dynamicznej aktualizacji obecny" if passed else "Brak skryptu dynamicznego updateu"
    print_test("Dynamic update script exists", passed, message)
    return passed

def test_json_ld_schema_valid(html: str) -> bool:
    """Test 8: Walidacja struktury JSON-LD"""
    json_ld = extract_json_ld(html)

    if not json_ld:
        print_test("JSON-LD schema valid", False, "Brak JSON-LD")
        return False

    required_fields = ["@context", "@type", "name", "description", "downloadUrl", "softwareVersion"]
    missing = [field for field in required_fields if field not in json_ld]

    passed = len(missing) == 0

    if passed:
        print_test("JSON-LD schema kompletne", True, f"Wszystkie wymagane pola obecne")
    else:
        print_test("JSON-LD schema niekompletne", False, f"Brakuje: {', '.join(missing)}")

    return passed

def test_github_pages_status() -> bool:
    """Test 9: Status GitHub Pages"""
    response = requests.get(f"{GITHUB_API}/pages")

    if response.status_code != 200:
        print_test("GitHub Pages status", False, f"HTTP {response.status_code}")
        return False

    data = response.json()
    status = data.get("status")
    html_url = data.get("html_url")

    passed = status == "built"
    message = f"Status: {status}, URL: {html_url}" if passed else f"Status: {status} (expected: built)"
    print_test("GitHub Pages deployment", passed, message)
    return passed

def test_release_tag_format(release_data: Dict) -> bool:
    """Test 10: Format tagu release (vX.Y.Z)"""
    tag = release_data.get("tag_name", "")
    version_pattern = r'^v?\d+\.\d+\.\d+$'

    passed = bool(re.match(version_pattern, tag))
    message = f"Tag: {tag}" if passed else f"Tag {tag} nie pasuje do wzorca vX.Y.Z"
    print_test("Release tag format", passed, message)
    return passed

def test_all_links_valid(html: str) -> bool:
    """Test 11: Sprawdzenie czy wszystkie linki/przyciski kierują do właściwych miejsc"""
    # Extract all href links from HTML
    all_links = re.findall(r'href="([^"]+)"', html)

    # Filter to only external links (skip fragments like #features)
    external_links = [link for link in all_links if link.startswith('http')]

    # Expected domains/paths
    expected_patterns = {
        'github.com/ai-fresh/ccgate': 'GitHub repo',
        'github.com/ai-fresh/ccgate/releases': 'Releases page',
        'github.com/ai-fresh/ccgate/issues': 'Issues page',
        'github.com/ai-fresh/ccgate-source': 'Source repo',
        'ai-fresh.github.io/ccgate': 'Landing page',
    }

    # Count valid links
    all_passed = True
    broken_links = []
    tested_urls = set()  # Avoid testing same URL multiple times

    for link in external_links[:10]:  # Test first 10 unique external links to avoid rate limits
        if link in tested_urls:
            continue
        tested_urls.add(link)

        try:
            # HEAD request with timeout to check if link is accessible
            response = requests.head(link, timeout=5, allow_redirects=True)

            if response.status_code in [200, 301, 302]:
                # Check if link matches expected patterns
                link_desc = None
                for pattern, desc in expected_patterns.items():
                    if pattern in link:
                        link_desc = desc
                        break

                desc = link_desc or link.split('/')[2]  # domain as fallback
                print_test(f"Link OK: {desc}", True, f"{link[:60]}{'...' if len(link) > 60 else ''}")
            else:
                print_test(f"Link broken", False, f"HTTP {response.status_code}: {link}")
                broken_links.append((link, response.status_code))
                all_passed = False

        except requests.exceptions.RequestException as e:
            print_test(f"Link error", False, f"{link}: {str(e)[:50]}")
            broken_links.append((link, str(e)))
            all_passed = False

    # Summary
    if all_passed:
        print_test("Wszystkie linki działają", True, f"Sprawdzono {len(tested_urls)} unikalnych linków")
    else:
        print_test("Znaleziono broken links", False, f"{len(broken_links)} broken z {len(tested_urls)} sprawdzonych")

    return all_passed

def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}🧪 Post-Release Validation Tests{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

    try:
        # Fetch data
        print(f"📡 Pobieranie danych z GitHub API i landing page...\n")
        release_data = get_latest_release()
        html = get_landing_page_content()

        tag_name = release_data["tag_name"]
        version = tag_name.lstrip("v")

        print(f"{Colors.GREEN}✓{Colors.RESET} Najnowszy release: {Colors.GREEN}{tag_name}{Colors.RESET}")
        print(f"{Colors.GREEN}✓{Colors.RESET} Landing page: {LANDING_PAGE}\n")

        # Allow version override from CLI
        if len(sys.argv) > 2 and sys.argv[1] == "--version":
            version = sys.argv[2]
            print(f"{Colors.YELLOW}⚠{Colors.RESET} Testing against custom version: {version}\n")

        print(f"{Colors.BLUE}--- Version Tests ---{Colors.RESET}")
        results = []
        results.append(test_latest_version_in_json_ld(html, version))
        results.append(test_download_links(html, version))

        print(f"\n{Colors.BLUE}--- Asset Availability Tests ---{Colors.RESET}")
        results.append(test_download_assets_accessible(release_data))

        print(f"\n{Colors.BLUE}--- SEO & Metadata Tests ---{Colors.RESET}")
        results.append(test_seo_files_exist())
        results.append(test_og_image_exists())
        results.append(test_canonical_url(html))
        results.append(test_json_ld_schema_valid(html))
        results.append(test_all_links_valid(html))

        print(f"\n{Colors.BLUE}--- Infrastructure Tests ---{Colors.RESET}")
        results.append(test_dynamic_update_script(html))
        results.append(test_github_pages_status())
        results.append(test_release_tag_format(release_data))

        # Summary
        passed = sum(results)
        total = len(results)
        percentage = (passed / total) * 100

        print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
        if passed == total:
            print(f"{Colors.GREEN}✓ Wszystkie testy przeszły: {passed}/{total} (100%){Colors.RESET}")
            print(f"{Colors.GREEN}🎉 Release jest gotowy do użycia!{Colors.RESET}")
            sys.exit(0)
        else:
            print(f"{Colors.RED}✗ Testy failed: {total - passed}/{total} ({100 - percentage:.0f}%){Colors.RESET}")
            print(f"{Colors.YELLOW}⚠ Napraw błędy przed ogłoszeniem release!{Colors.RESET}")
            sys.exit(1)

    except Exception as e:
        print(f"\n{Colors.RED}❌ Błąd podczas testowania: {e}{Colors.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
