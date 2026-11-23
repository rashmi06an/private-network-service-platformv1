# Backend A — Mac 3, port 3001

From this directory, create `.venv`, activate it, install `requirements.txt`,
then run `python app.py`. Stop the previous instance first; keep this terminal
open. The service binds `0.0.0.0:3001` with debug disabled.

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
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

From another terminal at repository root: `python3 -m unittest discover -s tests -v`.
For submitted network proof, use trusted HTTPS by private hostname through nginx.
Direct/localhost requests are useful diagnostics and do not replace that path.
See [member commands](../docs/team-commands.md) for failure, recovery and isolation.
