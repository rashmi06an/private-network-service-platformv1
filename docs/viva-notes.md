# Whole-system rehearsal notes

Every member should explain the full path in their own words. These notes are for
preparation; final viva answers are personal and should not be read out.

## DNS, names and cutover

DNS maps a name to an IP; it does not open TCP, check app health, or guarantee
that an address is correct. app/api point to the edge, so clients do not need
backend addresses. A backup resolver handles name-service failure only if clients
actually use it and its data agrees with the primary. Explicit dig and cached
system lookup are different observations. Split DNS routes only team1.test to
team servers; bare dig usually follows the global resolver instead.

TTL bounds how long a cache can reuse an answer. A record change is immediately
visible at a server but clients may retain OLD until expiry. Flushing a real cache
forces a fresh lookup earlier. This controls service migration/cutover delays.
Two resolvers must be changed and restored together; disagreeing answers are not
proof of TTL behavior. DNS cutover is manual recovery, not automatic HA.

## TCP, reliability, flow control and ports

DNS generally uses UDP53 here (TCP53 is also available); HTTPS uses TCP8443.
The client's ephemeral port plus its IP, and edge IP plus8443, identify a socket
pair. SYN → SYN-ACK → ACK synchronizes initial sequence numbers. Sequence numbers
count stream bytes; ACK is the next byte expected. A SYN consumes one sequence
number. Relative Seq0/Ack1 in a capture is a display convenience, not a universal
wire value. Loss can trigger retransmission; duplicate ACKs and reordering need
context rather than automatically implying an application failure.

Receiver window advertises buffering capacity, providing TCP flow control. Window
scaling expands its range. This differs from congestion control, which adapts the
sender to network conditions. Use the actual SYN/window/SEQ/ACK/retransmission
frames in the saved capture to illustrate these concepts.

## TLS and HTTPS

TCP is established before TLS. ClientHello offers versions/ciphers and SNI;
ServerHello selects parameters; server authentication uses its certificate and
proof of the associated key. The client checks hostname SAN, validity and trust.
Key agreement derives traffic keys; Finished authenticates the handshake.
TLS terminates at nginx; the backend leg is ordinary HTTP on the private LAN.
Wireshark therefore sees encrypted application data on the client-edge leg.

TLS 1.3 encrypts handshake messages after ServerHello, including Certificate.
A compatibility ChangeCipherSpec is not the TLS 1.3 key agreement itself.
The controlled TLS 1.2 trace makes the literal Certificate message visible while
retaining trust verification. Never use -k as the final certificate demonstration.

## HTTP versions, REST and caches

HTTP/1.1 uses textual request/status/header framing and persistent connections.
HTTP/2 multiplexes streams over TCP, uses binary framing and header compression;
it is negotiated by ALPN here. `curl --http2` must actually report HTTP/2; a
fallback1.1 is not a successful HTTP/2 exhibit. HTTP/3 uses QUIC over UDP and
integrates TLS 1.3; explain it, no HTTP/3 service is required for this project.
REST endpoints use HTTP methods/resources and return small JSON representations.

A fresh cache hit reuses a stored response within freshness lifetime, potentially
without contacting the origin. A conditional request sends a validator; 304 means
reuse the stored body, with no new body transferred. A full new response is 200
with the representation, for example after a validator mismatch. curl does not
cache between ordinary invocations; two curl200s do not prove a fresh cache hit.
The project demonstrates Cache-Control and an actual conditional304. ETag can
match across A/B because the cache-demo body is identical; X-Backend identifies
which backend answered without changing that representation.

## Balancing, isolation and resilience

nginx round robin distributes independent requests among the upstreams. Passive
checks learn from failed traffic; error/timeout retry can send the same safe GET
to the other backend, and fail_timeout suppresses the failed server temporarily.
Recovery allows it to rejoin; this does not make the edge itself redundant.
The cloud equivalent is an application load balancer; private DNS resembles a
managed DNS service, and backend instances resemble application servers.

The C firewall permits only Mac 2 to backend ports, stopping direct client bypass
of the TLS edge. A timeout alone could also mean a stopped server; compare a
contemporaneous allowed connection from Mac 2 and rule counters. Rollback restores
the prior rule state without removing another PF owner's enable reference.
When a standby is deliberately used as an edge, either finish C and roll back or
explicitly authorize both designated edge IPs during cutover. Keep ordinary
clients denied under the combined policy. The LAN/router and single primary edge
remain shared failure dependencies; floating VIP/automatic DNS failover with a
second always-on edge would remove the primary edge SPOF more fully.

## Email and layer diagnosis

SMTP transfers/sends mail; IMAP synchronizes mailboxes; POP3 downloads messages.
They are application protocols using transport and optional/required TLS according
to deployment. They are explanation-only; no email server is part of this build.

DNS/HTTP map to application; TCP/UDP to transport; IP to network; Ethernet/Wi-Fi
to link. TLS sits above TCP and below HTTP (the rubric calls it session/transport).
Diagnose DNS first, then TCP reachability, TLS identity/trust, edge HTTP and upstream
app response. Explain the hypothesis and evidence aloud, even if a fix is partial.
