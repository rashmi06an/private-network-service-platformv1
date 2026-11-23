#!/usr/bin/env python3
"""Fast-forward this team's checkout while preserving colliding local evidence."""
import argparse
import os
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

BRANCH = 'samiksha/submission-readiness'
IPS = {'mac1': '10.7.27.145', 'mac2': '10.7.25.25',
       'mac3': '10.7.28.78', 'mac4': '10.7.27.247'}


def git(*args):
    return subprocess.check_output(['git', *args]).decode().strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--role', choices=IPS)
    args = parser.parse_args()
    root = Path(git('rev-parse', '--show-toplevel'))
    os.chdir(root)
    if args.role:
        actual = subprocess.check_output(['ipconfig', 'getifaddr', 'en0']).decode().strip()
        if actual != IPS[args.role]:
            raise RuntimeError('Wrong Mac: expected %s for %s; found %s' %
                               (IPS[args.role], args.role, actual))
        print('ROLE=%s IP=%s' % (args.role, actual), flush=True)
    if git('branch', '--show-current') != BRANCH:
        raise RuntimeError('Switch to %s before updating' % BRANCH)
    for flags in [[], ['--cached']]:
        if subprocess.run(['git', 'diff', *flags, '--quiet']).returncode != 0:
            raise RuntimeError('Tracked files have local changes; preserve/review them before updating')
    subprocess.run(['git', 'fetch', 'origin', BRANCH], check=True)
    # Pin this fetch rather than relying on a clone's remote-tracking refspec.
    target = git('rev-parse', 'FETCH_HEAD')
    if subprocess.run(['git', 'merge-base', '--is-ancestor', 'HEAD', target]).returncode:
        raise RuntimeError('Local history cannot fast-forward; no evidence was moved')
    incoming = set(subprocess.check_output(
        ['git', 'ls-tree', '-r', '--name-only', '-z', target]).split(b'\0'))
    untracked = set(subprocess.check_output(
        ['git', 'ls-files', '--others', '--exclude-standard', '-z']).split(b'\0'))
    collisions = sorted(incoming & untracked - {b''})
    for raw in collisions:
        path = Path(raw.decode())
        if path.parts[:2] != ('evidence', 'verification'):
            raise RuntimeError('Untracked non-evidence collision: %s; preserve it manually' % path)
        if (root / path).is_symlink() or not (root / path).is_file():
            raise RuntimeError('Refusing to move a non-regular evidence file: %s' % path)
    if collisions:
        state = root / '.local-state'
        state.mkdir(exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        backup = Path(tempfile.mkdtemp(prefix='evidence-before-update-' + stamp + '-', dir=state))
        print('LOCAL_EVIDENCE_BACKUP=%s' % backup, flush=True)
        for raw in collisions:
            relative = Path(raw.decode())
            destination = backup / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(root / relative), str(destination))
            print('Preserved: %s' % relative, flush=True)
    subprocess.run(['git', 'merge', '--ff-only', target], check=True)
    print('PASS: checkout updated; original colliding logs remain in the printed local backup')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError, OSError) as error:
        print('STOP: %s' % error, file=sys.stderr)
        sys.exit(1)
