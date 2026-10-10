"""Read-only portfolio HTTP boundary; financial/evidence logic stays in evaluate."""
import json
import logging
import math
import multiprocessing as mp
from pathlib import Path
from threading import BoundedSemaphore
from urllib.parse import parse_qs

from .policy import BLOCKED

MAX_QUERY = 4096
TIMEOUT = 120
LIMITS = {
    'cash_floor': (0, 10000), 'max_leverage': (0, 20),
    'min_coverage': (0, 50), 'cash_access': (0, 1),
    'operating_cash_access': (0, 1), 'dividend_factor': (0, 3),
    'synergy': (0, 2000), 'benchmark': (0, .30), 'spread': (0, .30),
    'gross_annual_capex_dks': (0, 5000), 'gross_annual_capex_fl': (0, 5000),
    'variable_cost_share_dks': (0, 1), 'variable_cost_share_fl': (0, 1),
}
SYNTHETIC = {'cash_floor', 'max_leverage', 'min_coverage', 'fee_convention', 'frequency'}
PUBLIC = set(LIMITS) | {'growth_dks', 'growth_fl', 'refinance', 'fee_convention', 'frequency'}


def validate_query(raw, default_mode='synthetic', frequency=1):
    if len(raw.encode('utf-8')) > MAX_QUERY:
        raise ValueError('Request query exceeds 4096 bytes')
    q = parse_qs(raw, keep_blank_values=True, max_num_fields=24)
    if any(len(v) != 1 or not v[0] for v in q.values()):
        raise ValueError('Each input must have one nonempty value')
    mode = q.get('mode', [default_mode])[0]
    if mode not in ('synthetic', 'public', 'strict'):
        raise ValueError('Unknown analysis mode')
    allowed = SYNTHETIC if mode == 'synthetic' else PUBLIC if mode == 'public' else set()
    if set(q) - allowed - {'mode'}:
        raise ValueError('Unsupported input for this analysis mode')
    for key in set(q) & set(LIMITS):
        value = float(q[key][0])
        low, high = LIMITS[key]
        if not math.isfinite(value) or not low <= value <= high:
            raise ValueError(f'{key} must be finite and between {low} and {high}')
    for key in ('growth_dks', 'growth_fl'):
        if key in q:
            xs = q[key][0].split(',')
            if len(xs) not in (1, 5):
                raise ValueError('Growth needs one or five annual fractions')
            if any(not math.isfinite(float(x)) or not -.5 <= float(x) <= .5 for x in xs):
                raise ValueError('Hosted growth inputs must be between -0.5 and 0.5')
    if 'refinance' in q and q['refinance'][0] not in ('true', 'false'):
        raise ValueError('Refinance must be true or false')
    if 'fee_convention' in q and q['fee_convention'][0] not in ('fixed_budget', 'issued_debt'):
        raise ValueError('Invalid fee convention')
    f = q.get('frequency', [str(frequency if mode == 'synthetic' else 1)])[0]
    if f not in ('1', '4') or (mode != 'synthetic' and f != '1'):
        raise ValueError('Only synthetic mode supports quarterly timing')
    q['mode'], q['frequency'] = [mode], [f]
    return q


def error_payload(message):
    return json.dumps({'error': message, 'recommendation_status': BLOCKED}).encode()


def calculate_request(options, query, api):
    from .cli import evaluate
    from .exports import dashboard
    from .public_inputs import form_overrides
    mode = query['mode'][0]
    public = dict(options.get('public_choices') or {})
    if mode == 'public':
        public.update(form_overrides(query))
    overrides = {k: float(query[k][0]) for k in ('cash_floor', 'max_leverage', 'min_coverage') if k in query} if mode == 'synthetic' else None
    # No request can select paths, mutate facts, or write shared SQLite/output files.
    _, report = evaluate(options.get('case'), options.get('illustration'),
                         mode == 'synthetic', None, not options.get('quick', False),
                         overrides, mode == 'public', public,
                         int(query['frequency'][0]),
                         query.get('fee_convention', [options.get('fee_convention')])[0])
    return (json.dumps(report, ensure_ascii=False, allow_nan=False) if api else dashboard(report)).encode('utf-8')


def _worker(pipe, options, query, api):
    try:
        pipe.send((200, calculate_request(options, query, api)))
    except (ValueError, KeyError, TypeError):
        pipe.send((422, error_payload('These assumptions could not be evaluated. Check the input ranges.')))
    except Exception:
        logging.exception('Calculation failed')
        pipe.send((500, error_payload('Calculation unavailable. Please retry later.')))
    finally:
        pipe.close()


def isolated_calculation(options, query, api, timeout=TIMEOUT, worker=_worker):
    """Terminate overdue work, rather than letting a timed-out thread keep running."""
    ctx = mp.get_context('spawn')
    receiver, sender = ctx.Pipe(duplex=False)
    process = ctx.Process(target=worker, args=(sender, options, query, api), daemon=True)
    try:
        process.start()
        sender.close()
        if not receiver.poll(timeout):
            return 503, error_payload('Calculation time limit reached. Try a simpler scenario later.')
        try:
            return receiver.recv()
        except EOFError:
            return 503, error_payload('Calculation worker stopped. Please retry later.')
    finally:
        if process.pid is not None:
            process.join(.1)
            if process.is_alive():
                process.terminate()
                process.join(2)
            if process.is_alive():
                process.kill()
                process.join()
            process.close()
        sender.close()
        receiver.close()


class Application:
    def __init__(self, options, runner=isolated_calculation):
        self.options = dict(options)
        self.runner = runner
        self.slot = BoundedSemaphore(1)

    def __call__(self, env, start_response):
        status, body, kind = 200, b'', 'application/json'
        method, path = env.get('REQUEST_METHOD'), env.get('PATH_INFO', '/')
        try:
            if method not in ('GET', 'HEAD'):
                status, body = 405, error_payload('Only GET and HEAD are supported')
            elif env.get('CONTENT_LENGTH', '') not in ('', '0') or env.get('HTTP_TRANSFER_ENCODING'):
                status, body = 413, error_payload('Request bodies are not accepted')
            elif len(env.get('QUERY_STRING', '').encode()) > MAX_QUERY:
                status, body = 414, error_payload('Request query too long')
            elif path == '/healthz':
                body = b'{"status":"ok"}'
            elif path == '/api/bond-risk':
                from .markets import from_query
                body = json.dumps(from_query(env.get('QUERY_STRING', '')), allow_nan=False).encode()
            elif path not in ('/', '/api/report'):
                status, body = 404, error_payload('Not found')
            else:
                query = validate_query(env.get('QUERY_STRING', ''), self.options.get('mode', 'synthetic'), self.options.get('frequency', 1))
                if method == 'HEAD':
                    kind = 'text/html' if path == '/' else kind
                elif not self.slot.acquire(blocking=False):
                    status, body = 503, error_payload('The simulator is busy. Please retry shortly.')
                else:
                    try:
                        status, body = self.runner(self.options, query, path == '/api/report')
                        if status == 200 and path == '/':
                            kind = 'text/html'
                    finally:
                        self.slot.release()
        except ValueError as exc:
            status, body = 422, error_payload(str(exc))
        except Exception:
            logging.exception('Request failed')
            status, body = 500, error_payload('Service unavailable. Please retry later.')
        from http import HTTPStatus
        headers = [('Content-Type', kind + '; charset=utf-8'), ('Content-Length', str(len(body))),
                   ('Cache-Control', 'no-store'), ('X-Content-Type-Options', 'nosniff'),
                   ('X-Frame-Options', 'DENY'), ('Referrer-Policy', 'no-referrer'),
                   ('Content-Security-Policy', "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")]
        if status == 503:
            headers.append(('Retry-After', '5'))
        if status == 405:
            headers.append(('Allow', 'GET, HEAD'))
        start_response(f'{status} {HTTPStatus(status).phrase}', headers)
        return [b'' if method == 'HEAD' else body]


def serve(args):
    from .cli import read_case
    if not 1 <= args.serve <= 65535:
        raise ValueError('Port must be between 1 and 65535')
    if args.database or args.output:
        raise ValueError('Web mode does not write databases or output folders; use the CLI for saved runs')
    options = dict(case=str(args.case.resolve()) if args.case else None,
                   illustration=str(args.illustrative_inputs.resolve()) if args.illustrative_inputs else None,
                   public_choices=read_case(args.public_assumptions) if args.public_assumptions else {},
                   quick=args.quick, frequency=args.frequency, fee_convention=args.fee_convention,
                   mode='public' if args.public_information else 'synthetic' if args.demo else 'strict')
    if args.case:
        read_case(args.case)  # Fail startup clearly if the deployed case is unavailable.
    app = Application(options)
    print(f'Live evidence dashboard: http://{args.host}:{args.serve}', flush=True)
    try:
        from waitress import serve as run_server
    except ImportError:
        if args.host not in ('127.0.0.1', 'localhost', '::1'):
            raise RuntimeError('Public hosting requires pip install ".[web]"')
        from wsgiref.simple_server import make_server
        with make_server(args.host, args.serve, app) as server:
            server.serve_forever()
    else:
        run_server(app, host=args.host, port=args.serve, threads=4,
                   connection_limit=32, backlog=32, channel_timeout=150,
                   max_request_header_size=16384, max_request_body_size=4096,
                   expose_tracebacks=False)
