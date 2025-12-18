import cv2
import face_recognition
import numpy as np
import pickle
import os 
from .db_helper import register_pelajar_baru

# Pastikan path ini benar sesuai struktur foldermu
DB_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
# Perbaiki nama file agar konsisten (tadi ada typo encoding vs encodings)
ENCODING_FILE = os.path.join(DB_FOLDER, 'face_encodings.pickle') 

def get_all_known_encodings():
    if os.path.exists(ENCODING_FILE):
        with open(ENCODING_FILE, 'rb') as f:
            return pickle.load(f)
    else:
        return {"encodings": [], "ids": [], "names": []}
    
def mulai_rekam_wajah(nisn, nama_lengkap, kelas, jurusan):
    
    id_pelajar = register_pelajar_baru(nisn, nama_lengkap, kelas, jurusan)
    if id_pelajar is None:
        return False, "Pendaftaran gagal, NISN mungkin sudah terdaftar."
    
    print(f"\n[INFO]: Siswa/i {nama_lengkap} (ID: {id_pelajar}). Mulai merekam...")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return False, "Gagal membuka kamera. Pastikan tidak dipakai aplikasi lain."
    
    SAMPLE_COUNT_TARGET = 7
    samples_captured = 0 
    encodings_list = []
    
    while samples_captured < SAMPLE_COUNT_TARGET:
        ret, frame = cap.read()
        if not ret: break 
        
        frame = cv2.flip(frame, 1)
        
        # UI Overlay
        cv2.putText(frame, f"Siswa: {nama_lengkap}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, f"Sampel: {samples_captured}/{SAMPLE_COUNT_TARGET}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, "Tekan 'S' simpan, 'Q' batal", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        cv2.imshow("ATLAS Perekam Wajah", frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        # --- PERBAIKAN 1: INDENTASI ---
        if key == ord('s'):
            face_locations = face_recognition.face_locations(frame)
            
            # Cek jumlah wajah (Semua logika ini MASUK ke dalam if 's')
            if len(face_locations) == 1:
                face_encoding = face_recognition.face_encodings(frame, face_locations)
                
                if face_encoding: 
                    encodings_list.append(face_encoding[0])
                    samples_captured += 1 
                    
                    cv2.putText(frame, "TEREKAM!", (10, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                    cv2.imshow("ATLAS Perekam Wajah", frame) # Syntax imshow: (NamaWindow, Gambar)
                    cv2.waitKey(500) # Pause 0.5 detik
                    
            elif len(face_locations) > 1:
                print(" [WARNING]: Wajah terdeteksi lebih dari 1.")
            else: 
                print(" [WARNING]: Wajah tidak terdeteksi")
        # ------------------------------
            
        if key == ord('q') or key == 27: # 27 = ESC
            print("[INFO] Pendaftaran dibatalkan user.")
            break
        
    # --- PERBAIKAN 2: RELEASE DI LUAR LOOP ---
    # Kode ini sekarang sejajar dengan while, bukan di dalamnya
    cap.release()
    cv2.destroyAllWindows()
    # -----------------------------------------
    
    # Simpan Data
    if len(encodings_list) >= SAMPLE_COUNT_TARGET:
        print("[INFO] Menghitung rata-rata wajah...")
        avg_encoding = np.mean(encodings_list, axis=0)
        
        data = get_all_known_encodings()
        data["encodings"].append(avg_encoding)
        data["ids"].append(id_pelajar)
        data["names"].append(nama_lengkap)
        
        # Pastikan folder ada sebelum simpan
        if not os.path.exists(DB_FOLDER):
            os.makedirs(DB_FOLDER)

        with open(ENCODING_FILE, 'wb') as f:
            pickle.dump(data, f)
            
        return True, f"Wajah {nama_lengkap} berhasil disimpan!"
        
    else:
        return False, "Pendaftaran dibatalkan / Sampel kurang."