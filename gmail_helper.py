"""
Gmail API Helper for sending emails via Replit's Gmail connector
"""
import os
import requests
import logging
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

connection_settings = None

def get_gmail_credentials():
    """Get Gmail API credentials from Replit connector"""
    global connection_settings
    
    hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
    
    repl_identity = os.environ.get('REPL_IDENTITY')
    web_repl_renewal = os.environ.get('WEB_REPL_RENEWAL')
    
    if repl_identity:
        x_replit_token = f'repl {repl_identity}'
    elif web_repl_renewal:
        x_replit_token = f'depl {web_repl_renewal}'
    else:
        logging.error('X_REPLIT_TOKEN not found for repl/depl')
        return None
    
    try:
        response = requests.get(
            f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=google-mail',
            headers={
                'Accept': 'application/json',
                'X_REPLIT_TOKEN': x_replit_token
            }
        )
        data = response.json()
        connection = data.get('items', [{}])[0] if data.get('items') else {}
        settings = connection.get('settings', {})
        
        access_token = settings.get('access_token') or settings.get('oauth', {}).get('credentials', {}).get('access_token')
        
        if not access_token:
            logging.error('Gmail not connected or missing access token')
            return None
        
        connection_settings = settings
        return access_token
    except Exception as e:
        logging.error(f'Error getting Gmail credentials: {e}')
        return None

def send_email_via_gmail(to_email, subject, html_content, plain_text=None, from_email=None):
    """Send email using Gmail API. Returns (success, error_message)"""
    access_token = get_gmail_credentials()
    
    if not access_token:
        error_msg = 'Gmail credentials not available - please reconnect Gmail'
        logging.error(error_msg)
        return False, error_msg
    
    # Default sender email
    sender_email = from_email or os.environ.get('GMAIL_SENDER_EMAIL', 'info@sumo-rest.co.il')
    
    try:
        message = MIMEMultipart('alternative')
        message['From'] = sender_email
        message['To'] = to_email
        message['Subject'] = subject
        
        if plain_text:
            text_part = MIMEText(plain_text, 'plain', 'utf-8')
            message.attach(text_part)
        
        html_part = MIMEText(html_content, 'html', 'utf-8')
        message.attach(html_part)
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        logging.info(f'Sending email via Gmail to {to_email} with subject: {subject}')
        
        response = requests.post(
            'https://gmail.googleapis.com/gmail/v1/users/me/messages/send',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            json={'raw': raw_message}
        )
        
        if response.status_code in (200, 201, 202):
            logging.info(f'Email sent successfully via Gmail to {to_email}')
            return True, None
        else:
            error_msg = f'Gmail API error {response.status_code}: {response.text}'
            logging.error(error_msg)
            return False, error_msg
    except Exception as e:
        error_msg = f'Error sending email: {str(e)}'
        logging.error(error_msg)
        return False, error_msg

def generate_unsubscribe_token(email):
    """Generate a secure signed token for unsubscribe links"""
    from itsdangerous import URLSafeTimedSerializer
    secret_key = os.environ.get('SESSION_SECRET', 'fallback-secret-key')
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(email, salt='unsubscribe')

def verify_unsubscribe_token(token, max_age_days=30):
    """Verify an unsubscribe token and return the email. Returns None if invalid."""
    from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
    secret_key = os.environ.get('SESSION_SECRET', 'fallback-secret-key')
    serializer = URLSafeTimedSerializer(secret_key)
    try:
        email = serializer.loads(token, salt='unsubscribe', max_age=max_age_days * 24 * 60 * 60)
        return email
    except (SignatureExpired, BadSignature):
        return None

def add_unsubscribe_footer(html_content, email, base_url=None):
    """Add unsubscribe footer to email HTML content for newsletter subscribers"""
    import urllib.parse
    if not base_url:
        base_url = os.environ.get('BASE_URL', 'https://sumo-rest.co.il')
    
    token = generate_unsubscribe_token(email)
    unsubscribe_url = f"{base_url}/newsletter/unsubscribe?token={urllib.parse.quote(token)}"
    
    footer = f"""
    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; text-align: center; font-size: 12px; color: #6b7280;">
        <p>קיבלת הודעה זו כי נרשמת לניוזלטר שלנו.</p>
        <p><a href="{unsubscribe_url}" style="color: #3b82f6; text-decoration: underline;">לחץ כאן להסרה מרשימת התפוצה</a></p>
    </div>
    """
    
    if '</div>' in html_content:
        last_div = html_content.rfind('</div>')
        return html_content[:last_div] + footer + html_content[last_div:]
    else:
        return html_content + footer

def send_newsletter_email(to_email, subject, html_content, base_url=None):
    """Send newsletter email with automatic unsubscribe footer. Returns (success, error_message)"""
    content_with_footer = add_unsubscribe_footer(html_content, to_email, base_url)
    return send_email_via_gmail(to_email, subject, content_with_footer)

def send_new_message_notification(message_type, message_data, admin_email, custom_subject=None):
    """Send notification for new message received"""
    if message_type == 'contact':
        subject = custom_subject or f"הודעת יצירת קשר חדשה - {message_data.get('name', 'לקוח')}"
        html_content = f"""
        <div dir="rtl" style="font-family: Arial, sans-serif;">
            <h2>הודעת יצירת קשר חדשה</h2>
            <p><strong>שם:</strong> {message_data.get('name', '-')}</p>
            <p><strong>אימייל:</strong> {message_data.get('email', '-')}</p>
            <p><strong>טלפון:</strong> {message_data.get('phone', '-')}</p>
            <hr>
            <p><strong>הודעה:</strong></p>
            <p>{message_data.get('message', '-')}</p>
        </div>
        """
    elif message_type == 'catering':
        subject = custom_subject or f"פנייה חדשה לקייטרינג - {message_data.get('name', 'לקוח')}"
        html_content = f"""
        <div dir="rtl" style="font-family: Arial, sans-serif;">
            <h2>פנייה חדשה לקייטרינג</h2>
            <p><strong>שם:</strong> {message_data.get('name', '-')}</p>
            <p><strong>אימייל:</strong> {message_data.get('email', '-')}</p>
            <p><strong>טלפון:</strong> {message_data.get('phone', '-')}</p>
            <p><strong>סוג אירוע:</strong> {message_data.get('event_type', '-')}</p>
            <p><strong>תאריך אירוע:</strong> {message_data.get('event_date', '-')}</p>
            <p><strong>מספר אורחים:</strong> {message_data.get('guest_count', '-')}</p>
            <hr>
            <p><strong>הודעה:</strong></p>
            <p>{message_data.get('message', '-')}</p>
        </div>
        """
    elif message_type == 'career':
        subject = custom_subject or f"מועמדות חדשה לעבודה - {message_data.get('name', 'מועמד')}"
        html_content = f"""
        <div dir="rtl" style="font-family: Arial, sans-serif;">
            <h2>מועמדות חדשה לעבודה</h2>
            <p><strong>שם:</strong> {message_data.get('name', '-')}</p>
            <p><strong>אימייל:</strong> {message_data.get('email', '-')}</p>
            <p><strong>טלפון:</strong> {message_data.get('phone', '-')}</p>
            <p><strong>משרה:</strong> {message_data.get('position', '-')}</p>
            <hr>
            <p><strong>הודעה:</strong></p>
            <p>{message_data.get('message', '-')}</p>
        </div>
        """
    else:
        return False
    
    return send_email_via_gmail(admin_email, subject, html_content)
