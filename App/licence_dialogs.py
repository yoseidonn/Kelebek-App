from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
import os, sys, datetime
from Client import client


class LisansDialog(QDialog):
    def __init__(self, header_text: str, subheader_text: str, found_key: str, found_date: str) -> None:
        super().__init__()
        loadUi(os.path.join("Forms", "lisans_dialog.ui"), self)
        self.header_text = header_text
        self.subheader_text = subheader_text
        self.found_key = found_key
        self.found_date = found_date
        self.code = 0
        
        self.set_ui()
        self.set_signals()
        if self.found_date != "BLANK":
            year, month, day = [int(i) for i in self.found_date.split("-")]
            end_date = datetime.datetime(year, month, day)
            now = datetime.datetime.now()
            if end_date < now:
                self.header_text = "Kelebek lisans geçersiz"
                self.subheader_text = "Girdiğiniz lisansın süresi dolmuş."
                self.header.setText(self.header_text)
                self.subheader.setText(self.subheader_text)
            else:
                print("[LOG] Date is not over. Verified.")
                self.code = 1
                QTimer.singleShot(0, lambda: self.done(1))

        self.set_ws()
        
    def set_ui(self):
        self.header.setAlignment(Qt.AlignCenter)
        self.subheader.setAlignment(Qt.AlignCenter)
        self.okBtn.setIcon(QIcon(os.path.join("Images", "icon", "check.svg")))
    
    def set_signals(self):
        self.skipBtn.clicked.connect(self.skip)
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
        
        response = client.validate_licence_key(key=key)
        status_code = response["Status-Code"]
        end_date = response["End-Date"]
        print(f"[LOG] Response: {response}")

        if status_code == 900:
            print("[LICENCE] Verified.")
            self.code = 1
            self.write_key_date(key, end_date)
            QTimer.singleShot(0, lambda: self.done(1))
            return
            
        elif status_code == 901:
            print("[LICENCE] Invalid serial number.")
            self.header_text = "Çok fazla cihaz"
            self.subheader_text = "Girdiğiniz lisansı izin verdiğinden fazla cihazda kullanamazsınız."
            
        elif status_code == 910:
            print("[LICENCE] Expired.")
            self.write_key('')
            self.header_text = "Kelebek lisans geçersiz"
            self.subheader_text = "Girdiğiniz lisansın süresi dolmuş."

        elif status_code == 904:
            print("[LICENCE] Invalid.")
            self.header_text = "Kelebek lisans geçersiz"
            self.subheader_text = "Cihazınızda bulunan Kelebek lisans geçersiz."

        elif status_code == 1000:
            print(f"[VALIDATION] Network error. Status code: {status_code}")
            self.header_text = "Kelebek lisans doğrulanamadı"
            self.subheader_text = "Lütfen internet bağlantınızı kontrol edin."
            
        else:
            print(f"[ERROR] Unknown error occured. Status code: {status_code}")
            self.header_text = "Kelebek lisans doğrulanamadı"
            self.subheader_text = "Lütfen internet bağlantınızı kontrol edin."
        
        self.header.setText(self.header_text)
        self.subheader.setText(self.subheader_text)
        self.keyInput.setStyleSheet("background-color: rgba(245, 102, 66, 175);")
        self.okBtn.setStyleSheet("background-color: rgba(245, 102, 66, 175);")
        
    def set_ws(self):
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.exec_()
        
    def write_key_date(self, key: str, end_date: str):
        with open(".env", "w", encoding="utf-8") as file:
            file.write(f"LICENCE_KEY={key}\nEND_DATE={end_date}\nSERVER_IP=http://185.87.252.226")
            
    def skip(self):
        self.code = -1
        QTimer.singleShot(0, lambda: self.done(1))