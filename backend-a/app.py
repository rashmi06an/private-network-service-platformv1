from flask import Flask, jsonify, make_response, request

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
    response = jsonify(
        backend="A",
        status="ok"
    )
    response.headers["Cache-Control"] = "no-store"
    return response

@app.route("/api/cache-demo", methods=["GET"])
def cache_demo():
    # The representation is identical on A/B, so validation survives load balancing.
    # Backend identity remains observable in X-Backend, not in the cached body.
    response = make_response(jsonify(message="Cache demonstration", version=2))
    response.headers["Cache-Control"] = "public, max-age=60"
    response.set_etag("team1-cache-v2")
    response.make_conditional(request)
    return response

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=3001,
        debug=False
    )
