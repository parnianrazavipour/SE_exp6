from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

db_config = {
    "host": "db",
    "user": "root",
    "password": "password",
    "database": "microservices"
}


@app.route('/data', methods=['GET', 'POST'])
def handle_data():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    if request.method == 'GET':
        cursor.execute("SELECT * FROM records")
        rows = cursor.fetchall()
        conn.close()
        return jsonify(rows)
    elif request.method == 'POST':
        data = request.get_json()
        cursor.execute("INSERT INTO records (name, value) VALUES (%s, %s)", (data['name'], data['value']))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Record added'}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)