#!/usr/bin/env python3
"""Start/stop the assigned backend independently of a terminal, using its fixed checkout."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ROLES = {'a': ('10.7.28.78', 3001), 'b': ('10.7.27.247', 3002)}


def ps(pid, field):
    result = subprocess.run(['ps', '-ww', '-p', str(pid), '-o', field+'='],
                            capture_output=True, text=True,
                            env=dict(os.environ, LC_ALL='C'))
    return result.stdout.strip()


def owned(entry, app):
    try:
        return (entry['uid'] == os.getuid() and ps(entry['pid'], 'uid') == str(os.getuid())
                and entry['birth'] == ps(entry['pid'], 'lstart')
                and str(app) in ps(entry['pid'], 'command'))
    except (KeyError, TypeError):
        return False


def healthy(port, label):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open('http://127.0.0.1:%s/api/status' % port, timeout=1) as response:
            data = json.load(response)
            if data != {'backend': label.upper(), 'status': 'ok'} or response.headers.get('Cache-Control') != 'no-store':
                return False
        with opener.open('http://127.0.0.1:%s/api/cache-demo' % port, timeout=1) as response:
            return response.headers.get('ETag') == '"team1-cache-v2"' and json.load(response).get('version') == 2
    except (OSError, ValueError):
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('backend', choices=ROLES)
    parser.add_argument('action', choices=['start', 'stop', 'status'])
    args = parser.parse_args()
    ip, port = ROLES[args.backend]
    actual = subprocess.check_output(['ipconfig', 'getifaddr', 'en0'], text=True).strip()
    if actual != ip:
        raise RuntimeError('Wrong Mac: backend%s requires%s; found%s' % (args.backend.upper(), ip, actual))
    app = ROOT / ('backend-'+args.backend) / 'app.py'
    python = app.parent / '.venv/bin/python'
    state = ROOT / '.local-state/backend-services'
    state.mkdir(parents=True, exist_ok=True)
    state.chmod(0o700)
    file = state / (args.backend+'.json')
    log = state / (args.backend+'.log')
    entry = json.loads(file.read_text()) if file.exists() else None
    valid = entry is not None and owned(entry, app)
    if args.action == 'status':
        if not valid:
            raise RuntimeError('No matching managed backend process; unrelated processes were left untouched')
        print('PID=%s APP=%s LOG=%s' % (entry['pid'], app, log))
        if not healthy(port, args.backend):
            raise RuntimeError('Registered process is running but current application checks fail; inspect log')
        print('PASS: assigned backend process and current v2 application are healthy')
        return
    if args.action == 'stop':
        if not valid:
            if entry is not None:
                raise RuntimeError('Stale process registration; refusing to signal a different PID instance')
            print('Already stopped by this manager; no other process was signalled')
            return
        os.kill(entry['pid'], signal.SIGTERM)
        deadline = time.monotonic()+5
        while owned(entry, app) and time.monotonic() < deadline:
            time.sleep(.1)
        if owned(entry, app):
            raise RuntimeError('Owned process did not stop; inspect it before another action')
        file.unlink()
        print('STOPPED: backend%s PID%s' % (args.backend.upper(), entry['pid']))
        return
    if valid:
        if not healthy(port, args.backend):
            raise RuntimeError('Existing owned process is unhealthy; stop it explicitly and inspect log')
        print('PASS: already running backend%s PID%s' % (args.backend.upper(), entry['pid']))
        return
    if not app.is_file() or not python.is_file():
        raise RuntimeError('Prepare this checkout backend and its .venv first')
    try:
        with socket.create_connection(('127.0.0.1', port), timeout=.5):
            raise RuntimeError('Port%s already occupied; inspect lsof and stop only the identified old backend first' % port)
    except OSError:
        pass
    descriptor = os.open(log, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(descriptor, 'ab', buffering=0) as output:
        process = subprocess.Popen([str(python), '-u', str(app)], cwd=ROOT,
                                   stdin=subprocess.DEVNULL, stdout=output,
                                   stderr=subprocess.STDOUT, start_new_session=True)
    entry = {'pid': process.pid, 'uid': os.getuid(), 'birth': ps(process.pid, 'lstart'),
             'app': str(app), 'started_utc': datetime.now(timezone.utc).isoformat()}
    temporary = file.with_suffix('.%s.tmp' % os.getpid())
    temporary.write_text(json.dumps(entry, indent=2)+'\n'); temporary.chmod(0o600); temporary.replace(file)
    deadline = time.monotonic()+8
    while process.poll() is None and time.monotonic() < deadline:
        if owned(entry, app) and healthy(port, args.backend):
            print('PASS: background backend%s PID%s PORT%s\nAPP=%s\nLOG=%s' %
                  (args.backend.upper(), process.pid, port, app, log))
            return
        time.sleep(.2)
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill(); process.wait()
    file.unlink(missing_ok=True)
    raise RuntimeError('Backend failed startup; inspect%s' % log)


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print('FAIL:', error, file=sys.stderr)
        sys.exit(1)
