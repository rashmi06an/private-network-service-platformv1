from flask import Flask, jsonify, make_response, request

app = Flask(__name__)


@app.after_request
def add_backend_header(response):
    response.headers["X-Backend"] = "B"
    return response


@app.route("/", methods=["GET"])
def home():
    return jsonify(
        backend="B",
        message="Backend B is running"
    )


@app.route("/api/status", methods=["GET"])
def status():
    response = jsonify(
        backend="B",
        status="ok"
    )
    response.headers["Cache-Control"] = "no-store"
    return response

@app.route("/api/cache-demo", methods=["GET"])
def cache_demo():
    # Same representation and validator as A; the next request may reach either.
    response = make_response(jsonify(message="Cache demonstration", version=2))
    response.headers["Cache-Control"] = "public, max-age=60"
    response.set_etag("team1-cache-v2")
    response.make_conditional(request)
    # Werkzeug serving supplies the wire Date header; avoid a duplicate Date.
    response.headers.pop("Date", None)
    return response

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=3002,
        debug=False
    )
