# Backend B — Mac 4

Backend B is one of the two application servers used in the **Private Network Service Platform** project.

It runs on **Mac 4** and serves HTTP requests on **TCP port 3002**. It is designed to receive requests through the nginx reverse proxy and load balancer running on Mac 2.

## Student Details

- **Name:** Ankit Raj Singh
- **Enrollment Number:** 2401010075
- **Role:** Mac 4 — Backend Server B + Test Client
- **Backend Identifier:** B
- **Port:** 3002

## Network Role

The Phase 1 request flow is:

Client → Private DNS → Mac 2 (nginx) → Backend A / Backend B

Backend B runs on Mac 4:

Mac 2 (nginx) → Mac 4 (Backend B :3002)

The application listens on `0.0.0.0` so that it can be accessed by other machines connected to the same private LAN.

## Technology

- Python 3
- Flask
- HTTP/REST
- TCP Port 3002

## API Endpoints

### GET /

Confirms that Backend B is running.

Example response:

```json
{
  "backend": "B",
  "message": "Backend B is running"
}
```

### GET /api/status

Returns the service status and backend identifier.

Example response:

```json
{
  "backend": "B",
  "status": "ok"
}
```

Every response also includes the header `X-Backend: B` so the load balancer
can be observed alternating between Backend A and Backend B.

## Run

```bash
cd backend-b
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

The server then listens on `0.0.0.0:3002`.

Verify locally:

```bash
curl -i http://localhost:3002/api/status
```
