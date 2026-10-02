# Backend A — Mac 3

Backend A is one of the two application servers used in the **Private Network Service Platform** project.

It runs on **Mac 3** and serves HTTP requests on **TCP port 3001**. It is designed to receive requests through the nginx reverse proxy and load balancer running on Mac 2.

## Student Details

- **Name:** Shubhaang Kataruka
- **Enrollment Number:** 2401010450
- **Role:** Mac 3 — Backend Server A
- **Backend Identifier:** A
- **Port:** 3001

## Network Role

The Phase 1 request flow is:

Client → Private DNS → Mac 2 (nginx) → Backend A / Backend B

Backend A runs on Mac 3:

Mac 2 (nginx) → Mac 3 (Backend A :3001)

The application listens on `0.0.0.0` so that it can be accessed by other machines connected to the same private LAN.

## Technology

- Python 3
- Flask
- HTTP/REST
- TCP Port 3001

## API Endpoints

### GET /

Confirms that Backend A is running.

Example response:

```json
{
  "backend": "A",
  "message": "Backend A is running"
}
```

### GET /api/status

Returns HTTP 200 with `{"backend":"A","status":"ok"}`.
All responses include `X-Backend: A`.

### GET /api/cache-demo

Returns HTTP 200 with Backend A's cache demonstration JSON,
`Cache-Control: public, max-age=60`, and `ETag: "backend-a-v1"`.
A request with `If-None-Match: "backend-a-v1"` returns HTTP 304
Not Modified with an empty body and the same cache headers.

## Setup and run on Mac 3

From the repository root:

```sh
cd backend-a
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

The server listens on `0.0.0.0:3001` with debug mode disabled.
Keep this terminal open; stop the server with Ctrl+C.
The virtual environment and Python caches are ignored by Git.
Do not commit credentials, certificates, or private keys.

## Local and LAN testing

In a second terminal:

```sh
curl -i http://127.0.0.1:3001/
curl -i http://127.0.0.1:3001/api/status
```

Expect HTTP 200, Backend A JSON, and `X-Backend: A`.
Find Mac 3's current LAN IP in macOS Network settings. From another
machine on the same LAN (including Mac 2), replace `MAC3_IP` below:

```sh
curl -i http://MAC3_IP:3001/
curl -i http://MAC3_IP:3001/api/status
```

Allow incoming connections for Python in the macOS firewall if prompted.
The repository's `scripts/test-backends.sh MAC3_IP MAC4_IP` can check
both backends. Match Mac 2's nginx upstream to Mac 3's current IP.

## Caching tests

```sh
curl -i http://127.0.0.1:3001/api/cache-demo
curl -i -H 'If-None-Match: "backend-a-v1"' http://127.0.0.1:3001/api/cache-demo
curl -i -H 'If-None-Match: "different-version"' http://127.0.0.1:3001/api/cache-demo
```

Expect 200, 304 with no body, and 200 respectively. Verify the cache
headers and `X-Backend: A`. Repeat using Mac 3's LAN IP. A cache may reuse
a fresh response for 60 seconds; a conditional request validates its ETag.
These curl commands demonstrate headers and validation, not a browser cache hit.

Run the small regression check from `backend-a/`:

```sh
python test_app.py
```

## Failure and recovery demonstration

1. Confirm both backends respond and Mac 2's load balancing works.
2. Stop Backend A with Ctrl+C. A direct request to Mac 3 port 3001 should
   fail to connect. Do not stop Backend B.
3. Repeat requests through Mac 2's configured application URL. Observe
   Backend B responses and record any errors; failover depends on nginx's
   retry and upstream configuration. If neither backend is available,
   nginx may return 502.
4. Restart Backend A with `python app.py`. Confirm `/api/status` returns
   200 and `X-Backend: A`, then repeat the load balancing test.
5. Save demonstration evidence separately; never include private keys.
