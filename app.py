from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Configuration (In a real app, load from DB or .env)
FREE_UNAVAILABLE = False
VALID_KEYS = {"OMNEXIS-PREMIUM-1", "OMNEXIS-TEST-KEY"}
CURRENT_VERSION = "v1.0.0"

# Separate URLs for free and premium binary/assets
FREE_DOWNLOAD_URL = os.getenv("FREE_DOWNLOAD_URL", "https://github.com/edaq1/loaderget/releases/download/FREE/OMNEXIS.exe")
PREMIUM_DOWNLOAD_URL = os.getenv("PREMIUM_DOWNLOAD_URL", "https://github.com/edaq1/loaderget/releases/download/PREMIUM/omnexispremium.exe")

GLOBAL_STATUS = os.getenv("GLOBAL_STATUS", "Undetected / Online")


import json
from datetime import datetime, timedelta

def load_keys():
    keys_path = os.path.join(os.path.dirname(__file__), 'keys.json')
    if os.path.exists(keys_path):
        with open(keys_path, 'r') as f:
            return json.load(f)
    return []

def save_keys(keys_data):
    keys_path = os.path.join(os.path.dirname(__file__), 'keys.json')
    with open(keys_path, 'w') as f:
        json.dump(keys_data, f, indent=4)

@app.route('/api/access', methods=['POST'])
def handle_access():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON/Empty Request"}), 400

    tier = data.get("tier", "premium")

    if tier == "free":
        if FREE_UNAVAILABLE:
            return jsonify({"status": "free_unavailable"})
        else:
            return jsonify({
                "status": "success",
                "url": FREE_DOWNLOAD_URL,
                "version": CURRENT_VERSION
            })

    elif tier == "premium":
        key = data.get("key", "").strip()
        hwid = data.get("hwid", "").strip()

        if not key:
            return jsonify({"status": "error", "message": "No key provided."})
            
        if not hwid:
             return jsonify({"status": "error", "message": "No HWID provided."})

        keys_data = load_keys()
        target_key = next((k for k in keys_data if k["key"] == key), None)
        
        if target_key:
            now = datetime.now()
            
            # Első használat beállítása
            if target_key["first_used"] is None:
                target_key["first_used"] = now.isoformat()
                target_key["hwid"] = hwid
                save_keys(keys_data)
            
            # HWID Ellenőrzés
            if target_key["hwid"] != hwid:
                return jsonify({"status": "error", "message": "Invalid HWID. This key is bound to another device."})
                
            # Lejárat Ellenőrzés (30 nap)
            first_used = datetime.fromisoformat(target_key["first_used"])
            expires_at = first_used + timedelta(days=30)
            if now > expires_at:
                return jsonify({"status": "error", "message": "This key has expired."})
                
            return jsonify({
                "status": "success",
                "url": PREMIUM_DOWNLOAD_URL,
                "version": CURRENT_VERSION,
                "expires_at": expires_at.isoformat()
            })
        else:
            return jsonify({"status": "error", "message": "Invalid key."})
    
    return jsonify({"status": "error", "message": "Unknown tier requested."}), 400

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "online", "message": "Omnexis Backend is running."})

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({"global_status": GLOBAL_STATUS})


if __name__ == '__main__':
    # Running locally
    app.run(host='0.0.0.0', port=5000)
