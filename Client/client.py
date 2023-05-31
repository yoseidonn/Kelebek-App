import requests, json
import os, sys, dotenv
dotenv.load_dotenv()

"""
CODES:
123 Not implemented

700 Succesfully created tables
701 Error occured while creating tables
702 Table not found

800 Key successfully registed
801 Error occured while registering key

900 Licence verified
910 Licence has expired
920 Invalid licence

1000 Network error
1001 No internet
"""

#SERVER = os.getenv("SERVER_IP")
SERVER = "http://localhost:5000/"

# Development functions
def create_key_tables():
    headers = {"Content-Type": "application/json"}

    response = requests.get(SERVER+"create_key_tables", headers=headers)
    if response.status_code == 200:  # 200 - Basarili durum kodu
        response_json = response.json()
        return response_json

    else: # Ağ hatası, Durum kodu geri dondurulur
        return {"Status-Code": response.status_code}

def drop_key_tables():
    headers = {"Content-Type": "application/json"}
    
    response = requests.get(SERVER+"drop_key_tables", headers=headers)
    if response.status_code == 200:  # 200 - Basarili durum kodu
        response_json = response.json()
        return response_json

    else: # Ağ hatası, Durum kodu geri dondurulur
        return {"Status-Code": response.status_code}

def get_activated_keys():
    headers = {"Content-Type": "application/json"}
    
    response = requests.get(SERVER+"get_activated_keys", headers=headers)
    if response.status_code == 200:  # 200 - Basarili durum kodu
        response_json = response.json()
        return response_json

    else: # Ağ hatası, Durum kodu geri dondurulur
        return {"Status-Code": response.status_code}

def get_registered_keys():
    headers = {"Content-Type": "application/json"}
    
    response = requests.get(SERVER+"get_registered_keys", headers=headers)
    if response.status_code == 200:  # 200 - Basarili durum kodu
        response_json = response.json()
        return response_json

    else: # Ağ hatası, Durum kodu geri dondurulur
        return json.dumps({"Status-Code": response.status_code})
    
#######################################################################

def activate_licence_key(key: str):
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"Key": key})
    
    response = requests.get(SERVER+"activate_licence_key", headers=headers, data=data)
    if response.status_code == 200:  # 200 - Basarili durum kodu
        response_json = response.json()
        return response_json

    else: # Ağ hatası, Durum kodu geri dondurulur
        return json.dumps({"Status-Code": response.status_code})

def register_new_licence_key_and_get(licence_duration: str) -> str:
    """
    Key seller api will use this to create a new key and send it to customer
    """
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"Licence-Duration": licence_duration})
    
    response = requests.get(SERVER+"register_new_licence_key_and_get", headers=headers, data=data)
    if response.status_code == 200:  # 200 - Basarili durum kodu
        response_json = response.json()
        return response_json

    else: # Ağ hatası, Durum kodu geri dondurulur
        return json.dumps({"Status-Code": response.status_code})

def validate_licence_key(licence_key: str):
    """
    Desktop application will use this to validate user's licence key
    """
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"Key": licence_key})

    try:
        response = requests.get(SERVER+"validate_licence_key", headers=headers, data=data)
    except Exception as e:
        return {"Status-Code": 1000, "error": e}
    
    if response.status_code == 200:  # 200 - Basarili durum kodu
        response_json = response.json()
        return response_json
    
    else: #  Ağ hatası, Durum kodu geri dondurulur
        return json.dumps({"Status-Code": response.status_code})
    

if __name__ == "__main__":
    text = """Bir işlem seçin:
    a - Tabloları oluştur
    b - Tabloları sil
    c - Aktif   anahtarları getir
    d - Kayıtlı anahtarları getir
    
    1 - Anahtar kayıtla ve al
    2 - Anahtar aktifleştir
    3 - Anahtar doğrula
    
    q - Çıkış
    -> """
    while True:
        islem = input(text)
        print()

        if islem == "q":
            break
        
        elif islem == "a":
            response = create_key_tables()
            print(f"[LOG] {response}\n")

        elif islem == "b":
            response = drop_key_tables()
            print(f"[LOG] {response}\n")
        
        elif islem == "c":
            response = get_activated_keys()
            print(f"[LOG] {response}\n")
        
        elif islem == "d":
            response = get_registered_keys()
            print(f"[LOG] {response}\n")
        
        #######################################
        
        elif islem == "1":
            licence_duration = input("Enter the duration for your key (months): ")
            response = register_new_licence_key_and_get(licence_duration)
            print(f"[LOG] {response}\n")
        
        elif islem == "2":
            key = input("Enter the key you want to activate: ")
            response = activate_licence_key(key)
            print(f"[LOG] {response}\n")

        elif islem == "3":
            print(f"[LOG] {response}\n")
            key = input("Enter the key you want to validate: ")
            response = validate_licence_key(key)
            print(f"[LOG] {response}\n")
            
        else:
            print("Invalid operation...")
            
    print("[LOG] Çıkış yapılıyor.")