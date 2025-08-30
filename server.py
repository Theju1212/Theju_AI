# server.py
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

# Load .env in local dev (will silently do nothing in production if .env missing)
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    # In dev you may allow running without key, but warn the developer
    print("WARNING: GROQ_API_KEY not found in environment. /chat will fail until set.")

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)  # In production restrict origins: CORS(app, origins=["https://your-site.com"])

# Create client only when API_KEY is available
client = Groq(api_key=API_KEY) if API_KEY else None

@app.route("/chat", methods=["POST"])
def chat():
    if not client:
        return jsonify({"reply": "Server not configured with an API key."}), 500

    data = request.get_json() or {}
    message = data.get("message", "")

    resp = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": message}],
        temperature=0.6,
        max_tokens=256
    )
    reply = resp.choices[0].message.content
    return jsonify({"reply": reply})

@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")

@app.route("/<path:path>")
def serve_file(path):
    return send_from_directory(".", path)

if __name__ == "__main__":
    # Use PORT if the host provides one (Render, Railway, etc. set $PORT)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
