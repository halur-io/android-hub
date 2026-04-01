#!/usr/bin/env python3
"""
SUMO Print Agent
================
Run this script on a computer at the restaurant (Mac/PC) that is on the
same network as the thermal printer. It polls the cloud server for new
orders and prints them automatically.

Setup:
  1. Install Python 3 on the Mac
  2. Copy this file to the Mac
  3. Edit the CONFIG section below
  4. Run:  python3 print_agent.py

The script will run continuously, checking for new orders every few seconds.
"""

import json
import socket
import time
import sys
import urllib.request
import urllib.error

# ─── CONFIG ─────────────────────────────────────────────────────────
SERVER_URL = "https://your-app.replit.app"   # Your deployed site URL
PRINT_AGENT_KEY = "sumo-print-2024-secure"   # Must match PRINT_AGENT_KEY env var on server
PRINTER_IP = "10.100.10.10"                  # Thermal printer IP on local network
PRINTER_PORT = 9100                          # Default ESC/POS port
POLL_INTERVAL = 5                            # Seconds between checks
CHECKER_COPIES = 2                           # Checker bon copies
PAYMENT_COPIES = 1                           # Payment bon copies
STATION_BONS = True                          # Print station bons (kitchen, bar, etc.)
# ────────────────────────────────────────────────────────────────────

ESC = b'\x1b'
GS = b'\x1d'
INIT = ESC + b'@'
CUT_FULL = GS + b'V\x00'
ALIGN_LEFT = ESC + b'a\x00'
ALIGN_CENTER = ESC + b'a\x01'
ALIGN_RIGHT = ESC + b'a\x02'
FONT_NORMAL = ESC + b'!\x00'
FONT_DOUBLE_H = ESC + b'!\x10'
FONT_DOUBLE = ESC + b'!\x30'
BOLD_ON = ESC + b'E\x01'
BOLD_OFF = ESC + b'E\x00'


class BonBuilder:
    def __init__(self):
        self.buf = bytearray()

    def _add(self, data):
        if isinstance(data, str):
            self.buf.extend(data.encode('utf-8'))
        else:
            self.buf.extend(data)

    def init(self): self._add(INIT)
    def cut(self): self._add(b'\n\n\n'); self._add(CUT_FULL)
    def align(self, a): self._add({'center': ALIGN_CENTER, 'right': ALIGN_RIGHT}.get(a, ALIGN_LEFT))
    def font(self, s): self._add({'double': FONT_DOUBLE, 'double_h': FONT_DOUBLE_H}.get(s, FONT_NORMAL))
    def bold(self, on=True): self._add(BOLD_ON if on else BOLD_OFF)
    def text(self, t): self._add(t + '\n')
    def line(self, ch='-', w=32): self._add(ch * w + '\n')
    def dashed(self): self.line('-')
    def thick(self): self.line('=')


def build_checker(b, o):
    b.init()
    b.align('center')
    b.font('double')
    b.text('SUMO')
    b.font('double_h')
    type_he = 'משלוח' if o['order_type'] == 'delivery' else 'איסוף עצמי'
    b.text(type_he)
    b.font('double')
    b.text(f'#{o["order_number"]}')
    b.font('normal')
    b.text(o.get('created_at', ''))
    b.thick()
    b.align('right')

    if o.get('customer_notes'):
        b.bold(); b.text(f'⚠ {o["customer_notes"]}'); b.bold(False)
    if o.get('delivery_notes'):
        b.bold(); b.text(f'🚗 {o["delivery_notes"]}'); b.bold(False)

    b.font('double_h')
    b.bold(); b.text(o.get('customer_name', '')); b.font('normal')
    b.text(o.get('customer_phone', ''))
    if o.get('delivery_address'):
        addr = o['delivery_address']
        if o.get('delivery_city'): addr += f', {o["delivery_city"]}'
        b.text(addr)
    b.bold(False)
    b.dashed()

    for item in o.get('items', []):
        name = item.get('name_he') or item.get('item_name_he') or item.get('name', '')
        qty = item.get('qty') or item.get('quantity', 1)
        b.bold(); b.text(f'{qty}× {name}'); b.bold(False)
        for op in (item.get('options') or []):
            op_name = op.get('choice_name_he') or op.get('name', str(op)) if isinstance(op, dict) else str(op)
            b.text(f'  + {op_name}')

    b.thick()
    b.align('right')
    b.font('double')
    b.bold(); b.text(f'סה"כ: ₪{o["total_amount"]:.0f}'); b.bold(False)
    b.font('normal')
    b.align('center')
    b.text(f'צ׳קר | {time.strftime("%H:%M")}')
    b.cut()


def build_payment(b, o):
    b.init()
    b.align('center')
    b.font('double')
    b.text('SUMO')
    b.font('double_h')
    b.text('בון תשלום')
    b.font('double')
    b.text(f'#{o["order_number"]}')
    b.font('normal')
    type_he = 'משלוח' if o['order_type'] == 'delivery' else 'איסוף עצמי'
    b.text(f'{type_he} | {o.get("created_at", "")}')
    b.thick()
    b.align('right')
    b.font('double_h')
    b.bold(); b.text(o.get('customer_name', '')); b.bold(False)
    b.font('normal')
    b.dashed()

    for item in o.get('items', []):
        name = item.get('name_he') or item.get('item_name_he') or item.get('name', '')
        qty = item.get('qty') or item.get('quantity', 1)
        price = item.get('price') or item.get('unit_price', 0)
        total = qty * price
        b.bold(); b.text(f'{qty}× {name}  ₪{total:.0f}'); b.bold(False)

    b.dashed()
    b.text(f'סכום: ₪{o["subtotal"]:.0f}')
    if o.get('delivery_fee', 0) > 0:
        b.text(f'משלוח: ₪{o["delivery_fee"]:.0f}')
    if o.get('discount_amount', 0) > 0:
        b.text(f'הנחה: -₪{o["discount_amount"]:.0f}')
    b.thick()
    b.font('double')
    b.bold(); b.text(f'לתשלום: ₪{o["total_amount"]:.0f}'); b.bold(False)
    b.font('normal')
    b.align('center')
    b.text(f'תשלום: {o.get("payment_method", "—")}')
    b.text(time.strftime('%H:%M'))
    b.cut()


def build_station(b, o, station_name, station_items):
    b.init()
    b.align('center')
    b.font('double')
    b.bold(); b.text(station_name); b.bold(False)
    b.font('double_h')
    b.text(f'#{o["order_number"]}')
    b.font('normal')
    type_he = 'משלוח' if o['order_type'] == 'delivery' else 'איסוף עצמי'
    b.text(f'{type_he} | {o.get("created_at", "")}')
    b.thick()
    b.align('right')
    if o.get('customer_notes'):
        b.bold(); b.text(f'⚠ {o["customer_notes"]}'); b.bold(False)
    for item in station_items:
        name = item.get('name_he') or item.get('item_name_he') or item.get('name', '')
        qty = item.get('qty') or item.get('quantity', 1)
        b.bold(); b.text(f'{qty}× {name}'); b.bold(False)
    b.align('center')
    b.dashed()
    b.text(f'#{o["order_number"]} | {station_name} | {time.strftime("%H:%M")}')
    b.cut()


def send_to_printer(data):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((PRINTER_IP, PRINTER_PORT))
        s.sendall(bytes(data))
        s.close()
        return True
    except Exception as e:
        print(f'  ❌ Printer error: {e}')
        return False


def api_get(path):
    url = f'{SERVER_URL}{path}'
    req = urllib.request.Request(url, headers={'X-Print-Key': PRINT_AGENT_KEY})
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f'  HTTP error {e.code}: {e.read().decode("utf-8", errors="replace")}')
        return None
    except Exception as e:
        print(f'  Connection error: {e}')
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
        print(f'  Mark-printed error: {e}')
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

    return send_to_printer(b.buf)


def main():
    print('╔══════════════════════════════════════╗')
    print('║     SUMO Print Agent v1.0            ║')
    print('╠══════════════════════════════════════╣')
    print(f'║ Server:  {SERVER_URL[:30]:<30}║')
    print(f'║ Printer: {PRINTER_IP}:{PRINTER_PORT:<19}║')
    print(f'║ Poll:    every {POLL_INTERVAL}s{" " * 20}║')
    print('╚══════════════════════════════════════╝')
    print()

    if SERVER_URL == "https://your-app.replit.app":
        print('⚠️  Please edit SERVER_URL in the script!')
        sys.exit(1)
    if PRINT_AGENT_KEY == "change-me-to-a-secret":
        print('⚠️  Please set PRINT_AGENT_KEY in the script!')
        sys.exit(1)

    print('🔄 Watching for new orders...\n')

    while True:
        try:
            data = api_get('/ops/api/orders/unprinted')
            if data and data.get('ok'):
                orders = data.get('orders', [])
                if orders:
                    print(f'📦 Found {len(orders)} new order(s)')
                    printed_ids = []
                    for order in orders:
                        num = order['order_number']
                        name = order['customer_name']
                        print(f'  🖨  Printing #{num} ({name})...', end=' ')
                        if print_order(order):
                            print('✅')
                            printed_ids.append(order['id'])
                        else:
                            print('❌ FAILED')

                    if printed_ids:
                        api_post('/ops/api/orders/mark-printed', {'order_ids': printed_ids})
                        print(f'  ✅ Marked {len(printed_ids)} order(s) as printed\n')
        except KeyboardInterrupt:
            print('\n👋 Shutting down...')
            break
        except Exception as e:
            print(f'  Error: {e}')

        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    main()
