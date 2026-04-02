#!/usr/bin/env python3
"""
SUMO Print Agent v3.0
=====================
Run this on a Mac at the restaurant, same network as the thermal printer.
Polls the server for new orders and prints them automatically.

Usage:
  python3 print_agent.py              # Normal mode (sends to printer)
  python3 print_agent.py --test       # Test mode (shows output, no printer)
  python3 print_agent.py --test-once  # Fetch once, show output, exit

Printer: HSPOS HS-C830ULWB (80mm, ESC/POS, ISO-8859-8)
"""

import json
import socket
import time
import sys
import urllib.request
import urllib.error

# --- CONFIG ---------------------------------------------------------
SERVER_URL = "https://cad2a536-a2eb-41a8-a0a3-6f4a608fee70-00-2gvg9dtirvl7z.picard.replit.dev"
PRINT_AGENT_KEY = "sumo-print-2024-secure"
PRINTER_IP = "10.100.10.10"
PRINTER_PORT = 9100
POLL_INTERVAL = 5
CHECKER_COPIES = 2
PAYMENT_COPIES = 1
STATION_BONS = True
CUT_FEED_LINES = 6
ENCODING = 'iso-8859-8'
CODEPAGE_NUM = 32
# --------------------------------------------------------------------

TEST_MODE = '--test' in sys.argv or '--test-once' in sys.argv
TEST_ONCE = '--test-once' in sys.argv
FIRST_RUN = True

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


def set_codepage():
    return ESC + b't' + bytes([CODEPAGE_NUM])


def encode_text(t):
    try:
        return t.encode(ENCODING)
    except (UnicodeEncodeError, LookupError):
        safe = ''
        for ch in t:
            try:
                ch.encode(ENCODING)
                safe += ch
            except UnicodeEncodeError:
                safe += '?'
        return safe.encode(ENCODING, errors='replace')


class BonBuilder:
    def __init__(self):
        self.buf = bytearray()
        self.preview_lines = []
        self._bold = False
        self._font = 'normal'

    def _add(self, data):
        if isinstance(data, str):
            self.buf.extend(encode_text(data))
        else:
            self.buf.extend(data)

    def init(self):
        self._add(INIT)
        self._add(set_codepage())

    def cut(self):
        self._add(b'\n' * CUT_FEED_LINES)
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
        name = item.get('name_he') or item.get('item_name_he') or item.get('name', '')
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
        name = item.get('name_he') or item.get('item_name_he') or item.get('name', '')
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
        name = item.get('name_he') or item.get('item_name_he') or item.get('name', '')
        qty = item.get('qty') or item.get('quantity', 1)
        b.align('right')
        b.font('double_h')
        b.bold()
        b.text(f'{name} {qty}')
        b.bold(False)
        b.font('normal')

    b.dashed()
    b.align('center')
    b.font('double')
    b.bold()
    b.text(f'*** {type_he} ***')
    b.bold(False)
    b.font('normal')
    b.text(f'{order_num} | {station_name} | {time.strftime("%H:%M")}')
    b.cut()


def send_to_printer(data):
    if TEST_MODE:
        print(f'  [SIM] Would send {len(data)} bytes to {PRINTER_IP}:{PRINTER_PORT}')
        return True
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((PRINTER_IP, PRINTER_PORT))
        s.sendall(bytes(data))
        s.close()
        return True
    except Exception as e:
        print(f'  [ERR] Printer error: {e}')
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


def print_order(order):
    b = BonBuilder()

    for _ in range(CHECKER_COPIES):
        build_checker(b, order)

    for _ in range(PAYMENT_COPIES):
        build_payment(b, order)

    if STATION_BONS and order.get('items_by_station'):
        for st_name, st_items in order['items_by_station'].items():
            build_station(b, order, st_name, st_items)

    if TEST_MODE:
        print('\n' + '=' * 50)
        print('  BON PREVIEW')
        print('=' * 50)
        print(b.get_preview())
        print('=' * 50 + '\n')

    return send_to_printer(b.buf)


def main():
    global FIRST_RUN
    mode_str = 'TEST MODE' if TEST_MODE else 'LIVE MODE'
    print('+----------------------------------------------+')
    print(f'|   SUMO Print Agent v3.0  ({mode_str})')
    print('+----------------------------------------------+')
    print(f'| Server:  {SERVER_URL[:42]}')
    if not TEST_MODE:
        print(f'| Printer: {PRINTER_IP}:{PRINTER_PORT}')
    else:
        print(f'| Printer: SIMULATED')
    print(f'| Poll:    every {POLL_INTERVAL}s')
    print(f'| Encoding: {ENCODING} (codepage {CODEPAGE_NUM})')
    print('+----------------------------------------------+')
    print()

    if SERVER_URL == "https://your-app.replit.app":
        print('[ERR] Please edit SERVER_URL in the script!')
        sys.exit(1)

    print('[OK] Watching for new orders...\n')

    while True:
        try:
            data = api_get('/ops/api/orders/unprinted')
            if data and data.get('ok'):
                orders = data.get('orders', [])
                if orders:
                    if FIRST_RUN and not TEST_MODE:
                        print(f'[SKIP] First run: {len(orders)} old order(s) found, marking as printed')
                        old_ids = [o['id'] for o in orders]
                        api_post('/ops/api/orders/mark-printed', {'order_ids': old_ids})
                        print(f'[OK] Marked {len(old_ids)} old order(s). Only NEW orders will print.\n')
                        FIRST_RUN = False
                        time.sleep(POLL_INTERVAL)
                        continue

                    FIRST_RUN = False
                    print(f'[NEW] {len(orders)} new order(s)')
                    printed_ids = []
                    for order in orders:
                        num = order['order_number']
                        name = order['customer_name']
                        total = order.get('total_amount', 0)
                        otype = order.get('order_type', '')
                        items_count = len(order.get('items', []))
                        print(f'  >> #{num} | {name} | {otype} | {items_count} items | {total:.0f} NIS')

                        if TEST_MODE:
                            for item in order.get('items', []):
                                iname = item.get('name_he') or item.get('item_name_he') or item.get('name', '?')
                                iqty = item.get('qty') or item.get('quantity', 1)
                                print(f'     {iqty}x {iname}')

                        if print_order(order):
                            print(f'     [OK] Printed')
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

        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    main()
