# Post-Release Testing Guide

Kompletny przewodnik testowania po opublikowaniu nowej wersji CC Gate.

## Automatyczne Testy (CI)

Po każdym release, GitHub Actions automatycznie uruchamia testy weryfikujące:
- ✅ Synchronizację landing page z najnowszą wersją
- ✅ Dostępność plików do pobrania
- ✅ Pliki SEO (sitemap, robots, llms.txt)
- ✅ Status GitHub Pages

Zobacz: [`.github/workflows/verify-release.yml`](.github/workflows/verify-release.yml)

## Manualne Testy

### 1. Quick Verification (Bash)

Szybkie sprawdzenie po release:

```bash
./quick_verify.sh
```

**Weryfikuje:**
- ✅ Wersja w JSON-LD
- ✅ Linki do pobrania
- ✅ Dostępność assets (PKG/DMG)
- ✅ Pliki SEO
- ✅ Status GitHub Pages

**Czas:** ~10s

---

### 2. Full Test Suite (Python)

Kompletne testy post-release:

```bash
python3 test_release.py
```

**Weryfikuje:**
- ✅ **Version Tests:** JSON-LD, download links
- ✅ **Asset Tests:** Dostępność plików (HEAD requests)
- ✅ **SEO Tests:** sitemap, robots, llms.txt, OG image, canonical URL
- ✅ **Infrastructure:** Dynamic update script, GitHub Pages, tag format

**Czas:** ~15-20s

**Test konkretnej wersji:**
```bash
python3 test_release.py --version 2.8.2
```

---

### 3. Manual Browser Tests

Po każdym release **ręcznie sprawdź w przeglądarce**:

#### a) Landing Page Load Test
1. Otwórz: https://ai-fresh.github.io/ccgate/
2. Sprawdź DevTools Console:
   ```
   ✅ Updated to v2.8.2
   ```
3. Sprawdź czy nie ma błędów JS

#### b) Download Test
1. Kliknij "Download for macOS"
2. Sprawdź czy pobiera się najnowsza wersja (.pkg)
3. Sprawdź nazwa pliku: `CC.Gate-2.8.2.pkg`

#### c) Social Preview Test
Sprawdź preview na social media:

**Facebook/LinkedIn:**
- https://developers.facebook.com/tools/debug/
- URL: `https://ai-fresh.github.io/ccgate/`
- Sprawdź: obrazek 1200x630, tytuł, opis

**Twitter:**
- https://cards-dev.twitter.com/validator
- URL: `https://ai-fresh.github.io/ccgate/`
- Sprawdź: Twitter Card Large Image

#### d) Mobile Responsive Test
1. DevTools → Toggle device toolbar (Cmd+Shift+M)
2. Test na różnych rozmiarach:
   - iPhone 14 Pro (430x932)
   - iPad (768x1024)
   - Desktop (1920x1080)

---

### 4. SEO & Discovery Tests

#### a) Google Search Console
1. https://search.google.com/search-console
2. Sprawdź "URL Inspection" dla landing page
3. Request indexing (jeśli nowa wersja)

#### b) Google Rich Results Test
1. https://search.google.com/test/rich-results
2. URL: `https://ai-fresh.github.io/ccgate/`
3. Sprawdź czy JSON-LD SoftwareApplication jest valid

#### c) Sitemap Validation
```bash
curl https://ai-fresh.github.io/ccgate/sitemap.xml | xmllint --format -
```

**Sprawdź:**
- ✅ Valid XML
- ✅ `<lastmod>` jest aktualny
- ✅ `<loc>` wskazuje na poprawny URL

#### d) Robots.txt Test
```bash
curl https://ai-fresh.github.io/ccgate/robots.txt
```

**Sprawdź:**
- ✅ `Allow: /`
- ✅ `Sitemap:` URL jest poprawny

#### e) llms.txt for AI Crawlers
```bash
curl https://ai-fresh.github.io/ccgate/llms.txt
```

**Sprawdź:**
- ✅ Markdown format
- ✅ Linki są aktualne
- ✅ Wersja jest najnowsza (jeśli wymieniona)

---

### 5. Download & Installation Tests

#### a) PKG Installer Test (macOS)

**Download:**
```bash
curl -LO "https://github.com/ai-fresh/ccgate/releases/latest/download/CC.Gate-2.8.2.pkg"
```

**Verify signature (if signed):**
```bash
pkgutil --check-signature CC.Gate-2.8.2.pkg
```

**Test install:**
1. Right-click → Open
2. Install w `/Applications/`
3. Sprawdź czy app się uruchamia
4. Sprawdź wersję w "About"

**Remove quarantine (if needed):**
```bash
xattr -cr "/Applications/CC Gate.app"
```

#### b) DMG Test (if available)

**Download:**
```bash
curl -LO "https://github.com/ai-fresh/ccgate/releases/latest/download/CC.Gate-2.8.2.dmg"
```

**Mount & verify:**
```bash
hdiutil attach CC.Gate-2.8.2.dmg
ls -la "/Volumes/CC Gate/"
hdiutil detach "/Volumes/CC Gate"
```

---

### 6. Dual-Repo Sync Test

Sprawdź czy oba repozytoria mają ten sam release:

```bash
# Private source repo
gh release view v2.8.2 --repo ai-fresh/ccgate-source

# Public landing repo
gh release view v2.8.2 --repo ai-fresh/ccgate
```

**Sprawdź:**
- ✅ Oba mają ten sam tag `v2.8.2`
- ✅ Public repo ma załączone binaria (PKG/DMG)
- ✅ Release notes są spójne

---

### 7. GitHub Release Page Test

Sprawdź stronę release na GitHubie:

https://github.com/ai-fresh/ccgate/releases/latest

**Checklist:**
- ✅ Tag format: `v2.8.2` (not `2.8.2` or `version-2.8.2`)
- ✅ Release title: czytelny (np. "CC Gate 2.8.2")
- ✅ Description: changelog + download instructions
- ✅ Assets: PKG i/lub DMG załączone
- ✅ Assets size: rozsądny (~2-5 MB dla PKG, ~2-4 MB dla DMG)
- ✅ "Latest" badge: widoczny na tym release

---

### 8. Analytics & Monitoring Tests

#### a) GitHub Insights
Sprawdź po 24h od release:

1. https://github.com/ai-fresh/ccgate/graphs/traffic
2. Sprawdź wzrost "Views" i "Unique visitors"
3. Sprawdź "Referring sites" (skąd przychodzą użytkownicy)

#### b) Release Downloads
```bash
gh api repos/ai-fresh/ccgate/releases/latest --jq '.assets[] | {name, download_count}'
```

**Monitoruj:**
- Ile razy pobrano PKG vs DMG
- Czy liczby rosną w czasie

---

### 9. Update Checker Test (In-App)

Po release, sprawdź czy app wykrywa update:

1. Uruchom **starszą wersję** CC Gate (np. 2.8.1)
2. Otwórz Settings → About
3. Kliknij "Check for Updates"
4. Sprawdź czy pokazuje: "New version 2.8.2 available"

---

### 10. Regression Tests

Sprawdź czy nowa wersja nie zepsuła podstawowych funkcji:

**Core Features:**
- ✅ App uruchamia się bez crash
- ✅ Menu bar icon pojawia się
- ✅ Hook installation działa
- ✅ Questions window otwiera się
- ✅ Settings zapisują się
- ✅ Project list ładuje się
- ✅ Auto-accept tiers działają

**Run unit tests:**
```bash
cd ccgate-source/
swift test
```

---

## Częstość Testów

| Test | Kiedy | Priorytet |
|------|-------|-----------|
| Quick verify | Po każdym release | ⚡️ Zawsze |
| Full Python suite | Po każdym release | ⚡️ Zawsze |
| Browser tests | Po każdym release | 🔸 Wysokie |
| Installation test | Major/minor release | 🔸 Wysokie |
| SEO validation | Po zmianach w HTML | 🔹 Średnie |
| Social preview | Po zmianach w meta tags | 🔹 Średnie |
| Analytics check | Co tydzień | ⚪️ Niskie |
| Dual-repo sync | Po każdym release | ⚡️ Zawsze |

---

## Checklist: Release Day

Po opublikowaniu nowego release:

```bash
# 1. Czekaj na GitHub Pages rebuild (2-3 min)
sleep 180

# 2. Quick verification
./quick_verify.sh

# 3. Full test suite
python3 test_release.py

# 4. Browser check
open https://ai-fresh.github.io/ccgate/

# 5. Download test
curl -LO "https://github.com/ai-fresh/ccgate/releases/latest/download/CC.Gate-2.8.2.pkg"
pkgutil --check-signature CC.Gate-2.8.2.pkg

# 6. Dual-repo sync check
gh release view v2.8.2 --repo ai-fresh/ccgate-source
gh release view v2.8.2 --repo ai-fresh/ccgate

# 7. Optional: Update landing page HTML (for SEO)
./update_landing_page.sh 2.8.2
```

---

## Troubleshooting

### Landing page ma starą wersję

**Przyczyny:**
1. GitHub Pages jeszcze się nie przebudował → czekaj 5 min
2. Cache w przeglądarce → Cmd+Shift+R (hard refresh)
3. JavaScript nie zadziałał → sprawdź Console w DevTools
4. Hardcoded URLs nie zaktualizowane → użyj `./update_landing_page.sh`

**Fix:**
```bash
# Sprawdź status Pages
gh api repos/ai-fresh/ccgate/pages --jq '.status'

# Jeśli "built", użyj update script
./update_landing_page.sh 2.8.2
```

---

### Asset 404 Not Found

**Przyczyny:**
1. Release nie ma załączonych plików
2. Nazwa pliku się zmieniła (np. `CC.Gate` → `CCGate`)
3. URL hardcoded w HTML nie pasuje do faktycznej nazwy

**Fix:**
```bash
# Sprawdź faktyczne nazwy assets
gh api repos/ai-fresh/ccgate/releases/latest --jq '.assets[].name'

# Zaktualizuj HTML jeśli trzeba
./update_landing_page.sh 2.8.2
```

---

### Tests failing w CI

**Debug:**
```bash
# Lokalnie uruchom te same testy
python3 test_release.py

# Sprawdź logs w GitHub Actions
gh run list --workflow=verify-release.yml
gh run view <run-id> --log
```

---

## Contributing to Tests

Dodawanie nowych testów:

1. **Bash (quick_verify.sh):** Dla szybkich sprawdzeń bez dependencji
2. **Python (test_release.py):** Dla złożonych testów z API calls
3. **GitHub Actions:** Dla automatyzacji CI/CD

**Przykład nowego testu:**

```python
def test_new_feature(html: str) -> bool:
    """Test X: Description"""
    # ... test logic ...
    passed = True  # or False
    print_test("Test name", passed, "message")
    return passed
```

Dodaj wywołanie w `main()`:
```python
results.append(test_new_feature(html))
```

---

## Resources

- [GitHub Pages Docs](https://docs.github.com/en/pages)
- [Google Rich Results Test](https://search.google.com/test/rich-results)
- [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/)
- [Twitter Card Validator](https://cards-dev.twitter.com/validator)
- [Schema.org SoftwareApplication](https://schema.org/SoftwareApplication)
- [llms.txt Standard](https://llmstxt.org/)
