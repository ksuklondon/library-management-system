# Schemat bazy danych - System Zarządzania Biblioteką

## Przegląd

Baza danych PostgreSQL 15 zawiera 9 głównych tabel przechowujących wszystkie dane systemu.

**Nazwa bazy:** `biblioteka`  
**Kodowanie:** UTF-8  
**Strefa czasowa:** Europe/Warsaw (ważne dla naliczania kar)

---

## Lista tabel

1. **users** - Dane użytkowników systemu
2. **books** - Informacje o książkach
3. **book_copies** - Fizyczne egzemplarze książek
4. **reservations** - Rezerwacje egzemplarzy
5. **loans** - Wypożyczenia egzemplarzy
6. **notifications** - Powiadomienia użytkowników (DODATEK)
7. **audit_logs** - Logi audytowe (DODATEK)
8. **settings** - Ustawienia systemowe (OPCJONALNIE)
9. **refresh_tokens** - Tokeny odświeżające sesję

---

## Szczegółowy opis tabel

### 1. Tabela: users

**Opis:** Przechowuje dane wszystkich użytkowników systemu (Czytelnicy, Bibliotekarze, Administratorzy)

#### Kolumny:

| Nazwa              | Typ          | Ograniczenia                            | Opis                                |
| ------------------ | ------------ | --------------------------------------- | ----------------------------------- |
| id                 | UUID         | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unikalny identyfikator użytkownika  |
| email              | VARCHAR(255) | NOT NULL, UNIQUE                        | Adres email (login)                 |
| password_hash      | VARCHAR(255) | NOT NULL                                | Hash hasła (bcrypt, koszt 12)       |
| first_name         | VARCHAR(100) | NOT NULL                                | Imię                                |
| last_name          | VARCHAR(100) | NOT NULL                                | Nazwisko                            |
| phone              | VARCHAR(20)  | NULL                                    | Numer telefonu (opcjonalny)         |
| role               | VARCHAR(20)  | NOT NULL, DEFAULT 'READER'              | Rola użytkownika                    |
| is_active          | BOOLEAN      | NOT NULL, DEFAULT TRUE                  | Czy konto aktywne (nie zablokowane) |
| is_deleted         | BOOLEAN      | NOT NULL, DEFAULT FALSE                 | Soft delete                         |
| blocked_by_id      | UUID         | NULL, FOREIGN KEY → users(id)           | Admin który zablokował              |
| blocked_at         | TIMESTAMP    | NULL                                    | Data blokady                        |
| role_changed_at    | TIMESTAMP    | NULL                                    | Data ostatniej zmiany roli          |
| role_changed_by_id | UUID         | NULL, FOREIGN KEY → users(id)           | Admin który zmienił rolę            |
| deleted_by_id      | UUID         | NULL, FOREIGN KEY → users(id)           | Admin który usunął                  |
| deleted_at         | TIMESTAMP    | NULL                                    | Data usunięcia (soft delete)        |
| created_at         | TIMESTAMP    | NOT NULL, DEFAULT NOW()                 | Data utworzenia konta               |
| updated_at         | TIMESTAMP    | NOT NULL, DEFAULT NOW()                 | Data ostatniej aktualizacji         |

#### Enum: UserRole

```sql
CREATE TYPE user_role AS ENUM ('READER', 'LIBRARIAN', 'ADMIN');
```

#### Ograniczenia:

```sql
-- Klucz główny
PRIMARY KEY (id)

-- Email unikalny (tylko dla nie usuniętych)
CREATE UNIQUE INDEX idx_users_email_active ON users(email) WHERE is_deleted = FALSE;

-- Sprawdzanie roli
CHECK (role IN ('READER', 'LIBRARIAN', 'ADMIN'))

-- Email musi być poprawnym adresem
CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')

-- Klucze obce
FOREIGN KEY (blocked_by_id) REFERENCES users(id) ON DELETE SET NULL
FOREIGN KEY (role_changed_by_id) REFERENCES users(id) ON DELETE SET NULL
FOREIGN KEY (deleted_by_id) REFERENCES users(id) ON DELETE SET NULL
```

#### Indeksy:

```sql
-- Szybkie wyszukiwanie po emailu (logowanie)
CREATE UNIQUE INDEX idx_users_email ON users(email) WHERE is_deleted = FALSE;

-- Filtrowanie po roli
CREATE INDEX idx_users_role ON users(role) WHERE is_deleted = FALSE;

-- Filtrowanie po statusie
CREATE INDEX idx_users_active ON users(is_active) WHERE is_deleted = FALSE;

-- Wyszukiwanie po imieniu/nazwisku
CREATE INDEX idx_users_name ON users(first_name, last_name) WHERE is_deleted = FALSE;
```

---

### 2. Tabela: books

**Opis:** Przechowuje informacje o książkach (katalog)

#### Kolumny:

| Nazwa         | Typ          | Ograniczenia                            | Opis                           |
| ------------- | ------------ | --------------------------------------- | ------------------------------ |
| id            | UUID         | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unikalny identyfikator książki |
| isbn          | VARCHAR(20)  | NOT NULL, UNIQUE                        | Numer ISBN (unikalny)          |
| title         | VARCHAR(200) | NOT NULL                                | Tytuł książki                  |
| authors       | TEXT[]       | NOT NULL                                | Lista autorów (array)          |
| publisher     | VARCHAR(200) | NOT NULL                                | Wydawnictwo                    |
| year          | INTEGER      | NOT NULL                                | Rok wydania                    |
| pages         | INTEGER      | NULL                                    | Liczba stron                   |
| genre         | VARCHAR(100) | NULL                                    | Gatunek literacki              |
| description   | TEXT         | NULL                                    | Opis książki                   |
| cover_url     | VARCHAR(500) | NULL                                    | URL okładki (DODATEK)          |
| is_deleted    | BOOLEAN      | NOT NULL, DEFAULT FALSE                 | Soft delete                    |
| deleted_by_id | UUID         | NULL, FOREIGN KEY → users(id)           | Admin który usunął             |
| deleted_at    | TIMESTAMP    | NULL                                    | Data usunięcia                 |
| created_at    | TIMESTAMP    | NOT NULL, DEFAULT NOW()                 | Data dodania do systemu        |
| updated_at    | TIMESTAMP    | NOT NULL, DEFAULT NOW()                 | Data ostatniej aktualizacji    |

#### Ograniczenia:

```sql
-- Klucz główny
PRIMARY KEY (id)

-- ISBN unikalny (tylko dla nie usuniętych)
CREATE UNIQUE INDEX idx_books_isbn_active ON books(isbn) WHERE is_deleted = FALSE;

-- Rok wydania realistyczny
CHECK (year >= 1000 AND year <= EXTRACT(YEAR FROM CURRENT_DATE) + 1)

-- Liczba stron dodatnia
CHECK (pages IS NULL OR pages > 0)

-- Klucz obcy
FOREIGN KEY (deleted_by_id) REFERENCES users(id) ON DELETE SET NULL
```

#### Indeksy:

```sql
-- Szybkie wyszukiwanie po ISBN
CREATE UNIQUE INDEX idx_books_isbn ON books(isbn) WHERE is_deleted = FALSE;

-- Wyszukiwanie po gatunku
CREATE INDEX idx_books_genre ON books(genre) WHERE is_deleted = FALSE;

-- Full-text search w tytule (polskie znaki)
CREATE INDEX idx_books_title_fts ON books USING gin(to_tsvector('polish', title)) WHERE is_deleted = FALSE;

-- Full-text search w autorach
CREATE INDEX idx_books_authors_fts ON books USING gin(to_tsvector('polish', array_to_string(authors, ' '))) WHERE is_deleted = FALSE;

-- Sortowanie po roku wydania
CREATE INDEX idx_books_year ON books(year DESC) WHERE is_deleted = FALSE;

-- Sortowanie po tytule
CREATE INDEX idx_books_title_sort ON books(title) WHERE is_deleted = FALSE;
```

---

### 3. Tabela: book_copies

**Opis:** Przechowuje fizyczne egzemplarze książek

#### Kolumny:

| Nazwa            | Typ         | Ograniczenia                            | Opis                               |
| ---------------- | ----------- | --------------------------------------- | ---------------------------------- |
| id               | UUID        | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unikalny identyfikator egzemplarza |
| book_id          | UUID        | NOT NULL, FOREIGN KEY → books(id)       | Identyfikator książki              |
| inventory_number | VARCHAR(50) | NOT NULL, UNIQUE                        | Numer inwentarzowy (auto)          |
| status           | VARCHAR(20) | NOT NULL, DEFAULT 'AVAILABLE'           | Status egzemplarza                 |
| condition        | VARCHAR(20) | NOT NULL, DEFAULT 'GOOD'                | Stan fizyczny                      |
| notes            | TEXT        | NULL                                    | Uwagi dotyczące egzemplarza        |
| is_deleted       | BOOLEAN     | NOT NULL, DEFAULT FALSE                 | Soft delete                        |
| deleted_by_id    | UUID        | NULL, FOREIGN KEY → users(id)           | Staff który usunął                 |
| deleted_at       | TIMESTAMP   | NULL                                    | Data usunięcia                     |
| created_at       | TIMESTAMP   | NOT NULL, DEFAULT NOW()                 | Data dodania egzemplarza           |
| updated_at       | TIMESTAMP   | NOT NULL, DEFAULT NOW()                 | Data ostatniej aktualizacji        |

#### Enum: CopyStatus

```sql
CREATE TYPE copy_status AS ENUM (
    'AVAILABLE',      -- Dostępny do wypożyczenia
    'RESERVED',       -- Zarezerwowany
    'LOANED',         -- Wypożyczony
    'MAINTENANCE',    -- W konserwacji
    'DAMAGED',        -- Uszkodzony
    'LOST'            -- Zgubiony
);
```

#### Enum: CopyCondition

```sql
CREATE TYPE copy_condition AS ENUM (
    'GOOD',           -- Dobry stan
    'WORN',           -- Zużyty
    'DAMAGED',        -- Uszkodzony
    'LOST'            -- Zgubiony
);
```

#### Ograniczenia:

```sql
-- Klucz główny
PRIMARY KEY (id)

-- Numer inwentarzowy unikalny
UNIQUE (inventory_number)

-- Klucz obcy do książki (CASCADE - usunięcie książki usuwa egzemplarze)
FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE

-- Klucz obcy do użytkownika
FOREIGN KEY (deleted_by_id) REFERENCES users(id) ON DELETE SET NULL

-- Sprawdzanie statusu
CHECK (status IN ('AVAILABLE', 'RESERVED', 'LOANED', 'MAINTENANCE', 'DAMAGED', 'LOST'))

-- Sprawdzanie stanu
CHECK (condition IN ('GOOD', 'WORN', 'DAMAGED', 'LOST'))
```

#### Indeksy:

```sql
-- Szybkie wyszukiwanie po numerze inwentarzowym
CREATE UNIQUE INDEX idx_copies_inventory ON book_copies(inventory_number);

-- Sprawdzanie dostępności dla danej książki (NAJWAŻNIEJSZY!)
CREATE INDEX idx_copies_book_status ON book_copies(book_id, status) WHERE is_deleted = FALSE;

-- Filtrowanie po statusie
CREATE INDEX idx_copies_status ON book_copies(status) WHERE is_deleted = FALSE;

-- Dostępne egzemplarze (często używane)
CREATE INDEX idx_copies_available ON book_copies(book_id) WHERE status = 'AVAILABLE' AND is_deleted = FALSE;
```

---

### 4. Tabela: reservations

**Opis:** Przechowuje rezerwacje egzemplarzy przez czytelników

#### Kolumny:

| Nazwa               | Typ         | Ograniczenia                            | Opis                                   |
| ------------------- | ----------- | --------------------------------------- | -------------------------------------- |
| id                  | UUID        | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unikalny identyfikator rezerwacji      |
| user_id             | UUID        | NOT NULL, FOREIGN KEY → users(id)       | Identyfikator użytkownika              |
| book_copy_id        | UUID        | NOT NULL, FOREIGN KEY → book_copies(id) | Identyfikator egzemplarza              |
| status              | VARCHAR(20) | NOT NULL, DEFAULT 'ACTIVE'              | Status rezerwacji                      |
| reserved_at         | TIMESTAMP   | NOT NULL, DEFAULT NOW()                 | Data utworzenia rezerwacji             |
| expires_at          | TIMESTAMP   | NOT NULL                                | Data wygaśnięcia (reserved_at + 3 dni) |
| cancelled_at        | TIMESTAMP   | NULL                                    | Data anulowania                        |
| cancelled_by_id     | UUID        | NULL, FOREIGN KEY → users(id)           | Kto anulował (user/staff)              |
| cancellation_reason | TEXT        | NULL                                    | Powód anulowania                       |
| completed_at        | TIMESTAMP   | NULL                                    | Data realizacji (checkout)             |

#### Enum: ReservationStatus

```sql
CREATE TYPE reservation_status AS ENUM (
    'ACTIVE',         -- Aktywna rezerwacja
    'CANCELLED',      -- Anulowana
    'EXPIRED',        -- Wygasła (nie odebrano)
    'COMPLETED'       -- Zrealizowana (wypożyczono)
);
```

#### Ograniczenia:

```sql
-- Klucz główny
PRIMARY KEY (id)

-- Klucze obce (CASCADE)
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
FOREIGN KEY (book_copy_id) REFERENCES book_copies(id) ON DELETE CASCADE
FOREIGN KEY (cancelled_by_id) REFERENCES users(id) ON DELETE SET NULL

-- Sprawdzanie statusu
CHECK (status IN ('ACTIVE', 'CANCELLED', 'EXPIRED', 'COMPLETED'))

-- Data wygaśnięcia musi być w przyszłości
CHECK (expires_at > reserved_at)

-- Jeden egzemplarz może mieć tylko 1 aktywną rezerwację (CONSTRAINT BIZNESOWY!)
CREATE UNIQUE INDEX idx_reservations_copy_active
ON reservations(book_copy_id)
WHERE status = 'ACTIVE';
```

#### Indeksy:

```sql
-- Historia rezerwacji użytkownika
CREATE INDEX idx_reservations_user ON reservations(user_id, status);

-- Aktywne rezerwacje użytkownika (dla limitu 3)
CREATE INDEX idx_reservations_user_active
ON reservations(user_id)
WHERE status = 'ACTIVE';

-- Wygasłe rezerwacje (dla background job czyszczenia)
CREATE INDEX idx_reservations_expired
ON reservations(expires_at)
WHERE status = 'ACTIVE';

-- Rezerwacje do zrealizowania
CREATE INDEX idx_reservations_book_active
ON reservations(book_copy_id, status)
WHERE status = 'ACTIVE';
```

---

### 5. Tabela: loans

**Opis:** Przechowuje wypożyczenia egzemplarzy

#### Kolumny:

| Nazwa          | Typ           | Ograniczenia                            | Opis                                |
| -------------- | ------------- | --------------------------------------- | ----------------------------------- |
| id             | UUID          | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unikalny identyfikator wypożyczenia |
| user_id        | UUID          | NOT NULL, FOREIGN KEY → users(id)       | Identyfikator użytkownika           |
| book_copy_id   | UUID          | NOT NULL, FOREIGN KEY → book_copies(id) | Identyfikator egzemplarza           |
| reservation_id | UUID          | NULL, FOREIGN KEY → reservations(id)    | Powiązana rezerwacja (jeśli była)   |
| loaned_at      | TIMESTAMP     | NOT NULL, DEFAULT NOW()                 | Data wypożyczenia                   |
| due_date       | TIMESTAMP     | NOT NULL                                | Termin zwrotu (loaned_at + 14 dni)  |
| returned_at    | TIMESTAMP     | NULL                                    | Faktyczna data zwrotu               |
| extended_at    | TIMESTAMP     | NULL                                    | Data przedłużenia (jeśli było)      |
| fine_amount    | DECIMAL(10,2) | NOT NULL, DEFAULT 0.00                  | Kwota kary (0.00-100.00 PLN)        |
| fine_paid      | BOOLEAN       | NOT NULL, DEFAULT FALSE                 | Czy kara opłacona                   |
| fine_paid_at   | TIMESTAMP     | NULL                                    | Data opłacenia kary                 |
| status         | VARCHAR(20)   | NOT NULL, DEFAULT 'ACTIVE'              | Status wypożyczenia                 |
| created_at     | TIMESTAMP     | NOT NULL, DEFAULT NOW()                 | Data utworzenia rekordu             |
| updated_at     | TIMESTAMP     | NOT NULL, DEFAULT NOW()                 | Data ostatniej aktualizacji         |

#### Enum: LoanStatus

```sql
CREATE TYPE loan_status AS ENUM (
    'ACTIVE',         -- Aktywne wypożyczenie
    'RETURNED',       -- Zwrócone
    'OVERDUE'         -- Przeterminowane
);
```

#### Ograniczenia:

```sql
-- Klucz główny
PRIMARY KEY (id)

-- Klucze obce (CASCADE)
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
FOREIGN KEY (book_copy_id) REFERENCES book_copies(id) ON DELETE CASCADE
FOREIGN KEY (reservation_id) REFERENCES reservations(id) ON DELETE SET NULL

-- Sprawdzanie statusu
CHECK (status IN ('ACTIVE', 'RETURNED', 'OVERDUE'))

-- Termin zwrotu po dacie wypożyczenia
CHECK (due_date > loaned_at)

-- Data zwrotu po dacie wypożyczenia (jeśli jest)
CHECK (returned_at IS NULL OR returned_at >= loaned_at)

-- Kwota kary między 0 a 100 PLN
CHECK (fine_amount >= 0 AND fine_amount <= 100.00)

-- Przedłużenie tylko dla aktywnych
CHECK (extended_at IS NULL OR (extended_at >= loaned_at AND status = 'ACTIVE'))
```

#### Indeksy:

```sql
-- Historia wypożyczeń użytkownika
CREATE INDEX idx_loans_user_status ON loans(user_id, status);

-- Aktywne wypożyczenia użytkownika (dla limitu 5)
CREATE INDEX idx_loans_user_active
ON loans(user_id)
WHERE status IN ('ACTIVE', 'OVERDUE');

-- Aktywne wypożyczenia egzemplarza
CREATE INDEX idx_loans_copy_active
ON loans(book_copy_id)
WHERE status IN ('ACTIVE', 'OVERDUE');

-- Przeterminowane wypożyczenia (dla background job naliczania kar)
CREATE INDEX idx_loans_overdue
ON loans(due_date)
WHERE status = 'ACTIVE' AND returned_at IS NULL;

-- Nieopłacone kary
CREATE INDEX idx_loans_unpaid_fines
ON loans(user_id, fine_amount, fine_paid)
WHERE fine_amount > 0 AND fine_paid = FALSE;

-- Wypożyczenia do zwrotu (sortowanie po terminie)
CREATE INDEX idx_loans_due_soon
ON loans(due_date)
WHERE status = 'ACTIVE'
ORDER BY due_date ASC;
```

---

### 6. Tabela: notifications (DODATEK)

**Opis:** Powiadomienia dla użytkowników

#### Kolumny:

| Nazwa      | Typ          | Ograniczenia                            | Opis                                 |
| ---------- | ------------ | --------------------------------------- | ------------------------------------ |
| id         | UUID         | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unikalny identyfikator powiadomienia |
| user_id    | UUID         | NOT NULL, FOREIGN KEY → users(id)       | Identyfikator użytkownika            |
| type       | VARCHAR(50)  | NOT NULL                                | Typ powiadomienia                    |
| title      | VARCHAR(200) | NOT NULL                                | Tytuł powiadomienia                  |
| message    | TEXT         | NOT NULL                                | Treść powiadomienia                  |
| read       | BOOLEAN      | NOT NULL, DEFAULT FALSE                 | Czy przeczytane                      |
| read_at    | TIMESTAMP    | NULL                                    | Data przeczytania                    |
| created_at | TIMESTAMP    | NOT NULL, DEFAULT NOW()                 | Data utworzenia                      |

#### Enum: NotificationType

```sql
CREATE TYPE notification_type AS ENUM (
    'LOAN_EXPIRING',           -- Zbliża się termin zwrotu (2 dni przed)
    'LOAN_OVERDUE',            -- Przeterminowane wypożyczenie
    'RESERVATION_READY',       -- Rezerwacja gotowa do odbioru
    'RESERVATION_CANCELLED',   -- Rezerwacja anulowana przez staff
    'RESERVATION_EXPIRED'      -- Rezerwacja wygasła (nie odebrano)
);
```

#### Ograniczenia:

```sql
-- Klucz główny
PRIMARY KEY (id)

-- Klucz obcy (CASCADE)
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE

-- Sprawdzanie typu
CHECK (type IN ('LOAN_EXPIRING', 'LOAN_OVERDUE', 'RESERVATION_READY', 'RESERVATION_CANCELLED', 'RESERVATION_EXPIRED'))
```

#### Indeksy:

```sql
-- Nieprzeczytane powiadomienia użytkownika
CREATE INDEX idx_notifications_user_unread
ON notifications(user_id, read, created_at DESC)
WHERE read = FALSE;

-- Wszystkie powiadomienia użytkownika
CREATE INDEX idx_notifications_user
ON notifications(user_id, created_at DESC);
```

---

### 7. Tabela: audit_logs (DODATEK)

**Opis:** Logi audytowe - historia krytycznych operacji

#### Kolumny:

| Nazwa       | Typ          | Ograniczenia                            | Opis                                       |
| ----------- | ------------ | --------------------------------------- | ------------------------------------------ |
| id          | UUID         | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unikalny identyfikator logu                |
| user_id     | UUID         | NULL, FOREIGN KEY → users(id)           | Kto wykonał akcję (NULL = system)          |
| action      | VARCHAR(100) | NOT NULL                                | Typ akcji                                  |
| entity_type | VARCHAR(50)  | NOT NULL                                | Typ encji (User, Book, Loan, etc.)         |
| entity_id   | UUID         | NOT NULL                                | ID encji której dotyczy                    |
| metadata    | JSONB        | NULL                                    | Dodatkowe dane (poprzednie wartości, etc.) |
| ip_address  | VARCHAR(45)  | NULL                                    | Adres IP                                   |
| user_agent  | TEXT         | NULL                                    | User agent przeglądarki                    |
| created_at  | TIMESTAMP    | NOT NULL, DEFAULT NOW()                 | Data operacji                              |

#### Przykładowe akcje:

- USER_LOGIN, USER_LOGOUT, USER_REGISTERED
- USER_ROLE_CHANGED, USER_BLOCKED, USER_UNBLOCKED, USER_DELETED
- BOOK_CREATED, BOOK_UPDATED, BOOK_DELETED
- COPY_CREATED, COPY_STATUS_CHANGED, COPY_DELETED
- RESERVATION_CREATED, RESERVATION_CANCELLED
- LOAN_CREATED, LOAN_RETURNED, LOAN_EXTENDED
- FINE_PAID

#### Ograniczenia:

```sql
-- Klucz główny
PRIMARY KEY (id)

-- Klucz obcy (SET NULL - zachowujemy logi nawet po usunięciu użytkownika)
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
```

#### Indeksy:

```sql
-- Logi według użytkownika
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, created_at DESC);

-- Logi według akcji
CREATE INDEX idx_audit_logs_action ON audit_logs(action, created_at DESC);

-- Logi według encji
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id, created_at DESC);

-- Logi według daty
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);

-- JSONB index dla metadanych
CREATE INDEX idx_audit_logs_metadata ON audit_logs USING gin(metadata);
```

---

### 8. Tabela: settings (OPCJONALNIE)

**Opis:** Ustawienia systemowe

#### Kolumny:

| Nazwa         | Typ          | Ograniczenia                  | Opis                                          |
| ------------- | ------------ | ----------------------------- | --------------------------------------------- |
| key           | VARCHAR(100) | PRIMARY KEY                   | Klucz ustawienia                              |
| value         | TEXT         | NOT NULL                      | Wartość (może być JSON)                       |
| value_type    | VARCHAR(20)  | NOT NULL                      | Typ wartości (string, int, float, bool, json) |
| description   | TEXT         | NULL                          | Opis ustawienia                               |
| updated_by_id | UUID         | NULL, FOREIGN KEY → users(id) | Admin który zmienił                           |
| updated_at    | TIMESTAMP    | NOT NULL, DEFAULT NOW()       | Data ostatniej zmiany                         |

#### Przykładowe ustawienia:

```sql
INSERT INTO settings (key, value, value_type, description) VALUES
('reservation_duration_days', '3', 'int', 'Czas trwania rezerwacji w dniach'),
('loan_duration_days', '14', 'int', 'Czas trwania wypożyczenia w dniach'),
('max_reservations_per_user', '3', 'int', 'Maksymalna liczba aktywnych rezerwacji na użytkownika'),
('max_loans_per_user', '5', 'int', 'Maksymalna liczba aktywnych wypożyczeń na użytkownika'),
('fine_per_day', '1.00', 'float', 'Kara za jeden dzień przeterminowania (PLN)'),
('max_fine_amount', '100.00', 'float', 'Maksymalna kara (PLN)'),
('allow_loan_extension', 'true', 'bool', 'Czy można przedłużać wypożyczenia'),
('notification_loan_expiring_days', '2', 'int', 'Ile dni przed terminem wysłać powiadomienie');
```

#### Ograniczenia:

```sql
-- Klucz główny
PRIMARY KEY (key)

-- Klucz obcy
FOREIGN KEY (updated_by_id) REFERENCES users(id) ON DELETE SET NULL

-- Sprawdzanie typu wartości
CHECK (value_type IN ('string', 'int', 'float', 'bool', 'json'))
```

---

### 9. Tabela: refresh_tokens

**Opis:** Tokeny odświeżające sesję (dla bezpieczeństwa)

#### Kolumny:

| Nazwa      | Typ          | Ograniczenia                            | Opis                      |
| ---------- | ------------ | --------------------------------------- | ------------------------- |
| id         | UUID         | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unikalny identyfikator    |
| user_id    | UUID         | NOT NULL, FOREIGN KEY → users(id)       | Identyfikator użytkownika |
| token_hash | VARCHAR(255) | NOT NULL, UNIQUE                        | Hash tokenu (SHA-256)     |
| expires_at | TIMESTAMP    | NOT NULL                                | Data wygaśnięcia (14 dni) |
| revoked    | BOOLEAN      | NOT NULL, DEFAULT FALSE                 | Czy unieważniony (logout) |
| revoked_at | TIMESTAMP    | NULL                                    | Data unieważnienia        |
| created_at | TIMESTAMP    | NOT NULL, DEFAULT NOW()                 | Data utworzenia           |

#### Ograniczenia:

```sql
-- Klucz główny
PRIMARY KEY (id)

-- Hash tokenu unikalny
UNIQUE (token_hash)

-- Klucz obcy (CASCADE)
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE

-- Token musi wygasnąć w przyszłości
CHECK (expires_at > created_at)
```

#### Indeksy:

```sql
-- Szybkie wyszukiwanie po hashu tokenu (weryfikacja)
CREATE UNIQUE INDEX idx_refresh_tokens_hash ON refresh_tokens(token_hash);

-- Tokeny użytkownika (do unieważnienia przy wylogowaniu)
CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id, revoked);

-- Wygasłe tokeny (do czyszczenia przez background job)
CREATE INDEX idx_refresh_tokens_expired
ON refresh_tokens(expires_at)
WHERE revoked = FALSE;
```

---

## Relacje między tabelami

### Diagram relacji (opis tekstowy):

**1. users → users (self-reference):**

- blocked_by_id → users(id)
- role_changed_by_id → users(id)
- deleted_by_id → users(id)

**2. books → users:**

- deleted_by_id → users(id)

**3. book_copies → books:**

- book_id → books(id) (CASCADE)

**4. book_copies → users:**

- deleted_by_id → users(id)

**5. reservations → users:**

- user_id → users(id) (CASCADE)
- cancelled_by_id → users(id)

**6. reservations → book_copies:**

- book_copy_id → book_copies(id) (CASCADE)

**7. loans → users:**

- user_id → users(id) (CASCADE)

**8. loans → book_copies:**

- book_copy_id → book_copies(id) (CASCADE)

**9. loans → reservations:**

- reservation_id → reservations(id)

**10. notifications → users:**

- user_id → users(id) (CASCADE)

**11. audit_logs → users:**

- user_id → users(id) (SET NULL)

**12. settings → users:**

- updated_by_id → users(id)

**13. refresh_tokens → users:**

- user_id → users(id) (CASCADE)

---

## Triggery

### Trigger: aktualizuj_updated_at

**Opis:** Automatycznie aktualizuje pole `updated_at` przy każdej zmianie rekordu

```sql
CREATE OR REPLACE FUNCTION aktualizuj_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Zastosuj dla wszystkich tabel z polem updated_at
CREATE TRIGGER trigger_users_updated
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION aktualizuj_updated_at();

CREATE TRIGGER trigger_books_updated
BEFORE UPDATE ON books
FOR EACH ROW EXECUTE FUNCTION aktualizuj_updated_at();

CREATE TRIGGER trigger_copies_updated
BEFORE UPDATE ON book_copies
FOR EACH ROW EXECUTE FUNCTION aktualizuj_updated_at();

CREATE TRIGGER trigger_loans_updated
BEFORE UPDATE ON loans
FOR EACH ROW EXECUTE FUNCTION aktualizuj_updated_at();

CREATE TRIGGER trigger_settings_updated
BEFORE UPDATE ON settings
FOR EACH ROW EXECUTE FUNCTION aktualizuj_updated_at();
```

---

### Trigger: sprawdz_limit_rezerwacji

**Opis:** Sprawdza czy użytkownik nie przekroczył limitu 3 aktywnych rezerwacji

```sql
CREATE OR REPLACE FUNCTION sprawdz_limit_rezerwacji()
RETURNS TRIGGER AS $$
DECLARE
    liczba_aktywnych INTEGER;
BEGIN
    SELECT COUNT(*) INTO liczba_aktywnych
    FROM reservations
    WHERE user_id = NEW.user_id
      AND status = 'ACTIVE';

    IF liczba_aktywnych >= 3 THEN
        RAISE EXCEPTION 'Użytkownik ma już 3 aktywne rezerwacje (limit)';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_limit_rezerwacji
BEFORE INSERT ON reservations
FOR EACH ROW EXECUTE FUNCTION sprawdz_limit_rezerwacji();
```

---

### Trigger: sprawdz_limit_wypozyczen

**Opis:** Sprawdza czy użytkownik nie przekroczył limitu 5 aktywnych wypożyczeń

```sql
CREATE OR REPLACE FUNCTION sprawdz_limit_wypozyczen()
RETURNS TRIGGER AS $$
DECLARE
    liczba_aktywnych INTEGER;
BEGIN
    SELECT COUNT(*) INTO liczba_aktywnych
    FROM loans
    WHERE user_id = NEW.user_id
      AND status IN ('ACTIVE', 'OVERDUE');

    IF liczba_aktywnych >= 5 THEN
        RAISE EXCEPTION 'Użytkownik ma już 5 aktywnych wypożyczeń (limit)';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_limit_wypozyczen
BEFORE INSERT ON loans
FOR EACH ROW EXECUTE FUNCTION sprawdz_limit_wypozyczen();
```

---

### Trigger: zmien_status_egzemplarza

**Opis:** Automatycznie zmienia status egzemplarza przy wypożyczeniu/zwrocie

```sql
CREATE OR REPLACE FUNCTION zmien_status_egzemplarza()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        -- Wypożyczenie - zmień status na LOANED
        UPDATE book_copies
        SET status = 'LOANED'
        WHERE id = NEW.book_copy_id;

    ELSIF (TG_OP = 'UPDATE' AND NEW.returned_at IS NOT NULL AND OLD.returned_at IS NULL) THEN
        -- Zwrot - zmień status na AVAILABLE
        UPDATE book_copies
        SET status = 'AVAILABLE'
        WHERE id = NEW.book_copy_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_status_egzemplarza
AFTER INSERT OR UPDATE ON loans
FOR EACH ROW EXECUTE FUNCTION zmien_status_egzemplarza();
```

---

## 📊 Widoki (Views)

### Widok: dostepne_ksiazki

**Opis:** Pokazuje książki z liczbą dostępnych egzemplarzy

```sql
CREATE VIEW dostepne_ksiazki AS
SELECT
    b.id,
    b.isbn,
    b.title,
    b.authors,
    b.publisher,
    b.year,
    b.genre,
    COUNT(c.id) AS wszystkie_egzemplarze,
    COUNT(c.id) FILTER (WHERE c.status = 'AVAILABLE') AS dostepne_egzemplarze
FROM books b
LEFT JOIN book_copies c ON b.id = c.book_id AND c.is_deleted = FALSE
WHERE b.is_deleted = FALSE
GROUP BY b.id;
```

**Użycie:**

```sql
SELECT * FROM dostepne_ksiazki WHERE dostepne_egzemplarze > 0;
```

---

### Widok: przeterminowane_wypozyczenia

**Opis:** Pokazuje przeterminowane wypożyczenia z obliczoną karą

```sql
CREATE VIEW przeterminowane_wypozyczenia AS
SELECT
    l.id,
    l.user_id,
    u.email,
    u.first_name,
    u.last_name,
    l.book_copy_id,
    b.title,
    l.loaned_at,
    l.due_date,
    CURRENT_DATE - DATE(l.due_date) AS dni_przeterminowania,
    LEAST((CURRENT_DATE - DATE(l.due_date)) * 1.00, 100.00) AS obliczona_kara,
    l.fine_amount,
    l.fine_paid
FROM loans l
JOIN users u ON l.user_id = u.id
JOIN book_copies c ON l.book_copy_id = c.id
JOIN books b ON c.book_id = b.id
WHERE l.status IN ('ACTIVE', 'OVERDUE')
  AND l.returned_at IS NULL
  AND l.due_date < CURRENT_DATE;
```

**Użycie:**

```sql
SELECT * FROM przeterminowane_wypozyczenia WHERE fine_paid = FALSE;
```

---

### Widok: statystyki_uzytkownikow

**Opis:** Podsumowanie aktywności użytkowników

```sql
CREATE VIEW statystyki_uzytkownikow AS
SELECT
    u.id,
    u.email,
    u.first_name,
    u.last_name,
    u.role,
    COUNT(DISTINCT r.id) FILTER (WHERE r.status = 'ACTIVE') AS aktywne_rezerwacje,
    COUNT(DISTINCT l.id) FILTER (WHERE l.status IN ('ACTIVE', 'OVERDUE')) AS aktywne_wypozyczenia,
    COUNT(DISTINCT l.id) FILTER (WHERE l.status = 'OVERDUE') AS przeterminowane_wypozyczenia,
    COALESCE(SUM(l.fine_amount) FILTER (WHERE l.fine_paid = FALSE), 0) AS nieoplacone_kary
FROM users u
LEFT JOIN reservations r ON u.id = r.user_id
LEFT JOIN loans l ON u.id = l.user_id
WHERE u.is_deleted = FALSE
GROUP BY u.id;
```

---

## Zapytania przykładowe

### 1. Najpopularniejsze książki (najwięcej wypożyczeń)

```sql
SELECT
    b.title,
    b.authors,
    COUNT(l.id) AS liczba_wypozyczen
FROM books b
JOIN book_copies c ON b.id = c.book_id
JOIN loans l ON c.id = l.book_copy_id
WHERE b.is_deleted = FALSE
GROUP BY b.id, b.title, b.authors
ORDER BY liczba_wypozyczen DESC
LIMIT 10;
```

---

### 2. Użytkownicy z największą sumą kar

```sql
SELECT
    u.first_name,
    u.last_name,
    u.email,
    SUM(l.fine_amount) AS suma_kar,
    COUNT(l.id) FILTER (WHERE l.fine_amount > 0) AS liczba_kar
FROM users u
JOIN loans l ON u.id = l.user_id
WHERE l.fine_paid = FALSE
  AND u.is_deleted = FALSE
GROUP BY u.id, u.first_name, u.last_name, u.email
HAVING SUM(l.fine_amount) > 0
ORDER BY suma_kar DESC;
```

---

### 3. Książki bez dostępnych egzemplarzy

```sql
SELECT
    b.title,
    b.authors,
    b.isbn,
    COUNT(c.id) AS wszystkie_egzemplarze,
    COUNT(c.id) FILTER (WHERE c.status = 'AVAILABLE') AS dostepne
FROM books b
LEFT JOIN book_copies c ON b.id = c.book_id AND c.is_deleted = FALSE
WHERE b.is_deleted = FALSE
GROUP BY b.id, b.title, b.authors, b.isbn
HAVING COUNT(c.id) FILTER (WHERE c.status = 'AVAILABLE') = 0
   AND COUNT(c.id) > 0;
```

---

### 4. Aktywne rezerwacje z czasem oczekiwania

```sql
SELECT
    u.first_name,
    u.last_name,
    b.title,
    r.reserved_at,
    r.expires_at,
    EXTRACT(EPOCH FROM (r.expires_at - NOW())) / 3600 AS godzin_do_wygasniecia
FROM reservations r
JOIN users u ON r.user_id = u.id
JOIN book_copies c ON r.book_copy_id = c.id
JOIN books b ON c.book_id = b.id
WHERE r.status = 'ACTIVE'
ORDER BY r.reserved_at;
```

---

## Migracje (Alembic)

### Tworzenie migracji

```bash
# Wygeneruj nową migrację
alembic revision --autogenerate -m "Utworzenie tabeli users"

# Zastosuj migrację
alembic upgrade head

# Cofnij migrację
alembic downgrade -1

# Historia migracji
alembic history

# Aktualna wersja
alembic current
```

---

## Podsumowanie schematu

**Liczby:**

- 9 głównych tabel
- 5 typów ENUM
- 13 relacji Foreign Key
- 30+ indeksów dla wydajności
- 3 widoki pomocnicze
- 3 triggery dla automatyzacji

**Zgodność z diagramem klas:**

- ✅ Wszystkie tabele zgodne z diagramem UML
- ✅ Relacje 1:N poprawnie zaimplementowane
- ✅ Enums zgodne z diagramem
- ✅ Soft delete dla User, Book, BookCopy
- ✅ Audyt (blocked_by, deleted_by, role_changed_by)

**Zgodność z wymaganiami:**

- ✅ Obsługa 3 ról (RBAC)
- ✅ Limity (3 rezerwacje, 5 wypożyczeń)
- ✅ Kary (1.00 PLN/dzień, max 100 PLN)
- ✅ Rezerwacje wygasają po 3 dniach
- ✅ Wypożyczenia na 14 dni
- ✅ Transakcyjność (SELECT FOR UPDATE constraints)

**Rozmiar przewidywanych danych:**

- Użytkownicy: ~100-1000 rekordów
- Książki: ~1000-10000 rekordów
- Egzemplarze: ~3000-30000 rekordów (średnio 3 na książkę)
- Rezerwacje: ~100-500 aktywnych, ~10000 w historii
- Wypożyczenia: ~10000-100000 rekordów (historia)

**Backup i utrzymanie:**

- Codzienne kopie zapasowe (pg_dump)
- Retention: 30 dni
- VACUUM ANALYZE co tydzień
- Reindeksowanie co miesiąc

---

**Schemat bazy danych stworzony zgodnie z diagramem klas UML i wymaganiami projektu.**
