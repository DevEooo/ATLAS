import sqlite3, csv, os
from datetime import datetime
from tkinter import messagebox

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DB_FILE = os.path.join(PROJECT_ROOT, 'database', 'atlas.db')

def export_log_csv():
    if not os.path.exists(DB_FILE):
        return False, "[FAIL]: Database tidak ditemukan"
    
    try:
        connect = sqlite3.connect(DB_FILE)
        cursor = connect.cursor()
        
        query = """
            SELECT absensi.tanggal_absen, 
            absensi.waktu_absen,
            siswa.nama_lengkap,
            siswa.kelas,
            siswa.jurusan,
            absensi.tipe_absen,
            absensi.akurasi_kecocokan
            FROM absensi JOIN siswa ON absensi.id_siswa = siswa.id
            ORDER BY absensi.id DESC 
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            return False, "Data absensi masih kosong"
        
        timestamp = datetime.now().strftime("%S-%M-%H_%d-%m-%Y")
        filename = f"Log_Absensi_ATLAS{timestamp}.csv"
        output_path = os.path.join(PROJECT_ROOT, filename)
        
        with open(output_path, 'w', newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["Tanggal", "Jam", "Nama Siswa", "Kelas", "Status", "Akurasi"])
            writer.writerow(rows)
            
        return True, f"Data berhasil disimpan di \n {filename}" 
        
    except Exception as e:
        print(f"[ERROR]: {e}")
        
    finally: 
        if connect:
            connect.close()
            
            