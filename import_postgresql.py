#!/usr/bin/env python3

"""
Import danych testowych CSV do PostgreSQL.

Założenia:

 nazwa pliku CSV = nazwa tabeli
 pierwszy wiersz zawiera nazwy kolumn
 import wykonywany jest w kolejności zgodnej z kluczami obcymi
 dane logowania pobierane są z pliku database_creds.json
  """

import csv
import json
import psycopg2
import sys
from pathlib import Path

SCHEMA_FILE = "postgreseversion.sql"

IMPORT_ORDER = [
    "klient",
    "adres",
    "produkt",
    "zamowienie",
    "pozycja_zamowienia",
    "faktura"
]

def load_credentials(creds_path="database_creds.json"):
    creds_file = Path(creds_path)

    if not creds_file.exists():
        print(f"Nie znaleziono pliku {creds_path}")
        sys.exit(1)

    try:
        with open(creds_file, "r", encoding="utf-8") as f:
            creds = json.load(f)

        required = [
            "host",
            "port",
            "database",
            "user",
            "password"
        ]

        for field in required:
            if field not in creds:
                print(
                    f" Brak pola '{field}' "
                    f"w pliku {creds_path}"
                )
                sys.exit(1)

        return creds

    except json.JSONDecodeError:
        print(" Niepoprawny plik JSON.")
        sys.exit(1)


def create_schema(conn, schema_file=SCHEMA_FILE):

    sql_file = Path(schema_file)

    if not sql_file.exists():
        print(
            f" Nie znaleziono {schema_file}. "
            f"Pomijam tworzenie schematu."
        )
        return

    try:
        with open(sql_file, "r", encoding="utf-8") as f:
            sql = f.read()

        with conn.cursor() as cursor:
            cursor.execute(sql)

        conn.commit()

        print(" Schemat został utworzony.")

    except psycopg2.Error as e:
        conn.rollback()
        print(f" Błąd tworzenia schematu:\n{e}")
        sys.exit(1)


def table_exists(conn, table_name):


    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'nautsa'
                AND table_name = %s
            )
            """,
            (table_name,)
        )

        return cursor.fetchone()[0]


def import_csv_to_postgresql(csv_path, table_name, conn):


    try:

        with open(csv_path, "r", encoding="utf-8") as f:

            try:
                header = next(csv.reader(f))
            except StopIteration:
                print(
                    f" {csv_path.name} jest pusty."
                )
                return

            f.seek(0)

            columns = ", ".join(
                f'"{c}"'
                for c in header
            )

            copy_sql = f"""
                COPY nautsa.{table_name}
                ({columns})
                FROM STDIN
                WITH (
                    FORMAT CSV,
                    HEADER TRUE
                )
            """

            with conn.cursor() as cursor:
                cursor.copy_expert(copy_sql, f)

            conn.commit()

            print(
                f" {table_name}: "
                f"zaimportowano dane."
            )

    except psycopg2.Error as e:

        conn.rollback()

        print(
            f" Błąd PostgreSQL "
            f"dla tabeli {table_name}:\n{e}"
        )

    except Exception as e:

        conn.rollback()

        print(
            f"Błąd importu "
            f"{table_name}: {e}"
        )


def main():


    csv_dir = input(
        "Podaj katalog z CSV "
        "(ENTER = bieżący katalog): "
    ).strip()

    if not csv_dir:
        csv_dir = "."

    csv_dir = Path(csv_dir)

    if not csv_dir.exists():
        print(f" Katalog nie istnieje: {csv_dir}")
        sys.exit(1)

    creds = load_credentials()

    try:

        with psycopg2.connect(
            host=creds["host"],
            port=creds["port"],
            database=creds["database"],
            user=creds["user"],
            password=creds["password"]
        ) as conn:

            print(" Połączono z PostgreSQL.")

            create_schema(conn)

            available_files = {
                f.stem: f
                for f in csv_dir.glob("*.csv")
            }

            if not available_files:
                print(" Nie znaleziono plików CSV.")
                return

            print(
                f"\nZnaleziono "
                f"{len(available_files)} plików CSV.\n"
            )

            for table_name in IMPORT_ORDER:

                if table_name not in available_files:
                    continue

                if not table_exists(conn, table_name):

                    print(
                        f" Pominięto {table_name} "
                        f"(brak tabeli)."
                    )

                    continue

                csv_file = available_files[table_name]

                print(
                    f" Import: "
                    f"{csv_file.name} "
                    f"-> {table_name}"
                )

                import_csv_to_postgresql(
                    csv_file,
                    table_name,
                    conn
                )

            print("\nImport zakończony.")

    except psycopg2.Error as e:

        print(
            f" Błąd połączenia "
            f"z PostgreSQL:\n{e}"
        )


if __name__ == "__main__":
    main()
