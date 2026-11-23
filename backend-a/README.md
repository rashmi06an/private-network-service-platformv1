# Backend A — Mac 3, port 3001

Prepare the virtual environment in this checkout, then use the role-checked
background manager below. It starts this exact application path in a detached
session and logs under `.local-state/backend-services`. Closing its launch terminal
does not stop it. The service binds `0.0.0.0:3001` with debug disabled.

| Endpoint | Behavior |
|---|---|
| GET / | Backend A running JSON |
| GET /api/status | status=ok, backend=A; Cache-Control:no-store |
| GET /api/cache-demo | same body as the other backend, max-age=60, ETag:"team1-cache-v2" |

Every response carries `X-Backend: A`. Matching conditional cache-demo
requests return empty HTTP 304; weak tags, tag lists and wildcard use Werkzeug's
standard conditional handling. An unmatched tag gives 200. HEAD has no body.
Backend identity is in the header rather than the shared cache-demo body.

```bash
cd "$HOME/Documents/CN-submission"
python3 -m venv backend-a/.venv
backend-a/.venv/bin/python -m pip install -r backend-a/requirements.txt
python3 scripts/backend-service.py a start
```

From another terminal at repository root: `python3 -m unittest discover -s tests -v`.
For submitted network proof, use trusted HTTPS by private hostname through nginx.
Direct/localhost requests are useful diagnostics and do not replace that path.
See [member commands](../docs/team-commands.md) for failure, recovery and isolation.

Lifecycle commands from checkout root:

```bash
python3 scripts/backend-service.py a status
python3 scripts/backend-service.py a stop
python3 scripts/backend-service.py a start
```

The manager records UID/PID/birth time and checks the exact app path before
signalling a process. It refuses an unknown occupied port; stop an identified
previous foreground instance before first adoption. It checks current no-store
and shared-v2 application behavior before reporting startup success. This is a
detached process, not an automatic restart or boot service: rerun start after
a logout/reboot or unexpected process exit. Use stop/start for controlled HA tests.
