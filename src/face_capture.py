import cv2, face_recognition, numpy as np, pickle, os 
from .db_helper import register_pelajar_baru

DB_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
ENCODING_FILE = os.path.join(DB_FOLDER, 'face_encoding.pickle')

def get_all_known_encodings():
    if os.path.exists(ENCODING_FILE):
        with open(ENCODING_FILE, 'rb') as f:
            return pickle.load(f)
    else:
        return {"encodings": [], "ids": [], "names": []}
    
def mulai_rekam_wajah(nisn, nama_lengkap, kelas, jurusan):
    
    id_pelajar = register_pelajar_baru(nisn, nama_lengkap, kelas, jurusan)
    if id_pelajar is None:
        return False, "Pendaftaran gagal, NISN sudah exist."
    
    print(f"\n[INFO]: Siswa/i dengan nama {nama_lengkap} terdaftar dengan ID: {id_pelajar}. Mulai merekam...")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return False, "Gagal membuka kamera, pastikan kamera tidak digunakan aplikasi lain."
    
    SAMPLE_COUNT_TARGET = 7
    samples_captured = 0 
    encodings_list = []
    
    while samples_captured < SAMPLE_COUNT_TARGET:
        ret, frame = cap.read()
        if not ret: break 
        
        frame = cv2.flip(frame, 1)
        
        cv2.putText(frame, f"Siswa/i: {nama_lengkap} | Sampel: {samples_captured} / {SAMPLE_COUNT_TARGET}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, "Tekan 'S' untuk ambil sample", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        cv2.imshow("ATLAS Perekam Wajah (Tekan Esc untuk batal)", frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s'):
            face_locations = face_recognition.face_locations(frame)
            if len(face_locations) == 1:
                face_encoding = face_recognition.face_encodings(frame, face_locations)
                
                if face_encoding: 
                    encodings_list.append(face_encoding[0])
                    samples_captured += 1 
                    
                    cv2.putText(frame, "Direkam!", (10, 400), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1, (0, 0, 255), 3)
                    cv2.imshow(frame, "ATLAS Perekam Wajah (Tekan Esc untuk batal.)")
                    cv2.waitKey(500)
                    
        elif len(face_locations) > 1:
            print(" [WARNING]: Wajah terdeteksi lebih dari 1.")
        else: 
            print(" [WARNING]: Wajah tidak terdeteksi")
            
        if key == ord('esc'):
            break
        
        cap.release()
        cv2.destroyAllWindows()
        
        if len(encodings_list) >= SAMPLE_COUNT_TARGET:
            avg_encoding = np.mean(encodings_list, axis=0)
            
            data = get_all_known_encodings()
            data["encodings"].append(avg_encoding)
            data["ids"].append(id_pelajar)
            data["names"].append(nama_lengkap)
            
            with open(ENCODING_FILE, 'wb') as f:
                pickle.dump(data, f)
                
            return True, f"Wajah dengan nama {nama_lengkap} berhasil didaftarkan! Total {len(data['encodings'])} data."
        
        else:
            return False, "Pendaftaran wajah dibatalkan/kurang sampel."
        
    