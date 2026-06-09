PRAGMA foreign_keys = ON;

-- =========================================================
-- TABELA KLIENT
-- =========================================================

CREATE TABLE klient (
    id_klienta INTEGER PRIMARY KEY AUTOINCREMENT,

    typ_klienta TEXT NOT NULL
        CHECK (
            typ_klienta IN (
                'osoba_fizyczna',
                'firma'
            )
        ),

    imie TEXT,
    nazwisko TEXT,

    nazwa_firmy TEXT,

    email TEXT NOT NULL UNIQUE,

    telefon TEXT,

    pesel TEXT UNIQUE,

    nip_firmy TEXT UNIQUE,

    data_utworzenia DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CHECK (
        (
            typ_klienta = 'osoba_fizyczna'
            AND imie IS NOT NULL
            AND nazwisko IS NOT NULL
            AND pesel IS NOT NULL
            AND nip_firmy IS NULL
            AND nazwa_firmy IS NULL
        )
        OR
        (
            typ_klienta = 'firma'
            AND nazwa_firmy IS NOT NULL
            AND nip_firmy IS NOT NULL
            AND pesel IS NULL
        )
    )
);

-- =========================================================
-- TABELA ADRES
-- =========================================================

CREATE TABLE adres (
    id_adresu INTEGER PRIMARY KEY AUTOINCREMENT,

    ulica TEXT NOT NULL,
    numer_domu TEXT NOT NULL,
    numer_mieszkania TEXT,

    miasto TEXT NOT NULL,
    kod_pocztowy TEXT NOT NULL,

    kraj TEXT NOT NULL DEFAULT 'Polska',

    typ_adresu TEXT NOT NULL
        CHECK (
            typ_adresu IN (
                'dostawowy',
                'fakturowy',
                'korespondencyjny'
            )
        ),

    id_klienta INTEGER NOT NULL,

    FOREIGN KEY (id_klienta)
        REFERENCES klient(id_klienta)
        ON DELETE CASCADE
);

-- =========================================================
-- TABELA PRODUKT
-- =========================================================

CREATE TABLE produkt (
    id_produktu INTEGER PRIMARY KEY AUTOINCREMENT,

    nazwa TEXT NOT NULL,

    producent TEXT NOT NULL
        DEFAULT 'Nieznany',

    opis TEXT,

    cena_jednostkowa NUMERIC NOT NULL
        CHECK (cena_jednostkowa >= 0),

    stan_magazynowy INTEGER NOT NULL
        DEFAULT 0
        CHECK (stan_magazynowy >= 0),

    typ_produktu TEXT NOT NULL
        CHECK (
            typ_produktu IN (
                'plyta_glowna',
                'pamiec_ram',
                'procesor',
                'karta_graficzna',
                'dysk',
                'obudowa',
                'zasilacz',
                'inne'
            )
        ),

    data_dodania DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- TABELA ZAMOWIENIE
-- =========================================================

CREATE TABLE zamowienie (
    id_zamowienia INTEGER PRIMARY KEY AUTOINCREMENT,

    data_zlozenia DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    data_wysylki DATETIME,

    status TEXT NOT NULL
        CHECK (
            status IN (
                'przyjete',
                'oplacone',
                'w_realizacji',
                'wyslane',
                'dostarczone',
                'anulowane'
            )
        ),

    metoda_platnosci TEXT NOT NULL
        CHECK (
            metoda_platnosci IN (
                'przelew',
                'karta',
                'blik',
                'za_pobraniem'
            )
        ),

    wartosc_calkowita NUMERIC NOT NULL
        CHECK (wartosc_calkowita >= 0),

    id_klienta INTEGER NOT NULL,

    adres_dostawy_id INTEGER NOT NULL,

    FOREIGN KEY (id_klienta)
        REFERENCES klient(id_klienta)
        ON DELETE RESTRICT,

    FOREIGN KEY (adres_dostawy_id)
        REFERENCES adres(id_adresu)
        ON DELETE RESTRICT,

    CHECK (
        data_wysylki IS NULL
        OR data_wysylki >= data_zlozenia
    )
);

-- =========================================================
-- TABELA POZYCJA_ZAMOWIENIA
-- =========================================================

CREATE TABLE pozycja_zamowienia (
    id_pozycji INTEGER PRIMARY KEY AUTOINCREMENT,

    liczba_sztuk INTEGER NOT NULL
        CHECK (liczba_sztuk > 0),

    cena_w_momencie_zakupu NUMERIC NOT NULL
        CHECK (cena_w_momencie_zakupu >= 0),

    id_zamowienia INTEGER NOT NULL,

    id_produktu INTEGER NOT NULL,

    FOREIGN KEY (id_zamowienia)
        REFERENCES zamowienie(id_zamowienia)
        ON DELETE CASCADE,

    FOREIGN KEY (id_produktu)
        REFERENCES produkt(id_produktu)
        ON DELETE RESTRICT,

    UNIQUE (id_zamowienia, id_produktu)
);

-- =========================================================
-- TABELA FAKTURA
-- =========================================================

CREATE TABLE faktura (
    id_faktury INTEGER PRIMARY KEY AUTOINCREMENT,

    numer_faktury TEXT NOT NULL UNIQUE,

    data_wystawienia DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    kwota_brutto NUMERIC NOT NULL
        CHECK (kwota_brutto >= 0),

    sciezka_pliku TEXT,

    id_zamowienia INTEGER NOT NULL UNIQUE,

    FOREIGN KEY (id_zamowienia)
        REFERENCES zamowienie(id_zamowienia)
        ON DELETE RESTRICT
);

-- =========================================================
-- INDEKSY
-- =========================================================

CREATE INDEX idx_adres_klient
ON adres(id_klienta);

CREATE INDEX idx_zamowienie_klient
ON zamowienie(id_klienta);

CREATE INDEX idx_zamowienie_status
ON zamowienie(status);

CREATE INDEX idx_pozycja_zamowienie
ON pozycja_zamowienia(id_zamowienia);

CREATE INDEX idx_pozycja_produkt
ON pozycja_zamowienia(id_produktu);

CREATE INDEX idx_produkt_typ
ON produkt(typ_produktu);

CREATE INDEX idx_faktura_zamowienie
ON faktura(id_zamowienia);
