from flask import Flask, request
import requests, json, psycopg2
import random, string, datetime

CHARS = list(string.ascii_uppercase + string.digits)
random.shuffle(CHARS)

"""
CODES:
900 Licence verified
910 Licence has expired
920 Invalid licence
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
    cur.execute("CREATE TABLE IF NOT EXISTS activated_keys (KeyID INT, Key VARCHAR(255), ActivationDate VARCHAR(255), LicenceDuration VARCHAR(255))")
    cur.execute("CREATE TABLE IF NOT EXISTS registered_keys (KeyID SERIAL PRIMARY KEY, Key VARCHAR(255), LicenceDuration VARCHAR(255))")
    conn.commit()

    data = {"message": "Succesfully created tables"}
    return json.dumps(data)

@app.route("/drop_key_tables")
def drop_key_tables():
    cur.execute("DROP TABLE IF EXISTS activated_keys")
    cur.execute("DROP TABLE IF EXISTS registered_keys")
    conn.commit()

    data = {"message": "Succesfully dropped tables"}
    return json.dumps(data)

@app.route("/activate_random_key")
def activate_random_key():
    key_id = random.randint(1, 100.000)
    key = json.loads(create_licence_key())["licence_key"]
    activation_date = datetime.datetime(1,2,3).now().strftime("%Y,%m,%d,%H,%M,%S")
    licence_duration = str(random.randint(1, 10)) # Months
    
    flag = True
    while flag:
        try:
            cur.execute("INSERT INTO activated_keys (KeyID, Key, ActivationDate, LicenceDuration) VALUES (%s, %s, %s, %s)", (key_id, key, activation_date, licence_duration))
            conn.commit()
            flag = False
        except:
            pass
        
    data = {"key_id": key_id,"key": key, "activation_date": activation_date, "licence_duration": licence_duration}
    return json.dumps(data)

@app.route("/register_random_key")
def register_random_key():
    key = json.loads(create_licence_key())["licence_key"]
    licence_duration = str(random.randint(1, 10)) # Months
    
    cur.execute("INSERT INTO registered_keys (Key, LicenceDuration) VALUES (%s, %s)", (key, licence_duration))
    cur.execute("SELECT FROM registered_keys")
    conn.commit()
    
    data = {"key": key, "licence_duration": licence_duration}
    return json.dumps(data)

@app.route("/get_activated_keys")
def get_activated_keys():
    try:
        cur.execute("SELECT * FROM activated_keys")
        result = cur.fetchall()
        data = {"keys": result}
    except Exception as e:
        data = {"error": "Activated_keys table not exists"}
    
    return json.dumps(data)

@app.route("/get_registered_keys")
def get_registered_keys():
    try:
        cur.execute("SELECT * FROM registered_keys")
        result = cur.fetchall()
        data = {"keys": result}
    except Exception as e:
        data = {"error": "Registered_keys table not exists"}
    
    return json.dumps(data)
    
@app.route('/create_licence_key')
def create_licence_key():
    # TODO LETS CREATE A LOGIC THAT LOOKS FOR EVERY KEY WHICH ARE ALREADY CREATED AND CREATES A NEW AND RANDOM KEY, THEN RETURN IT
    new_licence_key = "Ee9#XyRz7$Qm"
    cur.execute("SELECT * FROM activated_keys")
    keys = [key[1] for key in cur.fetchall()]
    
    new_key = "".join(random.choices(CHARS, k=19))
    while new_key in keys:
        new_key = "".join(random.choices(CHARS, k=19))
    
    new_key = list(new_key)
    new_key[4], new_key[9], new_key[14] = "-", "-", "-"
    new_key = "".join(new_key)

    data = {"licence_key": new_key}
    return json.dumps(data)

#######################################################

@app.route('/check_licence_key')
def check_licence():
    data = request.get_json()
    # TODO LETS CREATE A LOGIC THAT TAKES Key FROM Data AND COMPARE WITH THE DATA IN ACTIVATED KEYS
    key = data["key"]

    cur.execute("SELECT * FROM activated_keys WHERE Key = %s", (key,))
    activated_keys = cur.fetchall()

    if activated_keys:
        activation_date = key[2]
        licence_duration = int(key[3])

        year, month, day, hour, minute, second = [int(i) for i in activation_date.split(",")]
        new_year = (month + licence_duration) // 12
        new_month = (month + licence_duration) % 12
        new_day, new_hour, new_minute, new_second = [int(i) for i in datetime.datetime(1,2,3).now().strftime("%d,%H,%M,%S").split(",")]
        
        end_date = datetime.datetime(new_year, new_month, new_day, new_hour, new_minute, new_second)
        now = datetime.datetime().now()
        if now > end_date:
            registered_keys = cur.fetchall()
            # TODO ....
            
    return json.dumps({'message': 900})

#######################################################

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
    
