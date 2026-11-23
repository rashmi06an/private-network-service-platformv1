#!/usr/bin/env python3
"""Measure a real temporary dnsmasq client cache; never fabricate DNS responses.

Both DNS Macs must schedule dns-record.sh for the SAME future epoch first.
expiry/flush use ttl.team1.test. cutover uses app.team1.test and normal HTTPS.
"""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

PRIMARY='10.7.27.145'
BACKUP='10.7.27.247'
OLD='10.7.25.25'
NEW='10.7.28.78'
ROOT=Path(__file__).resolve().parents[1]

def stamp():return datetime.now(timezone.utc).isoformat(timespec='milliseconds')
def run(args,**kwargs):return subprocess.run(args,check=True,text=True,**kwargs)
def answer(server,port,name):
    r=run(['dig','@'+server,'-p',str(port),name,'A','+time=2','+tries=1','+noall','+answer'],capture_output=True)
    for line in r.stdout.splitlines():
        cols=line.split()
        if len(cols)>=5 and cols[0]==name+'.' and cols[3]=='A':
            print(f'{stamp()} server={server}:{port} {line}',flush=True)
            return cols[4],int(cols[1])
    raise RuntimeError(f'No IPv4 answer from {server}:{port}: {r.stdout.strip()}')
def expected(server,port,name,ip):
    result=answer(server,port,name)
    if result[0]!=ip:raise RuntimeError(f'{server}:{port}: expected {ip}, observed {result[0]}')
    return result
def wait_until(epoch):
    while time.time()<epoch:time.sleep(min(.25,epoch-time.time()))
def flush_system():
    run(['sudo','-n','dscacheutil','-flushcache'])
    run(['sudo','-n','killall','-HUP','mDNSResponder'])
def https(state,label,expected_ip,expected_edge):
    headerfile=state/(label+'.headers')
    r=run(['/usr/bin/curl','--noproxy','*','--connect-timeout','3','--max-time','10',
           '-sS','-D',str(headerfile),'-o','/dev/null','-w','%{http_code} %{remote_ip}',
           'https://app.team1.test:8443/api/status'],capture_output=True)
    print(f'{stamp()} HTTPS_{label}={r.stdout}',flush=True)
    headers=headerfile.read_text();print(headers,flush=True)
    values=dict(line.split(':',1) for line in headers.lower().splitlines() if ':' in line)
    if r.stdout.split()!=['200',expected_ip]:raise RuntimeError(f'{label}: wrong HTTP code or connected IP')
    if values.get('x-edge','').strip()!=expected_edge:raise RuntimeError(f'{label}: wrong/missing X-Edge')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=['expiry','flush','cutover'])
    p.add_argument('epoch',type=int,help='Same future Unix epoch scheduled on BOTH DNS Macs')
    args=p.parse_args()
    if not 12<args.epoch-time.time()<=600:raise RuntimeError('Start 12 seconds to 10 minutes before the scheduled change')
    actual=run(['ipconfig','getifaddr','en0'],capture_output=True).stdout.strip()
    if actual!=OLD:raise RuntimeError('Run the client experiment on Mac 2 (10.7.25.25)')
    name='app.team1.test' if args.mode=='cutover' else 'ttl.team1.test'
    dnsmasq=shutil.which('dnsmasq')
    if not dnsmasq:
        prefix=run(['brew','--prefix','dnsmasq'],capture_output=True).stdout.strip()
        dnsmasq=str(Path(prefix)/'sbin/dnsmasq')
    if not Path(dnsmasq).is_file():raise RuntimeError('Install dnsmasq on Mac 2: brew install dnsmasq')
    state=ROOT/'.local-state'/f'client-cache-{args.mode}-{args.epoch}'
    state.mkdir(parents=True,exist_ok=False)
    config=state/'client-cache.conf'
    cache_host = OLD if args.mode=='cutover' else '127.0.0.1'
    cache_port = 53 if args.mode=='cutover' else 53535
    config.write_text(f'port={cache_port}\nlisten-address={cache_host}\nbind-interfaces\nno-resolv\nno-hosts\ncache-size=200\nstrict-order\n'
                      f'server=/team1.test/{PRIMARY}\nserver=/team1.test/{BACKUP}\n')
    resolver=Path('/etc/resolver/team1.test')
    before=resolver.read_bytes() if resolver.exists() else None
    altered=False
    process=None
    daemon_pid=None
    logfile=(state/'cache-process.txt').open('w')
    try:
        if args.mode=='cutover':
            # macOS ignores localhost/non-53 scoped overrides on current releases.
            # Use the coordinator's actual LAN address and port 53, refusing collisions.
            run(['sudo','-v'])
            listeners=subprocess.run(['sudo','-n','lsof','-t','-nP',f'-iUDP@{OLD}:53',f'-iTCP@{OLD}:53'],capture_output=True,text=True)
            if listeners.stdout.strip():raise RuntimeError('Mac 2 port 53 already occupied; do not stop an unrelated DNS process')
            run(['sudo','-n',dnsmasq,'--conf-file='+str(config),'--pid-file='+str(state/'cache.pid'),'--log-facility='+str(state/'daemon-log.txt')])
            daemon_pid=int((state/'cache.pid').read_text().strip())
        else:
            process=subprocess.Popen([dnsmasq,'--keep-in-foreground','--conf-file='+str(config),'--pid-file='+str(state/'cache.pid')],stdout=logfile,stderr=subprocess.STDOUT)
            time.sleep(.5)
            if process.poll() is not None:raise RuntimeError('Temporary cache could not start; inspect '+str(state/'cache-process.txt'))
        expected(PRIMARY,53,name,OLD);expected(BACKUP,53,name,OLD)
        if args.mode=='cutover':
            if before is not None:(state/'resolver.before').write_bytes(before)
            else:(state/'resolver.was-absent').touch()
            scoped=state/'resolver.cache';scoped.write_text(f'nameserver {cache_host}\n')
            run(['sudo','-n','mkdir','-p','/etc/resolver'])
            run(['sudo','-n','install','-m','644',str(scoped),str(resolver)])
            altered=True;flush_system()
        print(f'{stamp()} ARMED mode={args.mode} record={name} change_epoch={args.epoch}; cache is real dnsmasq on client Mac 2',flush=True)
        wait_until(args.epoch-3)
        if args.mode=='cutover':
            # Background OS lookups may have used this resolver while it was armed.
            # Clear only this owned cache before the measured30-second interval.
            command=subprocess.run(['ps','-ww','-p',str(daemon_pid),'-o','command='],capture_output=True,text=True).stdout
            if str(config) not in command:raise RuntimeError('Temporary cache PID no longer matches this experiment')
            run(['sudo','-n','kill','-HUP',str(daemon_pid)])
            time.sleep(.1)
            print(f'{stamp()} PRE_PRIME_RESET: owned cache cleared before measured TTL interval',flush=True)
        ip,ttl=expected(cache_host,cache_port,name,OLD)
        primed=time.monotonic()
        if ttl!=30:raise RuntimeError(f'Expected newly primed TTL 30, got {ttl}')
        if args.mode=='cutover':https(state,'before-change',OLD,'primary-mac2')
        wait_until(args.epoch+2)
        expected(PRIMARY,53,name,NEW);expected(BACKUP,53,name,NEW)
        expected(cache_host,cache_port,name,OLD)
        if args.mode=='cutover':https(state,'cached-old-after-change',OLD,'primary-mac2')
        if args.mode=='flush':
            print(f'{stamp()} MANUAL_FLUSH: SIGHUP only to temporary client-cache PID {process.pid}',flush=True)
            process.send_signal(signal.SIGHUP);time.sleep(.25)
            expected(cache_host,cache_port,name,NEW)
            elapsed=time.monotonic()-primed
            if elapsed>=ttl:raise RuntimeError('Flush happened after natural expiry; repeat the experiment')
            print(f'PASS: manual cache flush changed OLD -> NEW before TTL expiry; elapsed={elapsed:.2f}s',flush=True)
        else:
            deadline=primed+ttl+12
            while time.monotonic()<deadline:
                ip,remaining=answer(cache_host,cache_port,name)
                elapsed=time.monotonic()-primed
                print(f'elapsed_since_priming={elapsed:.2f}s remaining_ttl={remaining}',flush=True)
                if ip==NEW:
                    if elapsed<ttl-2:raise RuntimeError('Answer changed before the cached TTL elapsed')
                    if args.mode=='cutover':
                        flush_system() # clear any additional macOS cache; underlying DNS cache has naturally expired
                        https(state,'new-after-expiry',NEW,'standby-mac3')
                    print(f'PASS: natural cached OLD -> NEW after expiry; elapsed={elapsed:.2f}s',flush=True)
                    break
                if ip!=OLD:raise RuntimeError('Unexpected third DNS answer')
                time.sleep(2)
            else:raise RuntimeError('Client cache did not refresh to NEW before deadline')
    finally:
        try:
            if altered:
                # Restore even if an earlier assertion failed. Allow password entry if
                # a longer-than-expected test outlasted the cached sudo credential.
                if before is None:run(['sudo','rm','-f',str(resolver)])
                else:run(['sudo','install','-m','644',str(state/'resolver.before'),str(resolver)])
                run(['sudo','dscacheutil','-flushcache'])
                run(['sudo','killall','-HUP','mDNSResponder'])
                print('RESTORED: previous macOS scoped DNS file',flush=True)
        finally:
            if daemon_pid is not None:
                command=subprocess.run(['ps','-ww','-p',str(daemon_pid),'-o','command='],capture_output=True,text=True).stdout
                if str(config) in command:run(['sudo','kill','-TERM',str(daemon_pid)])
            if process is not None and process.poll() is None:
                process.terminate()
                try:process.wait(timeout=4)
                except subprocess.TimeoutExpired:process.kill();process.wait()
            logfile.close()
            print('NEXT: restore the changed record on BOTH DNS Macs with dns-record.sh; verify both-up before another test.',flush=True)

if __name__=='__main__':
    try:main()
    except (Exception,KeyboardInterrupt) as error:
        print('FAIL:',error,file=sys.stderr);sys.exit(1)
