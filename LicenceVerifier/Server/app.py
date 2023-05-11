from flask import Flask, request
import requests, json, psycopg2

app = Flask(__name__)

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="kelebeklisans",
    user="kelebekdev",
    password="ppmi4jGaPHD7"  
)
cur = conn.cursor()

@app.route("/create_tables")
def create_keys_table():
    cur.execute("CREATE TABLE activated_keys (KeyID int, Key varchar(255), ActivationDate varchar(255), LicenceDuration varchar(255))")
    return json.dumps({"message": "Succesfully created table"})
    
@app.route('/create_licence_key', methods=['GET'])
def create_licence_key():
    #cur.execute("CREATE TABLE activated_keys (KeyID int, Key varchar(255), ActivationDate varchar(255), LicenceDuration varchar(255))")
    new_licence_key, secret_key = "Ee9#XyRz7$Qm", "230421"
    data = {"licence_key": new_licence_key, "secret_key": secret_key}
    return json.dumps(data)

@app.route('/accept_licence_key')
def accept_licence_key():
    data = request.get_json()
    new_licence_key, secret_key = data["licence_key"], data["secret_key"]

    return json.dumps({"message": f"Key:{new_licence_key}, Secret key: {secret_key} accepted and added into database."})

@app.route('/check_licence', methods=['POST'])
def check_licence():
    data = request.get_json()

    cur.execute("INSERT INTO your_table (column1, column2) VALUES (%s, %s)", (data['column1'], data['column2']))
    conn.commit()

    return json.dumps({'message': 'Data written successfully!'})

if __name__ == '__main__':
    app.run(port=5002)