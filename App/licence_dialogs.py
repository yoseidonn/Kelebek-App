from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
import os, sys, datetime
from Client import client
from . import logs
from .logs import logger

BASE_DIR = os.getenv("BASE_DIR")

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
        
        try:
            with open(os.path.join(BASE_DIR, "kelebek.conf"), "r", encoding="utf-8") as f:
                content = f.readline()[:-1]
                key, value = content.split("=")
                logger.debug(key, value)
                if key == "CLEAR_DATE_CACHE" and value == "True":
                    self.write_key_date(key=self.found_key, end_date="", skip_date="")
                    os.remove(os.path.join(BASE_DIR, "kelebek.conf"))
                    logger.info("Clearing date cache")  
                    self.validate_key(key=self.found_key, init=True)
                    
        except Exception as e:
            logger.info(f"{str(e)} | kelebek.conf bulunamadı")
            
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
        # Empty style sheets meant to make it normal
        self.keyInput.setStyleSheet("")
        self.okBtn.setStyleSheet("")
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
        if status_code in [900, 901, 910, 904]:
            end_date = response["End-Date"]
        logger.debug(f"Response: {response}")

        if status_code == 900:
            logger.debug("Verified.")
            self.code = 1
            self.write_key_date(key, end_date, "")
            QTimer.singleShot(0, lambda: self.done(1))
            return
            
        elif status_code == 901:
            logger.debug("Invalid serial number.")
            self.header_text = "Çok fazla cihaz"
            self.subheader_text = "Girdiğiniz lisansı izin verdiğinden fazla cihazda kullanamazsınız."
            
        elif status_code == 910:
            logger.debug("Expired.")
            self.header_text = "Kelebek lisans geçersiz"
            self.subheader_text = "Girdiğiniz lisansın süresi dolmuş."

        elif status_code == 904:
            logger.debug("Invalid.")
            self.header_text = "Kelebek lisans geçersiz"
            self.subheader_text = "Cihazınızda bulunan Kelebek lisans geçersiz."

        elif status_code == 1000:
            logger.debug(f"Network error. Status code: {status_code}")
            self.header_text = "Kelebek lisans doğrulanamadı"
            self.subheader_text = "Lütfen internet bağlantınızı kontrol edin."
            
        else:
            logger.debug(f"Unknown error occured. Status code: {status_code}")
            self.header_text = "Kelebek lisans doğrulanamadı"
            self.subheader_text = "Bilinmeyen bir hata meydana geldi, lütfen daha sonra tekrar deneyiniz."
        
        self.header.setText(self.header_text)
        self.subheader.setText(self.subheader_text)
        self.keyInput.setStyleSheet("background-color: rgba(245, 102, 66, 175);")
        self.okBtn.setStyleSheet("background-color: rgba(245, 102, 66, 175);")
        
    def set_ws(self):
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.exec_()
        
    def write_key_date(self, key: str, end_date: str, skip_date: str):
        try:
            with open(".env", "w", encoding="utf-8") as file:
                file.write(f"LICENCE_KEY={key}\nEND_DATE={end_date}\nSKIP_DATE={skip_date}\nSERVER_IP=http://kelebeksistemi.com.tr/")
        except Exception as e:
            logger.error(str(e))
            
    def skip(self):
        self.code = -1
        skip_date = datetime.datetime.now().strftime("%Y-%m-%d")
        with open(".env", "w", encoding="utf-8") as file:
            file.write(f"LICENCE_KEY=\nEND_DATE=\nSKIP_DATE={skip_date}\nSERVER_IP=http://kelebeksistemi.com.tr/")
        QTimer.singleShot(0, lambda: self.done(1))