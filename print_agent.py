#!/usr/bin/env python3
"""
SUMO Print Agent v4.0 - Multi-Printer Edition
==============================================
Run this on a Mac at the restaurant, same network as the thermal printers.
Fetches printer config from the server per branch, then polls for new orders
and routes each bon to the correct printer by station.

Usage:
  python3 print_agent.py --branch 1              # Normal mode (sends to printers)
  python3 print_agent.py --branch 1 --test        # Test mode (shows output, no printer)
  python3 print_agent.py --branch 1 --test-once   # Fetch once, show output, exit

Printer: HSPOS HS-C830ULWB (80mm, ESC/POS, ISO-8859-8)
"""

import json
import os
import socket
import time
import sys
import argparse
import urllib.request
import urllib.error
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- CONFIG ---------------------------------------------------------
SERVER_URL = os.environ.get("PRINT_AGENT_SERVER", "https://cad2a536-a2eb-41a8-a0a3-6f4a608fee70-00-2gvg9dtirvl7z.picard.replit.dev")
PRINT_AGENT_KEY = os.environ.get("PRINT_AGENT_KEY", "sumo-print-2024-secure")
POLL_INTERVAL = 5
POLL_INTERVAL_SSE_ACTIVE = 30
SSE_RETRY_INTERVAL = 5
SSE_CONNECTED = False
_printed_ids_lock = threading.Lock()
_recently_printed_ids = {}
DEDUP_TTL = 120
# --------------------------------------------------------------------

parser = argparse.ArgumentParser(description='SUMO Print Agent v4.0')
parser.add_argument('--branch', type=int, required=True, help='Branch ID to fetch printers for')
parser.add_argument('--test', action='store_true', help='Test mode (no actual printing)')
parser.add_argument('--test-once', action='store_true', help='Fetch once, show output, exit')
args = parser.parse_args()

BRANCH_ID = args.branch
TEST_MODE = args.test or args.test_once
TEST_ONCE = args.test_once
FIRST_RUN = True

PRINTERS_CONFIG = {}
DEFAULT_PRINTER = None
STATION_MAP = {}

ESC = b'\x1b'
GS = b'\x1d'
INIT = ESC + b'@'
CUT_FULL = GS + b'V\x00'
ALIGN_LEFT = ESC + b'a\x00'
ALIGN_CENTER = ESC + b'a\x01'
ALIGN_RIGHT = ESC + b'a\x02'
FONT_NORMAL = ESC + b'!\x00'
FONT_DOUBLE_H = ESC + b'!\x10'
FONT_DOUBLE_W = ESC + b'!\x20'
FONT_DOUBLE = ESC + b'!\x30'
BOLD_ON = ESC + b'E\x01'
BOLD_OFF = ESC + b'E\x00'
UNDERLINE_ON = ESC + b'-\x01'
UNDERLINE_OFF = ESC + b'-\x00'
INVERT_ON = GS + b'B\x01'
INVERT_OFF = GS + b'B\x00'


def set_codepage(cp_num):
    return ESC + b't' + bytes([cp_num])


def encode_text(t, encoding='iso-8859-8'):
    try:
        return t.encode(encoding)
    except (UnicodeEncodeError, LookupError):
        safe = ''
        for ch in t:
            try:
                ch.encode(encoding)
                safe += ch
            except UnicodeEncodeError:
                safe += '?'
        return safe.encode(encoding, errors='replace')


class BonBuilder:
    def __init__(self, encoding='iso-8859-8', codepage_num=32, cut_feed_lines=6):
        self.buf = bytearray()
        self.preview_lines = []
        self._bold = False
        self._font = 'normal'
        self.encoding = encoding
        self.codepage_num = codepage_num
        self.cut_feed_lines = cut_feed_lines

    def _add(self, data):
        if isinstance(data, str):
            self.buf.extend(encode_text(data, self.encoding))
        else:
            self.buf.extend(data)

    def init(self):
        self._add(INIT)
        self._add(set_codepage(self.codepage_num))

    def cut(self):
        self._add(b'\n' * self.cut_feed_lines)
        self._add(CUT_FULL)
        if TEST_MODE:
            self.preview_lines.append('---CUT---')
            self.preview_lines.append('')

    def align(self, a):
        self._add({'center': ALIGN_CENTER, 'right': ALIGN_RIGHT}.get(a, ALIGN_LEFT))

    def font(self, s):
        self._add({'double': FONT_DOUBLE, 'double_h': FONT_DOUBLE_H, 'double_w': FONT_DOUBLE_W}.get(s, FONT_NORMAL))
        self._font = s

    def bold(self, on=True):
        self._add(BOLD_ON if on else BOLD_OFF)
        self._bold = on

    def invert(self, on=True):
        self._add(INVERT_ON if on else INVERT_OFF)

    def text(self, t):
        self._add(t + '\n')
        if TEST_MODE:
            mark = '** ' if self._bold else '   '
            self.preview_lines.append(f'{mark}{t}')

    def line(self, ch='-', w=42):
        self._add(ch * w + '\n')
        if TEST_MODE:
            self.preview_lines.append('   ' + ch * w)

    def dashed(self): self.line('-')
    def thick(self): self.line('=')
    def feed(self, n=1): self._add(b'\n' * n)

    def get_preview(self):
        return '\n'.join(self.preview_lines)


def build_checker(b, o):
    b.init()
    order_num = o['order_number']
    type_he = 'משלוח' if o['order_type'] == 'delivery' else 'איסוף עצמי'
    customer = o.get('customer_name', '')
    phone = o.get('customer_phone', '')
    created = o.get('created_at', '')

    b.align('right')
    b.font('normal')
    b.text(f'{phone}  :טלפון')
    b.text(f'SUMO')
    b.dashed()

    b.align('right')
    b.font('normal')
    b.bold()
    b.text(f'{customer} - הזמנה {order_num}')
    b.bold(False)
    b.text(created)
    b.feed(1)

    if o.get('customer_notes'):
        b.bold()
        b.text(f'הערות: {o["customer_notes"]}')
        b.bold(False)
    if o.get('delivery_notes'):
        b.bold()
        b.text(f'הערות משלוח: {o["delivery_notes"]}')
        b.bold(False)

    b.dashed()

    for item in o.get('items', []):
        name = item.get('print_name') or item.get('name_he') or item.get('item_name_he') or item.get('name', '')
        qty = item.get('qty') or item.get('quantity', 1)
        b.align('right')
        b.font('double_h')
        b.bold()
        b.text(f'{name} {qty}')
        b.bold(False)
        b.font('normal')
        for op in (item.get('options') or []):
            op_name = op.get('choice_name_he') or op.get('name', str(op)) if isinstance(op, dict) else str(op)
            b.text(f'{op_name}')
        for ex_ing in (item.get('excluded_ingredients') or []):
            b.bold()
            b.text(f'ללא {ex_ing}')
            b.bold(False)
        b.dashed()

    if o.get('delivery_address'):
        b.align('right')
        b.font('normal')
        addr = o['delivery_address']
        if o.get('delivery_city'):
            addr += f', {o["delivery_city"]}'
        b.text(f'כתובת: {addr}')
        b.dashed()

    b.feed(1)
    b.align('center')
    b.font('double')
    b.invert(True)
    b.text(f' SUMO - {order_num} ')
    b.invert(False)
    b.font('normal')

    b.feed(1)
    b.align('center')
    b.font('double')
    b.bold()
    b.text(f'*** {type_he} ***')
    b.bold(False)
    b.font('normal')

    b.feed(1)
    b.align('center')
    b.text(f'SUMO - {order_num}')
    b.text(phone)

    b.cut()


def build_payment(b, o):
    b.init()
    order_num = o['order_number']
    type_he = 'משלוח' if o['order_type'] == 'delivery' else 'איסוף עצמי'
    customer = o.get('customer_name', '')
    phone = o.get('customer_phone', '')

    b.align('right')
    b.font('normal')
    b.text(f'{phone}  :טלפון')
    b.text('SUMO - בון תשלום')
    b.dashed()

    b.align('right')
    b.bold()
    b.text(f'{customer} - הזמנה {order_num}')
    b.bold(False)
    b.text(f'{type_he} | {o.get("created_at", "")}')
    b.dashed()

    for item in o.get('items', []):
        name = item.get('print_name') or item.get('name_he') or item.get('item_name_he') or item.get('name', '')
        qty = item.get('qty') or item.get('quantity', 1)
        price = item.get('price') or item.get('unit_price', 0)
        total = qty * price
        b.align('right')
        b.bold()
        b.text(f'{total:.0f}  {name} {qty}')
        b.bold(False)

    b.dashed()
    b.align('right')
    b.text(f'{o["subtotal"]:.0f} :סכום')
    if o.get('delivery_fee', 0) > 0:
        b.text(f'{o["delivery_fee"]:.0f} :משלוח')
    if o.get('discount_amount', 0) > 0:
        b.text(f'{o["discount_amount"]:.0f}- :הנחה')
    b.thick()
    b.font('double')
    b.bold()
    b.text(f'{o["total_amount"]:.0f} :לתשלום')
    b.bold(False)
    b.font('normal')
    b.feed(1)
    b.align('center')
    b.text(f'תשלום: {o.get("payment_method", "-")}')
    b.text(time.strftime('%H:%M'))
    b.cut()


def build_station(b, o, station_name, station_items):
    b.init()
    order_num = o['order_number']
    type_he = 'משלוח' if o['order_type'] == 'delivery' else 'איסוף עצמי'

    b.align('center')
    b.font('double')
    b.bold()
    b.text(station_name)
    b.bold(False)
    b.font('normal')
    b.text(f'{order_num} | {o.get("created_at", "")}')
    b.dashed()

    if o.get('customer_notes'):
        b.align('right')
        b.bold()
        b.text(f'הערות: {o["customer_notes"]}')
        b.bold(False)

    for item in station_items:
        name = item.get('print_name') or item.get('name_he') or item.get('item_name_he') or item.get('name', '')
        qty = item.get('qty') or item.get('quantity', 1)
        b.align('right')
        b.font('double_h')
        b.bold()
        b.text(f'{name} {qty}')
        b.bold(False)
        b.font('normal')
        for op in (item.get('options') or []):
            op_name = op.get('choice_name_he') or op.get('name', str(op)) if isinstance(op, dict) else str(op)
            b.text(f'{op_name}')
        for ex_ing in (item.get('excluded_ingredients') or []):
            b.bold()
            b.text(f'ללא {ex_ing}')
            b.bold(False)

    b.dashed()
    b.align('center')
    b.font('double')
    b.bold()
    b.text(f'*** {type_he} ***')
    b.bold(False)
    b.font('normal')
    b.text(f'{order_num} | {station_name} | {time.strftime("%H:%M")}')
    b.cut()


def send_to_printer(data, ip, port):
    if TEST_MODE:
        print(f'  [SIM] Would send {len(data)} bytes to {ip}:{port}')
        return True
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((ip, port))
        s.sendall(bytes(data))
        s.close()
        return True
    except Exception as e:
        print(f'  [ERR] Printer error ({ip}:{port}): {e}')
        return False


def api_get(path):
    url = f'{SERVER_URL}{path}'
    req = urllib.request.Request(url, headers={'X-Print-Key': PRINT_AGENT_KEY})
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f'  [ERR] HTTP {e.code}: {e.read().decode("utf-8", errors="replace")[:200]}')
        return None
    except Exception as e:
        print(f'  [ERR] Connection: {e}')
        return None


def api_post(path, body):
    url = f'{SERVER_URL}{path}'
    data = json.dumps(body).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={
        'Content-Type': 'application/json',
        'X-Print-Key': PRINT_AGENT_KEY
    })
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f'  [ERR] Mark-printed: {e}')
        return None


def fetch_printer_config():
    global PRINTERS_CONFIG, DEFAULT_PRINTER, STATION_MAP
    data = api_get(f'/ops/api/branch/{BRANCH_ID}/printers')
    if not data or not data.get('ok'):
        print('[ERR] Failed to fetch printer config from server')
        return False

    PRINTERS_CONFIG = {p['id']: p for p in data.get('printers', [])}
    DEFAULT_PRINTER = data.get('default_printer')
    STATION_MAP = data.get('station_map', {})

    branch_name = data.get('branch_name', f'Branch {BRANCH_ID}')
    print(f'[OK] Branch: {branch_name}')
    print(f'[OK] Loaded {len(PRINTERS_CONFIG)} printer(s)')

    if DEFAULT_PRINTER:
        print(f'     Default: {DEFAULT_PRINTER["name"]} ({DEFAULT_PRINTER["ip_address"]}:{DEFAULT_PRINTER["port"]})')

    for st_name, pr in STATION_MAP.items():
        print(f'     Station "{st_name}" -> {pr["name"]} ({pr["ip_address"]})')

    if not DEFAULT_PRINTER and not STATION_MAP:
        print('[WARN] No printers configured -- orders will not print')

    return True


def get_printer_for_station(station_name):
    if station_name in STATION_MAP:
        return STATION_MAP[station_name]
    return DEFAULT_PRINTER


def print_order(order):
    if not DEFAULT_PRINTER and not STATION_MAP:
        print('  [ERR] No printers configured for this branch')
        return False

    all_ok = True
    dp = DEFAULT_PRINTER
    if dp:
        enc = dp.get('encoding', 'iso-8859-8')
        cp = dp.get('codepage_num', 32)
        cfl = dp.get('cut_feed_lines', 6)
        checker_copies = dp.get('checker_copies', 2)
        payment_copies = dp.get('payment_copies', 1)

        b = BonBuilder(encoding=enc, codepage_num=cp, cut_feed_lines=cfl)
        for _ in range(checker_copies):
            build_checker(b, order)
        for _ in range(payment_copies):
            build_payment(b, order)

        if TEST_MODE:
            print('\n' + '=' * 50)
            print(f'  BON PREVIEW -> {dp["name"]} ({dp["ip_address"]})')
            print('=' * 50)
            print(b.get_preview())
            print('=' * 50 + '\n')

        if not send_to_printer(b.buf, dp['ip_address'], dp['port']):
            all_ok = False

    if order.get('items_by_station'):
        printer_jobs = {}
        for st_name, st_items in order['items_by_station'].items():
            pr = get_printer_for_station(st_name)
            if not pr:
                print(f'  [WARN] No printer for station "{st_name}", items will not print')
                continue
            pr_key = (pr['ip_address'], pr['port'])
            if pr_key not in printer_jobs:
                printer_jobs[pr_key] = {'printer': pr, 'stations': {}}
            printer_jobs[pr_key]['stations'][st_name] = st_items

        for pr_key, job in printer_jobs.items():
            pr = job['printer']
            b_st = BonBuilder(encoding=pr.get('encoding', 'iso-8859-8'),
                              codepage_num=pr.get('codepage_num', 32),
                              cut_feed_lines=pr.get('cut_feed_lines', 6))

            for st_name, st_items in job['stations'].items():
                build_station(b_st, order, st_name, st_items)

            if TEST_MODE:
                print('\n' + '=' * 50)
                print(f'  STATION BON -> {pr["name"]} ({pr["ip_address"]})')
                print('=' * 50)
                print(b_st.get_preview())
                print('=' * 50 + '\n')

            if not send_to_printer(b_st.buf, pr['ip_address'], pr['port']):
                print(f'  [ERR] Station bon failed for {pr["name"]}')
                all_ok = False

    return all_ok


LOCAL_API_PORT = int(os.environ.get("PRINT_AGENT_PORT", 8899))


class PrintAgentAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *a):
        pass

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path == '/status':
            self._json(200, {
                'ok': True,
                'agent': 'SUMO Print Agent v4.0',
                'branch_id': BRANCH_ID,
                'printers': list(PRINTERS_CONFIG.values()),
                'default_printer': DEFAULT_PRINTER,
                'station_map': STATION_MAP,
            })
        elif self.path == '/test-all':
            results = []
            for pid, pr in PRINTERS_CONFIG.items():
                ip = pr['ip_address']
                port = pr['port']
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(3)
                    s.connect((ip, port))
                    s.close()
                    results.append({'id': int(pid), 'name': pr['name'], 'ip': ip, 'port': port, 'status': 'connected'})
                except socket.timeout:
                    results.append({'id': int(pid), 'name': pr['name'], 'ip': ip, 'port': port, 'status': 'timeout'})
                except ConnectionRefusedError:
                    results.append({'id': int(pid), 'name': pr['name'], 'ip': ip, 'port': port, 'status': 'refused'})
                except Exception as e:
                    results.append({'id': int(pid), 'name': pr['name'], 'ip': ip, 'port': port, 'status': 'error', 'error': str(e)})
            self._json(200, {'ok': True, 'results': results})
        elif self.path.startswith('/test/'):
            pid = self.path.split('/test/')[-1]
            pr = PRINTERS_CONFIG.get(pid) or PRINTERS_CONFIG.get(int(pid)) if pid.isdigit() else None
            if not pr:
                self._json(404, {'ok': False, 'error': 'Printer not found'})
                return
            ip = pr['ip_address']
            port = pr['port']
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((ip, port))
                s.close()
                self._json(200, {'ok': True, 'status': 'connected', 'name': pr['name']})
            except socket.timeout:
                self._json(200, {'ok': True, 'status': 'timeout', 'name': pr['name']})
            except ConnectionRefusedError:
                self._json(200, {'ok': True, 'status': 'refused', 'name': pr['name']})
            except Exception as e:
                self._json(200, {'ok': True, 'status': 'error', 'name': pr['name'], 'error': str(e)})
        else:
            self._json(404, {'ok': False, 'error': 'Not found'})


def start_local_api():
    server = HTTPServer(('0.0.0.0', LOCAL_API_PORT), PrintAgentAPIHandler)
    print(f'[API] Local API server on port {LOCAL_API_PORT}')
    print(f'[API] Test from iPad/phone: http://<mac-ip>:{LOCAL_API_PORT}/test-all')
    server.serve_forever()


def _is_recently_printed(order_id):
    now = time.time()
    with _printed_ids_lock:
        expired = [k for k, t in _recently_printed_ids.items() if now - t > DEDUP_TTL]
        for k in expired:
            del _recently_printed_ids[k]
        return order_id in _recently_printed_ids


def _mark_recently_printed(order_id):
    with _printed_ids_lock:
        _recently_printed_ids[order_id] = time.time()


def _process_sse_order(order):
    print_job_id = order.get('print_job_id')
    dedup_key = f'sse_{print_job_id}' if print_job_id else f'sse_{order.get("id")}'
    if _is_recently_printed(dedup_key):
        print(f'  [SSE] Print job for order #{order.get("order_number", "?")} already processed, skipping')
        return

    num = order.get('order_number', '?')
    name = order.get('customer_name', '')
    total = order.get('total_amount', 0)
    otype = order.get('order_type', '')
    items_count = len(order.get('items', []))
    print(f'  [SSE] >> #{num} | {name} | {otype} | {items_count} items | {total:.0f} NIS')

    if TEST_MODE:
        for item in order.get('items', []):
            iname = item.get('print_name') or item.get('name_he') or item.get('item_name_he') or item.get('name', '?')
            iqty = item.get('qty') or item.get('quantity', 1)
            print(f'     {iqty}x {iname}')

    order_id = order.get('id')
    if print_order(order):
        print(f'     [OK] Printed (instant via SSE)')
        _mark_recently_printed(dedup_key)
        _mark_recently_printed(f'poll_{order_id}')
        if TEST_MODE:
            print(f'  [TEST] Would mark order {order_id} as printed')
        else:
            api_post('/ops/api/orders/mark-printed', {'order_ids': [order_id]})
    else:
        print(f'     [FAIL] Print failed (will retry via polling)')


def sse_listener():
    global SSE_CONNECTED
    url = f'{SERVER_URL}/ops/api/orders/stream?branch_id={BRANCH_ID}'
    headers = {'X-Print-Key': PRINT_AGENT_KEY, 'Accept': 'text/event-stream'}

    while True:
        try:
            req = urllib.request.Request(url, headers=headers)
            resp = urllib.request.urlopen(req, timeout=60)
            SSE_CONNECTED = True
            print('[SSE] Connected to event stream')
            buf = ''
            while True:
                chunk = resp.read(1)
                if not chunk:
                    break
                buf += chunk.decode('utf-8', errors='replace')
                while '\n\n' in buf:
                    msg, buf = buf.split('\n\n', 1)
                    for line in msg.split('\n'):
                        if line.startswith('data: '):
                            data_str = line[6:]
                            try:
                                event = json.loads(data_str)
                                event_type = event.get('type', '')
                                if event_type == 'connected':
                                    print('[SSE] Stream ready — listening for print jobs')
                                elif event_type == 'new_print_job':
                                    print(f'[SSE] Received print job for order #{event.get("order_number", "?")}')
                                    _process_sse_order(event)
                            except json.JSONDecodeError:
                                pass
        except Exception as e:
            SSE_CONNECTED = False
            print(f'[SSE] Disconnected: {e} — retrying in {SSE_RETRY_INTERVAL}s (polling fallback active)')
        SSE_CONNECTED = False
        time.sleep(SSE_RETRY_INTERVAL)


def main():
    global FIRST_RUN
    mode_str = 'TEST MODE' if TEST_MODE else 'LIVE MODE'
    print('+----------------------------------------------+')
    print(f'|   SUMO Print Agent v4.0  ({mode_str})')
    print('+----------------------------------------------+')
    print(f'| Server:  {SERVER_URL[:42]}')
    print(f'| Branch:  {BRANCH_ID}')
    print(f'| Poll:    every {POLL_INTERVAL}s (fallback)')
    print(f'| SSE:     enabled (primary channel)')
    print('+----------------------------------------------+')
    print()

    if SERVER_URL == "https://your-app.replit.app":
        print('[ERR] Please edit SERVER_URL in the script!')
        sys.exit(1)

    print('[...] Fetching printer config from server...')
    if not fetch_printer_config():
        print('[ERR] Cannot start without printer config. Check server URL and branch ID.')
        sys.exit(1)

    api_thread = threading.Thread(target=start_local_api, daemon=True)
    api_thread.start()

    if not TEST_ONCE:
        sse_thread = threading.Thread(target=sse_listener, daemon=True)
        sse_thread.start()
        print('[SSE] Started SSE listener thread')

    print()
    print('[OK] Watching for new orders...\n')

    while True:
        try:
            current_poll = POLL_INTERVAL_SSE_ACTIVE if SSE_CONNECTED else POLL_INTERVAL

            data = api_get(f'/ops/api/orders/unprinted?branch_id={BRANCH_ID}')
            if data and data.get('ok'):
                orders = data.get('orders', [])
                if orders:
                    if FIRST_RUN and not TEST_MODE:
                        print(f'[SKIP] First run: {len(orders)} old order(s) found, marking as printed')
                        old_ids = [o['id'] for o in orders]
                        api_post('/ops/api/orders/mark-printed', {'order_ids': old_ids})
                        for oid in old_ids:
                            _mark_recently_printed(f'poll_{oid}')
                        print(f'[OK] Marked {len(old_ids)} old order(s). Only NEW orders will print.\n')
                        FIRST_RUN = False
                        time.sleep(current_poll)
                        continue

                    FIRST_RUN = False
                    prefix = '[POLL/backup]' if SSE_CONNECTED else '[POLL]'
                    printed_ids = []
                    for order in orders:
                        if _is_recently_printed(f'poll_{order["id"]}'):
                            continue
                        num = order['order_number']
                        name = order['customer_name']
                        total = order.get('total_amount', 0)
                        otype = order.get('order_type', '')
                        items_count = len(order.get('items', []))
                        print(f'  {prefix} >> #{num} | {name} | {otype} | {items_count} items | {total:.0f} NIS')

                        if TEST_MODE:
                            for item in order.get('items', []):
                                iname = item.get('print_name') or item.get('name_he') or item.get('item_name_he') or item.get('name', '?')
                                iqty = item.get('qty') or item.get('quantity', 1)
                                print(f'     {iqty}x {iname}')

                        if print_order(order):
                            print(f'     [OK] Printed')
                            _mark_recently_printed(f'poll_{order["id"]}')
                            printed_ids.append(order['id'])
                        else:
                            print(f'     [FAIL] Print failed')

                    if printed_ids:
                        if TEST_MODE:
                            print(f'\n  [TEST] Would mark {len(printed_ids)} order(s) as printed')
                        else:
                            api_post('/ops/api/orders/mark-printed', {'order_ids': printed_ids})
                            print(f'  [OK] Marked {len(printed_ids)} order(s) as printed\n')
                else:
                    FIRST_RUN = False
            elif data:
                print(f'  [WARN] Server: {data}')
            else:
                print(f'  [WARN] No response from server')

            if TEST_ONCE:
                print('\n[DONE] Test complete!')
                break

        except KeyboardInterrupt:
            print('\n[EXIT] Shutting down...')
            break
        except Exception as e:
            print(f'  [ERR] {e}')

        time.sleep(current_poll)


if __name__ == '__main__':
    main()
