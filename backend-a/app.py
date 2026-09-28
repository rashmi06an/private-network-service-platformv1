from flask import Flask, jsonify, make_response

app = Flask(__name__)


@app.after_request
def add_backend_header(response):
    response.headers["X-Backend"] = "A"
    return response


@app.route("/", methods=["GET"])
def home():
    return jsonify(
        message="Backend A is running",
        backend="A"
    )


@app.route("/api/status", methods=["GET"])
def status():
    return jsonify(
        backend="A",
        status="ok"
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=3001,
        debug=False
    )
