from flask import render_template, request, flash, redirect, url_for, jsonify, send_from_directory, session
from flask_mail import Message
from app import app, mail
from database import db
from forms import ContactForm, ReservationForm, NewsletterForm
from models import MenuCategory, MenuItem, Branch, SiteSettings, MediaFile, MenuSettings, ReservationSettings, CustomSection, WorkingHours, TermsOfUse, PrivacyPolicy, GalleryPhoto, NewsletterSubscriber
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
    
    # Get gallery images for homepage section (8 photos)
    gallery_images = GalleryPhoto.query.filter_by(
        is_active=True
    ).order_by(GalleryPhoto.display_order).limit(8).all()
    logging.debug(f"Found {len(gallery_images)} gallery images for homepage")
    for img in gallery_images[:3]:
        logging.debug(f"Gallery image: {img.file_path}")
    
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
    """Full menu page - Optimized to prevent N+1 queries"""
    context = get_context_data()
    
    # Get menu images uploaded by admin
    menu_images = MediaFile.query.filter_by(
        section='menu',
        is_active=True
    ).order_by(MediaFile.display_order).all()
    
    # Get all categories that should be shown in menu
    categories = MenuCategory.query.filter_by(is_active=True, show_in_menu=True).order_by(MenuCategory.display_order).all()
    
    # Get ALL menu items in ONE query (not per category) - PERFORMANCE FIX
    all_items = MenuItem.query.options(joinedload(MenuItem.dietary_properties)).filter_by(
        is_available=True
    ).order_by(MenuItem.display_order).all()
    
    # Group items by category in Python (faster than multiple DB queries)
    items_by_category = {}
    for item in all_items:
        if item.category_id not in items_by_category:
            items_by_category[item.category_id] = []
        items_by_category[item.category_id].append(item)
    
    # Assign items to their categories
    for category in categories:
        category.items = items_by_category.get(category.id, [])
    
    return render_template('public/menu.html',
                         **context,
                         categories=categories,
                         menu_images=menu_images)

@app.route('/order')
def order_page():
    """Online ordering page - Optimized to prevent N+1 queries"""
    context = get_context_data()
    
    # Check if online ordering OR delivery is disabled
    ordering_enabled = context['settings'].enable_online_ordering and context['settings'].enable_delivery
    
    if not ordering_enabled:
        # Show disabled page instead of redirecting
        return render_template('public/order.html',
                             **context,
                             ordering_disabled=True,
                             categories=[])
    
    # Get all categories
    categories = MenuCategory.query.filter_by(is_active=True).order_by(MenuCategory.display_order).all()
    
    # Get ALL menu items that allow delivery - Filter by availability
    all_items = MenuItem.query.options(joinedload(MenuItem.dietary_properties)).filter_by(
        is_available=True,
        allow_delivery=True
    ).order_by(MenuItem.display_order).all()
    
    # Group items by category in Python (faster than multiple DB queries)
    items_by_category = {}
    for item in all_items:
        if item.category_id not in items_by_category:
            items_by_category[item.category_id] = []
        items_by_category[item.category_id].append(item)
    
    # Assign items to their categories
    for category in categories:
        category.items = items_by_category.get(category.id, [])
    
    return render_template('public/order.html',
                         **context,
                         ordering_disabled=False,
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

@app.route('/catering', methods=['GET', 'POST'])
def catering_page():
    """Catering & Special Events page"""
    from models import CateringPackage, CateringHighlight, CateringGalleryImage, CateringContact
    
    context = get_context_data()
    success = False
    error = None
    
    # Handle form submission
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            event_date = request.form.get('event_date', '').strip()
            event_type = request.form.get('event_type', '').strip()
            guest_count = request.form.get('guest_count', '').strip()
            message = request.form.get('message', '').strip()
            
            if not name or not email or not phone or not message:
                error = 'נא למלא את כל השדות הנדרשים' if context.get('language') == 'he' else 'Please fill all required fields'
            else:
                # Save to database
                contact = CateringContact(
                    name=name,
                    email=email,
                    phone=phone,
                    event_date=event_date if event_date else None,
                    event_type=event_type if event_type else None,
                    guest_count=int(guest_count) if guest_count else None,
                    message=message
                )
                db.session.add(contact)
                db.session.commit()
                
                success = True
                
                # TODO: Send email notification to restaurant
                
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Catering contact form error: {str(e)}")
            error = 'אירעה שגיאה. אנא נסה שוב' if context.get('language') == 'he' else 'An error occurred. Please try again'
    
    # Get active packages ordered by display order
    packages = CateringPackage.query.filter_by(is_active=True).order_by(CateringPackage.display_order).all()
    
    # Get active highlights
    highlights = CateringHighlight.query.filter_by(is_active=True).order_by(CateringHighlight.display_order).all()
    
    # Get active gallery images
    gallery_images = CateringGalleryImage.query.filter_by(is_active=True).order_by(CateringGalleryImage.display_order).all()
    
    return render_template('public/catering.html',
                         **context,
                         packages=packages,
                         highlights=highlights,
                         gallery_images=gallery_images,
                         success=success,
                         error=error)

@app.route('/careers', methods=['GET', 'POST'])
def careers_page():
    """Careers page with job positions and application form"""
    from models import CareerPosition, CareerContact
    
    context = get_context_data()
    success = False
    error = None
    
    # Handle form submission
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            position_select = request.form.get('position_select', '').strip()
            position_other = request.form.get('position_other', '').strip()
            message = request.form.get('message', '').strip()
            
            if not name or not email or not phone or not message or not position_select:
                error = 'נא למלא את כל השדות הנדרשים' if context.get('language') == 'he' else 'Please fill all required fields'
            else:
                # Determine position_id and position_other
                position_id = None
                position_other_text = None
                
                if position_select == 'other':
                    if not position_other:
                        error = 'נא לציין את המשרה המבוקשת' if context.get('language') == 'he' else 'Please specify the desired position'
                    else:
                        position_other_text = position_other
                else:
                    position_id = int(position_select)
                
                if not error:
                    # Save to database
                    contact = CareerContact(
                        name=name,
                        email=email,
                        phone=phone,
                        position_id=position_id,
                        position_other=position_other_text,
                        message=message
                    )
                    db.session.add(contact)
                    db.session.commit()
                    
                    success = True
                    
                    # TODO: Send email notification to restaurant
                
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Career application form error: {str(e)}")
            error = 'אירעה שגיאה. אנא נסה שוב' if context.get('language') == 'he' else 'An error occurred. Please try again'
    
    # Get active positions ordered by display order
    positions = CareerPosition.query.filter_by(is_active=True).order_by(CareerPosition.display_order).all()
    
    return render_template('public/careers.html',
                         **context,
                         positions=positions,
                         success=success,
                         error=error)

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

@app.route('/newsletter/subscribe', methods=['POST'])
def newsletter_subscribe():
    """Newsletter subscription"""
    context = get_context_data()
    email = request.form.get('email', '').strip()
    
    if email:
        try:
            existing = NewsletterSubscriber.query.filter_by(email=email).first()
            
            if existing:
                if existing.is_active:
                    flash('כבר נרשמת לניוזלטר!' if context['language'] == 'he' else 'Already subscribed!', 'info')
                else:
                    existing.is_active = True
                    existing.unsubscribed_at = None
                    db.session.commit()
                    flash('נרשמת מחדש!' if context['language'] == 'he' else 'Resubscribed!', 'success')
            else:
                subscriber = NewsletterSubscriber(
                    email=email,
                    source=request.form.get('source', 'footer')
                )
                db.session.add(subscriber)
                db.session.commit()
                flash('תודה על הרשמתך!' if context['language'] == 'he' else 'Thank you for subscribing!', 'success')
        except Exception as e:
            logging.error(f'Error subscribing: {e}')
            flash('שגיאה' if context['language'] == 'he' else 'Error', 'error')
    else:
        flash('אנא הזן כתובת אימייל' if context['language'] == 'he' else 'Please enter an email', 'error')
    
    return redirect(request.referrer or url_for('index'))

@app.route('/accessibility')
def accessibility_statement():
    """Accessibility statement - IS 5568 compliance"""
    context = get_context_data()
    return render_template('public/accessibility.html', **context)

@app.route('/privacy-policy')
def privacy_policy_page():
    """Privacy policy page"""
    context = get_context_data()
    privacy = PrivacyPolicy.query.filter_by(is_active=True).first()
    context['privacy'] = privacy
    return render_template('public/privacy.html', **context)

@app.errorhandler(404)
def not_found(error):
    # Check if this is an admin route
    if request.path.startswith('/admin'):
        return render_template('admin/error.html', 
                             error_code=404,
                             error_title='Page Not Found',
                             error_message='The admin page you are looking for does not exist.',
                             suggestion='Try accessing the admin panel at <a href="/admin/">/admin/</a>'), 404
    
    # Return proper 404 page for public routes
    context = get_context_data()
    return render_template('public/404.html', **context), 404

@app.errorhandler(500)
def internal_error(error):
    if request.path.startswith('/admin'):
        return render_template('admin/error.html',
                             error_code=500,
                             error_title='Server Error',
                             error_message='An internal server error occurred.',
                             suggestion='Please try again or contact support.'), 500
    
    # Return proper 500 error page for public routes
    context = get_context_data()
    return render_template('public/500.html', **context), 500

# Example 2 Routes - Black/Dramatic/Elegant Theme
@app.route('/example2/')
def example2_index():
    """Example 2 Homepage with dramatic black/gold theme"""
    context = get_context_data()
    context['theme'] = 'example2'
    
    hero_video = MediaFile.query.filter_by(
        section='hero',
        file_type='video',
        is_active=True
    ).order_by(MediaFile.display_order).first()
    
    featured_items = MenuItem.query.options(joinedload(MenuItem.dietary_properties)).filter_by(
        is_signature=True,
        is_available=True
    ).order_by(MenuItem.display_order).limit(6).all()
    
    gallery_images = GalleryPhoto.query.filter_by(
        is_active=True
    ).order_by(GalleryPhoto.display_order).limit(8).all()
    
    reservation_settings = ReservationSettings.query.first()
    if not reservation_settings:
        reservation_settings = ReservationSettings()
    
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

@app.route('/example2/menu')
def example2_menu():
    """Example 2 Menu page with black/gold theme"""
    context = get_context_data()
    context['theme'] = 'example2'
    
    menu_images = MediaFile.query.filter_by(
        section='menu',
        is_active=True
    ).order_by(MediaFile.display_order).all()
    
    categories = MenuCategory.query.filter_by(is_active=True, show_in_menu=True).order_by(MenuCategory.display_order).all()
    
    all_items = MenuItem.query.options(joinedload(MenuItem.dietary_properties)).filter_by(
        is_available=True
    ).order_by(MenuItem.display_order).all()
    
    items_by_category = {}
    for item in all_items:
        if item.category_id not in items_by_category:
            items_by_category[item.category_id] = []
        items_by_category[item.category_id].append(item)
    
    for category in categories:
        category.items = items_by_category.get(category.id, [])
    
    return render_template('public/menu.html',
                         **context,
                         menu_images=menu_images,
                         categories=categories)

@app.route('/example2/gallery')
def example2_gallery():
    """Example 2 Gallery page with black/gold theme"""
    context = get_context_data()
    context['theme'] = 'example2'
    
    gallery_images = MediaFile.query.filter_by(
        section='gallery',
        file_type='image',
        is_active=True
    ).order_by(MediaFile.display_order).all()
    
    return render_template('public/gallery.html',
                         **context,
                         gallery_images=gallery_images)

@app.route('/example2/catering', methods=['GET', 'POST'])
def example2_catering():
    """Example 2 Catering page with black/gold theme"""
    from models import CateringPackage, CateringHighlight, CateringGalleryImage, CateringContact
    
    context = get_context_data()
    context['theme'] = 'example2'
    success = False
    error = None
    
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            event_date = request.form.get('event_date', '').strip()
            event_type = request.form.get('event_type', '').strip()
            guest_count = request.form.get('guest_count', '').strip()
            message = request.form.get('message', '').strip()
            
            if not name or not email or not phone or not message:
                error = 'נא למלא את כל השדות הנדרשים' if context.get('language') == 'he' else 'Please fill all required fields'
            else:
                contact = CateringContact(
                    name=name,
                    email=email,
                    phone=phone,
                    event_date=event_date if event_date else None,
                    event_type=event_type if event_type else None,
                    guest_count=int(guest_count) if guest_count else None,
                    message=message
                )
                db.session.add(contact)
                db.session.commit()
                success = True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Catering contact form error: {str(e)}")
            error = 'אירעה שגיאה. אנא נסה שוב' if context.get('language') == 'he' else 'An error occurred. Please try again'
    
    packages = CateringPackage.query.filter_by(is_active=True).order_by(CateringPackage.display_order).all()
    highlights = CateringHighlight.query.filter_by(is_active=True).order_by(CateringHighlight.display_order).all()
    gallery_images = CateringGalleryImage.query.filter_by(is_active=True).order_by(CateringGalleryImage.display_order).all()
    
    return render_template('public/catering.html',
                         **context,
                         packages=packages,
                         highlights=highlights,
                         gallery_images=gallery_images,
                         success=success,
                         error=error)

@app.route('/example2/contact', methods=['GET', 'POST'])
def example2_contact():
    """Example 2 Contact page with black/gold theme"""
    from models import ContactMessage
    
    context = get_context_data()
    context['theme'] = 'example2'
    form = ContactForm()
    
    if form.validate_on_submit():
        try:
            contact = ContactMessage(
                name=form.name.data,
                email=form.email.data,
                phone=form.phone.data,
                subject=form.subject.data,
                message=form.message.data
            )
            db.session.add(contact)
            db.session.commit()
            
            flash('הודעתך נשלחה בהצלחה!' if context['language'] == 'he' else 'Your message has been sent successfully!', 'success')
            return redirect(url_for('example2_contact'))
        except Exception as e:
            db.session.rollback()
            logging.error(f'Contact form error: {e}')
            flash('אירעה שגיאה בשליחת ההודעה' if context['language'] == 'he' else 'An error occurred sending your message', 'error')
    
    return render_template('public/contact.html', **context, form=form)

@app.route('/example2/careers')
def example2_careers():
    """Example 2 Careers page with black/gold theme"""
    from models import CareerPosition
    
    context = get_context_data()
    context['theme'] = 'example2'
    
    positions = CareerPosition.query.filter_by(is_active=True).order_by(CareerPosition.display_order).all()
    
    return render_template('public/careers.html', **context, positions=positions)

@app.route('/example2/terms')
def example2_terms():
    """Example 2 Terms page with black/gold theme"""
    context = get_context_data()
    context['theme'] = 'example2'
    terms = TermsOfUse.query.filter_by(is_active=True).first()
    context['terms'] = terms
    return render_template('public/terms.html', **context)

@app.route('/example2/order')
def example2_order():
    """Example 2 Order page with black/gold theme"""
    context = get_context_data()
    context['theme'] = 'example2'
    
    ordering_enabled = context['settings'].enable_online_ordering and context['settings'].enable_delivery
    
    if not ordering_enabled:
        return render_template('public/order.html',
                             **context,
                             ordering_disabled=True,
                             categories=[])
    
    categories = MenuCategory.query.filter_by(is_active=True).order_by(MenuCategory.display_order).all()
    
    all_items = MenuItem.query.options(joinedload(MenuItem.dietary_properties)).filter_by(
        is_available=True,
        allow_delivery=True
    ).order_by(MenuItem.display_order).all()
    
    items_by_category = {}
    for item in all_items:
        if item.category_id not in items_by_category:
            items_by_category[item.category_id] = []
        items_by_category[item.category_id].append(item)
    
    for category in categories:
        category.items = items_by_category.get(category.id, [])
    
    return render_template('public/order.html',
                         **context,
                         ordering_disabled=False,
                         categories=categories)
