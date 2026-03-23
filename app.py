from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Configuration (In a real app, load from DB or .env)
FREE_UNAVAILABLE = True
VALID_KEYS = {"OMNEXIS-PREMIUM-1", "OMNEXIS-TEST-KEY"}
CURRENT_VERSION = "v1.0.0"

# Separate URLs for free and premium binary/assets
FREE_DOWNLOAD_URL = os.getenv("FREE_DOWNLOAD_URL", "https://github.com/edaq1/loaderget/releases/download/free/omnexisfree.exe")
PREMIUM_DOWNLOAD_URL = os.getenv("PREMIUM_DOWNLOAD_URL", "https://github.com/edaq1/loaderget/releases/download/PREMIUM/omnexispremium.exe")


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

        if key in VALID_KEYS:
            # Here you would also check HWID in a real DB
            return jsonify({
                "status": "success",
                "url": PREMIUM_DOWNLOAD_URL,
                "version": CURRENT_VERSION
            })
        else:
            return jsonify({"status": "error", "message": "Invalid key."})
    
    return jsonify({"status": "error", "message": "Unknown tier requested."}), 400

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "online", "message": "Omnexis Backend is running."})


if __name__ == '__main__':
    # Running locally
    app.run(host='0.0.0.0', port=5000)
