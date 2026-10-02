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
    return jsonify(
        backend="A",
        status="ok"
    )

@app.route("/api/cache-demo", methods=["GET"])
def cache_demo():
    etag = '"backend-a-v1"'

    if request.headers.get("If-None-Match") == etag:
        response = make_response("", 304)
    else:
        response = make_response(jsonify(
            backend="A",
            message="Cache demonstration"
        ))

    response.headers["Cache-Control"] = "public, max-age=60"
    response.headers["ETag"] = etag

    return response

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=3001,
        debug=False
    )
