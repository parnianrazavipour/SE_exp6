from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DATABASE_PATH = "/app/data/data.db"
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row

with conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            value TEXT NOT NULL
        )
    """)

@app.route('/data', methods=['GET', 'POST'])
def handle_data():
    try:
        cursor = conn.cursor()
        if request.method == 'GET':
            cursor.execute("SELECT * FROM records")
            rows = cursor.fetchall()
            return jsonify([dict(row) for row in rows]), 200
        elif request.method == 'POST':
            data = request.get_json()
            cursor.execute("INSERT INTO records (name, value) VALUES (?, ?)", (data['name'], data['value']))
            conn.commit()
            return jsonify({'message': 'Record added'}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)