import requests, json
import os, sys, dotenv
dotenv.load_dotenv()

"""
CODES:
900 Licence verified
910 Licence has expired
920 Invalid licence
1000 Network error
1001 No internet
"""

SERVER = os.getenv("SERVER_IP")

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

    else: # Lisans dogrulanamadi
        return {"status_code": response.status_code}
    
def accept_licence_key(new_licence_key: str, secret_key: str):
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"licence_key": new_licence_key, "secret_key": secret_key})

    try:
        response = requests.get(SERVER+"accept_licence_key", headers=headers, data=data)
    except Exception as e:
        print(f"\n[ERROR]\n{e}\n\n")
        return {"status_code": 1000}
    
    if response.status_code == 200:  # 200 - Basarili durum kodu
        response_json = response.json()
        return response_json

    else: # Lisans dogrulanamadi, False ve durum kodu geri dondurulur
        return {"status_code": response.status_code}


def check_licence_key(licence_key: str):
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"licence_key": licence_key})

    try:
        response = requests.get(SERVER+"check_licence_key", headers=headers, data=data)
    except Exception as e:
        return {"status_code": 1000, "error": e}
    
    if response.status_code == 200:  # 200 - Basarili durum kodu
        response_json = response.json()
        return response_json
    
    else: # Lisans dogrulanamadi, False ve durum kodu geri dondurulur
        return {"status_code": response.status_code, "content": response.content.decode()[:20]}
    

if __name__ == "__main__":
    print("[LOG] Creating licence key...")
    print(f"[LOG] Response: {create_licence_key()}\n")
