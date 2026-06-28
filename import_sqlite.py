#!/usr/bin/env python3
"""
Import danych testowych CSV do bazy SQLite.

Założenia:
- nazwa pliku CSV = nazwa tabeli
- pierwszy wiersz zawiera nazwy kolumn
- import wykonywany jest w kolejności zgodnej z kluczami obcymi
"""

import csv
import sqlite3
import sys
from pathlib import Path


DB_PATH = "nautsa.db"

IMPORT_ORDER = [
    "klient",
    "adres",
    "produkt",
    "zamowienie",
    "pozycja_zamowienia",
    "faktura"
]


def table_exists(conn, table_name):
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name=?
        """,
        (table_name,)
    )

    return cursor.fetchone() is not None


def import_csv_to_sqlite(csv_path, table_name, conn):
    try:
        with open(csv_path, "r", encoding="utf-8", newline="") as csvfile:

            reader = csv.reader(csvfile)

            try:
                header = next(reader)
            except StopIteration:
                print(f"[POMINIĘTO] {csv_path.name} - pusty plik")
                return

            rows = list(reader)

            if not rows:
                print(f"[POMINIĘTO] {csv_path.name} - brak danych")
                return

            columns = ", ".join(f'"{col}"' for col in header)
            placeholders = ", ".join("?" for _ in header)

            sql = (
                f"INSERT INTO {table_name} "
                f"({columns}) "
                f"VALUES ({placeholders})"
            )

            cursor = conn.cursor()
            cursor.executemany(sql, rows)

            conn.commit()

            print(
                f"[OK] {table_name}: "
                f"zaimportowano {len(rows)} rekordów"
            )

    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"[BŁĄD FK/UNIQUE] {table_name}: {e}")

    except sqlite3.Error as e:
        conn.rollback()
        print(f"[BŁĄD SQLITE] {table_name}: {e}")

    except Exception as e:
        conn.rollback()
        print(f"[BŁĄD] {table_name}: {e}")


def main():

    csv_dir = input(
        "Podaj katalog z plikami CSV "
        "(ENTER = bieżący katalog): "
    ).strip()

    if not csv_dir:
        csv_dir = "."

    csv_dir = Path(csv_dir)

    if not csv_dir.exists():
        print(f"Katalog nie istnieje: {csv_dir}")
        sys.exit(1)

    try:
        with sqlite3.connect(DB_PATH) as conn:

            conn.execute("PRAGMA foreign_keys = ON")

            print(f"Połączono z bazą: {DB_PATH}")

            available_files = {
                f.stem: f
                for f in csv_dir.glob("*.csv")
            }

            if not available_files:
                print("Nie znaleziono plików CSV.")
                return

            print(
                f"Znaleziono {len(available_files)} "
                f"plików CSV.\n"
            )

            for table_name in IMPORT_ORDER:

                if table_name not in available_files:
                    continue

                if not table_exists(conn, table_name):
                    print(
                        f"[POMINIĘTO] "
                        f"Tabela '{table_name}' nie istnieje."
                    )
                    continue

                csv_file = available_files[table_name]

                print(
                    f"Import: "
                    f"{csv_file.name} -> {table_name}"
                )

                import_csv_to_sqlite(
                    csv_file,
                    table_name,
                    conn
                )

            print("\nImport zakończony.")

    except sqlite3.Error as e:
        print(f"Błąd połączenia z bazą: {e}")


if __name__ == "__main__":
    main()