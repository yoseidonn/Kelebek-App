import requests, json, threading
import os, sys

SERVER = "http://185.87.252.226:5002/"

def create_tables():
    headers = {"Content-Type": "application/json"}

    response = requests.get(SERVER+"create_tables", headers=headers)
    if response.status_code == 200:  # 200 - Basarili durum kodu
        response_json = response.json()
        return response_json

    else: # Lisans dogrulanamadi, False ve durum kodu geri dondurulur
        return False, response.status_code

def create_licence_key() -> str:
    headers = {"Content-Type": "application/json"}
    
    response = requests.get(SERVER+"create_licence_key", headers=headers)
    if response.status_code == 200:  # 200 - Basarili durum kodu
        response_json = response.json()
        new_licence_key, secret_key = response_json["licence_key"], response_json["secret_key"]
        isAccepted = accept_licence_key(new_licence_key, secret_key)
        print(f"Is Accepted: {isAccepted}")
        return response_json

    else: # Lisans dogrulanamadi, False ve durum kodu geri dondurulur
        return False, response.status_code
    
def accept_licence_key(new_licence_key: str, secret_key: str):
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"licence_key": new_licence_key, "secret_key": secret_key})

    response = requests.get(SERVER+"accept_licence_key", headers=headers, data=data)
    if response.status_code == 200:  # 200 - Basarili durum kodu
        response_json = response.json()
        return response_json

    else: # Lisans dogrulanamadi, False ve durum kodu geri dondurulur
        return False, response.status_code


def check_licence(licence_key: str):
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"licence_key": licence_key})

    response = requests.post(SERVER+"check_licence", headers=headers, data=data)
    if response.status_code == 200:  # 200 - Basarili durum kodu
        response_json = response.json()
        return response_json
    
    else: # Lisans dogrulanamadi, False ve durum kodu geri dondurulur
        return False, response.status_code

if __name__ == "__main__":
    print(create_licence_key())
