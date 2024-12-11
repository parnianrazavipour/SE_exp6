from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

backend_url = "http://nginx"

@app.route('/api/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def route_request(endpoint):
    try:
        response = requests.request(
            method=request.method,
            url=f"{backend_url}/{endpoint}",
            json=request.get_json() if request.method in ['POST', 'PUT'] else None,
            headers=request.headers
        )
        return (response.text, response.status_code)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)