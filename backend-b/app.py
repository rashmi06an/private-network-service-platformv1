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
    return jsonify(
        backend="B",
        status="ok"
    )

@app.route("/api/cache-demo", methods=["GET"])
def cache_demo():
    etag = '"backend-b-v1"'

    if request.headers.get("If-None-Match") == etag:
        response = make_response("", 304)
    else:
        response = make_response(jsonify(
            backend="B",
            message="Cache demonstration"
        ))

    response.headers["Cache-Control"] = "public, max-age=60"
    response.headers["ETag"] = etag

    return response

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=3002,
        debug=False
    )
