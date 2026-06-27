from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# 存放清單項目的檔案
DATA_FILE = "gui_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"items": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    data = load_data()
    return render_template("index.html", items=data["items"])

@app.route("/api/add", methods=["POST"])
def add_item():
    text = request.json.get("text", "").strip()
    if text:
        data = load_data()
        data["items"].append(text)
        save_data(data)
        return jsonify({"success": True, "items": data["items"]})
    return jsonify({"success": False, "message": "請輸入文字"})

@app.route("/api/clear", methods=["POST"])
def clear_items():
    save_data({"items": []})
    return jsonify({"success": True, "items": []})

@app.route("/api/items", methods=["GET"])
def get_items():
    data = load_data()
    return jsonify({"items": data["items"]})

if __name__ == "__main__":
    print("啟動伺服器: http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
