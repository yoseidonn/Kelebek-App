from flask import Flask, request
import requests, json, psycopg2
import random, string, datetime

CHARS = list(string.ascii_uppercase + string.digits)
random.shuffle(CHARS)

"""
CODES:
123 Not implemented

700 Succesfully created tables
701 Database error
702 Table not found

800 Key successfully registed
801 Error occured while registering key

900 Licence verified
910 Licence has expired
920 Invalid licence

1000 Network error
1001 No internet
"""

app = Flask(__name__)
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="postgres",
    user="postgres",
    password="123456"
)
cur = conn.cursor()

#######################################################

@app.route("/create_key_tables")
def create_key_tables():
    try:
        cur.execute("CREATE TABLE IF NOT EXISTS activated_keys (KeyID INT, Key VARCHAR(255), ActivationDate VARCHAR(255), LicenceDuration VARCHAR(255))")
        cur.execute("CREATE TABLE IF NOT EXISTS registered_keys (KeyID SERIAL PRIMARY KEY, Key VARCHAR(255), LicenceDuration VARCHAR(255))")
        conn.commit()
        data = {"Status-Code": 700}
        
    except Exception as e:
        conn.rollback()
        data = {"Status-Code": 701, "Error-Message": str(e)}
    
    print(f"\n[LOG] Data = {data}\n")
    return json.dumps(data)

@app.route("/drop_key_tables")
def drop_key_tables():
    try:
        cur.execute("DROP TABLE IF EXISTS activated_keys")
        cur.execute("DROP TABLE IF EXISTS registered_keys")
        conn.commit()
        data = {"Status-Code": 700}
        
    except Exception as e:
        conn.rollback()
        data = {"Status-Code": 701, "Error-Message": str(e)}
   
    print(f"\n[LOG] Data = {data}\n")
    return json.dumps(data)

@app.route("/get_activated_keys")
def get_activated_keys():
    try:
        cur.execute("SELECT * FROM activated_keys")
        result = cur.fetchall()
        data = {"Keys": result, "Status-Code": 700}
        
    except Exception as e:
        conn.rollback()
        data = {"Status-Code": 702, 'Error-Message': str(e)}
    
    print(f"\n[LOG] Data = {data}\n")
    return json.dumps(data)

@app.route("/get_registered_keys")
def get_registered_keys():
    try:
        cur.execute("SELECT * FROM registered_keys")
        result = cur.fetchall()
        data = {"Keys": result, "Status-Code": 700}
        
    except Exception as e:
        conn.rollback()
        data = {"Status-Code": 702, "Error-Message": str(e)}
    
    print(f"\n[LOG] Data = {data}\n")
    return json.dumps(data)
    
#######################################################

@app.route("/register_new_licence_key_and_get")
def register_new_licence_key_and_get():
    try:
        data = request.get_json()
        licence_duration = data["Licence-Duration"]
        
        cur.execute("SELECT * FROM activated_keys")
        keys = [key[1] for key in cur.fetchall()]
        
        new_key = "".join(random.choices(CHARS, k=19))
        while new_key in keys:
            new_key = "".join(random.choices(CHARS, k=19))
        
        new_key = list(new_key)
        new_key[4], new_key[9], new_key[14] = "-", "-", "-"
        new_key = "".join(new_key)

        cur.execute("INSERT INTO registered_keys (Key, LicenceDuration) VALUES (%s, %s)", (new_key, licence_duration))
        conn.commit()
        
        send_data = {"Key": new_key, "Licence-Duration": licence_duration, "Status-Code": 800}
        
    except Exception as e:
        print(f"[LOG] Error occured: {e}\n")
        conn.rollback()
        send_data = {"Status-Code": 801}

    return json.dumps(send_data)

@app.route("/activate_licence_key")
def activate_licence_key():
    return json.dumps({"Status-Code": 123})

@app.route('/validate_licence_key')
def validate_licence():
    # TODO LETS CREATE A LOGIC THAT TAKES Key FROM Data AND COMPARE WITH THE DATA IN ACTIVATED KEYS
    try:
        data = request.get_json()
        key = data["Key"]

        cur.execute("SELECT * FROM activated_keys WHERE Key = %s", (key,))
        activated_keys = cur.fetchall()
        
        if activated_keys:
            # Aktif edilmiş anahtar
            activation_date = key[2]
            licence_duration = int(key[3])

            year, month, day, hour, minute, second = [int(i) for i in activation_date.split(",")]
            new_year = (month + licence_duration) // 12
            new_month = (month + licence_duration) % 12
            new_day, new_hour, new_minute, new_second = [int(i) for i in datetime.datetime(1,2,3).now().strftime("%d,%H,%M,%S").split(",")]
            
            end_date = datetime.datetime(new_year, new_month, new_day, new_hour, new_minute, new_second)
            now = datetime.datetime().now()
            
            if now > end_date:
                # Tarihi geçmiş
                send_data = {"Status-Code": 910}
                
            else:
                # Tarihi geçmemiş
                send_data = {"Status-Code": 900}
            
        else:
    
            cur.execute("SELECT * FROM registered_keys")
            registered_keys = cur.fetchall()
            
            if key not in registered_keys:
                # Anahtar kayıtlı değil
                send_data = {"Status-Code": 920}
            else:
                # Kayıtlı anahtarı aktif et
                activation_date = datetime.datetime().now().strftime("%Y,%m,%d,%H,%M,%S")
                cur.execute("SELECT KeyID, LicenceDuration FROM registered_keys WHERE Key = %s", (key,))
                keyID, licence_duration = cur.fetchone()
                print(f"[LOG] Licence duration type: {type(licence_duration)}")
                    
                cur.execute("DELETE FROM registered_keys WHERE 'Key' = %s", (key,))
                cur.execute("INSER INTO activated_keys (Key) VALUES (%s %s %s)")
                    
                send_data = {'Status-Code': 901}
        
                
    except Exception as e:
        conn.rollback()
        send_data = {'Status-Code': 701, "Error-Message": str(e)}
        return json.dumps(send_data)
        
    return json.dumps(send_data)


#######################################################

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
    
