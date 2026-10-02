# Packet Captures — Task G

Save Wireshark captures (`.pcap` / `.pcapng`) here, and copy exported
screenshots into `evidence/phase1/wireshark/`.

## What to capture (single `https://app.team1.test/api/status` request)

| Layer          | What to point to in the capture                                   |
|----------------|-------------------------------------------------------------------|
| DNS            | Query for `app.team1.test` + response carrying Mac 2's IP (53/UDP)|
| TCP handshake  | `SYN -> SYN-ACK -> ACK` before any application data (443/TCP)     |
| TLS handshake  | `ClientHello`, `ServerHello`, `Certificate`, `ChangeCipherSpec`   |
| Encrypted data | `Application Data` frames — show the HTTP payload is not readable  |
| Ports          | Client ephemeral source port + server well-known port per layer   |

## How to capture

1. Open Wireshark on the client Mac, choose the Wi-Fi/LAN interface.
2. Apply a capture/display filter, e.g.
   `dns || tcp.port == 443` (add `|| udp.port == 53`).
3. Run the request:
   ```bash
   dig app.team1.test
   curl -v https://app.team1.test/api/status
   ```
4. Stop the capture and **File → Save As** a `.pcapng` into this folder.
5. Export annotated screenshots of each handshake into
   `evidence/phase1/wireshark/`.

> Tip: capture `dig` and `curl` in the *same* session so the DNS → TCP → TLS → HTTP
> sequence appears together in one file.
