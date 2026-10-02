# Client DNS Setup

DNS Server:
MAC1_IP_HERE

Clients:
- Mac 2 — Samiksha
- Mac 3 — Shubhaang
- Mac 4 — Ankit

Required DNS records:

app.team1.test -> MAC2_IP_HERE
api.team1.test -> MAC2_IP_HERE

Verification:

dig app.team1.test
dig api.team1.test

Expected result:

Both domains should resolve to the private IP of Mac 2.