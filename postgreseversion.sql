CREATE SCHEMA IF NOT EXISTS nautsa;

-- =========================================================
-- TYPY ENUM
-- =========================================================

CREATE TYPE nautsa.typ_klienta_enum AS ENUM (
    'osoba_fizyczna',
    'firma'
);

CREATE TYPE nautsa.typ_adresu_enum AS ENUM (
    'dostawowy',
    'fakturowy',
    'korespondencyjny'
);

CREATE TYPE nautsa.typ_produktu_enum AS ENUM (
    'plyta_glowna',
    'pamiec_ram',
    'procesor',
    'karta_graficzna',
    'dysk',
    'obudowa',
    'zasilacz',
    'inne'
);

CREATE TYPE nautsa.status_zamowienia_enum AS ENUM (
    'przyjete',
    'oplacone',
    'w_realizacji',
    'wyslane',
    'dostarczone',
    'anulowane'
);

CREATE TYPE nautsa.metoda_platnosci_enum AS ENUM (
    'przelew',
    'karta',
    'blik',
    'za_pobraniem'
);

-- =========================================================
-- TABELA KLIENT
-- =========================================================

CREATE TABLE IF NOT EXISTS nautsa.klient (
    id_klienta SERIAL PRIMARY KEY,

    typ_klienta nautsa.typ_klienta_enum NOT NULL,

    imie VARCHAR(100),
    nazwisko VARCHAR(100),

    nazwa_firmy VARCHAR(255),

    email VARCHAR(255) NOT NULL UNIQUE,
    telefon VARCHAR(20),

    pesel CHAR(11) UNIQUE,
    nip_firmy VARCHAR(15) UNIQUE,

    data_utworzenia TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT check_klient_spojnosc
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

CREATE TABLE IF NOT EXISTS nautsa.adres (
    id_adresu SERIAL PRIMARY KEY,

    ulica VARCHAR(255) NOT NULL,
    numer_domu VARCHAR(10) NOT NULL,
    numer_mieszkania VARCHAR(10),

    miasto VARCHAR(100) NOT NULL,
    kod_pocztowy VARCHAR(10) NOT NULL,

    kraj VARCHAR(100) NOT NULL DEFAULT 'Polska',

    typ_adresu nautsa.typ_adresu_enum NOT NULL,

    id_klienta INTEGER NOT NULL,

    CONSTRAINT fk_adres_klient
        FOREIGN KEY (id_klienta)
        REFERENCES nautsa.klient(id_klienta)
        ON DELETE CASCADE
);

-- =========================================================
-- TABELA PRODUKT
-- =========================================================

CREATE TABLE IF NOT EXISTS nautsa.produkt (
    id_produktu SERIAL PRIMARY KEY,

    nazwa VARCHAR(255) NOT NULL,

    producent VARCHAR(100) NOT NULL DEFAULT 'Nieznany',

    opis TEXT,

    cena_jednostkowa NUMERIC(10,2) NOT NULL
        CHECK (cena_jednostkowa >= 0),

    stan_magazynowy INTEGER NOT NULL DEFAULT 0
        CHECK (stan_magazynowy >= 0),

    typ_produktu nautsa.typ_produktu_enum NOT NULL,

    data_dodania TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- TABELA ZAMOWIENIE
-- =========================================================

CREATE TABLE IF NOT EXISTS nautsa.zamowienie (
    id_zamowienia SERIAL PRIMARY KEY,

    data_zlozenia TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    data_wysylki TIMESTAMPTZ,

    status nautsa.status_zamowienia_enum NOT NULL,

    metoda_platnosci nautsa.metoda_platnosci_enum NOT NULL,

    wartosc_calkowita NUMERIC(10,2) NOT NULL
        CHECK (wartosc_calkowita >= 0),

    id_klienta INTEGER NOT NULL,

    adres_dostawy_id INTEGER NOT NULL,

    CONSTRAINT fk_zamowienie_klient
        FOREIGN KEY (id_klienta)
        REFERENCES nautsa.klient(id_klienta)
        ON DELETE RESTRICT,

    CONSTRAINT fk_zamowienie_adres
        FOREIGN KEY (adres_dostawy_id)
        REFERENCES nautsa.adres(id_adresu)
        ON DELETE RESTRICT,

    CONSTRAINT check_data_wysylki
        CHECK (
            data_wysylki IS NULL
            OR data_wysylki >= data_zlozenia
        )
);

-- =========================================================
-- TABELA POZYCJA_ZAMOWIENIA
-- =========================================================

CREATE TABLE IF NOT EXISTS nautsa.pozycja_zamowienia (
    id_pozycji SERIAL PRIMARY KEY,

    liczba_sztuk INTEGER NOT NULL
        CHECK (liczba_sztuk > 0),

    cena_w_momencie_zakupu NUMERIC(10,2) NOT NULL
        CHECK (cena_w_momencie_zakupu >= 0),

    id_zamowienia INTEGER NOT NULL,

    id_produktu INTEGER NOT NULL,

    CONSTRAINT fk_pozycja_zamowienie
        FOREIGN KEY (id_zamowienia)
        REFERENCES nautsa.zamowienie(id_zamowienia)
        ON DELETE CASCADE,

    CONSTRAINT fk_pozycja_produkt
        FOREIGN KEY (id_produktu)
        REFERENCES nautsa.produkt(id_produktu)
        ON DELETE RESTRICT,

    CONSTRAINT unique_produkt_w_zamowieniu
        UNIQUE (id_zamowienia, id_produktu)
);

-- =========================================================
-- TABELA FAKTURA
-- =========================================================

CREATE TABLE IF NOT EXISTS nautsa.faktura (
    id_faktury SERIAL PRIMARY KEY,

    numer_faktury VARCHAR(100) NOT NULL UNIQUE,

    data_wystawienia TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    kwota_brutto NUMERIC(10,2) NOT NULL
        CHECK (kwota_brutto >= 0),

    sciezka_pliku TEXT,

    id_zamowienia INTEGER NOT NULL UNIQUE,

    CONSTRAINT fk_faktura_zamowienie
        FOREIGN KEY (id_zamowienia)
        REFERENCES nautsa.zamowienie(id_zamowienia)
        ON DELETE RESTRICT
);

-- =========================================================
-- INDEKSY
-- =========================================================

CREATE INDEX idx_adres_klient
ON nautsa.adres(id_klienta);

CREATE INDEX idx_zamowienie_klient
ON nautsa.zamowienie(id_klienta);

CREATE INDEX idx_zamowienie_status
ON nautsa.zamowienie(status);

CREATE INDEX idx_pozycja_zamowienie
ON nautsa.pozycja_zamowienia(id_zamowienia);

CREATE INDEX idx_pozycja_produkt
ON nautsa.pozycja_zamowienia(id_produktu);

CREATE INDEX idx_produkt_typ
ON nautsa.produkt(typ_produktu);

CREATE INDEX idx_faktura_zamowienie
ON nautsa.faktura(id_zamowienia);
