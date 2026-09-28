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
