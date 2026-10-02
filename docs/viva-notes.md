# Viva Notes — Phase 1 Concepts

Every team member should be able to explain **any** of these, not just their own role.

## DNS

- **What DNS does here:** maps `app.team1.test` to Mac 2's private IP. It is a
  *directory lookup*, not a connection.
- **Resolution vs connection:** DNS finds the IP (53/UDP); the browser then opens a
  *separate* TCP+TLS connection to that IP on 8443. They are independent layers —
  DNS can fail while raw IP connectivity still works, and vice versa.
- **Why `.test`:** reserved namespace; `.local` conflicts with macOS mDNS.

## TCP

- **Three-way handshake:** `SYN → SYN-ACK → ACK` establishes the connection before
  any HTTP data is sent.
- **Ports / socket pair:** client uses an ephemeral source port; server uses a
  well-known port (443 is the standard for HTTPS — we use 8443; backends on 3001/3002).
  A connection is identified by the 4-tuple (src IP, src port, dst IP, dst port).
- **Reliability:** sequence + acknowledgement numbers let TCP detect loss and
  reorder/retransmit; flow control uses the advertised window.

## TLS / HTTPS

- **Termination:** TLS is terminated at nginx (Mac 2); traffic to the backends is
  plain HTTP on the trusted LAN.
- **Handshake order:** `ClientHello → ServerHello → Certificate → Key Exchange → Finished`.
- **Why the payload is encrypted in Wireshark:** after the handshake it is
  `Application Data`; use `curl -v` to see the cleartext request/response.
- **Certificate trust:** the local CA (mkcert) is added to each client's trust store,
  so no `-k` flag is needed in the demo.

## HTTP / REST + Load balancing

- **REST endpoints:** `GET /` and `GET /api/status` returning JSON with a `backend`
  identifier; each response carries `X-Backend: A|B`.
- **Reverse proxy:** clients only ever talk to the edge; they never know or need the
  backend IPs. The edge forwards to an `upstream` pool.
- **Round-robin:** repeated requests alternate between Backend A and B, visible via
  the `X-Backend` header.

## Caching

- **Cache-Control: max-age=60** → a fresh response can be reused for 60s (cache hit).
- **ETag + If-None-Match** → a conditional request returns **304 Not Modified** with
  no body when unchanged.
- **Three cases:** fresh cache hit (no request sent) vs conditional request (304, no
  body) vs full new request (200, full body).

## OSI ↔ TCP/IP quick map

DNS/HTTP = Application · TLS = Session/Transport · TCP/UDP = Transport ·
IP = Network · Ethernet = Link.
