"""Verify a running local or deployed portfolio server; never writes model data."""
import argparse
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import HTTPError
from urllib.request import urlopen


def verify(base):
    def get(path, expected=200):
        try:
            response = urlopen(base.rstrip('/') + path, timeout=150)
        except HTTPError as exc:
            response = exc
        with response:
            body = response.read()
            assert response.status == expected, (path, response.status, body[:200])
            return body
    assert json.loads(get('/healthz'))['status'] == 'ok'
    home = get('/').decode()
    assert 'Atlas' in home and 'synthetic' in home
    assert 'Translate yield moves' in home and 'Credit Risk' in home
    bond = json.loads(get('/api/bond-risk?benchmark=0.05'))
    assert bond['price'] < 100 and bond['dv01'] > 0
    get('/api/bond-risk?years=1000000', 422)
    print('PASS default dashboard and bounded bond-risk endpoint', flush=True)
    first = json.loads(get('/api/report?mode=synthetic&cash_floor=900&frequency=4'))
    assert first['model']['config']['policy']['cash_floor'] == 900
    assert first['model']['frequency'] == 4
    second = json.loads(get('/api/report?mode=synthetic'))
    assert second['model']['config']['policy']['cash_floor'] != 900
    assert len(second['model']['joint_stress']['cells']) == 27
    print('PASS live recalculation, quarterly timing and visitor isolation', flush=True)
    public = json.loads(get('/api/report?mode=public&cash_access=0.5'))
    assert public['public_information']['assumptions']['cash_access'] == .5
    strict = json.loads(get('/api/report?mode=strict'))
    for result in (first, second, public, strict):
        assert result['evidence']['blocked']
        assert result['preferred_structure'] is None
        assert result['recommendation_status'] == 'Blocked — insufficient verified evidence.'
    assert 'model' not in strict and 'public_information' not in strict
    for mode in ('public', 'strict'):
        assert 'Company-specific recommendation' in get('/?mode=' + mode).decode()
    print('PASS public and strict modes preserve evidence gate', flush=True)
    get('/api/report?cash_floor=nan', 422)
    get('/api/report?mode=strict&cash_floor=1', 422)
    get('/data/historical.json', 404)
    print('PASS invalid inputs and private routes rejected', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url', nargs='?')
    parser.add_argument('--local', action='store_true', help='Start and stop a test server')
    args = parser.parse_args()
    if args.local:
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        root = Path(__file__).resolve().parents[1]
        process = subprocess.Popen([sys.executable, '-m', 'financing', 'data/historical.json',
                                    '--demo', '--host', '127.0.0.1', '--serve', str(port)], cwd=root)
        try:
            url = f'http://127.0.0.1:{port}'
            for _ in range(100):
                try:
                    with urlopen(url+'/healthz', timeout=1) as response:
                        assert response.status == 200
                    break
                except OSError:
                    if process.poll() is not None:
                        raise RuntimeError('Test server stopped during startup')
                    time.sleep(.1)
            verify(url)
        finally:
            process.terminate()
            process.wait(timeout=10)
    elif args.url:
        verify(args.url)
    else:
        parser.error('Supply a URL or --local')
