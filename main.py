# By Ronak aka L

import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import os
import sys

if sys.stdout is not None:
    sys.stdout.reconfigure(encoding='utf-8')


CODES_FILE = "codes.txt"

class ModernQRScanner:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("QR Cam")
        self.window.geometry("800x600")
        self.window.configure(bg="#1e1e2f")

        self.cap = None
        self.running = False
        self.paused = False
        self.detector = cv2.QRCodeDetector()
        self.allowed_codes = self.load_allowed_codes()

        self.create_ui()

    def create_ui(self):
        title = tk.Label(
            self.window,
            text="📷 Modern QR Code Scanner",
            font=("Segoe UI", 20, "bold"),
            bg="#1e1e2f",
            fg="#00ffcc"
        )
        title.pack(pady=20)


        button_frame = tk.Frame(self.window, bg="#1e1e2f")
        button_frame.pack(pady=20)

        style = ttk.Style()
        style.configure("TButton",
                        font=("Segoe UI", 12, "bold"),
                        padding=10,
                        relief="flat",
                        background="#00ffcc",
                        foreground="#000")
        style.map("TButton", background=[("active", "#00ffaa")])

        ttk.Button(button_frame, text="Start Camera", command=self.start_camera).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Pause", command=self.pause_camera).grid(row=0, column=1, padx=10)
        ttk.Button(button_frame, text="Resume", command=self.resume_camera).grid(row=0, column=2, padx=10)
        ttk.Button(button_frame, text="Reload Codes", command=self.reload_codes).grid(row=0, column=3, padx=10)
        ttk.Button(button_frame, text="Exit", command=self.close_app).grid(row=0, column=4, padx=10)

        self.status_label = tk.Label(
            self.window,
            text="Status: Ready to scan",
            font=("Segoe UI", 12),
            bg="#1e1e2f",
            fg="#ffffff"
        )
        self.status_label.pack(pady=10)

        self.video_label = tk.Label(self.window, bg="#2e2e3f")
        self.video_label.pack(pady=20)

    def load_allowed_codes(self):
        if not os.path.exists(CODES_FILE):
            messagebox.showerror(
                "Missing File!",
                "⚠️ 'codes.txt' not found!\n\nPlease place it in the same folder as the application."
            )
            return []
        try:
            with open(CODES_FILE, "r", encoding="utf-8") as f:
                codes = [code.strip() for code in f.read().split(",") if code.strip()]
                print(f"Loaded {len(codes)} allowed codes successfully.")
                return codes
        except Exception as e:
            messagebox.showerror("File Error", f"Error reading codes.txt:\n{str(e)}")
            return []

    def reload_codes(self):
        self.allowed_codes = self.load_allowed_codes()
        messagebox.showinfo("Reloaded", f"Reloaded {len(self.allowed_codes)} codes.")
        print("✅ Codes reloaded successfully.")

    def start_camera(self):
        if self.running:
            messagebox.showinfo("Already Running", "Camera is already running.")
            return

        self.running = True
        self.paused = False
        self.status_label.config(text="Status: Scanning...")
        self.cap = cv2.VideoCapture(0)
        threading.Thread(target=self.scan_qr, daemon=True).start()

    def pause_camera(self):
        if not self.running:
            return
        self.paused = True
        self.status_label.config(text="Status: Paused")

    def resume_camera(self):
        if not self.running:
            return
        self.paused = False
        self.status_label.config(text="Status: Resumed")

    def scan_qr(self):
        while self.running:
            if self.paused:
                continue

            ret, frame = self.cap.read()
            if not ret:
                break

            data, bbox, _ = self.detector.detectAndDecode(frame)

            if bbox is not None:
                pts = bbox.astype(int).reshape(-1, 2)
                for i in range(len(pts)):
                    cv2.line(frame, tuple(pts[i]), tuple(pts[(i + 1) % len(pts)]), (0, 255, 255), 2)

                if data:
                    if data in self.allowed_codes:
                        color = (0, 255, 0)
                        text = "Access Granted!"
                    else:
                        color = (0, 0, 255)
                        text = "Access Denied!"

                    cv2.putText(frame, text, (pts[0][0], pts[0][1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                    self.status_label.config(text=f"QR: {data} → {text}")

            self.show_frame(frame)

        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

    def show_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = cv2.resize(frame, (640, 480))
        image = Image.fromarray(img)
        photo = ImageTk.PhotoImage(image=image)
        self.video_label.config(image=photo)
        self.video_label.image = photo

    def close_app(self):
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.window.destroy()

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = ModernQRScanner()
    app.run()
