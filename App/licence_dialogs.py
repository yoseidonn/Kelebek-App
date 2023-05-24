from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
import os, Client.client as client


class LisansDialog(QDialog):
    def __init__(self, h1: str, h2: str) -> None:
        super().__init__()
        loadUi(os.path.join("Forms", "lisans_dialog.ui"), self)
        self.header_text = h1
        self.subheader_text = h2
        self.passed = False
        
        self.set_ui()
        self.set_signals()
        self.set_ws()

    def set_ui(self):
        self.header.setText(self.header_text)
        self.subheader.setText(self.subheader_text)
        self.header.setAlignment(Qt.AlignCenter)
        self.subheader.setAlignment(Qt.AlignCenter)
        self.okBtn.setIcon(QIcon(os.path.join("Images", "icon", "check.svg")))
    
    def set_signals(self):
        self.closeWindowBtn.clicked.connect(self.close)
        self.okBtn.clicked.connect(self.confirm)
        self.keyInput.textEdited.connect(self.text_changed)

    def text_changed(self):
        self.keyInput.setStyleSheet("background-color: white;")
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
        
    def check_key(self):
        key = self.keyInput.text()
        if len(key) != 19:
            return False
        return True
        
    def confirm(self):
        # TODO CONFIRM IF ITS VALID VIA DATABASE
        if not self.check_key():
            self.keyInput.setStyleSheet("background-color: rgba(245, 102, 66, 175);")
            return 
        
        key = self.keyInput.text()
        response = client.check_licence_key(key)
        status_code = response['status_code']
        #print(f"[VALIDATION] Status code: {status_code}")
        
        flag = True
        if status_code == 900:
            print("[VERIFIED] Licence key is confirmed. Application is starting.")
            flag = False

        elif status_code == 1000:
            error = response['error']
            print(f"[NETWORK ERROR] Network error. Exit code: {1000}, Error: {error}\n")
            exit()
            
        elif status_code == 910:
            print("[EXPIRED] Licence key is expired.")
            
        elif status_code == 920:
            print("[INVALID] Invalid key.")

        else:
            print(f"[ERROR] Unknown error occured. Status code: {status_code}")

        if flag:
            self.keyInput.setStyleSheet("background-color: rgba(245, 102, 66, 175);")
        else:
            self.confirmed()

    def confirmed(self):
        key = self.keyInput.text()
        self.key = key
        with open(".env", "w", encoding="utf-8") as file:
            file.write(f"LICENCE_KEY={key}\nSERVER_IP=http://185.87.252.226/")
        self.passed = True
        self.close()
        
    def set_ws(self):
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.exec()