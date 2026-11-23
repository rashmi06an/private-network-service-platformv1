# Packet evidence index

This index reuses actual screenshots already present on main. Frame numbers below
belong to the individual historical captures shown, not to a new common stream.
No saved binary for the new Mac3 flow was received; this index is partial evidence.

| Exhibit | Fields actually visible |
|---|---|
| [DNS query/response](../phase2/wireshark/dns-query-response-app-team1.png) | Query frame2516 and response2519; transaction0x5929; app.team1.test A10.7.25.25; client10.7.25.25 and DNS10.7.27.145; UDP61827↔53. |
| [TCP SYN detail](../wireshark/tcp-syn-detail.png) | Historical frame87, TCP stream4; client10.7.21.15:60391 → edge10.7.7.9:8443; relativeSEQ0, rawSEQ2358323391, nextSEQ1, ACK0; SYN/ECE/CWR; window65535; MSS1460; window-scale64; SACK permitted. Do not confuse the displayed Ethernet stream27 with TCP stream4. |
| [TLS handshake](../phase2/wireshark/tls-handshake-clienthello-serverhello.png) | Frame4115 ClientHello, reassembled from4114/4115; frame4133 ServerHello/ChangeCipherSpec/encrypted records; client10.7.27.145:56853 → edge10.7.25.25:8443. No decoded Certificate is visible. |
| [Historical exchange overview](../wireshark/tcp-tls-full-exchange.png) | Preserved original overview; use alongside SYN detail. No new frame numbers inferred from its filename. |
| [New Mac3 TLS1.2 observations](2026-11-23-tls12-client-observations.json) | Normal hostname resolves to primary, certificate validates, HTTP1.1 andHTTP2 each200; this is curl output, not packet decoding. |

A SYN consumes one sequence number, so relative nextSEQ is1 even with no payload.
ACK reports the next expected byte from the peer. The advertised receive window
is flow control; negotiated scaling applies to later windows, not the SYN's raw
window field. It differs from congestion control's sender-side congestion window.

TLS1.2 can expose Certificate before encryption starts; TLS1.3 encrypts handshake
messages after ServerHello. The compatibility ChangeCipherSpec in a TLS1.3 view
is not a decoded Certificate. Encrypted application records do not reveal HTTP
headers or bodies without appropriate session secrets; curl shows decrypted headers
at the endpoint. HTTPS443 is conventional; this project uses the permitted8443.

The unreceived binary prevents reopening and correlating the complete new DNS,
TCP three-way handshake, Certificate and encrypted application flow. Accordingly,
the saved-capture item remains unverified in the acceptance ledger. The collection
procedure remains in [the packet guide](../../docs/packet-evidence.md).
