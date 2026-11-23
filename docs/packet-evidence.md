# Saved packet captures and frame index

Screenshots are allowed evidence, but final demo step6 asks to open a saved capture.
Capture only the relevant project hosts/ports. Never include private keys in Git.
The commands below are executed on Mac 2, after all normal-state checks pass.

## Single-client capture: Mac 3, terminal 1

Use Mac 3 as the client so both DNS and HTTPS cross the LAN. Begin only after
normal DNS, trusted certificates, both updated backends and primary nginx pass.

```bash
cd "$HOME/Documents/CN-submission"
mkdir -p evidence/verification
sudo tcpdump -ni en0 -s 0 -w evidence/verification/mac3-full-flow.pcap '((host 10.7.27.145 or host 10.7.27.247) and port 53) or (host 10.7.25.25 and tcp port 8443)'
```

## Mac 3, terminal 2: normal hostname requests with validation

```bash
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
dig @10.7.27.145 app.team1.test
/usr/bin/curl --noproxy '*' --tlsv1.2 --tls-max 1.2 -v https://app.team1.test:8443/api/status
/usr/bin/curl --noproxy '*' --tlsv1.3 -v https://app.team1.test:8443/api/status
```

Stop tcpdump in terminal 1 with Ctrl+C. Open the saved pcap in Wireshark and
optionally export pcapng. Direct dig checks the server; normal curl uses system
DNS. Correlate actual hostname, timestamps, client IP and TCP streams. The
controlled TLS 1.2 request makes Certificate visible; TLS 1.3 encrypts the
handshake after ServerHello. Do not invent frame numbers before capture.

## Optional internal HTTP / backend failover capture (Mac 2)

```bash
sudo tcpdump -ni en0 -s 0 -w evidence/verification/backend-failover.pcap '(host 10.7.28.78 and tcp port 3001) or (host 10.7.27.247 and tcp port 3002)'
```

While recording, run the balanced/A-down sequence. Stop and open in Wireshark;
show plaintext backend HTTP/200 and, if observed, A RST/refused followed by B200.
Do not assert an RST exists unless the actual saved trace contains it.

## Complete a packet index from the actual trace

Write `evidence/verification/packet-index.md` with: capture filename, acquisition
host/time, client/DNS/edge IPs; DNS query/response frame numbers and transactionID;
matching TCP stream, SYN/SYN-ACK/ACK frame numbers and source/destination ports;
TLS ClientHello, ServerHello, Certificate (TLS 1.2), ChangeCipherSpec and encrypted
application-data frame numbers. Also explain TLS 1.3 encrypted certificate and the
actual SEQ/ACK/window fields. Add screenshots of those expanded details.

Useful filters: `dns.qry.name == "app.team1.test"`, `tcp.stream == N`,
`tls.handshake`, and `tcp.port == 3001 || tcp.port == 3002`.
Do not invent frame numbers before collecting the real capture. If Wireshark
exports pcapng, keep that alongside the pcap or use pcapng in the ledger.
