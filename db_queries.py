"""
Moduł zawiera przykładowe funkcje wykonujące zapytania SQL
dla bazy danych sklepu internetowego NautSA.

Autor: Michał Kraus
"""

import sqlite3
import psycopg2


# =====================================================
# SQLITE
# =====================================================

def sqlite_top_products(db_path="nautsa.db"):
    """
    Zwraca 10 najczęściej kupowanych produktów.

    Cel:
        Wykorzystanie funkcji agregujących i grupowania.

    Parametry:
        db_path (str): ścieżka do pliku SQLite.

    Zwraca:
        list[tuple]:
        (nazwa_produktu, liczba_sprzedanych_sztuk)
    """

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            p.nazwa,
            SUM(pz.liczba_sztuk) AS sprzedano
        FROM produkt p
        JOIN pozycja_zamowienia pz
            ON p.id_produktu = pz.id_produktu
        GROUP BY p.id_produktu
        ORDER BY sprzedano DESC
        LIMIT 10
    """)

    result = cursor.fetchall()

    conn.close()

    return result


def sqlite_customer_orders(email, db_path="nautsa.db"):
    """
    Zwraca wszystkie zamówienia klienta.

    Cel:
        Demonstracja JOIN i selekcji danych.

    Parametry:
        email (str): adres email klienta.

    Zwraca:
        list[tuple]
    """

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            z.id_zamowienia,
            z.data_zlozenia,
            z.status,
            z.wartosc_calkowita
        FROM zamowienie z
        JOIN klient k
            ON k.id_klienta = z.id_klienta
        WHERE k.email = ?
        ORDER BY z.data_zlozenia DESC
    """, (email,))

    result = cursor.fetchall()

    conn.close()

    return result


def sqlite_average_order_value(db_path="nautsa.db"):
    """
    Oblicza średnią wartość zamówienia.

    Cel:
        Wykorzystanie funkcji agregującej AVG().

    Zwraca:
        float
    """

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT AVG(wartosc_calkowita)
        FROM zamowienie
    """)

    result = cursor.fetchone()[0]

    conn.close()

    return result


def sqlite_clients_without_orders(db_path="nautsa.db"):
    """
    Wyszukuje klientów bez żadnego zamówienia.

    Cel:
        Demonstracja podzapytania.

    Zwraca:
        list[tuple]
    """

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id_klienta,
            email
        FROM klient
        WHERE id_klienta NOT IN (
            SELECT id_klienta
            FROM zamowienie
        )
    """)

    result = cursor.fetchall()

    conn.close()

    return result


def sqlite_order_summary(db_path="nautsa.db"):
    """
    Zwraca statystyki zamówień według statusu.

    Cel:
        Grupowanie oraz COUNT().

    Zwraca:
        list[tuple]
    """

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            status,
            COUNT(*)
        FROM zamowienie
        GROUP BY status
    """)

    result = cursor.fetchall()

    conn.close()

    return result


# =====================================================
# POSTGRESQL
# =====================================================

def pg_connect(creds):
    """
    Tworzy połączenie z PostgreSQL.

    Parametry:
        creds (dict):
            host, port, database, user, password

    Zwraca:
        connection
    """

    return psycopg2.connect(
        host=creds["host"],
        port=creds["port"],
        database=creds["database"],
        user=creds["user"],
        password=creds["password"]
    )


def pg_top_customers(creds):
    """
    Zwraca klientów generujących najwyższy obrót.

    Cel:
        JOIN + SUM() + GROUP BY.
    """

    conn = pg_connect(creds)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            k.email,
            SUM(z.wartosc_calkowita) AS obrot
        FROM nautsa.klient k
        JOIN nautsa.zamowienie z
            ON z.id_klienta = k.id_klienta
        GROUP BY k.email
        ORDER BY obrot DESC
        LIMIT 10
    """)

    result = cursor.fetchall()

    conn.close()

    return result


def pg_invoice_report(creds):
    """
    Zwraca raport faktur.

    Cel:
        Demonstracja JOIN pomiędzy
        klientem, zamówieniem i fakturą.
    """

    conn = pg_connect(creds)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            f.numer_faktury,
            k.email,
            f.kwota_brutto
        FROM nautsa.faktura f
        JOIN nautsa.zamowienie z
            ON z.id_zamowienia = f.id_zamowienia
        JOIN nautsa.klient k
            ON k.id_klienta = z.id_klienta
    """)

    result = cursor.fetchall()

    conn.close()

    return result


def pg_products_never_sold(creds):
    """
    Zwraca produkty, które nigdy
    nie wystąpiły w zamówieniu.

    Cel:
        Podzapytanie.
    """

    conn = pg_connect(creds)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT nazwa
        FROM nautsa.produkt
        WHERE id_produktu NOT IN (
            SELECT DISTINCT id_produktu
            FROM nautsa.pozycja_zamowienia
        )
    """)

    result = cursor.fetchall()

    conn.close()

    return result


def pg_order_statistics(creds):
    """
    Zwraca statystyki zamówień.

    Cel:
        MIN, MAX, AVG, COUNT.
    """

    conn = pg_connect(creds)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*),
            MIN(wartosc_calkowita),
            MAX(wartosc_calkowita),
            AVG(wartosc_calkowita)
        FROM nautsa.zamowienie
    """)

    result = cursor.fetchone()

    conn.close()

    return result


def pg_union_contacts(creds):
    """
    Zwraca listę wszystkich kontaktów.

    Cel:
        Demonstracja operatora UNION.
    """

    conn = pg_connect(creds)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT email AS kontakt
        FROM nautsa.klient

        UNION

        SELECT nip_firmy
        FROM nautsa.klient
        WHERE nip_firmy IS NOT NULL
    """)

    result = cursor.fetchall()

    conn.close()

    return result