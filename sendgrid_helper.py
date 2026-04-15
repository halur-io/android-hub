import os
import requests
import logging
from markupsafe import escape as html_escape

def get_sendgrid_credentials():
    """Get SendGrid API credentials from Replit connector"""
    hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
    
    repl_identity = os.environ.get('REPL_IDENTITY')
    web_repl_renewal = os.environ.get('WEB_REPL_RENEWAL')
    
    if repl_identity:
        x_replit_token = f'repl {repl_identity}'
    elif web_repl_renewal:
        x_replit_token = f'depl {web_repl_renewal}'
    else:
        logging.warning('X_REPLIT_TOKEN not found for repl/depl')
        return None, None
    
    try:
        response = requests.get(
            f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=sendgrid',
            headers={
                'Accept': 'application/json',
                'X_REPLIT_TOKEN': x_replit_token
            }
        )
        data = response.json()
        connection = data.get('items', [{}])[0] if data.get('items') else {}
        settings = connection.get('settings', {})
        
        api_key = settings.get('api_key')
        from_email = settings.get('from_email')
        
        if not api_key or not from_email:
            logging.warning('SendGrid not connected or missing credentials')
            return None, None
            
        return api_key, from_email
    except Exception as e:
        logging.error(f'Error getting SendGrid credentials: {e}')
        return None, None

def send_email_notification(to_email, subject, html_content, plain_text=None):
    """Send email using SendGrid API"""
    api_key, from_email = get_sendgrid_credentials()
    
    if not api_key or not from_email:
        logging.error('SendGrid credentials not available')
        return False
    
    logging.info(f'Sending email with subject: {subject}')
    
    try:
        response = requests.post(
            'https://api.sendgrid.com/v3/mail/send',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'personalizations': [{'to': [{'email': to_email}]}],
                'from': {'email': from_email},
                'subject': subject,
                'content': [
                    {'type': 'text/plain', 'value': plain_text or html_content},
                    {'type': 'text/html', 'value': html_content}
                ]
            }
        )
        
        if response.status_code in (200, 201, 202):
            logging.info('Email sent successfully')
            return True
        else:
            logging.error(f'SendGrid API error: status {response.status_code}')
            return False
    except Exception as e:
        logging.error(f'Error sending email via SendGrid: {e}')
        return False

def send_new_message_notification(message_type, message_data, admin_email, custom_subject=None):
    """Send notification for new message received"""
    def _esc(val, default='-'):
        return html_escape(str(val)) if val else default

    if message_type == 'contact':
        subject = custom_subject or f"הודעת יצירת קשר חדשה - {_esc(message_data.get('name', 'לקוח'))}"
        html_content = f"""
        <div dir="rtl" style="font-family: Arial, sans-serif;">
            <h2>הודעת יצירת קשר חדשה</h2>
            <p><strong>שם:</strong> {_esc(message_data.get('name'))}</p>
            <p><strong>אימייל:</strong> {_esc(message_data.get('email'))}</p>
            <p><strong>טלפון:</strong> {_esc(message_data.get('phone'))}</p>
            <hr>
            <p><strong>הודעה:</strong></p>
            <p>{_esc(message_data.get('message'))}</p>
        </div>
        """
    elif message_type == 'catering':
        subject = custom_subject or f"פנייה חדשה לקייטרינג - {_esc(message_data.get('name', 'לקוח'))}"
        html_content = f"""
        <div dir="rtl" style="font-family: Arial, sans-serif;">
            <h2>פנייה חדשה לקייטרינג</h2>
            <p><strong>שם:</strong> {_esc(message_data.get('name'))}</p>
            <p><strong>אימייל:</strong> {_esc(message_data.get('email'))}</p>
            <p><strong>טלפון:</strong> {_esc(message_data.get('phone'))}</p>
            <p><strong>סוג אירוע:</strong> {_esc(message_data.get('event_type'))}</p>
            <p><strong>תאריך אירוע:</strong> {_esc(message_data.get('event_date'))}</p>
            <p><strong>מספר אורחים:</strong> {_esc(message_data.get('guest_count'))}</p>
            <hr>
            <p><strong>הודעה:</strong></p>
            <p>{_esc(message_data.get('message'))}</p>
        </div>
        """
    elif message_type == 'career':
        subject = custom_subject or f"מועמדות חדשה לעבודה - {_esc(message_data.get('name', 'מועמד'))}"
        html_content = f"""
        <div dir="rtl" style="font-family: Arial, sans-serif;">
            <h2>מועמדות חדשה לעבודה</h2>
            <p><strong>שם:</strong> {_esc(message_data.get('name'))}</p>
            <p><strong>אימייל:</strong> {_esc(message_data.get('email'))}</p>
            <p><strong>טלפון:</strong> {_esc(message_data.get('phone'))}</p>
            <p><strong>משרה:</strong> {_esc(message_data.get('position'))}</p>
            <hr>
            <p><strong>הודעה:</strong></p>
            <p>{_esc(message_data.get('message'))}</p>
        </div>
        """
    else:
        return False
    
    return send_email_notification(admin_email, subject, html_content)
