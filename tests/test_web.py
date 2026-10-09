"""Public hosting boundaries, real worker lifecycle and evidence isolation."""
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import threading
import time
import unittest
from unittest.mock import patch

from financing.web import Application, calculate_request, isolated_calculation, validate_query
from financing.policy import BLOCKED

ROOT = Path(__file__).resolve().parents[1]
OPTIONS = {'case': str(ROOT / 'data/historical.json'), 'quick': True}


def slow_worker(pipe, *args):
    time.sleep(5)


def request(app, query='', path='/api/report', method='GET', **env):
    result = {}
    def start(status, headers):
        result.update(status=int(status.split()[0]), headers=dict(headers))
    result['body'] = b''.join(app({'PATH_INFO': path, 'REQUEST_METHOD': method,
                                 'QUERY_STRING': query, **env}, start))
    return result


class HostingTests(unittest.TestCase):
    def test_render_port_and_explicit_local_binding(self):
        from financing.cli import main
        with patch.dict(os.environ, {'PORT': '8123'}), patch('financing.web.serve') as server:
            self.assertEqual(main(['--demo', '--serve']), 0)
            self.assertEqual(server.call_args.args[0].serve, 8123)
            self.assertEqual(server.call_args.args[0].host, '0.0.0.0')
            main(['--demo', '--serve', '8765', '--host', '127.0.0.1'])
            self.assertEqual(server.call_args.args[0].host, '127.0.0.1')
            self.assertEqual(server.call_args.args[0].serve, 8765)

    def test_validation_before_computation(self):
        calls = []
        app = Application(OPTIONS, lambda *args: calls.append(args))
        for q in ('mode=bad', 'mode=strict&cash_floor=1', 'cash_floor=nan',
                  'cash_floor=inf', 'cash_floor=-1', 'cash_floor=1&cash_floor=2',
                  'frequency=999999', 'mode=public&frequency=4', 'mode=public&refinance=yes',
                  'mode=public&growth_dks=1,2', 'mode=public&growth_dks=nan',
                  'case=/etc/passwd', 'mode=', 'cash_floor=100000000', 'fee_convention=bad'):
            with self.subTest(query=q):
                self.assertEqual(request(app, q)['status'], 422)
        self.assertEqual(request(app, 'x=' + 'a'*4096)['status'], 414)
        self.assertEqual(request(app, method='POST')['status'], 405)
        self.assertEqual(request(app, CONTENT_LENGTH='5')['status'], 413)
        self.assertEqual(request(app, path='/data/historical.json')['status'], 404)
        self.assertEqual(request(app, path='/healthz')['status'], 200)
        self.assertEqual(request(app, method='HEAD', path='/')['body'], b'')
        self.assertEqual(calls, [])

    def test_busy_requests_do_not_queue_and_health_works(self):
        entered, release = threading.Event(), threading.Event()
        def runner(*args):
            entered.set()
            release.wait(3)
            return 200, b'{}'
        app = Application(OPTIONS, runner)
        thread = threading.Thread(target=lambda: request(app))
        thread.start()
        try:
            self.assertTrue(entered.wait(2))
            r = request(app)
            self.assertEqual(r['status'], 503)
            self.assertEqual(r['headers']['Retry-After'], '5')
            self.assertEqual(request(app, path='/healthz')['status'], 200)
        finally:
            release.set()
            thread.join()
        self.assertEqual(request(app)['status'], 200)

    def test_worker_timeout_terminates_and_next_request_succeeds(self):
        before = {p.pid for p in mp.active_children()}
        status, body = isolated_calculation(OPTIONS, validate_query('mode=strict'), True,
                                          timeout=.05, worker=slow_worker)
        self.assertEqual(status, 503)
        self.assertEqual({p.pid for p in mp.active_children()}, before)
        status, body = isolated_calculation(OPTIONS, validate_query('mode=strict'), True)
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)['recommendation_status'], BLOCKED)

    def test_no_shared_state_or_source_writes_and_gate_preserved(self):
        files = [p for p in (ROOT/'data').rglob('*') if p.is_file()]
        before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        first = json.loads(calculate_request(OPTIONS, validate_query('cash_floor=900'), True))
        second = json.loads(calculate_request(OPTIONS, validate_query(''), True))
        self.assertEqual(first['model']['config']['policy']['cash_floor'], 900)
        self.assertNotEqual(second['model']['config']['policy']['cash_floor'], 900)
        for r in (first, second):
            self.assertEqual(r['recommendation_status'], BLOCKED)
            self.assertIsNone(r['preferred_structure'])
        self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in files})

    def test_public_requests_remain_conditional_and_no_database_selected(self):
        from financing.cli import evaluate
        with patch('financing.cli.evaluate', wraps=evaluate) as call:
            report = json.loads(calculate_request(OPTIONS, validate_query('mode=public&cash_access=0.5'), True))
        self.assertIsNone(call.call_args.args[3])
        self.assertEqual(report['public_information']['assumptions']['cash_access'], .5)
        self.assertEqual(report['recommendation_status'], BLOCKED)
        self.assertIsNone(report['preferred_structure'])

    def test_unexpected_errors_hide_internal_paths(self):
        def broken(*args):
            raise RuntimeError('/private/path')
        with self.assertLogs(level='ERROR'):
            r = request(Application(OPTIONS, broken))
        self.assertEqual(r['status'], 500)
        self.assertNotIn(b'/private/path', r['body'])
        self.assertIn("frame-ancestors 'none'", r['headers']['Content-Security-Policy'])


if __name__ == '__main__':
    unittest.main()
