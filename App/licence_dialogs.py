from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
import os, sys, time
from Client import client


class LisansDialog(QDialog):
    def __init__(self, header_text: str, subheader_text: str, found_key: str) -> None:
        super().__init__()
        loadUi(os.path.join("Forms", "lisans_dialog.ui"), self)
        self.header_text = header_text
        self.subheader_text = subheader_text
        self.found_key = found_key
        
        self.set_ui()
        self.set_signals()
        self.set_ws()
        self.validate_key(self.found_key, init=True)
        
    def set_ui(self):
        self.header.setText(self.header_text)
        self.subheader.setText(self.subheader_text)
        self.header.setAlignment(Qt.AlignCenter)
        self.subheader.setAlignment(Qt.AlignCenter)
        self.okBtn.setIcon(QIcon(os.path.join("Images", "icon", "check.svg")))
    
    def set_signals(self):
        self.closeWindowBtn.clicked.connect(self.close)
        self.okBtn.clicked.connect(lambda: self.validate_key(self.keyInput.text()))
        self.keyInput.textEdited.connect(self.text_changed)

    def text_changed(self):
        self.keyInput.setStyleSheet("background-color: white;")
        self.okBtn.setStyleSheet("background-color: white;")
        key = self.keyInput.text()

        if not key:
            return
        
        lastChar: str = key[-1]
        lastChar = lastChar.upper()

        # Eğer boşluk konduysa sil. Eğer dörtlüden sonra gelen bir karakter ise - olmak zorunda.
        if len(key) != 1 and (len(key) == 5 or len(key) == 10 or len(key) == 15):
            if lastChar != "-":
                self.keyInput.setText(key[0:-1])
            return
        
        if not lastChar.isalnum() or lastChar == " ":
            self.keyInput.setText(key[0:-1])
        
    def validate_key(self, key: str, init = False):
        if not init and len(key) != 19:
            self.keyInput.setStyleSheet("background-color: rgba(245, 102, 66, 175);")
            self.okBtn.setStyleSheet("background-color: rgba(245, 102, 66, 175);")
            return

        response = client.validate_licence_key(key)
        status_code = response["Status-Code"]
        print(f"[LOG] Response: {response}")

        if status_code == 900:
            print("[VERIFIED] Licence key is valid.")
            self.write_key(key)
            QTimer.singleShot(0, lambda: self.done(1))
            return
            
        elif status_code == 901:
            print("[VERIFIED] Licence key is valid and activated.")
            self.write_key(key)
            QTimer.singleShot(0, lambda: self.done(1))
            return
            
        elif status_code == 910:
            print("[EXPIRED] Licence key is expired.")
            
        elif status_code == 920:
            print("[INVALID] Invalid key.")
            self.header_text = "Kelebek lisans geçersiz"
            self.subheader_text = "Cihazınızda bulunan Kelebek lisansı doğrulayamıyoruz."

        elif status_code == 1000:
            print(f"[VALIDATION] Network error. Status code: {status_code}")
            self.header_text = "Kelebek lisans doğrulanamadı"
            self.subheader_text = "Lütfen internet bağlantınızı kontrol edin."
            
        else:
            print(f"[ERROR] Unknown error occured. Status code: {status_code}")
            self.header_text = "Kelebek lisans doğrulanamadı"
            self.subheader_text = "Lütfen internet bağlantınızı kontrol edin."
        
        self.keyInput.setStyleSheet("background-color: rgba(245, 102, 66, 175);")
        self.okBtn.setStyleSheet("background-color: rgba(245, 102, 66, 175);")
        
    def set_ws(self):
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.show()
        
    def write_key(self, key: str):
        with open(".env", "w", encoding="utf-8") as file:
            file.write(f"LICENCE_KEY={key}\nSERVER_IP=http://185.87.252.226")