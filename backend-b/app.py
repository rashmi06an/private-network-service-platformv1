from flask import Flask, jsonify

app = Flask(__name__)


@app.after_request
def add_backend_header(response):
    response.headers["X-Backend"] = "B"
    return response


@app.route("/", methods=["GET"])
def home():
    return jsonify(
        message="Backend B is running",
        backend="B"
    )


@app.route("/api/status", methods=["GET"])
def status():
    return jsonify(
        backend="B",
        status="ok"
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=3002,
        debug=False
    )
