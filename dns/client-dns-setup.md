# Client DNS Setup

DNS Server (Mac 1):
10.7.17.21

Set this as the DNS resolver on each client Mac:
System Settings → Network → (Wi-Fi) Details → DNS → add `10.7.17.21`.

Clients:
- Mac 2 — Samiksha
- Mac 3 — Shubhaang
- Mac 4 — Ankit

Required DNS records (served by Mac 1):

app.team1.test -> 10.7.7.9
api.team1.test -> 10.7.7.9

Verification:

dig app.team1.test
dig api.team1.test

Expected result:

Both domains resolve to 10.7.7.9 (the private IP of Mac 2).
