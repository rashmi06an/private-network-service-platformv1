# TLS Certificate Setup Notes (Mac 2 edge)

How the HTTPS certificate for `app.team1.test` / `api.team1.test` was created, installed
on nginx, and trusted on the client Macs — so the final demo shows a valid padlock with
**no `-k` flag and no certificate warning**.

We use **mkcert** (a local CA) because self-signed certs can't be trusted cleanly across
machines. (`openssl` alternative is noted at the end.)

## 1. One-time: create the local CA (on Mac 2)

```bash
brew install mkcert nss          # nss = Firefox trust (optional)
mkcert -install                  # creates + trusts the local CA (the "rootCA") on Mac 2
mkcert -CAROOT                    # prints the CA folder — note this path
```

## 2. Issue the server certificate (on Mac 2)

```bash
cd /opt/homebrew/etc/nginx/certs    # create this folder if needed
mkcert app.team1.test api.team1.test
# produces:
#   app.team1.test+1.pem        (certificate)
#   app.team1.test+1-key.pem    (PRIVATE KEY — never commit this)
```

Point nginx at these files (see [tls.conf.example](tls.conf.example)):

```nginx
ssl_certificate     /opt/homebrew/etc/nginx/certs/app.team1.test+1.pem;
ssl_certificate_key /opt/homebrew/etc/nginx/certs/app.team1.test+1-key.pem;
ssl_protocols TLSv1.2 TLSv1.3;
```

```bash
sudo nginx -t && sudo nginx -s reload
```

## 3. Trust the CA on every client Mac (Mac 1, Mac 3, Mac 4)

The clients must trust the **same local CA**, otherwise they'd see a warning.

```bash
# On Mac 2: find the root CA and copy it to each client (AirDrop / scp):
mkcert -CAROOT        # e.g. /Users/<you>/Library/Application Support/mkcert
#   -> copy rootCA.pem to each client

# On each client Mac, add rootCA.pem to the System keychain as trusted:
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain rootCA.pem
```

(Alternatively, install mkcert on each client and run `mkcert -install` after copying the
same `rootCA.pem` / `rootCA-key.pem` into that machine's `mkcert -CAROOT` folder.)

## 4. Verify (no `-k`)

```bash
curl -v https://app.team1.test:8443/api/status     # 200 OK, no cert warning, no -k
# Browser: https://app.team1.test:8443  → padlock, no warning
```

## TLS handshake to explain in the viva

`ClientHello` → `ServerHello` → `Certificate` (+ key exchange) → `Finished`; after this the
HTTP payload is encrypted (Wireshark shows `Application Data`). Captures:
`evidence/wireshark/tls-client-hello.png` and `evidence/phase2/wireshark/tls-handshake-clienthello-serverhello.png`.

## Phase 2 note — standby edge (Mac 3)

The standby edge must present the **same** certificate for `app.team1.test`, so copy the
`certs/` folder from Mac 2 to Mac 3 (or re-issue with `mkcert app.team1.test api.team1.test`
on Mac 3 using the same shared CA). Otherwise the cutover would trigger a cert warning.

## Security

- The **private key** (`*-key.pem`) and `rootCA-key.pem` must **never** be committed to
  GitHub. `.gitignore` excludes `*.pem` and `*.key` (so no certificate or key is tracked).
- These are local-CA certs for a private `.test` domain — valid only inside the team LAN.

## OpenSSL alternative (if mkcert is not approved)

```bash
openssl req -x509 -newkey rsa:2048 -nodes -keyout app.team1.test-key.pem \
  -out app.team1.test.pem -days 365 \
  -subj "/CN=app.team1.test" \
  -addext "subjectAltName=DNS:app.team1.test,DNS:api.team1.test"
# then add app.team1.test.pem to each client's System keychain as trusted (as in step 3).
```
