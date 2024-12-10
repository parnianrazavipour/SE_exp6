from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# List of backend services (adjust ports in docker-compose.yml)
BACKEND_SERVICES = [
    "http://backend1:5001",
    "http://backend2:5002",
    "http://backend3:5003"
]

@app.route('/api/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def route_request(endpoint):
    backend_url = BACKEND_SERVICES[hash(endpoint) % len(BACKEND_SERVICES)]
    response = requests.request(
        method=request.method,
        url=f"{backend_url}/{endpoint}",
        json=request.get_json()
    )
    return (response.text, response.status_code)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
