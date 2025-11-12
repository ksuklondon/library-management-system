# Contributing Guidelines

## 🌿 Branching Strategy

Używamy uproszczonego Git Flow:

- `main` - produkcja, stabilna wersja (chroniona)
- `dev` - integracja, rozwój (tutaj łączymy feature branches)
- `feature/*` - nowe funkcjonalności
- `bugfix/*` - poprawki błędów
- `hotfix/*` - pilne poprawki produkcji

### Nazewnictwo branches

```
feature/auth-service          - nowa funkcjonalność
feature/catalog-search        - konkretna funkcja
bugfix/fix-fine-calculation   - poprawka błędu
hotfix/security-patch         - pilna poprawka
```

## 📝 Commit Messages

Format: `<type>: <short description>`

### Types:

- `feat:` - nowa funkcjonalność
- `fix:` - poprawka błędu
- `docs:` - dokumentacja
- `style:` - formatowanie (bez zmian w logice)
- `refactor:` - refaktoring kodu
- `test:` - dodanie/poprawka testów
- `chore:` - zmiany w konfiguracji, dependencies

### Przykłady:

```
feat(auth): add user registration endpoint (F1)
fix(loan): correct fine calculation timezone (NF29)
docs: update API documentation
refactor(catalog): extract search logic to service
test(auth): add unit tests for JWT validation
chore: update dependencies
```

## 🔄 Workflow

### 1. Rozpoczęcie pracy nad nową funkcjonalnością

```bash
# Pobierz najnowsze zmiany
git checkout dev
git pull origin dev

# Utwórz nowy branch
git checkout -b feature/nazwa-funkcjonalnosci

# Pracuj nad kodem...
```

### 2. Commitowanie zmian

```bash
# Sprawdź zmiany
git status

# Dodaj pliki
git add .

# Commit z opisowym komunikatem
git commit -m "feat(modul): opis zmian"

# Wypchnij na GitHub
git push -u origin feature/nazwa-funkcjonalnosci
```

### 3. Pull Request

1. Idź na GitHub → Twoje repo
2. Kliknij **"Compare & pull request"**
3. **Base:** `dev` ← **Compare:** `feature/nazwa-funkcjonalnosci`
4. Wypełnij opis PR:

```
   ## Opis
   Implementacja funkcjonalności X zgodnie z wymaganiem F1.

   ## Zmiany
   - Dodano endpoint /api/auth/register
   - Walidacja danych wejściowych
   - Testy jednostkowe

   ## Testy
   - [x] Testy jednostkowe przechodzą
   - [x] Kod zgodny z linterem
   - [x] Dokumentacja zaktualizowana
```

5. Kliknij **"Create pull request"**
6. Poczekaj na review / merge

### 4. Po zaakceptowaniu PR

```bash
# Przejdź na dev
git checkout dev

# Pobierz zmiany (Twój PR jest już w dev)
git pull origin dev

# Usuń lokalny branch (opcjonalnie)
git branch -d feature/nazwa-funkcjonalnosci

# Usuń zdalny branch (opcjonalnie)
git push origin --delete feature/nazwa-funkcjonalnosci
```

## 🔀 Rozwiązywanie konfliktów

Jeśli PR pokazuje konflikty:

```bash
# Przejdź na swój feature branch
git checkout feature/twoj-branch

# Pobierz najnowszy dev
git fetch origin dev

# Merge dev do swojego brancha
git merge origin/dev

# Rozwiąż konflikty w plikach
# (VS Code pokaże konflikty z znacznikami <<<<< ===== >>>>>)

# Po rozwiązaniu:
git add .
git commit -m "merge: resolve conflicts with dev"
git push
```

## ✅ Checklist przed PR

- [ ] Kod działa lokalnie
- [ ] Testy przechodzą (`pytest` dla Python, `npm test` dla frontend)
- [ ] Kod zgodny z linterem (Ruff dla Python, ESLint dla TS)
- [ ] Dokumentacja zaktualizowana (jeśli potrzeba)
- [ ] Commit messages są opisowe
- [ ] Branch jest aktualny z `dev`

## 👥 Review Process

- Każdy PR wymaga review (możesz sam zaaprobować dla projektu studenckiego)
- Sprawdź:
  - Czy kod jest czytelny
  - Czy nie ma duplikacji
  - Czy są testy
  - Czy działa zgodnie z wymaganiami

## 🚫 Czego unikać

- ❌ Commity bezpośrednio na `main` lub `dev`
- ❌ Force push (`git push -f`) na współdzielonych branchach
- ❌ Commitowanie secrets (.env, klucze API)
- ❌ Zbyt duże PR (podziel na mniejsze)
- ❌ Commitowanie plików z `node_modules`, `__pycache__`

## 🆘 Pomoc

Jeśli coś nie działa:

1. Sprawdź `git status`
2. Sprawdź `git log --oneline --graph`
3. Poszukaj błędu w dokumentacji Git
4. Zapytaj zespół

```

---
```
