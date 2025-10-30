from flask import render_template, request, flash, redirect, url_for, jsonify, send_from_directory, session
from flask_mail import Message
from app import app, mail
from forms import ContactForm, ReservationForm
from models import MenuCategory, MenuItem, Branch, SiteSettings, MediaFile, MenuSettings, ReservationSettings, CustomSection, WorkingHours, TermsOfUse, GalleryPhoto
from sqlalchemy.orm import joinedload
import logging
import os

def get_language():
    """Get current language from session or query param"""
    if 'lang' in request.args:
        session['language'] = request.args.get('lang')
    return session.get('language', 'he')

def get_menu_setting(key, default='true'):
    """Get menu setting value"""
    setting = MenuSettings.query.filter_by(setting_key=key).first()
    return setting.setting_value if setting else default

def get_context_data():
    """Get common context data for all pages"""
    settings = SiteSettings.query.first()
    if not settings:
        settings = SiteSettings()
    
    branches = Branch.query.filter_by(is_active=True).order_by(Branch.display_order).all()
    language = get_language()
    
    return {
        'settings': settings,
        'branches': branches,
        'language': language,
        'show_images': get_menu_setting('show_images') == 'true',
        'show_dietary_icons': get_menu_setting('show_dietary_icons') == 'true'
    }

@app.route('/')
def index():
    """Homepage with hero video"""
    context = get_context_data()
    
    # Get hero video
    hero_video = MediaFile.query.filter_by(
        section='hero',
        file_type='video',
        is_active=True
    ).order_by(MediaFile.display_order).first()
    
    # Get featured menu items
    featured_items = MenuItem.query.options(joinedload(MenuItem.dietary_properties)).filter_by(
        is_signature=True,
        is_available=True
    ).order_by(MenuItem.display_order).limit(6).all()
    
    # Get gallery preview images
    gallery_images = MediaFile.query.filter_by(
        section='gallery',
        file_type='image',
        is_active=True
    ).order_by(MediaFile.display_order).limit(6).all()
    
    # Get reservation settings
    reservation_settings = ReservationSettings.query.first()
    if not reservation_settings:
        reservation_settings = ReservationSettings()
    
    # Get custom sections
    custom_sections = CustomSection.query.filter_by(
        is_active=True,
        show_on_homepage=True
    ).order_by(CustomSection.display_order).all()
    
    return render_template('public/index.html',
                         **context,
                         hero_video=hero_video,
                         featured_items=featured_items,
                         gallery_images=gallery_images,
                         reservation_settings=reservation_settings,
                         custom_sections=custom_sections)

@app.route('/menu')
def menu_page():
    """Full menu page"""
    context = get_context_data()
    
    # Get menu images uploaded by admin
    menu_images = MediaFile.query.filter_by(
        section='menu',
        is_active=True
    ).order_by(MediaFile.display_order).all()
    
    categories = MenuCategory.query.filter_by(is_active=True).order_by(MenuCategory.display_order).all()
    
    # Get items for each category with dietary properties
    for category in categories:
        category.items = MenuItem.query.options(joinedload(MenuItem.dietary_properties)).filter_by(
            category_id=category.id,
            is_available=True
        ).order_by(MenuItem.display_order).all()
    
    return render_template('public/menu.html',
                         **context,
                         categories=categories,
                         menu_images=menu_images)

@app.route('/order')
def order_page():
    """Online ordering page"""
    context = get_context_data()
    
    if not context['settings'].enable_online_ordering:
        flash('Online ordering is currently disabled.' if context['language'] == 'en' else 'ההזמנות באינטרנט כרגע מושבתות.', 'warning')
        return redirect(url_for('index'))
    
    categories = MenuCategory.query.filter_by(is_active=True).order_by(MenuCategory.display_order).all()
    
    for category in categories:
        category.items = MenuItem.query.options(joinedload(MenuItem.dietary_properties)).filter_by(
            category_id=category.id,
            is_available=True
        ).order_by(MenuItem.display_order).all()
    
    return render_template('public/order.html',
                         **context,
                         categories=categories)

@app.route('/gallery')
def gallery_page():
    """Gallery page"""
    context = get_context_data()
    
    gallery_images = MediaFile.query.filter_by(
        section='gallery',
        file_type='image',
        is_active=True
    ).order_by(MediaFile.display_order).all()
    
    return render_template('public/gallery.html',
                         **context,
                         gallery_images=gallery_images)

@app.route('/terms')
def terms_page():
    """Terms of Use page"""
    context = get_context_data()
    
    # Get the active terms of use
    terms = TermsOfUse.query.filter_by(is_active=True).first()
    
    return render_template('public/terms.html',
                         **context,
                         terms=terms)

@app.route('/contact', methods=['GET', 'POST'])
def contact_page():
    """Contact page"""
    context = get_context_data()
    form = ContactForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            msg = Message(
                subject=f'Contact from {form.name.data}',
                recipients=[app.config.get('MAIL_USERNAME', 'info@sumo-restaurant.co.il')],
                body=f'''
New contact message:

Name: {form.name.data}
Email: {form.email.data}
Phone: {form.phone.data}

Message:
{form.message.data}
'''
            )
            mail.send(msg)
            flash('Message sent successfully!' if context['language'] == 'en' else 'ההודעה נשלחה בהצלחה!', 'success')
            return redirect(url_for('contact_page'))
        except Exception as e:
            logging.error(f'Error sending contact email: {e}')
            flash('Error sending message.' if context['language'] == 'en' else 'שגיאה בשליחת ההודעה.', 'error')
    
    return render_template('public/contact.html',
                         **context,
                         form=form)

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
