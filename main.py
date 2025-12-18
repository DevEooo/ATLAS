import os, cv2, pickle, sys, numpy as np, customtkinter as ctk, face_recognition
 
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, 'src'))

from src.db_helper import get_db_connection
from src.face_capture import mulai_rekam_wajah 
from src.exporter import export_log_csv, export_data_pelajar

ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("blue")

class ATLAS(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ATLAS - Attendance Tracking and Live Verification System")
        self.geometry("1160x720")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.known_face_encodings = []
        self.known_face_ids = []
        self.known_face_names = []
        
        self.cd = {} 
        
        self.load_encodings()
        
        self.buat_sidebar()
        self.buat_main_frame()

        self.cap = cv2.VideoCapture(0)
        self.setup_camera_res() 
        
        if not self.cap.isOpened():
             messagebox.showerror("Kamera tidak dapat diakses")
        
        self.looping_vid()

    def setup_camera_res(self):
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    def buat_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Menu", 
                                       font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 20))

        self.enroll_btn = ctk.CTkButton(self.sidebar_frame, text="Register", 
                                        height=40, command=self.open_enroller_window)
        self.enroll_btn.grid(row=1, column=0, padx=20, pady=10)

        self.report_option = ctk.CTkOptionMenu(self.sidebar_frame, values=["Log Absensi", "Data Pelajar"])
        self.report_option.grid(row=3, column=0, padx=20, pady=5)

        self.download_btn = ctk.CTkButton(self.sidebar_frame, text="Download", 
                                          fg_color="green", hover_color="darkgreen",
                                          command=self.download_action)
        self.download_btn.grid(row=4, column=0, padx=20, pady=(5, 10), sticky="n")

        self.exit_btn = ctk.CTkButton(self.sidebar_frame, text="Keluar", 
                                      fg_color="transparent", border_width=1, border_color="red", text_color="red",
                                      hover_color="#550000", command=self.on_closing)
        self.exit_btn.grid(row=5, column=0, padx=20, pady=20, sticky="s")

    def buat_main_frame(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.video_container = ctk.CTkFrame(self.main_frame, fg_color="black")
        self.video_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        
        self.video_label = ctk.CTkLabel(self.video_container, text="Memuat kamera...", text_color="white")
        self.video_label.pack(expand=True, fill="both")

        self.status_label = ctk.CTkLabel(self.main_frame, text="Menunggu Wajah...", 
                                         fg_color="#333333", corner_radius=8, height=45, 
                                         font=("Arial", 16, "bold"))
        self.status_label.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

    def download_action(self):
        pilihan = self.report_option.get()
        dialog = ctk.CTkInputDialog(text=f"Masukkan PIN Keamanan", title="Keamanan")
        pin = dialog.get_input()
        
        if pin == "atlas":
            success, msg = False, ""
            if pilihan == "Log Absensi": success, msg = export_log_csv()
            elif pilihan == "Data Pelajar": success, msg = export_data_pelajar()
            
            if success: messagebox.showinfo("Sukses", msg)
            else: messagebox.showwarning("Gagal", msg)
        elif pin is not None:
            messagebox.showerror("PIN yang dimasukan salah!")

    def load_encodings(self):
        try:
            pickle_path = os.path.join(BASE_DIR, 'database', 'face_encodings.pickle')
            if os.path.exists(pickle_path):
                with open(pickle_path, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data["encodings"]
                    self.known_face_ids = data["ids"]
                    self.known_face_names = data["names"]
                print(f"[INFO]: Database dimuat: {len(self.known_face_names)} wajah.")
            else:
                print("[INFO]: Database Kosong.")
        except Exception as e:
            print(f"[ERROR]: Gagal load pickle: {e}")

    def stop_camera(self):
        if self.cap.isOpened(): self.cap.release()
        self.video_label.configure(image=None, text="Menu pendaftaran aktif...")

    def restart_camera(self):
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
            self.setup_camera_res()
            self.looping_vid()

    def open_enroller_window(self):
        if not hasattr(self, 'enroller_window') or self.enroller_window is None or not self.enroller_window.winfo_exists():
            self.enroller_window = ToplevelEnroller(self)
        else:
            self.enroller_window.focus()

    def on_closing(self):
        if messagebox.askokcancel("Keluar", "Yakin mau tutup aplikasi ini?"):
            if self.cap.isOpened(): self.cap.release()
            self.destroy()

    def process_attendance(self, student_id, name, distance):
    
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            now = datetime.now()
            tgl = now.strftime("%Y-%m-%d")
            jam = now.strftime("%H:%M:%S")

            cursor.execute("""
                INSERT INTO absensi (id_siswa, tanggal_absen, waktu_absen, tipe_absen, akurasi_kecocokan)
                VALUES (?, ?, ?, ?, ?)
            """, (student_id, tgl, jam, "Masuk", float(distance)))
            
            conn.commit()
            conn.close()
            
            self.cd[student_id] = now
            print(f"[BERHASIL]: Absen tercatat dengan nama: {name}")
            
        except Exception as e:
            print(f"[ERROR]: Gagal melakukan absen: {e}")

    def looping_vid(self):
        if not self.cap.isOpened(): return

        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            oval_h = int(h / 2.7)
            oval_w = int(oval_h * 0.75)
            center_x, center_y = w // 2, h // 2
            
            mask = np.zeros((h, w, 3), dtype='uint8')
            cv2.ellipse(mask, (center_x, center_y), (oval_w, oval_h), 0, 0, 360, (255, 255, 255), -1)
            blur = cv2.GaussianBlur(frame, (21, 21), 0)
            dimmed = cv2.addWeighted(blur, 0.4, np.zeros_like(frame), 0.6, 0)
            mask_inv = cv2.bitwise_not(cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY))
            fg = cv2.bitwise_and(frame, frame, mask=cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY))
            bg = cv2.bitwise_and(dimmed, dimmed, mask=mask_inv)
            final_frame = cv2.add(fg, bg)
            
            border_color = (56, 56, 54) # Def
            status_bar_text = "Scanning Wajah..."  
            status_bar_color = "#333333" 

            face_locs = face_recognition.face_locations(rgb_small_frame)
            
            if face_locs:
                border_color = (0, 255, 255)  
                status_bar_text = "Mengidentifikasi..."
                status_bar_color = "orange"
        
                if self.known_face_encodings:
                    face_encs = face_recognition.face_encodings(rgb_small_frame, face_locs)
                    
                    for encoding in face_encs:
                        distances = face_recognition.face_distance(self.known_face_encodings, encoding)
                        
                        if len(distances) > 0:
                            best_idx = np.argmin(distances)
                            min_dist = distances[best_idx]
                            
                            if min_dist < 0.45:
                                name = self.known_face_names[best_idx]
                                s_id = self.known_face_ids[best_idx]
                                
                                is_already_present = False
                                if s_id in self.cd:
                                    last_time = self.cd[s_id]
                                    if (datetime.now() - last_time).total_seconds() < 3600:
                                        is_already_present = True
                                
                                if is_already_present:
                                    border_color = (0, 255, 255) 
                                    status_bar_text = f"⚠️ {name} Sudah absen, silahkan absen lagi di esok hari."
                                    status_bar_color = "orange"
                    
                                else:
                                    border_color = (0, 255, 0)
                                    status_bar_text = f"✅ Selamat Datang: {name}"
                                    status_bar_color = "#2CC985"
                                    self.process_attendance(s_id, name, min_dist)

                            elif min_dist < 0.65:
                                border_color = (0, 165, 255)
                                status_bar_text = "⚠️ Wajah Kurang Jelas, Coba mendekat"
                                status_bar_color = "orange"
                                
                            else:
                                border_color = (0, 0, 255)
                                status_bar_text = "Wajah tidak dikenali"
                                status_bar_color = "red"
    
                else:
                    border_color = (0, 0, 255)
                    status_bar_text = "Database Kosong"
                    status_bar_color = "#550000"

            cv2.ellipse(final_frame, (center_x, center_y), (oval_w, oval_h), 0, 0, 360, border_color, 4)
            
            self.status_label.configure(text=status_bar_text, fg_color=status_bar_color)

            rgb_img = cv2.cvtColor(final_frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_img)
            
            gui_w = self.video_label.winfo_width()
            gui_h = self.video_label.winfo_height()
            if gui_w < 10: gui_w, gui_h = w, h
            
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(gui_w, gui_h))
            self.video_label.configure(image=ctk_img, text="")
            self.video_label.image = ctk_img

        if self.cap.isOpened():
            self.after(20, self.looping_vid)

class ToplevelEnroller(ctk.CTkToplevel): ## Object to register
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.parent.stop_camera()
        
        self.title("Registrasi Wajah Baru")
        self.geometry("450x550")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grab_set() 
        
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        ctk.CTkLabel(self.frame, text="Form Data Siswa", font=("Arial", 18, "bold")).pack(pady=15)
        
        self.inputs = {}
        fields = ["NISN", "Nama Lengkap", "Kelas", "Jurusan"]
        for field in fields:
            ctk.CTkLabel(self.frame, text=field + ":", anchor="w").pack(fill="x", padx=30, pady=(10,0))
            entry = ctk.CTkEntry(self.frame, placeholder_text=f"Masukkan {field}...")
            entry.pack(fill="x", padx=30, pady=5)
            self.inputs[field] = entry
            
        self.btn_start = ctk.CTkButton(self.frame, text="Mulai Scan Wajah", height=40, command=self.process)
        self.btn_start.pack(pady=30, padx=30, fill="x")
        
        self.lbl_status = ctk.CTkLabel(self.frame, text="", text_color="yellow")
        self.lbl_status.pack()

    def on_close(self):
        self.parent.restart_camera()
        self.destroy()

    def process(self):
        data = {k: v.get().strip() for k, v in self.inputs.items()}
        if not all(data.values()):
            self.lbl_status.configure(text="Isi semua kolomnya ya!", text_color="yellow")
            return
            
        self.lbl_status.configure(text="Membuka kamera...", text_color="white")
        self.update()
        
        success, msg = mulai_rekam_wajah(data["NISN"], data["Nama Lengkap"], data["Kelas"], data["Jurusan"])
        
        if success:
            self.lbl_status.configure(text="Berhasil Terdaftar!", text_color="green")
            messagebox.showinfo("Berhasil", msg)
            self.parent.load_encodings()
            self.on_close()
        else:
            self.lbl_status.configure(text="Gagal Terdaftar, coba lagi ya", text_color="red")
            messagebox.showerror("Gagal", msg)

if __name__ == "__main__":
    app = ATLAS()
    app.mainloop()