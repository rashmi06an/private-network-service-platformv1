# Verified saved packet capture

[Original Mac3 capture](mac3-full-flow.pcap), received by AirDrop on Mac2.
57 packets,9772bytes; actual timestamps23November2026 07:23:14.314426–07:23:14.642163 UTC
(12:53:14 IST). SHA256:
`99c854a019996830f08dfe2b7ae6095faa237410dc4492cbf7452ea65adaceca`.
The original bytes are preserved. Frame numbers below are derived from this binary
using Wireshark tshark with TCP8443 decoded as TLS.

## DNS and sockets

| Event | Actual frames / fields |
|---|---|
| Private A query | Frame1: Mac3 10.7.28.78:64943 → primary DNS10.7.27.145:53/UDP; transaction0x4d79; app.team1.test |
| Matching answer | Frame3: reverse socket, same transaction, A10.7.25.25 |
| Optional resolver discovery | Frames2/4 and5/12 query _dns.resolver.arpa SVCB and get Refused from primary/backup. These are separate from the successful app A transaction. |
| HTTP1.1 TCP stream0 | Mac3 ephemeral58645 → primary10.7.25.25:8443; SYN6, SYN-ACK7, ACK8 |
| HTTP2 TCP stream1 | Mac3 ephemeral58648 → primary10.7.25.25:8443; SYN31, SYN-ACK33, ACK34 |

## TLS1.2 and encrypted application traffic

| Event | Stream0 / HTTP1.1 | Stream1 / HTTP2 |
|---|---|---|
| ClientHello / SNI app.team1.test | 9; ALPN http/1.1 | 35; offers h2,http/1.1 |
| ServerHello + visible Certificate | 13; ALPN http/1.1 | 38; ALPN h2 |
| ServerKeyExchange / ServerHelloDone | 14 | 39 |
| ClientKeyExchange + client ChangeCipherSpec + encrypted Finished | 16 | 41 |
| Server ChangeCipherSpec + encrypted Finished | 18 | 43 |
| Encrypted Application Data | Client20; server22 | Server44,49,51; client46,47 |

Both ServerHello messages selectTLS1.2 (0x0303) and cipher
TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 (0xc030). Certificate SANs include
app.team1.test and api.team1.test; see [actual Certificate dissection](mac3-full-flow-certificate-details.txt).
The [complete extracted frame fields](mac3-full-flow-fields.txt) preserve the
frame/socket/SEQ/ACK/window/record data. Original decrypted endpoint headers and
successful HTTP200 for B thenA are transcribed separately in
[Mac3 curl observations](2026-11-23-tls12-client-observations.json), matching07:23:14 UTC.
No TLS session secrets were supplied, so HTTP status/body are not read from encrypted records.
ALPN h2 in ServerHello independently confirms HTTP2 negotiation.

## TCP field explanation from actual packets

Stream0 SYN6 has relativeSEQ0, ACK0, window65535, MSS1460, scale64 and SACK permitted.
SYN-ACK7 isSEQ0/ACK1; ACK8 isSEQ1/ACK1. SYN consumes a sequence number without payload.
Frame8 raw receive window2059 × negotiated64 =131776 bytes. This is receiver flow
control, distinct from sender congestion control. ACK is the next byte expected
from the peer. The SYN window itself is unscaled.

Frame57 is a closing RST/ACK after encrypted traffic; it is not an upstream-outage
exhibit. The trace proves the requested DNS→TCP→TLS→encrypted-data path with
visible TLS1.2 Certificate. TLS1.3 encrypts handshake messages after ServerHello;
its certificate would not appear as a readable handshake without session secrets.
Historical screenshots are indexed [separately](packet-index-historical.md).

## Open during the demonstration

Open mac3-full-flow.pcap in Wireshark. Use `dns.id == 0x4d79`, `tcp.stream == 0`,
`tcp.stream == 1`, `tls.handshake.type == 11`, or `frame.number == 13`.
Port443 is conventional HTTPS; this project uses the permitted8443.
