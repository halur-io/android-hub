import bleach

ALLOWED_TAGS = [
    'a', 'abbr', 'b', 'blockquote', 'br', 'code',
    'div', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr',
    'i', 'li', 'ol', 'p', 'pre', 'span',
    'strong', 'sub', 'sup', 'table', 'tbody', 'td', 'th',
    'thead', 'tr', 'u', 'ul',
]

ALLOWED_ATTRIBUTES = {
    '*': ['dir', 'lang'],
    'a': ['href', 'title', 'target', 'rel'],
    'td': ['colspan', 'rowspan'],
    'th': ['colspan', 'rowspan'],
    'div': ['class'],
    'span': ['class'],
    'p': ['class'],
}

ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


def sanitize_html(value):
    if not value:
        return value
    return bleach.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )


def redact_email(email):
    if not email or '@' not in str(email):
        return '***@***'
    parts = str(email).split('@')
    local = parts[0]
    domain = parts[1]
    if len(local) <= 2:
        redacted_local = '*' * len(local)
    else:
        redacted_local = local[0] + '*' * (len(local) - 2) + local[-1]
    return f'{redacted_local}@{domain}'


def redact_phone(phone):
    if not phone:
        return '***'
    phone_str = str(phone)
    digits = ''.join(c for c in phone_str if c.isdigit())
    if len(digits) <= 4:
        return '***' + digits[-2:] if len(digits) >= 2 else '***'
    return '***' + digits[-4:]
