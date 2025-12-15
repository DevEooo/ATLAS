import cv2
import numpy as np

def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280) # Width
    cap.set(4, 720)  # Height

    print("[INFO] ATLAS System Starting...")
    print("[INFO] Tekan 'q' untuk keluar.")

    while True:
        success, frame = cap.read()
        if not success:
            print("Gagal membaca frame kamera")
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        mask = np.zeros((h, w, 3), dtype='uint8')
        
        center_x, center_y = w // 2, h // 2
        
        axes = (140, 200) 
        
        cv2.ellipse(mask, (center_x, center_y), axes, 0, 0, 360, (255, 255, 255), -1)

        blurred_frame = cv2.GaussianBlur(frame, (21, 21), 0) # Efek blur opsional
        dimmed_bg = cv2.addWeighted(blurred_frame, 0.6, np.zeros(frame.shape, frame.dtype), 0, 0)
        
        mask_gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        _, mask_binary = cv2.threshold(mask_gray, 10, 255, cv2.THRESH_BINARY)
        
        face_area = cv2.bitwise_and(frame, frame, mask=mask_binary)
        
        mask_inv = cv2.bitwise_not(mask_binary)
        bg_area = cv2.bitwise_and(dimmed_bg, dimmed_bg, mask=mask_inv)
        
        final_frame = cv2.add(face_area, bg_area)

        cv2.ellipse(final_frame, (center_x, center_y), axes, 0, 0, 360, (255, 255, 0), 2)

        cv2.putText(final_frame, "ATLAS SYSTEM: READY", (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(final_frame, "Posisikan wajah di dalam area", (center_x - 130, center_y + 240), 
                    cv2.FONT_HERSHEY_PLAIN, 1.2, (200, 200, 200), 1)

        cv2.imshow("ATLAS - Attendance System", final_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()