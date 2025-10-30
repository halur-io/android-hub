from flask import render_template, request, flash, redirect, url_for, jsonify, send_from_directory
from flask_mail import Message
from app import app, mail
from forms import ContactForm, ReservationForm
from models import MenuCategory, MenuItem, Branch
from sqlalchemy.orm import joinedload
import logging
import os

@app.route('/')
def index():
    # Serve the React app
    return send_from_directory('static/dist', 'index.html')

@app.route('/demo')
def demo():
    """Demo page showing dynamic content from admin"""
    return render_template('demo.html')

@app.route('/assets/<path:path>')
def serve_assets(path):
    return send_from_directory('static/dist/assets', path)

@app.route('/api/contact', methods=['POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        try:
            # Send email
            msg = Message(
                subject=f'פנייה חדשה מאתר סומו - {form.name.data}',
                recipients=[app.config.get('MAIL_USERNAME', 'info@sumo-restaurant.co.il')],
                body=f'''
פנייה חדשה מאתר סומו:

שם: {form.name.data}
אימייל: {form.email.data}
טלפון: {form.phone.data}

הודעה:
{form.message.data}
'''
            )
            mail.send(msg)
            flash('ההודעה נשלחה בהצלחה! נחזור אליך בהקדם.', 'success')
        except Exception as e:
            logging.error(f'Error sending contact email: {e}')
            flash('אירעה שגיאה בשליחת ההודעה. אנא נסה שוב מאוחר יותר.', 'error')
    else:
        flash('אנא מלא את כל השדות הנדרשים כראוי.', 'error')
    
    return redirect(url_for('index') + '#contact')

@app.route('/api/reservation', methods=['POST'])
def reservation():
    form = ReservationForm()
    if form.validate_on_submit():
        try:
            # Send email
            msg = Message(
                subject=f'הזמנת שולחן חדשה - סומו - {form.name.data}',
                recipients=[app.config.get('MAIL_USERNAME', 'reservations@sumo-restaurant.co.il')],
                body=f'''
הזמנת שולחן חדשה במסעדת סומו:

שם: {form.name.data}
אימייל: {form.email.data}
טלפון: {form.phone.data}
תאריך: {form.date.data.strftime('%d/%m/%Y')}
שעה: {form.time.data.strftime('%H:%M')}
מספר סועדים: {form.guests.data}

בקשות מיוחדות:
{form.special_requests.data if form.special_requests.data else 'אין'}
'''
            )
            mail.send(msg)
            flash('הזמנת השולחן נשלחה בהצלחה! נחזור אליך לאישור.', 'success')
        except Exception as e:
            logging.error(f'Error sending reservation email: {e}')
            flash('אירעה שגיאה בשליחת ההזמנה. אנא נסה שוב מאוחר יותר.', 'error')
    else:
        flash('אנא מלא את כל השדות הנדרשים כראוי.', 'error')
    
    return redirect(url_for('index') + '#reservation')

@app.errorhandler(404)
def not_found(error):
    # Check if this is an admin route
    if request.path.startswith('/admin'):
        return render_template('admin/error.html', 
                             error_code=404,
                             error_title='Page Not Found',
                             error_message='The admin page you are looking for does not exist.',
                             suggestion='Try accessing the admin panel at <a href="/admin/">/admin/</a>'), 404
    
    contact_form = ContactForm()
    reservation_form = ReservationForm()
    return render_template('index.html', contact_form=contact_form, reservation_form=reservation_form), 404

@app.errorhandler(500)
def internal_error(error):
    if request.path.startswith('/admin'):
        return render_template('admin/error.html',
                             error_code=500,
                             error_title='Server Error',
                             error_message='An internal server error occurred.',
                             suggestion='Please try again or contact support.'), 500
    
    contact_form = ContactForm()
    reservation_form = ReservationForm()
    return render_template('index.html', contact_form=contact_form, reservation_form=reservation_form), 500
