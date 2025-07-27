import os
import cv2
import hashlib
import face_recognition
import numpy as np
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QFileDialog, QMessageBox
)

IV = b'\x00' * 16  # Initialization vector for AES

def derive_key_from_face_encoding(encoding):
    hash_obj = hashlib.sha256()
    hash_obj.update(encoding.tobytes())
    return hash_obj.digest()

def encrypt_file(file_path, key):
    with open(file_path, 'rb') as f:
        data = f.read()
    cipher = Cipher(algorithms.AES(key), modes.CFB(IV), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data) + encryptor.finalize()
    with open(file_path + ".locked", 'wb') as f:
        f.write(encrypted_data)
    os.remove(file_path)

def decrypt_file(file_path, key):
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()
    cipher = Cipher(algorithms.AES(key), modes.CFB(IV), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    original_path = file_path.replace(".locked", "")
    with open(original_path, 'wb') as f:
        f.write(decrypted_data)
    os.remove(file_path)

def capture_face_key(return_encoding=False):
    cam = cv2.VideoCapture(0)
    while True:
        ret, frame = cam.read()
        if not ret:
            break
        cv2.imshow("Capture Face - Press 's' to Save", frame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break
    cam.release()
    cv2.destroyAllWindows()

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb)
    if not encodings:
        raise Exception("No face detected.")
    
    if return_encoding:
        return encodings[0]
    return derive_key_from_face_encoding(encodings[0])

class FileLockerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔐 Face-Based File Locker")
        self.setGeometry(200, 200, 500, 200)

        self.label = QLabel("Enter file path or click Browse:")
        self.file_input = QLineEdit()
        self.browse_button = QPushButton("📁 Browse")
        self.lock_button = QPushButton("🔒 Lock File")
        self.unlock_button = QPushButton("🔓 Unlock File")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.file_input)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.lock_button)
        layout.addWidget(self.unlock_button)
        self.setLayout(layout)

        self.browse_button.clicked.connect(self.browse_file)
        self.lock_button.clicked.connect(self.lock_file)
        self.unlock_button.clicked.connect(self.unlock_file)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            self.file_input.setText(file_path)

    def lock_file(self):
        try:
            path = self.file_input.text().strip().strip('"')
            if not os.path.exists(path):
                QMessageBox.warning(self, "❌ Error", "File not found.")
                return

            QMessageBox.information(self, "📸 Face Capture", "Press 's' to capture your face.")
            cam = cv2.VideoCapture(0)
            while True:
                ret, frame = cam.read()
                if not ret:
                    break
                cv2.imshow("Capture Face - Press 's' to Save", frame)
                if cv2.waitKey(1) & 0xFF == ord('s'):
                    break
            cam.release()
            cv2.destroyAllWindows()

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(rgb)
            if not encodings:
                raise Exception("No face detected.")

            encoding = encodings[0]
            key = derive_key_from_face_encoding(encoding)
            encrypt_file(path, key)

        # Save face encoding to .face file
            face_data_path = path + ".face"
            with open(face_data_path, 'wb') as f:
                f.write(encoding.tobytes())

            QMessageBox.information(self, "✅ Success", "File locked and face data saved.")
        except Exception as e:
            QMessageBox.warning(self, "❌ Error", str(e))


    def unlock_file(self):
        try:
            path = self.file_input.text().strip().strip('"')
            if not path.endswith(".locked") or not os.path.exists(path):
                QMessageBox.warning(self, "❌ Error", "Locked file not found or wrong extension.")
                return

        # Load stored face encoding
            face_data_path = path.replace(".locked", "") + ".face"
            if not os.path.exists(face_data_path):
                QMessageBox.warning(self, "❌ Error", "Stored face data not found.")
                return

            with open(face_data_path, 'rb') as f:
                stored_encoding = f.read()
            stored_encoding = np.frombuffer(stored_encoding, dtype=np.float64)

            QMessageBox.information(self, "📸 Face Capture", "Press 's' to verify your face.")
            cam = cv2.VideoCapture(0)
            while True:
                ret, frame = cam.read()
                if not ret:
                    break
                cv2.imshow("Verify Face - Press 's' to Proceed", frame)
                if cv2.waitKey(1) & 0xFF == ord('s'):
                    break
            cam.release()
            cv2.destroyAllWindows()

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(rgb)
            if not encodings:
                raise Exception("No face detected.")

            current_encoding = encodings[0]
            match = face_recognition.compare_faces([stored_encoding], current_encoding)[0]

            if not match:
                QMessageBox.warning(self, "❌ Error", "Face does not match. Access denied.")
                return

            key = derive_key_from_face_encoding(current_encoding)
            decrypt_file(path, key)
            os.remove(face_data_path)  # Optional: remove face file after successful unlock
            QMessageBox.information(self, "✅ Success", "File unlocked successfully.")
        except Exception as e:
            QMessageBox.warning(self, "❌ Error", str(e))

if __name__ == "__main__":
    app = QApplication([])
    window = FileLockerApp()
    window.show()
    app.exec_()
