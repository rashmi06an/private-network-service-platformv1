# TLS generation, trust and standby identity

The existing valid `app.team1.test.pem` and `app.team1.test-key.pem` may be reused.
Do not regenerate the CA during every demonstration. All clients must trust the
same issuing CA; faculty approval for a local CA/mkcert must be confirmed by the team.

## Generate only if the required leaf certificate is absent/invalid (Mac 2)

```bash
brew install mkcert
mkcert -install
sudo mkdir -p /opt/homebrew/etc/nginx/certs
mkcert -cert-file /tmp/team1-leaf.pem -key-file /tmp/team1-leaf-key.pem app.team1.test api.team1.test
sudo install -m 644 /tmp/team1-leaf.pem /opt/homebrew/etc/nginx/certs/app.team1.test.pem
sudo install -m 600 /tmp/team1-leaf-key.pem /opt/homebrew/etc/nginx/certs/app.team1.test-key.pem
rm /tmp/team1-leaf.pem /tmp/team1-leaf-key.pem
```

Explicit output filenames match [tls.conf.example](tls.conf.example); mkcert's
default `+1` naming is not assumed. Inspect the public certificate:

```bash
openssl x509 -in /opt/homebrew/etc/nginx/certs/app.team1.test.pem -noout -subject -issuer -dates -ext subjectAltName
```

## Client trust (every client, including Mac 1 / 3 / 4)

On the issuing Mac, `mkcert -CAROOT` locates **rootCA.pem**. Copy only that public
certificate to each client using AirDrop or another agreed local transfer. In its
receiving directory on each client:

```bash
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain rootCA.pem
/usr/bin/curl --noproxy '*' -v https://app.team1.test:8443/api/status
```

Capture hostname match, successful certificate verification and HTTP 200 on the
actual clients. Never copy `rootCA-key.pem` to clients and never commit any private
key. `.gitignore` keeps certificates/keys and per-Mac deployment state out of Git.

## Standby (Mac 3)

The standby needs a leaf certificate valid for the same names under a CA the
clients trust. It may use a separately issued leaf certificate. The CA signing
key remains on the issuing Mac. Transfer the standby leaf certificate and its
own leaf key securely to the corresponding `certs/` paths on Mac 3, with key mode
600. Sharing the exact primary leaf certificate/key is an alternative for this
local exercise, not a protocol requirement. No key belongs in evidence or GitHub.

## Self-signed alternative

If a local CA is not approved, create a self-signed leaf containing both DNS SANs
with OpenSSL and explicitly trust that certificate on each client. A self-signed
certificate can be trusted; omitting trust setup is what produces warnings.

```bash
openssl req -x509 -newkey rsa:2048 -nodes -days 365 -keyout app.team1.test-key.pem -out app.team1.test.pem -subj '/CN=app.team1.test' -addext 'subjectAltName=DNS:app.team1.test,DNS:api.team1.test'
```

TLS 1.3 encrypts handshake messages after ServerHello, including Certificate.
For the rubric's visible Certificate packet, capture a controlled TLS 1.2 session
with `--tlsv1.2 --tls-max 1.2` and keep trust validation enabled. Normal service
still supports both TLS 1.2 and 1.3. See [packet guide](../docs/packet-evidence.md).

References: [mkcert CA trust](https://github.com/FiloSottile/mkcert#installing-the-ca-on-other-systems),
[TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446.html#section-2).
