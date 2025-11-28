# utils_db.py

import sqlite3
from datetime import datetime

DB_NAME = 'atlas.db'

def connect_db():
    """Membuat koneksi ke database SQLite."""
    conn = sqlite3.connect(DB_NAME)
    return conn

def create_tables():
    """Membuat tabel KARYAWAN dan ABSENSI jika belum ada."""
    conn = connect_db()
    cursor = conn.cursor()

    # Tabel 1: KARYAWAN (Menyimpan data user dan face encoding)
    # Encoding disimpan sebagai BLOB (binary data)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS KARYAWAN (
            id INTEGER PRIMARY KEY,
            nama TEXT NOT NULL UNIQUE,
            jabatan TEXT,
            face_encoding BLOB
        )
    ''')

    # Tabel 2: ABSENSI (Menyimpan log absen)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ABSENSI (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            karyawan_id INTEGER,
            nama TEXT NOT NULL,
            waktu_absen TEXT NOT NULL,
            tanggal_absen TEXT NOT NULL,
            FOREIGN KEY (karyawan_id) REFERENCES KARYAWAN(id)
        )
    ''')

    conn.commit()
    conn.close()

# Pastikan tabel dibuat saat script ini diimpor atau dijalankan pertama kali
create_tables()

print(f"Database {DB_NAME} dan tabel telah disiapkan.")

# --- Tambahkan fungsi lain (insert_user, get_all_users, record_absen) nanti ---