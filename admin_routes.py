from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_from_directory, current_app
from flask_login import login_user, logout_user, login_required, current_user
# from flask_wtf.csrf import exempt  # Not available in this version
from werkzeug.utils import secure_filename
from database import db
from models import *
from permissions import require_permission, require_role, superadmin_required, has_permission
import os
from datetime import datetime
import json
import pandas as pd
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, DecimalField, IntegerField
from wtforms.validators import DataRequired, URL, Optional
from sqlalchemy.orm import joinedload
from PIL import Image

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Site Settings Form
class SiteSettingsForm(FlaskForm):
    site_name_he = StringField('שם האתר בעברית', validators=[DataRequired()])
    site_name_en = StringField('Site Name in English', validators=[DataRequired()])
    hero_title_he = StringField('כותרת ראשית בעברית')
    hero_title_en = StringField('Hero Title in English')
    hero_subtitle_he = StringField('כותרת משנה בעברית')
    hero_subtitle_en = StringField('Hero Subtitle in English')
    hero_description_he = TextAreaField('תיאור בעברית')
    hero_description_en = TextAreaField('Description in English')
    about_title_he = StringField('כותרת אודות בעברית')
    about_title_en = StringField('About Title in English')
    about_content_he = TextAreaField('תוכן אודות בעברית')
    about_content_en = TextAreaField('About Content in English')
    facebook_url = StringField('Facebook URL', validators=[Optional(), URL()])
    instagram_url = StringField('Instagram URL', validators=[Optional(), URL()])
    whatsapp_number = StringField('WhatsApp Number')
    
    # Feature Toggles
    enable_online_ordering = BooleanField('אפשר הזמנה אונליין / Enable Online Ordering')
    enable_english_language = BooleanField('אפשר שפה אנגלית / Enable English Language')
    enable_delivery = BooleanField('אפשר משלוחים / Enable Delivery')
    enable_pickup = BooleanField('אפשר איסוף עצמי / Enable Pickup')
    enable_menu_display = BooleanField('הצג תפריט / Show Menu')
    enable_gallery = BooleanField('הצג גלריה / Show Gallery')
    enable_contact_form = BooleanField('הצג טופס יצירת קשר / Show Contact Form')
    enable_table_reservations = BooleanField('אפשר הזמנת שולחנות / Enable Table Reservations')
    
    # Order Settings
    minimum_order_amount = DecimalField('סכום הזמנה מינימלי / Minimum Order Amount', validators=[Optional()])
    tax_rate = DecimalField('אחוז מע"מ / Tax Rate (%)', validators=[Optional()])
    
    submit = SubmitField('שמור')

UPLOAD_FOLDER = 'static/uploads'
CSV_UPLOAD_FOLDER = 'static/csv_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Images only, no video
ALLOWED_CSV_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    """Allow all media files (images and videos)"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_image_file(filename):
    """Allow only image files (no video)"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def allowed_csv_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_CSV_EXTENSIONS

def get_setting(key, default=''):
    """Helper function to get menu settings"""
    try:
        setting = MenuSettings.query.filter_by(setting_key=key).first()
        return setting.setting_value if setting else default
    except:
        return default

# Custom route for /admin without trailing slash
@admin_bp.route('', methods=['GET'])
def admin_redirect():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('admin.login'))

# Admin Login
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in!', 'info')
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('admin/login.html')
        
        user = AdminUser.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
    
    return render_template('admin/login.html')

# Admin Logout
@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))

# User Management Routes
@admin_bp.route('/users')
@login_required
@require_permission('users.view')
def users():
    """List all admin users"""
    users = AdminUser.query.order_by(AdminUser.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@require_permission('users.create')
def add_user():
    """Add new admin user"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        is_superadmin = request.form.get('is_superadmin') == 'on'
        
        # Validation
        if not username or not email or not password:
            flash('יש למלא את כל השדות הנדרשים', 'error')
            return render_template('admin/edit_user.html', user=None)
        
        if len(username) < 3:
            flash('שם המשתמש חייב להכיל לפחות 3 תווים', 'error')
            return render_template('admin/edit_user.html', user=None)
            
        if len(password) < 6:
            flash('הסיסמה חייבת להכיל לפחות 6 תווים', 'error')
            return render_template('admin/edit_user.html', user=None)
            
        # Check if username or email already exists
        existing_user = AdminUser.query.filter(
            (AdminUser.username == username) | (AdminUser.email == email)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                flash('שם המשתמש כבר קיים במערכת', 'error')
            else:
                flash('כתובת האימייל כבר קיימת במערכת', 'error')
            return render_template('admin/edit_user.html', user=None)
        
        # Create new user
        new_user = AdminUser(
            username=username,
            email=email,
            is_superadmin=is_superadmin
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'המשתמש {username} נוסף בהצלחה!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', user=None)

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@require_permission('users.edit')
def edit_user(user_id):
    """Edit existing admin user"""
    user = AdminUser.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        is_superadmin = request.form.get('is_superadmin') == 'on'
        
        # Validation
        if not username or not email:
            flash('יש למלא את כל השדות הנדרשים', 'error')
            return render_template('admin/edit_user.html', user=user)
        
        if len(username) < 3:
            flash('שם המשתמש חייב להכיל לפחות 3 תווים', 'error')
            return render_template('admin/edit_user.html', user=user)
            
        # Check if username or email already exists (excluding current user)
        existing_user = AdminUser.query.filter(
            ((AdminUser.username == username) | (AdminUser.email == email)) &
            (AdminUser.id != user_id)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                flash('שם המשתמש כבר קיים במערכת', 'error')
            else:
                flash('כתובת האימייל כבר קיימת במערכת', 'error')
            return render_template('admin/edit_user.html', user=user)
        
        # Update user
        user.username = username
        user.email = email
        user.is_superadmin = is_superadmin
        
        # Update password only if provided
        if password and len(password) >= 6:
            user.set_password(password)
        elif password and len(password) < 6:
            flash('הסיסמה חייבת להכיל לפחות 6 תווים', 'error')
            return render_template('admin/edit_user.html', user=user)
        
        db.session.commit()
        
        flash(f'פרטי המשתמש {username} עודכנו בהצלחה!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@require_permission('users.delete')
def delete_user(user_id):
    """Delete admin user"""
    user = AdminUser.query.get_or_404(user_id)
    
    # Prevent deleting self
    if user.id == current_user.id:
        return jsonify({'success': False, 'error': 'לא ניתן למחוק את המשתמש הנוכחי'}), 400
    
    # Prevent deleting the only superadmin
    if user.is_superadmin:
        superadmin_count = AdminUser.query.filter_by(is_superadmin=True).count()
        if superadmin_count <= 1:
            return jsonify({'success': False, 'error': 'לא ניתן למחוק את מנהל המערכת האחרון'}), 400
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'המשתמש {username} נמחק בהצלחה'})

# Newsletter Management
@admin_bp.route('/newsletter')
@login_required
def newsletter():
    """List all newsletter subscribers"""
    subscribers = NewsletterSubscriber.query.order_by(NewsletterSubscriber.subscribed_at.desc()).all()
    active_count = NewsletterSubscriber.query.filter_by(is_active=True).count()
    total_count = NewsletterSubscriber.query.count()
    return render_template('admin/newsletter.html', 
                         subscribers=subscribers,
                         active_count=active_count,
                         total_count=total_count)

@admin_bp.route('/newsletter/export')
@login_required
def newsletter_export():
    """Export newsletter subscribers to CSV"""
    subscribers = NewsletterSubscriber.query.filter_by(is_active=True).all()
    emails = [s.email for s in subscribers]
    return jsonify({'success': True, 'emails': emails, 'count': len(emails)})

@admin_bp.route('/newsletter/delete/<int:subscriber_id>', methods=['POST'])
@login_required
def delete_newsletter_subscriber(subscriber_id):
    """Delete newsletter subscriber"""
    subscriber = NewsletterSubscriber.query.get_or_404(subscriber_id)
    email = subscriber.email
    db.session.delete(subscriber)
    db.session.commit()
    return jsonify({'success': True, 'message': f'המנוי {email} נמחק בהצלחה'})

# Admin Dashboard
@admin_bp.route('/')
@login_required
def dashboard():
    stats = {
        'total_messages': ContactMessage.query.count(),
        'unread_messages': ContactMessage.query.filter_by(is_read=False).count(),
        'total_reservations': Reservation.query.count(),
        'pending_reservations': Reservation.query.filter_by(status='pending').count(),
        'active_branches': Branch.query.filter_by(is_active=True).count(),
        'menu_items': MenuItem.query.count(),
        'gallery_photos': GalleryPhoto.query.count()
    }
    return render_template('admin/dashboard.html', stats=stats)

# Site Settings Management
@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    settings = SiteSettings.query.first()
    if not settings:
        settings = SiteSettings()
        db.session.add(settings)
        db.session.commit()
    
    if request.method == 'POST':
        # General Settings
        settings.site_name_he = request.form.get('site_name_he')
        settings.site_name_en = request.form.get('site_name_en')
        settings.hero_title_he = request.form.get('hero_title_he')
        settings.hero_title_en = request.form.get('hero_title_en')
        settings.hero_subtitle_he = request.form.get('hero_subtitle_he')
        settings.hero_subtitle_en = request.form.get('hero_subtitle_en')
        settings.hero_description_he = request.form.get('hero_description_he')
        settings.hero_description_en = request.form.get('hero_description_en')
        settings.about_title_he = request.form.get('about_title_he')
        settings.about_title_en = request.form.get('about_title_en')
        settings.about_content_he = request.form.get('about_content_he')
        settings.about_content_en = request.form.get('about_content_en')
        settings.facebook_url = request.form.get('facebook_url')
        settings.instagram_url = request.form.get('instagram_url')
        settings.whatsapp_number = request.form.get('whatsapp_number')
        
        # Branding & Media - File Uploads
        if 'hero_desktop_image' in request.files:
            file = request.files['hero_desktop_image']
            if file and file.filename and allowed_image_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                original_ext = filename.rsplit('.', 1)[1].lower()
                filename_base = filename.rsplit('.', 1)[0]
                filename = f'hero_desktop_{timestamp}_{filename_base}.jpg'
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                # Save and optimize image
                try:
                    # Save original first to a temp location
                    temp_path = os.path.join(UPLOAD_FOLDER, f'temp_{timestamp}_{secure_filename(file.filename)}')
                    file.save(temp_path)
                    
                    # Verify file was saved and has content
                    if not os.path.exists(temp_path) or os.path.getsize(temp_path) < 100:
                        raise ValueError(f"Uploaded file is too small or empty: {os.path.getsize(temp_path) if os.path.exists(temp_path) else 0} bytes")
                    
                    # Open and verify image
                    img = Image.open(temp_path)
                    img.verify()  # Verify it's a valid image
                    
                    # Reopen after verify (verify closes the file)
                    img = Image.open(temp_path)
                    
                    # Check image dimensions are reasonable
                    if img.width < 10 or img.height < 10:
                        raise ValueError(f"Image dimensions too small: {img.width}x{img.height}")
                    
                    print(f"Original image: {img.width}x{img.height}, mode: {img.mode}, size: {os.path.getsize(temp_path)} bytes")
                    
                    # Resize if too large
                    if img.width > 1920:
                        ratio = 1920 / img.width
                        new_height = int(img.height * ratio)
                        img = img.resize((1920, new_height), Image.Resampling.LANCZOS)
                        print(f"Resized to: {img.width}x{img.height}")
                    
                    # Convert RGBA to RGB
                    if img.mode == 'RGBA':
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        rgb_img.paste(img, mask=img.split()[3])
                        img = rgb_img
                        print("Converted RGBA to RGB")
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                        print(f"Converted {img.mode} to RGB")
                    
                    # Save optimized version
                    img.save(filepath, 'JPEG', quality=85, optimize=True)
                    
                    # Verify saved file has content
                    if not os.path.exists(filepath) or os.path.getsize(filepath) < 100:
                        raise ValueError(f"Saved file is too small: {os.path.getsize(filepath) if os.path.exists(filepath) else 0} bytes")
                    
                    # Remove temp file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    
                    print(f"Hero image optimized and saved: {filename} ({os.path.getsize(filepath)} bytes)")
                except Exception as e:
                    print(f"Image optimization error: {e}. Saving original file instead.")
                    # If optimization fails, save original file
                    try:
                        if 'temp_path' in locals() and os.path.exists(temp_path):
                            # Copy temp to final location
                            import shutil
                            shutil.copy2(temp_path, filepath)
                            os.remove(temp_path)
                            print(f"Saved original file: {filename} ({os.path.getsize(filepath)} bytes)")
                        else:
                            # Save file directly
                            file.seek(0)
                            file.save(filepath)
                            print(f"Saved file directly: {filename} ({os.path.getsize(filepath)} bytes)")
                    except Exception as e2:
                        print(f"Failed to save file: {e2}")
                        flash(f'Error uploading hero image: {str(e2)}', 'error')
                
                settings.hero_desktop_image = filename
        
        if 'logo_image' in request.files:
            file = request.files['logo_image']
            if file and file.filename and allowed_image_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename_base = filename.rsplit('.', 1)[0]
                original_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'png'
                filename = f'logo_{timestamp}_{filename_base}.{original_ext}'
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                try:
                    temp_path = os.path.join(UPLOAD_FOLDER, f'temp_{timestamp}_{secure_filename(file.filename)}')
                    file.save(temp_path)
                    
                    # Optimize logo (keep transparency if PNG)
                    img = Image.open(temp_path)
                    
                    # Resize if too large (max 500px width for logo)
                    if img.width > 500:
                        ratio = 500 / img.width
                        new_height = int(img.height * ratio)
                        img = img.resize((500, new_height), Image.Resampling.LANCZOS)
                    
                    # Save optimized
                    if original_ext == 'png' and img.mode in ('RGBA', 'LA', 'P'):
                        img.save(filepath, 'PNG', optimize=True)
                    else:
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        img.save(filepath, 'JPEG', quality=90, optimize=True)
                        filename = f'logo_{timestamp}_{filename_base}.jpg'
                        filepath = os.path.join(UPLOAD_FOLDER, filename)
                        img.save(filepath, 'JPEG', quality=90, optimize=True)
                    
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    
                    print(f"Logo image optimized and saved: {filename}")
                except Exception as e:
                    print(f"Logo optimization error: {e}. Saving original file.")
                    if os.path.exists(temp_path):
                        os.rename(temp_path, filepath)
                    else:
                        file.seek(0)
                        file.save(filepath)
                
                settings.logo_image = filename
        
        if 'favicon_image' in request.files:
            file = request.files['favicon_image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'favicon_{timestamp}_{filename}'
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                try:
                    file.save(filepath)
                    print(f"Favicon saved: {filename}")
                except Exception as e:
                    print(f"Favicon save error: {e}")
                    flash(f'Error saving favicon: {str(e)}', 'error')
                
                settings.favicon_image = filename
        
        # Color Scheme
        settings.primary_color = request.form.get('primary_color') or request.form.get('primary_color_text') or '#1a3a6e'
        settings.accent_color = request.form.get('accent_color') or request.form.get('accent_color_text') or '#dc3545'
        
        # Feature Toggles (checkboxes)
        settings.enable_online_ordering = request.form.get('enable_online_ordering') == 'on'
        settings.enable_english_language = request.form.get('enable_english_language') == 'on'
        settings.enable_delivery = request.form.get('enable_delivery') == 'on'
        settings.enable_pickup = request.form.get('enable_pickup') == 'on'
        settings.enable_menu_display = request.form.get('enable_menu_display') == 'on'
        settings.enable_gallery = request.form.get('enable_gallery') == 'on'
        settings.enable_contact_form = request.form.get('enable_contact_form') == 'on'
        settings.enable_table_reservations = request.form.get('enable_table_reservations') == 'on'
        
        # Order & Delivery Settings
        min_order = request.form.get('minimum_order_amount')
        if min_order:
            settings.minimum_order_amount = float(min_order)
        
        delivery_fee = request.form.get('delivery_fee')
        if delivery_fee:
            settings.delivery_fee = float(delivery_fee)
        
        free_delivery = request.form.get('free_delivery_threshold')
        if free_delivery:
            settings.free_delivery_threshold = float(free_delivery)
        
        settings.estimated_delivery_time = request.form.get('estimated_delivery_time') or '45-60'
        
        tax = request.form.get('tax_rate')
        if tax:
            settings.tax_rate = float(tax)
        
        service_fee = request.form.get('service_fee_percentage')
        if service_fee:
            settings.service_fee_percentage = float(service_fee)
        
        settings.currency_symbol = request.form.get('currency_symbol') or '₪'
        
        # Advanced Features
        settings.google_analytics_id = request.form.get('google_analytics_id')
        settings.facebook_pixel_id = request.form.get('facebook_pixel_id')
        settings.maintenance_mode = request.form.get('maintenance_mode') == 'on'
        settings.announcement_enabled = request.form.get('announcement_enabled') == 'on'
        settings.announcement_text_he = request.form.get('announcement_text_he')
        settings.announcement_text_en = request.form.get('announcement_text_en')
        settings.announcement_bg_color = request.form.get('announcement_bg_color') or '#ffc107'
        
        db.session.commit()
        flash('Settings updated successfully! / ההגדרות עודכנו בהצלחה!', 'success')
        return redirect(url_for('admin.settings'))
    
    return render_template('admin/settings.html', settings=settings)

# Payment Settings
@admin_bp.route('/payment-settings', methods=['GET', 'POST'])
@login_required
def payment_settings():
    # Get or create Grow payment provider
    grow = PaymentConfiguration.query.filter_by(provider_name='grow').first()
    if not grow:
        grow = PaymentConfiguration(
            provider_name='grow',
            display_name_he='כרטיס אשראי (Grow)',
            display_name_en='Credit Card (Grow)',
            display_order=1,
            is_active=False
        )
        db.session.add(grow)
    
    # Get or create Max payment provider
    max_provider = PaymentConfiguration.query.filter_by(provider_name='max').first()
    if not max_provider:
        max_provider = PaymentConfiguration(
            provider_name='max',
            display_name_he='כרטיס אשראי (Max)',
            display_name_en='Credit Card (Max)',
            display_order=2,
            is_active=False
        )
        db.session.add(max_provider)
    
    db.session.commit()
    
    if request.method == 'POST':
        # Update Grow settings
        grow.is_active = request.form.get('grow_is_active') == 'on'
        grow.merchant_id = request.form.get('grow_user_id', '')
        grow.api_key = request.form.get('grow_page_code', '')
        grow.api_secret = request.form.get('grow_api_key', '')
        grow.display_name_he = request.form.get('grow_display_name_he', 'כרטיס אשראי')
        grow.display_name_en = request.form.get('grow_display_name_en', 'Credit Card')
        
        # Update Max settings
        max_provider.is_active = request.form.get('max_is_active') == 'on'
        max_provider.merchant_id = request.form.get('max_masof', '')
        max_provider.api_key = request.form.get('max_api_key', '')
        max_provider.display_name_he = request.form.get('max_display_name_he', 'כרטיס אשראי (Max)')
        max_provider.display_name_en = request.form.get('max_display_name_en', 'Credit Card (Max)')
        
        db.session.commit()
        flash('Payment settings updated successfully! / הגדרות התשלום עודכנו בהצלחה!', 'success')
        return redirect(url_for('admin.payment_settings'))
    
    return render_template('admin/payment_settings.html', grow=grow, max_provider=max_provider)

# Media Management
@admin_bp.route('/media')
@login_required
def media():
    media_files = MediaFile.query.order_by(MediaFile.section, MediaFile.display_order).all()
    return render_template('admin/media.html', media_files=media_files)

@admin_bp.route('/media/upload', methods=['POST'])
@login_required
def upload_media():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            
            # Create upload directory if it doesn't exist
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Save file directly - no processing
            file.save(filepath)
            
            # Create database entry
            media = MediaFile(
                filename=filename,
                file_path=f'/static/uploads/{filename}',
                file_type='video' if filename.lower().endswith(('.mp4', '.mov', '.avi')) else 'image',
                section=request.form.get('section', 'gallery'),
                caption_he=request.form.get('caption_he', ''),
                caption_en=request.form.get('caption_en', ''),
                display_order=int(request.form.get('display_order', 0))
            )
            db.session.add(media)
            db.session.commit()
            
            return jsonify({'success': True, 'id': media.id, 'path': media.file_path})
        
        return jsonify({'error': 'Invalid file type. Only images and videos allowed.'}), 400
    
    except Exception as e:
        current_app.logger.error(f"Upload error: {e}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@admin_bp.route('/media/delete/<int:id>', methods=['POST'])
@login_required
def delete_media(id):
    media = MediaFile.query.get_or_404(id)
    
    # Delete file from filesystem
    try:
        file_path = media.file_path.replace('/static/', 'static/')
        if os.path.exists(file_path):
            os.remove(file_path)
    except:
        pass
    
    db.session.delete(media)
    db.session.commit()
    
    return jsonify({'success': True})

# Branch Management
@admin_bp.route('/branches')
@login_required
def branches():
    branches = Branch.query.order_by(Branch.display_order).all()
    return render_template('admin/branches.html', branches=branches)

@admin_bp.route('/branches/edit/<int:id>', methods=['GET', 'POST'])
@admin_bp.route('/branches/new', methods=['GET', 'POST'])
@login_required
def edit_branch(id=None):
    if id:
        branch = Branch.query.get_or_404(id)
    else:
        branch = Branch()
    
    if request.method == 'POST':
        branch.name_he = request.form.get('name_he')
        branch.name_en = request.form.get('name_en')
        branch.address_he = request.form.get('address_he')
        branch.address_en = request.form.get('address_en')
        branch.phone = request.form.get('phone')
        branch.email = request.form.get('email')
        branch.waze_link = request.form.get('waze_link')
        branch.google_maps_link = request.form.get('google_maps_link')
        branch.is_active = request.form.get('is_active') == 'on'
        branch.display_order = int(request.form.get('display_order', 0))
        
        if not id:
            db.session.add(branch)
        
        db.session.commit()
        
        # Update working hours
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        days_he = ['ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת']
        
        for i, (day_en, day_he) in enumerate(zip(days, days_he)):
            wh = WorkingHours.query.filter_by(branch_id=branch.id, day_of_week=i).first()
            if not wh:
                wh = WorkingHours(branch_id=branch.id, day_of_week=i, day_name_en=day_en, day_name_he=day_he)
            
            wh.open_time = request.form.get(f'open_time_{i}', '12:00')
            wh.close_time = request.form.get(f'close_time_{i}', '23:00')
            wh.is_closed = request.form.get(f'is_closed_{i}') == 'on'
            
            db.session.add(wh)
        
        db.session.commit()
        flash('Branch saved successfully!', 'success')
        return redirect(url_for('admin.branches'))
    
    return render_template('admin/edit_branch.html', branch=branch)

@admin_bp.route('/branches/delete/<int:id>', methods=['POST'])
@login_required
def delete_branch(id):
    branch = Branch.query.get_or_404(id)
    db.session.delete(branch)
    db.session.commit()
    return jsonify({'success': True})

# Menu Management
@admin_bp.route('/menu')
@login_required
def menu():
    # Eager load menu items and their dietary properties
    categories = db.session.query(MenuCategory).filter_by(is_active=True).order_by(MenuCategory.display_order).all()
    
    # Load all menu items with their dietary properties
    for category in categories:
        category.menu_items = db.session.query(MenuItem).filter_by(category_id=category.id).order_by(MenuItem.display_order).all()
        for item in category.menu_items:
            # Ensure dietary properties are loaded
            item.dietary_properties = [prop for prop in item.dietary_properties if prop.is_active]
    
    return render_template('admin/menu.html', categories=categories)

@admin_bp.route('/menu/category/edit/<int:id>', methods=['GET', 'POST'])
@admin_bp.route('/menu/category/new', methods=['GET', 'POST'])
@login_required
def edit_category(id=None):
    if id:
        category = MenuCategory.query.get_or_404(id)
    else:
        category = MenuCategory()
    
    if request.method == 'POST':
        category.name_he = request.form.get('name_he')
        category.name_en = request.form.get('name_en')
        category.description_he = request.form.get('description_he')
        category.description_en = request.form.get('description_en')
        category.footer_text_he = request.form.get('footer_text_he')
        category.footer_text_en = request.form.get('footer_text_en')
        category.display_order = int(request.form.get('display_order', 0))
        category.is_active = request.form.get('is_active') == 'on'
        category.show_in_menu = request.form.get('show_in_menu') == 'on'
        category.show_in_order = request.form.get('show_in_order') == 'on'
        category.featured = request.form.get('featured') == 'on'
        category.icon = request.form.get('icon')
        category.color = request.form.get('color')
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_image_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"category_{timestamp}_{filename}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                category.image_path = f'uploads/{filename}'
        
        if not id:
            db.session.add(category)
        
        db.session.commit()
        flash('קטגוריה נשמרה בהצלחה!', 'success')
        return redirect(url_for('admin.menu'))
    
    return render_template('admin/enhanced_category.html', category=category)

@admin_bp.route('/menu/item/<int:item_id>/toggle-availability', methods=['POST'])
@login_required
def toggle_item_availability(item_id):
    """Quick toggle for menu item availability (for mobile-friendly updates)"""
    item = MenuItem.query.get_or_404(item_id)
    
    data = request.get_json() or {}
    item.is_available = data.get('is_available', not item.is_available)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'is_available': item.is_available,
        'message': 'זמינות עודכנה בהצלחה'
    })

@admin_bp.route('/menu/item/edit/<int:id>', methods=['GET', 'POST'])
@admin_bp.route('/menu/item/new', methods=['GET', 'POST'])
@login_required
def edit_menu_item(id=None):
    from flask_wtf import FlaskForm
    
    print(f"DEBUG: Route hit with method: {request.method}, id: {id}")  # Debug line
    
    # Create form for CSRF token (needs to be before any conditional logic)
    form = FlaskForm()
    
    if id:
        item = MenuItem.query.get_or_404(id)
    else:
        item = MenuItem()
    
    categories = MenuCategory.query.filter_by(is_active=True).all()
    dietary_properties = DietaryProperty.query.filter_by(is_active=True).order_by(DietaryProperty.display_order).all()
    
    if request.method == 'POST' and form.validate_on_submit():
        print(f"DEBUG: Form data received: {dict(request.form)}")  # Debug line
        print(f"DEBUG: All form data: {request.form.to_dict(flat=False)}")  # Debug line
        
        # Basic information
        item.category_id = int(request.form.get('category_id'))
        item.name_he = request.form.get('name_he')
        item.name_en = request.form.get('name_en')
        item.description_he = request.form.get('description_he')
        item.description_en = request.form.get('description_en')
        item.short_description_he = request.form.get('short_description_he')
        item.short_description_en = request.form.get('short_description_en')
        item.ingredients_he = request.form.get('ingredients_he')
        item.ingredients_en = request.form.get('ingredients_en')
        
        # Pricing
        item.base_price = float(request.form.get('base_price', 0))
        item.discount_percentage = float(request.form.get('discount_percentage', 0))
        
        # Handle dietary properties (many-to-many relationship)
        selected_property_ids = request.form.getlist('dietary_properties')
        print(f"DEBUG: Selected property IDs: {selected_property_ids}")  # Debug line
        # Clear existing properties
        item.dietary_properties.clear()
        # Add selected properties
        for property_id in selected_property_ids:
            if property_id.isdigit():
                property_obj = DietaryProperty.query.get(int(property_id))
                if property_obj and property_obj.is_active:
                    item.dietary_properties.append(property_obj)
                    print(f"DEBUG: Added property {property_obj.name_he}")  # Debug line
        
        # Operations & Availability
        item.is_available = request.form.get('is_available') == 'on'
        item.allow_delivery = request.form.get('allow_delivery') == 'on'
        item.allow_takeaway = request.form.get('allow_takeaway') == 'on'
        item.prep_time_minutes = int(request.form.get('prep_time_minutes', 0)) if request.form.get('prep_time_minutes') else None
        item.calories = int(request.form.get('calories', 0)) if request.form.get('calories') else None
        item.spice_level = int(request.form.get('spice_level', 0))
        
        # Special offers
        item.special_offer_text_he = request.form.get('special_offer_text_he')
        item.special_offer_text_en = request.form.get('special_offer_text_en')
        
        # Availability schedule
        item.available_from_time = request.form.get('available_from_time')
        item.available_to_time = request.form.get('available_to_time')
        
        # Display settings
        item.display_order = int(request.form.get('display_order', 0))
        
        # Custom tags (JSON)
        custom_tags = request.form.get('custom_tags', '').strip()
        if custom_tags:
            try:
                import json
                item.custom_tags = json.dumps([tag.strip() for tag in custom_tags.split(',') if tag.strip()])
            except:
                item.custom_tags = '[]'
        else:
            item.custom_tags = '[]'
        
        # Allergens (JSON)
        allergens = request.form.get('allergens', '').strip()
        if allergens:
            try:
                import json
                item.allergens = json.dumps([allergen.strip() for allergen in allergens.split(',') if allergen.strip()])
            except:
                item.allergens = '[]'
        else:
            item.allergens = '[]'
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"menu_{timestamp}_{filename}"
                
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                item.image_path = f'/static/uploads/{filename}'
        
        if not id:
            db.session.add(item)
        
        db.session.commit()
        flash('המנה נשמרה בהצלחה! ✓', 'success')
        return redirect(url_for('admin.menu'))
    
    return render_template('admin/enhanced_menu_item.html', form=form, item=item, categories=categories, dietary_properties=dietary_properties)

# Menu Settings Management
@admin_bp.route('/menu/settings')
@login_required
def menu_settings():
    settings = MenuSettings.query.all()
    return render_template('admin/menu_settings.html', settings=settings, get_setting=get_setting)

@admin_bp.route('/menu/settings/save', methods=['POST'])
@login_required
def save_menu_settings():
    settings_data = [
        ('menu_layout', 'Menu Layout Style', request.form.get('menu_layout', 'grid')),
        ('show_prices', 'Show Prices', request.form.get('show_prices', 'true')),
        ('show_images', 'Show Images', request.form.get('show_images', 'true')),
        ('show_dietary_icons', 'Show Dietary Icons', request.form.get('show_dietary_icons', 'true')),
        ('show_spice_level', 'Show Spice Level', request.form.get('show_spice_level', 'true')),
        ('show_prep_time', 'Show Preparation Time', request.form.get('show_prep_time', 'false')),
        ('show_calories', 'Show Calories', request.form.get('show_calories', 'false')),
        ('currency_symbol', 'Currency Symbol', request.form.get('currency_symbol', '₪')),
        ('items_per_page', 'Items Per Page', request.form.get('items_per_page', '12')),
    ]
    
    for key, description, value in settings_data:
        setting = MenuSettings.query.filter_by(setting_key=key).first()
        if setting:
            setting.setting_value = value
            setting.updated_at = datetime.utcnow()
        else:
            setting = MenuSettings(setting_key=key, setting_value=value, description=description)
            db.session.add(setting)
    
    db.session.commit()
    flash('Menu settings saved successfully!', 'success')
    return redirect(url_for('admin.menu_settings'))

@admin_bp.route('/menu/item/<int:item_id>/prices')
@login_required
def manage_item_prices(item_id):
    item = MenuItem.query.get_or_404(item_id)
    prices = MenuItemPrice.query.filter_by(menu_item_id=item_id).order_by(MenuItemPrice.display_order).all()
    return render_template('admin/item_prices.html', item=item, prices=prices)

@admin_bp.route('/menu/item/<int:item_id>/prices/add', methods=['POST'])
@login_required
def add_item_price(item_id):
    price = MenuItemPrice()
    price.menu_item_id = item_id
    price.size_name_he = request.form.get('size_name_he')
    price.size_name_en = request.form.get('size_name_en')
    price.price = float(request.form.get('price'))
    price.is_default = request.form.get('is_default') == 'on'
    price.display_order = int(request.form.get('display_order', 0))
    
    # If this is set as default, unset other defaults
    if price.is_default:
        MenuItemPrice.query.filter_by(menu_item_id=item_id).update({'is_default': False})
    
    db.session.add(price)
    db.session.commit()
    flash('Price option added successfully!', 'success')
    return redirect(url_for('admin.manage_item_prices', item_id=item_id))

@admin_bp.route('/menu/item/<int:item_id>/variations')
@login_required
def manage_item_variations(item_id):
    item = MenuItem.query.get_or_404(item_id)
    variations = MenuItemVariation.query.filter_by(menu_item_id=item_id).order_by(MenuItemVariation.display_order).all()
    return render_template('admin/item_variations.html', item=item, variations=variations)

@admin_bp.route('/menu/item/<int:item_id>/variations/add', methods=['POST'])
@login_required
def add_item_variation(item_id):
    variation = MenuItemVariation()
    variation.menu_item_id = item_id
    variation.variation_type = request.form.get('variation_type')
    variation.name_he = request.form.get('name_he')
    variation.name_en = request.form.get('name_en')
    variation.price_modifier = float(request.form.get('price_modifier', 0))
    variation.is_default = request.form.get('is_default') == 'on'
    variation.display_order = int(request.form.get('display_order', 0))
    
    db.session.add(variation)
    db.session.commit()
    flash('Variation added successfully!', 'success')
    return redirect(url_for('admin.manage_item_variations', item_id=item_id))

# Dietary Properties Management
@admin_bp.route('/menu/dietary-properties')
@login_required
def dietary_properties():
    properties = DietaryProperty.query.order_by(DietaryProperty.display_order).all()
    return render_template('admin/dietary_properties.html', properties=properties)

@admin_bp.route('/menu/dietary-properties/edit/<int:id>', methods=['GET', 'POST'])
@admin_bp.route('/menu/dietary-properties/new', methods=['GET', 'POST'])
@login_required
def edit_dietary_property(id=None):
    if id:
        prop = DietaryProperty.query.get_or_404(id)
    else:
        prop = DietaryProperty()
    
    if request.method == 'POST':
        prop.name_he = request.form.get('name_he')
        prop.name_en = request.form.get('name_en')
        prop.icon = request.form.get('icon')
        prop.color = request.form.get('color')
        prop.description_he = request.form.get('description_he')
        prop.description_en = request.form.get('description_en')
        prop.is_active = request.form.get('is_active') == 'on'
        prop.display_order = int(request.form.get('display_order', 0))
        
        if not id:
            db.session.add(prop)
        
        db.session.commit()
        flash('Dietary property saved successfully!', 'success')
        return redirect(url_for('admin.dietary_properties'))
    
    return render_template('admin/edit_dietary_property.html', property=prop)

@admin_bp.route('/menu/dietary-properties/toggle/<int:id>', methods=['POST'])
def toggle_dietary_property(id):
    # Check if user is logged in manually (bypass login_required for API)
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        prop = DietaryProperty.query.get_or_404(id)
        data = request.get_json() if request.is_json else request.form
        is_active = data.get('is_active', False)
        
        # Handle both boolean and string values
        if isinstance(is_active, str):
            is_active = is_active.lower() in ['true', '1', 'on', 'yes']
        
        prop.is_active = bool(is_active)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'property_id': id, 
            'new_status': prop.is_active
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/menu/dietary-properties/delete/<int:id>', methods=['POST'])
@login_required
def delete_dietary_property(id):
    # Skip CSRF validation for admin API endpoints
    from flask import current_app
    current_app.config['WTF_CSRF_ENABLED'] = False
    
    prop = DietaryProperty.query.get_or_404(id)
    db.session.delete(prop)
    db.session.commit()
    
    current_app.config['WTF_CSRF_ENABLED'] = True  # Re-enable CSRF
    return jsonify({'success': True})

@admin_bp.route('/menu/dietary-properties/reorder', methods=['POST'])
@login_required
def reorder_dietary_properties():
    property_ids = request.json.get('property_ids', [])
    for index, property_id in enumerate(property_ids):
        prop = DietaryProperty.query.get(property_id)
        if prop:
            prop.display_order = index
            db.session.add(prop)
    db.session.commit()
    return jsonify({'success': True})

# Menu Item Reordering System
@admin_bp.route('/menu/reorder')
@login_required
def menu_reorder():
    categories = MenuCategory.query.filter_by(is_active=True).order_by(MenuCategory.display_order).all()
    
    # Get menu items grouped by category
    menu_data = {}
    for category in categories:
        items_list = MenuItem.query.filter_by(category_id=category.id).order_by(MenuItem.display_order).all()
        menu_data[category.id] = {
            'category': category,
            'items': items_list
        }
    
    # Get items without category
    uncategorized_items = MenuItem.query.filter_by(category_id=None).order_by(MenuItem.display_order).all()
    
    return render_template('admin/menu_reorder.html', 
                         menu_data=menu_data, 
                         categories=categories,
                         uncategorized_items=uncategorized_items)

@admin_bp.route('/menu/reorder/items', methods=['POST'])
@login_required
def reorder_menu_items():
    item_orders = request.json.get('item_orders', {})
    
    for item_id, order_data in item_orders.items():
        item = MenuItem.query.get(int(item_id))
        if item:
            item.display_order = order_data['order']
            if 'category_id' in order_data:
                item.category_id = order_data['category_id'] if order_data['category_id'] != 'null' else None
            db.session.add(item)
    
    db.session.commit()
    return jsonify({'success': True})

@admin_bp.route('/menu/reorder/categories', methods=['POST'])
@login_required
def reorder_categories():
    category_ids = request.json.get('category_ids', [])
    for index, category_id in enumerate(category_ids):
        category = MenuCategory.query.get(category_id)
        if category:
            category.display_order = index
            db.session.add(category)
    db.session.commit()
    return jsonify({'success': True})

# CSV/Excel Import System
@admin_bp.route('/menu/import')
@login_required
def menu_import():
    return render_template('admin/menu_import.html')

@admin_bp.route('/menu/import/upload', methods=['POST'])
@login_required
def upload_csv():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('admin.menu_import'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('admin.menu_import'))
    
    if file and allowed_csv_file(file.filename):
        # Create upload directory if it doesn't exist
        os.makedirs(CSV_UPLOAD_FOLDER, exist_ok=True)
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(CSV_UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Read and preview the file
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath, encoding='utf-8')
            else:  # Excel files
                df = pd.read_excel(filepath)
            
            # Get first 5 rows for preview
            preview_data = df.head(5).to_dict('records')
            columns = list(df.columns)
            total_rows = len(df)
            
            # Get existing categories and dietary properties for mapping
            categories = MenuCategory.query.filter_by(is_active=True).all()
            dietary_properties = DietaryProperty.query.filter_by(is_active=True).all()
            
            return render_template('admin/csv_column_mapping.html', 
                                 filename=filename,
                                 columns=columns,
                                 preview_data=preview_data,
                                 total_rows=total_rows,
                                 categories=categories,
                                 dietary_properties=dietary_properties)
        
        except Exception as e:
            flash(f'Error reading file: {str(e)}', 'error')
            return redirect(url_for('admin.menu_import'))
    
    flash('Invalid file format. Please upload CSV, XLS, or XLSX files only.', 'error')
    return redirect(url_for('admin.menu_import'))

@admin_bp.route('/menu/import/process', methods=['POST'])
@login_required
def process_csv_import():
    filename = request.form.get('filename')
    if not filename:
        flash('No file to process', 'error')
        return redirect(url_for('admin.menu_import'))
    
    filepath = os.path.join(CSV_UPLOAD_FOLDER, filename)
    if not os.path.exists(filepath):
        flash('File not found', 'error')
        return redirect(url_for('admin.menu_import'))
    
    # Get column mappings from form
    mappings = {}
    for field in ['name_he', 'name_en', 'description_he', 'description_en', 'price', 'category', 'ingredients_he', 'ingredients_en']:
        column = request.form.get(f'mapping_{field}')
        if column and column != '':
            mappings[field] = column
    
    # Read the file
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath, encoding='utf-8')
        else:
            df = pd.read_excel(filepath)
        
        success_count = 0
        error_count = 0
        errors = []
        
        # Get default category if specified
        default_category_id = request.form.get('default_category')
        if default_category_id == '':
            default_category_id = None
        else:
            default_category_id = int(default_category_id) if default_category_id else None
        
        # Process each row
        for index, row in df.iterrows():
            try:
                # Create new menu item
                item = MenuItem()
                
                # Map basic fields
                if 'name_he' in mappings:
                    item.name_he = str(row[mappings['name_he']]) if pd.notna(row[mappings['name_he']]) else ''
                if 'name_en' in mappings:
                    item.name_en = str(row[mappings['name_en']]) if pd.notna(row[mappings['name_en']]) else ''
                if 'description_he' in mappings:
                    item.description_he = str(row[mappings['description_he']]) if pd.notna(row[mappings['description_he']]) else ''
                if 'description_en' in mappings:
                    item.description_en = str(row[mappings['description_en']]) if pd.notna(row[mappings['description_en']]) else ''
                if 'ingredients_he' in mappings:
                    item.ingredients_he = str(row[mappings['ingredients_he']]) if pd.notna(row[mappings['ingredients_he']]) else ''
                if 'ingredients_en' in mappings:
                    item.ingredients_en = str(row[mappings['ingredients_en']]) if pd.notna(row[mappings['ingredients_en']]) else ''
                
                # Handle price
                if 'price' in mappings and pd.notna(row[mappings['price']]):
                    try:
                        item.base_price = float(row[mappings['price']])
                    except:
                        item.base_price = 0
                
                # Handle category
                if 'category' in mappings and pd.notna(row[mappings['category']]):
                    category_name = str(row[mappings['category']])
                    category = MenuCategory.query.filter(
                        (MenuCategory.name_he == category_name) | 
                        (MenuCategory.name_en == category_name)
                    ).first()
                    if category:
                        item.category_id = category.id
                    else:
                        item.category_id = default_category_id
                else:
                    item.category_id = default_category_id
                
                # Set default values
                item.is_available = True
                item.display_order = index
                
                # Validate required fields
                if not item.name_he and not item.name_en:
                    errors.append(f'Row {index + 2}: Missing both Hebrew and English names')
                    error_count += 1
                    continue
                
                db.session.add(item)
                success_count += 1
                
            except Exception as e:
                errors.append(f'Row {index + 2}: {str(e)}')
                error_count += 1
        
        # Commit all changes
        try:
            db.session.commit()
            flash(f'Import completed! {success_count} items imported successfully.', 'success')
            if error_count > 0:
                flash(f'{error_count} items had errors and were skipped.', 'warning')
        except Exception as e:
            db.session.rollback()
            flash(f'Database error during import: {str(e)}', 'error')
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        return render_template('admin/import_results.html', 
                             success_count=success_count,
                             error_count=error_count,
                             errors=errors)
    
    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'error')
        return redirect(url_for('admin.menu_import'))

# Delete menu items and categories
@admin_bp.route('/menu/item/delete/<int:id>', methods=['POST'])
@login_required
def delete_menu_item(id):
    item = MenuItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True})

@admin_bp.route('/menu/category/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    category = MenuCategory.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({'success': True})

# ===== EXCEL MENU UPLOAD SYSTEM =====

@admin_bp.route('/menu/excel-upload')
@login_required  
def excel_menu_upload():
    """Excel menu upload interface with field mapping"""
    branches = Branch.query.filter_by(is_active=True).all()
    categories = MenuCategory.query.filter_by(is_active=True).all()
    return render_template('admin/excel_menu_upload.html', 
                         branches=branches, 
                         categories=categories)

@admin_bp.route('/menu/excel-upload/simple', methods=['POST'])
@login_required
def simple_excel_upload():
    """Direct Excel processing - bypass complex mapping"""
    try:
        if 'excel_file' not in request.files:
            flash('❌ לא נבחר קובץ Excel', 'error')
            return redirect(url_for('admin.excel_menu_upload'))
            
        file = request.files['excel_file']
        branch_id = request.form.get('branch_id')
        
        if not file.filename or not branch_id:
            flash('❌ חסרים נתונים', 'error')
            return redirect(url_for('admin.excel_menu_upload'))
        
        # Direct processing with pandas
        import pandas as pd
        from flask import session
        df = pd.read_excel(file)
        
        # Your Excel structure: category name, dish name, description, price
        df.columns = df.columns.astype(str).str.strip()
        
        current_app.logger.info(f"Excel columns: {list(df.columns)}")
        current_app.logger.info(f"Excel rows: {len(df)}")
        
        processed_items = []
        current_category = ''
        categories_created = {}  # Track created categories
        
        for index, row in df.iterrows():
            # Handle your exact column names
            category = str(row.get('category name', '')).strip() if pd.notna(row.get('category name')) else ''
            name = str(row.get('dish name', '')).strip() if pd.notna(row.get('dish name')) else ''
            description = str(row.get('description', '')).strip() if pd.notna(row.get('description')) else ''
            price = str(row.get('price', '')).strip() if pd.notna(row.get('price')) else ''
            
            # Category inheritance (Excel pattern)
            if category:
                current_category = category
            elif current_category:
                category = current_category
                
            # Only process rows with name and price
            if name and price:
                # Auto-create category if needed
                category_id = None
                if category and category not in categories_created:
                    # Check if category exists in database
                    existing_cat = MenuCategory.query.filter_by(name_he=category).first()
                    if existing_cat:
                        category_id = existing_cat.id
                        categories_created[category] = existing_cat.id
                    else:
                        # Create new category
                        new_category = MenuCategory(
                            name_he=category,
                            name_en=category,  # Default to same as Hebrew
                            display_order=len(categories_created) + 1,
                            is_active=True
                        )
                        db.session.add(new_category)
                        db.session.flush()  # Get ID without committing
                        category_id = new_category.id
                        categories_created[category] = category_id
                        current_app.logger.info(f"Created category: {category} with ID: {category_id}")
                elif category in categories_created:
                    category_id = categories_created[category]
                
                # Handle complex pricing like "56/62"
                price_parts = str(price).split('/')
                base_price = price_parts[0].strip()
                alt_price = price_parts[1].strip() if len(price_parts) > 1 else ''
                
                # Create object structure that template expects
                class SimpleItem:
                    def __init__(self, name, category, description, base_price, alt_price, has_multiple, cat_id):
                        self.item_id = f"item_{len(processed_items)}"
                        self.mapped_fields = {
                            'name': name,
                            'category': category,
                            'description': description
                        }
                        self.pricing = {
                            'base_price': base_price,
                            'alt_price': alt_price,
                            'has_multiple_prices': has_multiple
                        }
                        self.category_id = cat_id  # Store category ID for selection
                
                item = SimpleItem(name, category, description, base_price, alt_price, len(price_parts) > 1, category_id)
                processed_items.append(item)
        
        current_app.logger.info(f"Processed {len(processed_items)} items")
        current_app.logger.info(f"Created {len(categories_created)} categories: {list(categories_created.keys())}")
        
        # Commit all category creations
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error committing categories: {str(e)}")
        
        # No session storage needed - direct form processing
        
        return render_template('admin/excel_dish_settings.html',
                             items=processed_items,
                             categories=MenuCategory.query.filter_by(is_active=True).all(),
                             dietary_properties=DietaryProperty.query.filter_by(is_active=True).all(),
                             branch_id=branch_id)
                             
    except Exception as e:
        current_app.logger.error(f"Simple Excel upload error: {str(e)}")
        flash(f'❌ שגיאה: {str(e)}', 'error')
        return redirect(url_for('admin.excel_menu_upload'))

@admin_bp.route('/menu/excel-upload/process', methods=['POST'])
@login_required
def process_excel_upload():
    """Process uploaded Excel file and show field mapping interface"""
    try:
        if 'excel_file' not in request.files:
            flash('❌ לא נבחר קובץ Excel', 'error')
            return redirect(url_for('admin.excel_menu_upload'))
            
        file = request.files['excel_file']
        if file.filename == '':
            flash('❌ לא נבחר קובץ', 'error')
            return redirect(url_for('admin.excel_menu_upload'))
            
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            flash('❌ הקובץ חייב להיות בפורמט Excel (.xlsx או .xls)', 'error')
            return redirect(url_for('admin.excel_menu_upload'))
            
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"menu_upload_{timestamp}_{filename}"
        
        upload_path = os.path.join('temp_uploads', filename)
        os.makedirs('temp_uploads', exist_ok=True)
        file.save(upload_path)
        
        # Parse Excel file 
        import pandas as pd
        try:
            # Try to read all sheets
            excel_data = pd.read_excel(upload_path, sheet_name=None)
            
            parsed_data = {
                'file_path': upload_path,
                'filename': file.filename,
                'sheets': {},
                'suggested_mapping': {}
            }
            
            # Analyze each sheet
            for sheet_name, df in excel_data.items():
                # Clean column names
                df.columns = df.columns.astype(str).str.strip()
                
                sheet_info = {
                    'name': sheet_name,
                    'rows': len(df),
                    'columns': list(df.columns),
                    'sample_data': df.head(10).to_dict('records'),
                    'column_types': {col: str(dtype) for col, dtype in df.dtypes.to_dict().items()}
                }
                
                parsed_data['sheets'][sheet_name] = sheet_info
                
                # Suggest field mapping based on column names
                suggested_mapping = {}
                for col in df.columns:
                    col_lower = col.lower()
                    if any(word in col_lower for word in ['category', 'קטגוריה', 'סוג']):
                        suggested_mapping[col] = 'category'
                    elif any(word in col_lower for word in ['name', 'שם', 'מנה', 'dish']):
                        suggested_mapping[col] = 'name'
                    elif any(word in col_lower for word in ['desc', 'תיאור', 'description']):
                        suggested_mapping[col] = 'description' 
                    elif any(word in col_lower for word in ['price', 'מחיר', 'cost']):
                        suggested_mapping[col] = 'price'
                    elif any(word in col_lower for word in ['image', 'תמונה', 'photo']):
                        suggested_mapping[col] = 'image'
                
                parsed_data['suggested_mapping'][sheet_name] = suggested_mapping
            
            # Store in session for next step
            from flask import session
            session['excel_upload_data'] = parsed_data
            
            branches = Branch.query.filter_by(is_active=True).all()
            categories = MenuCategory.query.filter_by(is_active=True).all()
            
            return render_template('admin/excel_field_mapping.html',
                                 data=parsed_data,
                                 branches=branches,
                                 categories=categories)
                                 
        except Exception as e:
            current_app.logger.error(f"Excel parsing error: {str(e)}")
            flash(f'❌ שגיאה בקריאת קובץ Excel: {str(e)}', 'error')
            return redirect(url_for('admin.excel_menu_upload'))
            
    except Exception as e:
        current_app.logger.error(f"Excel upload error: {str(e)}")
        flash(f'❌ שגיאה בהעלאת הקובץ: {str(e)}', 'error')
        return redirect(url_for('admin.excel_menu_upload'))

@admin_bp.route('/menu/excel-upload/mapping', methods=['POST'])
@login_required
def process_excel_mapping():
    """Process field mapping and show comprehensive dish settings"""
    try:
        from flask import session
        excel_data = session.get('excel_upload_data')
        if not excel_data:
            flash('❌ לא נמצאו נתוני Excel. אנא התחל מחדש.', 'error')
            return redirect(url_for('admin.excel_menu_upload'))
            
        branch_id = request.form.get('branch_id')
        if not branch_id:
            flash('❌ לא נבחר סניף', 'error')
            return redirect(url_for('admin.excel_menu_upload'))
            
        # Parse mapping from form data
        mapping_data = {}
        for key, value in request.form.items():
            if key.startswith('mapping['):
                # Extract sheet and column from key like "mapping[Sheet1][column_name]"
                parts = key.replace('mapping[', '').replace(']', '').split('][')
                if len(parts) == 2:
                    sheet_name, column_name = parts
                    if sheet_name not in mapping_data:
                        mapping_data[sheet_name] = {}
                    mapping_data[sheet_name][column_name] = value
        
        # Debug: log the mapping data
        current_app.logger.info(f"Mapping data received: {mapping_data}")
        
        # Process Excel data with mapping
        import pandas as pd
        processed_items = []
        
        for sheet_name, mapping in mapping_data.items():
            if sheet_name not in excel_data['sheets']:
                continue
                
            # Read the Excel file again with proper handling
            df = pd.read_excel(excel_data['file_path'], sheet_name=sheet_name)
            df.columns = df.columns.astype(str).str.strip()
            
            # Reverse mapping for easier access
            field_to_column = {v: k for k, v in mapping.items() if v and v != 'ignore'}
            
            # Debug: log the field mapping
            current_app.logger.info(f"Field to column mapping for {sheet_name}: {field_to_column}")
            
            current_category = ''
            
            for index, row in df.iterrows():
                item_data = {
                    'sheet_name': sheet_name,
                    'row_index': index,
                    'original_data': dict(row),
                    'mapped_fields': {}
                }
                
                # Map fields according to user's mapping
                for field, column in field_to_column.items():
                    if column in row and pd.notna(row[column]) and str(row[column]).strip():
                        item_data['mapped_fields'][field] = str(row[column]).strip()
                
                # Handle category grouping (Excel pattern where category appears once)
                if 'category' in item_data['mapped_fields']:
                    current_category = item_data['mapped_fields']['category']
                elif current_category:
                    item_data['mapped_fields']['category'] = current_category
                
                # Debug: log mapped fields for first few items
                if index < 3:
                    current_app.logger.info(f"Row {index} mapped fields: {item_data['mapped_fields']}")
                
                # Only include items with required fields
                if 'name' in item_data['mapped_fields'] and 'price' in item_data['mapped_fields']:
                    # Handle complex pricing (like "56/62")
                    price_str = item_data['mapped_fields']['price']
                    price_parts = str(price_str).split('/')
                    
                    item_data['pricing'] = {
                        'base_price': price_parts[0].strip() if price_parts else '',
                        'alt_price': price_parts[1].strip() if len(price_parts) > 1 else '',
                        'has_multiple_prices': len(price_parts) > 1
                    }
                    
                    # Generate unique ID for each item
                    item_data['item_id'] = f"{sheet_name}_{index}"
                    
                    processed_items.append(item_data)
                else:
                    # Debug: log why item was skipped
                    if index < 5:
                        current_app.logger.info(f"Row {index} skipped - missing required fields. Has name: {'name' in item_data['mapped_fields']}, Has price: {'price' in item_data['mapped_fields']}")
        
        # Debug: log final count
        current_app.logger.info(f"Total processed items: {len(processed_items)}")
        
        # Store processed data in session
        session['processed_excel_items'] = {
            'items': processed_items,
            'branch_id': branch_id,
            'original_data': excel_data
        }
        
        # Get categories and other data for the settings interface
        categories = MenuCategory.query.filter_by(is_active=True).all()
        dietary_properties = DietaryProperty.query.filter_by(is_active=True).all()
        
        return render_template('admin/excel_dish_settings.html',
                             items=processed_items,
                             categories=categories, 
                             dietary_properties=dietary_properties,
                             branch_id=branch_id)
        
    except Exception as e:
        current_app.logger.error(f"Mapping processing error: {str(e)}")
        flash(f'❌ שגיאה בעיבוד המיפוי: {str(e)}', 'error')
        return redirect(url_for('admin.excel_menu_upload'))

@admin_bp.route('/menu/excel-upload/finalize-direct', methods=['POST'])
@login_required
def finalize_direct_excel_import():
    """Direct Excel import without session storage"""
    try:
        branch_id = request.form.get('branch_id')
        selected_items = request.form.getlist('selected_items[]')
        
        if not selected_items:
            flash('❌ לא נבחרו מנות לייבוא', 'error')
            return redirect(request.referrer)
            
        success_count = 0
        error_count = 0
        errors = []
        
        for item_id in selected_items:
            try:
                # Get form data for this item
                item_prefix = f'items[{item_id}]'
                name = request.form.get(f'{item_prefix}[name]')
                category_id = request.form.get(f'{item_prefix}[category_id]')
                description = request.form.get(f'{item_prefix}[description]')
                base_price = request.form.get(f'{item_prefix}[base_price]')
                alt_price = request.form.get(f'{item_prefix}[alt_price]')
                preparation_time = request.form.get(f'{item_prefix}[preparation_time]')
                spice_level = request.form.get(f'{item_prefix}[spice_level]')
                
                if not name or not base_price:
                    error_count += 1
                    errors.append(f'חסרים נתונים בסיסיים עבור מנה: {name or item_id}')
                    continue
                
                # Create menu item
                menu_item = MenuItem(
                    name_he=name,
                    name_en='',  # Leave English name empty to avoid duplication
                    description_he=description or '',
                    description_en='',  # Leave English description empty  
                    base_price=float(base_price),
                    category_id=int(category_id) if category_id else None,
                    is_available=True,
                    prep_time_minutes=int(preparation_time) if preparation_time else None
                )
                
                # Handle spice level
                if spice_level:
                    menu_item.spice_level = spice_level
                
                # Handle alternative price
                if alt_price and alt_price.strip():
                    try:
                        menu_item.alt_price = float(alt_price)
                    except ValueError:
                        pass
                
                db.session.add(menu_item)
                db.session.flush()  # Get ID
                
                # Handle dietary properties
                dietary_properties = request.form.getlist(f'{item_prefix}[dietary_properties][]')
                for prop_id in dietary_properties:
                    if prop_id:
                        menu_item.dietary_properties.append(DietaryProperty.query.get(int(prop_id)))
                
                success_count += 1
                current_app.logger.info(f"Successfully imported: {name}")
                
            except Exception as e:
                error_count += 1
                errors.append(f'שגיאה בייבוא {name if "name" in locals() else item_id}: {str(e)}')
                current_app.logger.error(f"Error importing item {item_id}: {str(e)}")
                continue
        
        # Commit all changes
        try:
            db.session.commit()
            current_app.logger.info(f"Successfully committed {success_count} items")
        except Exception as e:
            db.session.rollback()
            flash(f'❌ שגיאה בשמירת הנתונים: {str(e)}', 'error')
            return redirect(request.referrer)
        
        # Success message
        if success_count > 0:
            flash(f'✅ יובאו בהצלחה {success_count} מנות!', 'success')
        if error_count > 0:
            flash(f'⚠️ {error_count} מנות נכשלו בייבוא', 'warning')
            for error in errors[:5]:  # Show first 5 errors
                flash(f'📝 {error}', 'info')
        
        return redirect(url_for('admin.menu'))
        
    except Exception as e:
        current_app.logger.error(f"Direct import error: {str(e)}")
        flash(f'❌ שגיאה כללית: {str(e)}', 'error')
        return redirect(url_for('admin.excel_menu_upload'))

@admin_bp.route('/menu/excel-upload/finalize', methods=['POST'])
@login_required
def finalize_excel_import():
    """Finalize Excel import by saving selected dishes to database"""
    try:
        from flask import session
        processed_data = session.get('processed_excel_items')
        if not processed_data:
            flash('❌ לא נמצאו נתונים לייבוא. אנא התחל מחדש.', 'error')
            return redirect(url_for('admin.excel_menu_upload'))
            
        branch_id = request.form.get('branch_id')
        selected_items = request.form.getlist('selected_items[]')
        
        if not selected_items:
            flash('❌ לא נבחרו מנות לייבוא', 'error')
            return redirect(request.referrer)
            
        success_count = 0
        error_count = 0
        errors = []
        
        for item_id in selected_items:
            try:
                # Find original item data
                original_item = None
                for item in processed_data['items']:
                    if item['item_id'] == item_id:
                        original_item = item
                        break
                        
                if not original_item:
                    error_count += 1
                    errors.append(f'לא נמצא פריט: {item_id}')
                    continue
                
                # Get form data for this item
                item_prefix = f'items[{item_id}]'
                name = request.form.get(f'{item_prefix}[name]')
                category_id = request.form.get(f'{item_prefix}[category_id]')
                description = request.form.get(f'{item_prefix}[description]')
                base_price = request.form.get(f'{item_prefix}[base_price]')
                alt_price = request.form.get(f'{item_prefix}[alt_price]')
                preparation_time = request.form.get(f'{item_prefix}[preparation_time]')
                spice_level = request.form.get(f'{item_prefix}[spice_level]')
                
                if not name or not base_price:
                    error_count += 1
                    errors.append(f'שדות חובה חסרים עבור: {name or item_id}')
                    continue
                
                # Create new menu item
                menu_item = MenuItem(
                    name_he=name,
                    name_en=name,  # Default to Hebrew name
                    description_he=description or '',
                    description_en=description or '',
                    price=float(base_price),
                    category_id=int(category_id) if category_id else None,
                    branch_id=int(branch_id),
                    is_available=True,
                    is_featured=False,
                    preparation_time=int(preparation_time) if preparation_time else None,
                    spice_level=spice_level,
                    created_by=current_user.id
                )
                
                # Handle alternative pricing if exists
                if alt_price and alt_price.strip():
                    menu_item.alt_price = float(alt_price)
                
                db.session.add(menu_item)
                db.session.flush()  # Get the ID
                
                # Add dietary properties if selected
                dietary_props = request.form.getlist(f'{item_prefix}[dietary_properties][]')
                for prop_id in dietary_props:
                    if prop_id:
                        dietary_prop = DietaryProperty.query.get(int(prop_id))
                        if dietary_prop:
                            menu_item.dietary_properties.append(dietary_prop)
                
                # Handle image upload if provided
                image_file = request.files.get(f'{item_prefix}[image]')
                if image_file and image_file.filename:
                    try:
                        # Save image (implement based on your image handling system)
                        filename = secure_filename(image_file.filename)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"menu_{timestamp}_{filename}"
                        
                        image_path = os.path.join('static', 'uploads', 'menu', filename)
                        os.makedirs(os.path.dirname(image_path), exist_ok=True)
                        image_file.save(image_path)
                        
                        menu_item.image_url = f'/static/uploads/menu/{filename}'
                    except Exception as e:
                        current_app.logger.warning(f"Image upload failed for {name}: {str(e)}")
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f'שגיאה בייבוא {name or item_id}: {str(e)}')
                current_app.logger.error(f"Item import error: {str(e)}")
        
        # Commit all changes
        if success_count > 0:
            db.session.commit()
            
            # Clean up temporary files
            if processed_data.get('original_data', {}).get('file_path'):
                try:
                    os.remove(processed_data['original_data']['file_path'])
                except:
                    pass
            
            # Clear session data
            session.pop('excel_upload_data', None)
            session.pop('processed_excel_items', None)
            
        flash(f'✅ יובאו בהצלחה {success_count} מנות!', 'success')
        
        if error_count > 0:
            flash(f'⚠️ {error_count} מנות נכשלו בייבוא', 'warning')
            for error in errors[:5]:  # Show first 5 errors
                flash(f'• {error}', 'warning')
                
        return redirect(url_for('admin.menu'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Excel import finalization error: {str(e)}")
        flash(f'❌ שגיאה בסיום הייבוא: {str(e)}', 'error')
        return redirect(url_for('admin.excel_menu_upload'))

# ===== MENU PARSING FROM WORD DOCUMENTS =====

@admin_bp.route('/menu/parse-word', methods=['GET', 'POST'])
@login_required
def parse_word_menu():
    """Parse menu items from Word document content"""
    branches = Branch.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        try:
            # Get form data
            branch_id = request.form.get('branch_id')
            menu_content = request.form.get('menu_content')
            
            if not branch_id or not menu_content:
                flash('נא לבחור סניף ולהדביק את תוכן התפריט', 'error')
                return render_template('admin/parse_word_menu.html', branches=branches)
            
            # Import parser class
            from menu_parser import MenuParser
            parser = MenuParser()
            
            # Parse and get potential items for manual selection
            result = parser.parse_word_menu_simple(menu_content)
            
            if result['potential_items']:
                categories = MenuCategory.query.filter_by(is_active=True).all()
                flash(f'🔍 נמצאו {result["total_found"]} פריטים אפשריים. בחר אילו לייבא:', 'info')
                return render_template('admin/menu_selection.html', 
                                     items=result['potential_items'],
                                     branch_id=branch_id,
                                     categories=categories,
                                     result=result)
            else:
                flash('❌ לא נמצאו פריטים בפורמט הנכון. וודא שהמחירים מופיעים אחרי שמות המנות.', 'warning')
                
        except Exception as e:
            current_app.logger.error(f"Menu parsing error: {str(e)}")
            flash(f'❌ שגיאה בעיבוד התפריט: {str(e)}', 'error')
    
    categories = MenuCategory.query.filter_by(is_active=True).all()
    return render_template('admin/parse_word_menu.html', branches=branches, categories=categories)

@admin_bp.route('/menu/parse-word/process-selection', methods=['POST'])
@login_required  
def process_menu_selection():
    """Process user's selected menu items"""
    try:
        branch_id = request.form.get('branch_id')
        selected_items_json = request.form.get('selected_items')
        
        if not branch_id or not selected_items_json:
            flash('נתונים חסרים', 'error')
            return redirect(url_for('admin.parse_word_menu'))
        
        import json
        selected_items = json.loads(selected_items_json)
        
        # Import parser class
        from menu_parser import MenuParser
        parser = MenuParser()
        
        # Process only selected items
        result = parser.process_selected_items(
            selected_items=selected_items,
            branch_id=int(branch_id),
            uploaded_by=current_user.id
        )
        
        if result['success']:
            flash(f'✅ הייבוא הושלם! נוספו {result["items_added"]} פריטים', 'success')
            return redirect(url_for('admin.menu'))
        else:
            flash('❌ שגיאה בייבוא הפריטים', 'error')
            return redirect(url_for('admin.parse_word_menu'))
            
    except Exception as e:
        current_app.logger.error(f"Selection processing error: {str(e)}")
        flash(f'❌ שגיאה: {str(e)}', 'error')
        return redirect(url_for('admin.parse_word_menu'))

@admin_bp.route('/menu/parse-word/demo', methods=['POST'])
@login_required
def parse_word_menu_demo():
    """Parse the demo menu content provided by user"""
    try:
        branch_id = request.form.get('branch_id')
        if not branch_id:
            return jsonify({'error': 'נא לבחור סניף'}), 400
        
        # Demo menu content from the user's Word document
        demo_content = """ראשונות

56
הביס היפני
לחם חלב יפני מושחם, קרם אבוקדו, סביצ'ה דג לבן בתיבול יוזו, צילי חריף ,כוסברה ונענע

62
סלט טרופי 
מיקס חסה, בצל סגול, פרי טרופי, שירי צבעים, אבוקדו, קרוטונים אסייתים

34
קימצ'י קוריאני 

52
סלט ויאטנמי 
אטריות זכוכית, מלפפון, כרוב סגול, גזר, בצל ירוק,נבטים סינים​ ברוטב בוטנים ויאטנמי

28
חמוצים יפנים 

56/62
הקיסר האסייתי
חסה ליטל ג'ם, תירס אומאמי, בצל סגול, צלפים ,קלמארי פריך / עוף צלוי

38
אדממה של סומו 

58
קריספי רייס 
4 יח' קריספי מיני מאקי במילוי טרטר סלמון פיקנטי, שמנת, עירית.

42/32
אגרול ירקות/עוף
2 יח' אגרול ירקות/עוף - מוגש על מצע חסה אסייתית, צילי חריף, נענע, כוסברה ומתבלים אסייתיים

42/32
נאמס ירקות/עוף 
2 יח' ספרינג רול וויאטנמי במילוי ירקות/עוף על מצע חסה אסייתית, צ'ילי חריף, נענע, כוסברה ומתבלים אסייתיים

52
שרימפס פינגרז
שרימפס פינגרז 4 יח' עם רוטב טרטר ולימון

68
טטאקי סינטה כבושה
סינטה עגל בכבישה קרה, איולי כמהין ,איולי יוזו, עירית קצוצה וזסט לימון

58
קלמארי פריך
קלמרי מטוגן בציפוי פריך, מוגש עם רוטב חמוץ מתוק ו לימון​ 

58
פופ שרימפס
קוביות שרימפס בטמפורה עטופות באיולי יוזו, תבלין אומאמי​ ,עירית

ווק

60
סמוקי
אטריות ביצים, כרוב לבן, גזר, פטריות, באק צ'וי, אווז מעושן, בצל קריספי ברוטב טריאקי מעושן - תוספת עוף 12/ בקר 15/ שרימפס 20/ טופו 12

56
פאד תאי 
אטריות אורז, כרוב, גזר, בצל ירוק, נבטים סינים, שבבי בוטנים וכוסברה  - תוספת עוף 12/ בקר 15/ שרימפס 20/ טופו 12/ ביצה 5 

60
תאילנד הירוקה 
אטריות תרד ירוקים, קוביות אננס, זוקיני, ברוקולי, באק צ'וי ובצל ירוק ברוטב קארי ירוק וחלב קוקוס – תוספת עוף 12/ בקר 15/ שרימפס 20/ טופו 12

85
ים השחור
אטריות שחורות, שרימפס, קלמארי, צילי קוריאני, שום וגנגר,בצל ירוק ונבטים סינים

62
עוף קשיו 
עוף בטמפורה מוקפץ עם קשיו, בצל לבן, גמבה וצ'ילי מוגש עם אורז מאודה

52
פרייד רייס
אורז מוקפץ עם גזר, בצל לבן, כרוב, גמבה ברוטב סויה כהה בתוספת ביצת עין מעל - תוספת עוף 12/ בקר 15/ שרימפס 20/ טופו 12

64
החריפה 
אטריות ביצים, עוף, בצל לבן ופטריות מוקפצים ברוטב קארי אדום וחלב קוקוס מוגש עם שבבי בוטנים וקריספי בצל אסייתי

יקיטורי

78
יקיטורי עגל
לוליפופ עגל מוגש עם באק צ'וי​ ואורז מעושן

68
יקיטורי סלמון
גלייז צילי מותסס, צ'ימיצ'ורי יפני, ירקות חרוכים

58
יקיטורי עוף
שיפודי עוף במרינדה אסייתית על הגריל, מיקס פטריות מוקפצות ברוטב חמאת בוטנים קוריאני

78
יקיטורי שרימפס
יקיטורי שרימפס בתיבול ג'נג'ר שום, תבלינים יפנים ויוזו מוגש עם אבוקדו חרוך

68
יקטורי דג לבן
שיפוד של דג לבן במרינדה של קפיר ליים, ג'נג'ר ושום, מוגש עם רוטב קארי ירוק וחלב קוקוס בתוספת אורז מאודה​ ​

באנים

36
ביף באן  
פרוסות עגל פלאנצ'ה, קרם אבוקדו, חסה, בצל סגול וצ'ילי חריף

28
 Infected mushrooms
פטריות שינוגי פריכות, איולי קוג'י כמהין וסויט שימאגי

36
קריספי שרימפס באן
קולסלואו אסייתי, בצל סגול, חסה ואיולי יוזו

36
סיי באן
דג לבן טמפורה, איולי מעושן, סלט כרוב סגול אסייתי

ארוחות ילדים

50
מוקפץ ילדים
אטריות ביצים, עוף, טריאקי ושתיה קלה

50
באן שניצל
באן שניצל, ציפס​ ושתיה קלה

50
הוט דוג קוריאני
2 נקניקיות עוף קוריאני בציפוי דוריטוס/פנקו/טמפורה ושתיה קלה"""
        
        # Import parser class
        from menu_parser import MenuParser
        parser = MenuParser()
        
        # Parse the demo menu content
        result = parser.parse_word_menu_simple(demo_content)
        
        if result['potential_items']:
            categories = MenuCategory.query.filter_by(is_active=True).all()
            return jsonify({
                'success': True,
                'message': f'🔍 נמצאו {result["total_found"]} פריטים אפשריים',
                'items': result['potential_items'],
                'branch_id': branch_id,
                'categories': [{'id': c.id, 'name_he': c.name_he} for c in categories]
            })
        else:
            return jsonify({'success': False, 'error': 'לא נמצאו פריטים בפורמט הנכון'}), 400
            
    except Exception as e:
        current_app.logger.error(f"Demo menu parsing error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Gallery Management
@admin_bp.route('/gallery')
@login_required
def gallery():
    photos = GalleryPhoto.query.order_by(GalleryPhoto.display_order).all()
    return render_template('admin/gallery.html', photos=photos)

@admin_bp.route('/gallery/upload-single', methods=['POST'])
@login_required
def upload_single_gallery():
    """Upload ONE image at a time with automatic resizing for performance"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        
        # Always save as .jpg for consistency and smaller size
        base_name = filename.rsplit('.', 1)[0]
        filename = f"gallery_{timestamp}_{base_name}.jpg"
        
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Resize and optimize image for web
        try:
            img = Image.open(file.stream)
            
            # Convert RGBA to RGB if needed (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize if too large - max 1920px width for web
            max_width = 1920
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Save with optimization - 85% quality is great for web
            img.save(filepath, 'JPEG', quality=85, optimize=True)
            
        except Exception as img_error:
            current_app.logger.error(f"Image processing error: {str(img_error)}")
            # Fall back to saving original file if processing fails
            file.seek(0)
            file.save(filepath)
        
        # Create database entry
        photo = GalleryPhoto(
            file_path=f'/static/uploads/{filename}',
            caption_he=request.form.get('caption_he', ''),
            caption_en=request.form.get('caption_en', ''),
            display_order=GalleryPhoto.query.count()
        )
        db.session.add(photo)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'file_path': photo.file_path,
            'filename': file.filename
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Single file upload error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

# Checklist Management
@admin_bp.route('/checklist')
@login_required
def checklist():
    return render_template('admin/checklist_tasks.html')

# Menu Wizard Management
@admin_bp.route('/menu-wizard')
@login_required
def menu_wizard():
    try:
        # Preload branches data
        branches = Branch.query.filter_by(is_active=True).order_by(Branch.display_order).all()
        branches_data = [
            {
                'id': branch.id,
                'name_he': branch.name_he,
                'name_en': branch.name_en,
                'address_he': branch.address_he
            } for branch in branches
        ]
        
        # Preload categories with items
        categories = MenuCategory.query.filter_by(is_active=True).order_by(MenuCategory.display_order).all()
        categories_data = []
        
        for category in categories:
            items = MenuItem.query.filter_by(
                category_id=category.id,
                is_available=True
            ).order_by(MenuItem.display_order).all()
            
            category_data = {
                'id': category.id,
                'name_he': category.name_he,
                'name_en': category.name_en,
                'icon': category.icon,
                'color': category.color,
                'items': []
            }
            
            for item in items:
                item_data = {
                    'id': item.id,
                    'name_he': item.name_he,
                    'name_en': item.name_en,
                    'description_he': item.description_he,
                    'description_en': item.description_en,
                    'base_price': float(item.base_price) if item.base_price else 0,
                    'dietary_properties': [
                        {
                            'name_he': prop.name_he,
                            'name_en': prop.name_en,
                            'icon': prop.icon,
                            'color': prop.color
                        } for prop in item.dietary_properties if prop.is_active
                    ]
                }
                category_data['items'].append(item_data)
            
            categories_data.append(category_data)
        
        # Preload templates
        templates = MenuTemplate.query.order_by(MenuTemplate.created_at.desc()).all()
        templates_data = []
        
        for template in templates:
            template_data = {
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'branch_name': template.branch.name_he if template.branch else 'כללי',
                'is_default': template.is_default,
                'created_at': template.created_at.strftime('%Y-%m-%d'),
                'categories_count': len(template.categories_config) if template.categories_config else 0,
                'items_count': len(template.items_config) if template.items_config else 0
            }
            templates_data.append(template_data)
        
        return render_template('admin/menu_wizard.html', 
                             branches=branches_data,
                             categories=categories_data,
                             templates=templates_data)
                             
    except Exception as e:
        print(f"Error loading menu wizard data: {str(e)}")
        return render_template('admin/menu_wizard.html', 
                             branches=[],
                             categories=[],
                             templates=[])

# Menu Wizard API Routes
@admin_bp.route('/api/menu-wizard/categories')
@login_required
def api_menu_wizard_categories():
    """Get all active categories with their menu items"""
    try:
        categories = MenuCategory.query.filter_by(is_active=True).order_by(MenuCategory.display_order).all()
        result = []
        
        for category in categories:
            category_data = {
                'id': category.id,
                'name_he': category.name_he,
                'name_en': category.name_en,
                'description_he': category.description_he,
                'icon': category.icon,
                'color': category.color,
                'items_count': len([item for item in category.menu_items if item.is_available]),
                'items': []
            }
            
            # Add available menu items
            for item in category.menu_items:
                if item.is_available:
                    item_data = {
                        'id': item.id,
                        'name_he': item.name_he,
                        'description_he': item.description_he,
                        'base_price': float(item.base_price) if item.base_price else 0,
                        'spice_level': item.spice_level,
                        'prep_time_minutes': item.prep_time_minutes,
                        'dietary_properties': [
                            {
                                'name_he': prop.name_he,
                                'icon': prop.icon,
                                'color': prop.color
                            } for prop in item.dietary_properties if prop.is_active
                        ]
                    }
                    category_data['items'].append(item_data)
            
            result.append(category_data)
        
        return jsonify({'success': True, 'categories': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/menu-wizard/branches')
@login_required
def api_menu_wizard_branches():
    """Get all active branches"""
    try:
        branches = Branch.query.filter_by(is_active=True).order_by(Branch.display_order).all()
        result = [
            {
                'id': branch.id,
                'name_he': branch.name_he,
                'name_en': branch.name_en,
                'address_he': branch.address_he
            } for branch in branches
        ]
        return jsonify({'success': True, 'branches': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/menu-wizard/templates')
@login_required
def api_menu_wizard_templates():
    """Get all menu templates"""
    try:
        templates = MenuTemplate.query.order_by(MenuTemplate.created_at.desc()).all()
        result = []
        
        for template in templates:
            template_data = {
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'branch_name': template.branch.name_he if template.branch else 'כללי',
                'is_default': template.is_default,
                'created_at': template.created_at.strftime('%Y-%m-%d'),
                'categories_count': len(template.categories_config) if template.categories_config else 0,
                'items_count': len(template.items_config) if template.items_config else 0
            }
            result.append(template_data)
        
        return jsonify({'success': True, 'templates': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/menu-wizard/create-menu', methods=['POST'])
@login_required
def api_create_menu():
    """Create a new menu from wizard"""
    try:
        data = request.get_json()
        
        # Extract data
        menu_name = data.get('name', 'תפריט חדש')
        branch_id = data.get('branch_id')
        selected_categories = data.get('categories', [])
        selected_items = data.get('items', [])
        layout_config = data.get('layout', {})
        print_config = data.get('print_settings', {})
        style_config = data.get('style_settings', {})
        page_config = data.get('page_settings', {})
        save_as_template = data.get('save_as_template', False)
        template_name = data.get('template_name', '')
        
        # Validate required fields
        if not branch_id:
            return jsonify({'success': False, 'error': 'חובה לבחור סניף'}), 400
            
        if not selected_items:
            return jsonify({'success': False, 'error': 'חובה לבחור לפחות מנה אחת'}), 400
        
        # Build menu content
        menu_content = {
            'name': menu_name,
            'branch_id': branch_id,
            'categories': selected_categories,
            'items': selected_items,
            'layout': layout_config,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        # Create GeneratedMenu
        generated_menu = GeneratedMenu(
            name=menu_name,
            branch_id=branch_id,
            date_created=datetime.utcnow().date(),
            created_by=current_user.id if hasattr(current_user, 'id') else None,
            menu_content=menu_content,
            print_settings=print_config,
            style_settings=style_config,
            page_settings=page_config
        )
        
        db.session.add(generated_menu)
        
        # Save as template if requested
        template_id = None
        if save_as_template and template_name:
            menu_template = MenuTemplate(
                name=template_name,
                description=f'תבנית נוצרה מ-{menu_name}',
                branch_id=branch_id,
                created_by=current_user.id if hasattr(current_user, 'id') else None,
                categories_config=selected_categories,
                items_config=selected_items,
                layout_config=layout_config,
                print_config=print_config,
                style_config=style_config,
                page_config=page_config
            )
            db.session.add(menu_template)
            db.session.flush()  # Get the ID
            template_id = menu_template.id
            generated_menu.template_id = template_id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'menu_id': generated_menu.id,
            'template_id': template_id,
            'message': 'התפריט נוצר בהצלחה!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/menu-wizard/save-template', methods=['POST'])
@login_required
def api_save_menu_template():
    """Save menu configuration as template"""
    try:
        data = request.get_json()
        
        template_name = data.get('name')
        description = data.get('description', '')
        branch_id = data.get('branch_id')
        categories_config = data.get('categories', [])
        items_config = data.get('items', [])
        layout_config = data.get('layout', {})
        print_config = data.get('print_settings', {})
        style_config = data.get('style_settings', {})
        page_config = data.get('page_settings', {})
        
        if not template_name:
            return jsonify({'success': False, 'error': 'חובה להזין שם לתבנית'}), 400
            
        # Check if template name already exists
        existing = MenuTemplate.query.filter_by(name=template_name).first()
        if existing:
            return jsonify({'success': False, 'error': 'תבנית עם השם הזה כבר קיימת'}), 400
        
        menu_template = MenuTemplate(
            name=template_name,
            description=description,
            branch_id=branch_id,
            created_by=current_user.id if hasattr(current_user, 'id') else None,
            categories_config=categories_config,
            items_config=items_config,
            layout_config=layout_config,
            print_config=print_config,
            style_config=style_config,
            page_config=page_config
        )
        
        db.session.add(menu_template)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'template_id': menu_template.id,
            'message': 'התבנית נשמרה בהצלחה!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/menu-wizard/template/<int:template_id>')
@login_required
def api_get_menu_template(template_id):
    """Get specific template configuration"""
    try:
        template = MenuTemplate.query.get_or_404(template_id)
        
        result = {
            'id': template.id,
            'name': template.name,
            'description': template.description,
            'branch_id': template.branch_id,
            'categories_config': template.categories_config or [],
            'items_config': template.items_config or [],
            'layout_config': template.layout_config or {},
            'print_config': template.print_config or {},
            'style_config': template.style_config or {},
            'page_settings': template.page_config or {},
            'created_at': template.created_at.isoformat() if template.created_at else None
        }
        
        return jsonify({'success': True, 'template': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/menu-wizard/template/<int:template_id>', methods=['DELETE'])
@login_required
def api_delete_menu_template(template_id):
    """Delete menu template"""
    try:
        template = MenuTemplate.query.get_or_404(template_id)
        
        # Don't allow deletion of default templates
        if template.is_default:
            return jsonify({'success': False, 'error': 'לא ניתן למחוק תבנית ברירת מחדל'}), 400
        
        db.session.delete(template)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'התבנית נמחקה בהצלחה'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/menu-wizard/print-preview/<int:menu_id>')
@login_required
def api_menu_print_preview(menu_id):
    """Generate print preview for menu"""
    try:
        generated_menu = GeneratedMenu.query.get_or_404(menu_id)
        menu_content = generated_menu.menu_content
        
        # Get actual data for selected items with dietary properties
        selected_items = []
        if menu_content.get('items'):
            items_query = MenuItem.query.options(joinedload(MenuItem.dietary_properties)).filter(MenuItem.id.in_(menu_content['items']))
            selected_items = items_query.all()
        
        # Get branch info
        branch = Branch.query.get(generated_menu.branch_id)
        
        # Group items by category
        categories_with_items = {}
        for item in selected_items:
            category = item.category
            if category and category.id in menu_content.get('categories', []):
                if category.id not in categories_with_items:
                    categories_with_items[category.id] = {
                        'category': category,
                        'items': []
                    }
                categories_with_items[category.id]['items'].append(item)
        
        # Generate print HTML
        print_html = generate_menu_print_html(
            menu_name=generated_menu.name,
            branch=branch,
            categories_with_items=categories_with_items,
            print_settings=generated_menu.print_settings or {},
            layout_settings=menu_content.get('layout', {}),
            style_settings=generated_menu.style_settings or {},
            page_settings=generated_menu.page_settings or {},
            menu_description=generated_menu.description
        )
        
        return jsonify({
            'success': True,
            'html': print_html,
            'menu_name': generated_menu.name
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/menu-wizard/saved-menus')
@login_required
def api_saved_menus():
    """Get all saved generated menus"""
    try:
        menus = GeneratedMenu.query.order_by(GeneratedMenu.date_created.desc()).all()
        result = []
        
        for menu in menus:
            menu_data = {
                'id': menu.id,
                'name': menu.name,
                'branch_name': menu.branch.name_he if menu.branch else 'לא צוין',
                'date_created': menu.date_created.strftime('%Y-%m-%d'),
                'items_count': len(menu.menu_content.get('items', [])) if menu.menu_content else 0,
                'categories_count': len(menu.menu_content.get('categories', [])) if menu.menu_content else 0,
                'has_print_settings': bool(menu.print_settings),
                'has_style_settings': bool(menu.style_settings),
                'has_page_settings': bool(menu.page_settings)
            }
            result.append(menu_data)
        
        return jsonify({'success': True, 'menus': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/menu-wizard/saved-menu/<int:menu_id>')
@login_required
def api_get_saved_menu(menu_id):
    """Get a saved menu by ID"""
    try:
        menu = GeneratedMenu.query.get_or_404(menu_id)
        
        menu_data = {
            'id': menu.id,
            'name': menu.name,
            'branch_id': menu.branch_id,
            'branch_name': menu.branch.name_he if menu.branch else 'לא צוין',
            'date_created': menu.date_created.strftime('%Y-%m-%d'),
            'menu_content': menu.menu_content,
            'print_settings': menu.print_settings,
            'style_settings': menu.style_settings,
            'page_settings': menu.page_settings
        }
        
        return jsonify({'success': True, 'menu': menu_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/menu-wizard/delete-menu/<int:menu_id>', methods=['DELETE'])
@login_required 
def api_delete_saved_menu(menu_id):
    """Delete a saved menu"""
    try:
        menu = GeneratedMenu.query.get_or_404(menu_id)
        db.session.delete(menu)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'התפריט נמחק בהצלחה'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/menu-wizard/simple-print/<int:menu_id>', methods=['GET', 'POST'])
@login_required
def api_menu_simple_print(menu_id):
    """Generate simple table-based print HTML for menu"""
    try:
        generated_menu = GeneratedMenu.query.get_or_404(menu_id)
        menu_content = generated_menu.menu_content
        
        # Get current settings from request (for live preview) or use saved settings
        request_data = request.get_json() if request.method == 'POST' else {}
        
        # DEBUG: Check what's in the database
        import logging
        logging.debug(f"=== SETTINGS DEBUG for menu {menu_id} ===")
        logging.debug(f"Request data: {request_data}")
        logging.debug(f"Database page_settings: {generated_menu.page_settings}")
        
        current_print_settings = request_data.get('print_settings', generated_menu.print_settings or {})
        current_style_settings = request_data.get('style_settings', generated_menu.style_settings or {})
        current_page_settings = request_data.get('page_settings', generated_menu.page_settings or {})
        
        logging.debug(f"Final current_page_settings: {current_page_settings}")
        
        # Settings ready for print generation
        
        # Get actual data for selected items with dietary properties
        selected_items = []
        if menu_content.get('items'):
            items_query = MenuItem.query.options(joinedload(MenuItem.dietary_properties)).filter(MenuItem.id.in_(menu_content['items']))
            selected_items = items_query.all()
        
        # Get branch info
        branch = Branch.query.get(generated_menu.branch_id)
        
        # Group items by category
        categories_with_items = {}
        for item in selected_items:
            category = item.category
            if category:
                if category.id not in categories_with_items:
                    categories_with_items[category.id] = {
                        'category': category,
                        'items': []
                    }
                categories_with_items[category.id]['items'].append(item)
        
        # Create ordered list of categories based on page_settings if available
        # This prevents duplicates and respects the user's exact page configuration
        ordered_categories = []
        if current_page_settings.get('pageGroups'):
            # Extract unique categories from page groups in order
            seen_categories = set()
            for group in current_page_settings['pageGroups']:
                for category_id in group.get('categories', []):
                    if category_id not in seen_categories and category_id in categories_with_items:
                        ordered_categories.append((category_id, categories_with_items[category_id]))
                        seen_categories.add(category_id)
        else:
            # Fallback to menu_content order, but remove duplicates
            seen_categories = set()
            for category_id in menu_content.get('categories', []):
                if category_id not in seen_categories and category_id in categories_with_items:
                    ordered_categories.append((category_id, categories_with_items[category_id]))
                    seen_categories.add(category_id)
        
        # Generate simple print HTML with current settings (from request or saved)
        print_html = generate_simple_menu_print_html(
            menu_name=generated_menu.name,
            branch=branch,
            categories_with_items=ordered_categories,
            print_settings=current_print_settings,
            style_settings=current_style_settings,
            page_settings=current_page_settings,
            menu_description=generated_menu.description
        )
        
        return jsonify({
            'success': True,
            'html': print_html,
            'menu_name': generated_menu.name
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def generate_simple_menu_print_html(menu_name, branch, categories_with_items, print_settings=None, style_settings=None, page_settings=None, menu_description=None):
    """Generate 2-column print HTML with configurable page breaks"""
    
    # Default settings
    print_settings = print_settings or {}
    style_settings = style_settings or {}
    page_settings = page_settings or {}
    
    # Extract print settings
    show_prices = print_settings.get('show_prices', True)
    show_descriptions = print_settings.get('show_descriptions', True)
    show_category_icons = print_settings.get('show_category_icons', True)
    show_date = print_settings.get('show_date', True)
    show_branch_info = print_settings.get('show_branch_info', True)
    show_menu_title = print_settings.get('show_menu_title', True)
    
    # Extract page settings
    page_groups = page_settings.get('pageGroups', [])
    page_break_categories = page_settings.get('pageBreakCategories', [])
    
    # Advanced style settings
    primary_color = style_settings.get('primaryColor', '#2c3e50')
    secondary_color = style_settings.get('secondaryColor', '#e74c3c')
    primary_font = style_settings.get('primaryFont', 'Heebo')
    base_font_size = style_settings.get('baseFontSize', 'medium')
    icon_style = style_settings.get('iconStyle', 'solid')
    
    from datetime import datetime
    current_date = datetime.now().strftime('%d/%m/%Y')
    
    # Helper function to format a menu item
    def format_menu_item(item, show_prices, show_descriptions):
        item_html = '<div class="menu-item">'
        
        # Item header with name and price
        item_html += '<div class="item-header">'
        item_html += f'<span class="item-name">{item.name_he}</span>'
        
        if show_prices and item.base_price:
            try:
                price_value = int(float(item.base_price))
                item_html += f'<span class="item-price">₪ {price_value}</span>'
            except (ValueError, TypeError):
                pass
        
        item_html += '</div>'
        
        # Item description
        if show_descriptions and item.description_he:
            item_html += f'<div class="item-description">{item.description_he}</div>'
        
        # Dietary properties icons
        if item.dietary_properties:
            item_html += '<div class="dietary-icons">'
            for prop in item.dietary_properties:
                if prop.is_active:
                    icon_color = prop.color or '#666'
                    # Normalize icon name - add 'fa-' prefix if not present
                    icon_name = prop.icon if prop.icon and prop.icon.startswith('fa-') else f'fa-{prop.icon}'
                    item_html += f'<span class="dietary-icon" style="color: {icon_color};" title="{prop.name_he}">'
                    item_html += f'<i class="fas {icon_name}"></i>'
                    item_html += '</span>'
            item_html += '</div>'
        
        item_html += '</div>'
        return item_html
    
    # Create HTML with 2-column table layout and separate pages per category
    html = f'''
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>{menu_name}</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;700&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Heebo', Arial, sans-serif;
                font-size: 12pt;
                line-height: 1.4;
                color: {primary_color};
                direction: rtl;
                text-align: right;
            }}
            
            @page {{
                size: A4;
                margin: 15mm 15mm 15mm 15mm;
            }}
            
            .page-break {{
                page-break-before: always;
                break-before: page;
            }}
            
            .menu-header {{
                text-align: center;
                margin-bottom: 20px;
                border-bottom: 3px solid {secondary_color};
                padding-bottom: 15px;
            }}
            
            .menu-title {{
                font-size: 24pt;
                font-weight: 700;
                color: {primary_color};
                margin-bottom: 8px;
            }}
            
            .branch-info {{
                font-size: 14pt;
                color: {primary_color};
                margin-bottom: 5px;
            }}
            
            .print-date {{
                font-size: 11pt;
                color: #666;
            }}
            
            .page-group-container {{
                page-break-inside: avoid;
                break-inside: avoid;
                page-break-after: avoid;
                break-after: avoid;
            }}
            
            .category-title {{
                font-size: 18pt;
                font-weight: 600;
                color: {secondary_color};
                text-align: center;
                margin: 20px 0 15px 0;
                padding-bottom: 10px;
                border-bottom: 2px solid {secondary_color};
                page-break-after: avoid;
                break-after: avoid;
            }}
            
            .two-column-table {{
                width: 100%;
                table-layout: fixed;
                border-collapse: collapse;
                margin-bottom: 15px;
            }}
            
            .two-column-table td {{
                width: 50%;
                vertical-align: top;
                padding: 0 10px;
                border: none;
            }}
            
            .menu-item {{
                margin-bottom: 8px;
                padding: 3px 0;
                page-break-inside: avoid;
                break-inside: avoid;
            }}
            
            .item-header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 2px;
            }}
            
            .item-name {{
                font-size: 13pt;
                font-weight: 500;
                color: {primary_color};
                flex: 1;
                margin-left: 5px;
            }}
            
            .item-price {{
                font-size: 13pt;
                font-weight: 600;
                color: {secondary_color};
                white-space: nowrap;
            }}
            
            .item-description {{
                font-size: 10pt;
                color: #666;
                margin-top: 2px;
                font-style: italic;
            }}
            
            .dietary-icons {{
                display: flex;
                gap: 6px;
                margin-top: 4px;
                align-items: center;
            }}
            
            .dietary-icon {{
                font-size: 11pt;
                display: inline-flex;
                align-items: center;
            }}
            
            .dietary-icon i {{
                margin: 0;
            }}
            
            /* Menu description section */
            .menu-description-section {{
                margin-top: 30px;
                padding: 15px 20px;
                background: #f8f9fa;
                border-radius: 8px;
                text-align: center;
            }}
            
            .menu-description {{
                font-size: 11pt;
                color: #666;
                font-style: italic;
                margin: 0;
                line-height: 1.6;
            }}
            
            /* Icon legend section */
            .icon-legend {{
                margin-top: 25px;
                padding: 15px 20px;
                border-top: 2px solid {secondary_color};
                page-break-inside: avoid;
            }}
            
            .legend-title {{
                font-size: 14pt;
                font-weight: 600;
                color: {primary_color};
                margin-bottom: 12px;
                text-align: center;
            }}
            
            .legend-items {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 8px;
            }}
            
            .legend-item {{
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 10pt;
                color: #666;
            }}
            
            .legend-item i {{
                font-size: 12pt;
                width: 20px;
                text-align: center;
            }}
            
            /* Print optimizations */
            @media print {{
                .page-break {{
                    page-break-before: always !important;
                    break-before: page !important;
                }}
                
                .page-group-container {{
                    page-break-inside: avoid !important;
                    break-inside: avoid !important;
                    page-break-after: auto !important;
                    break-after: auto !important;
                }}
                
                .two-column-table {{
                    width: 100% !important;
                    table-layout: fixed !important;
                }}
                
                .two-column-table td {{
                    width: 50% !important;
                    padding: 0 8px !important;
                }}
                
                .menu-item {{
                    page-break-inside: avoid !important;
                    break-inside: avoid !important;
                }}
                
                .category-title {{
                    page-break-after: avoid !important;
                    break-after: avoid !important;
                }}
            }}
        </style>
    </head>
    <body>
        <!-- Header -->
        <div class="menu-header">
    '''
    
    # Only show title if setting is enabled
    if show_menu_title:
        html += f'<h1 class="menu-title">{menu_name}</h1>'
    
    if show_branch_info and branch:
        html += f'<div class="branch-info">{branch.name_he}</div>'
    
    if show_date:
        html += f'<div class="print-date">תאריך: {current_date}</div>'
    
    html += '</div>'
    
    # Create a mapping of category_id to category data for quick lookup
    category_data_map = {category_id: data for category_id, data in categories_with_items}
    
    # DEBUG: Log what we received
    import logging
    logging.debug(f"=== PRINT DEBUG ===")
    logging.debug(f"Page groups: {page_groups}")
    logging.debug(f"Categories with items (order): {[cat_id for cat_id, _ in categories_with_items]}")
    logging.debug(f"Category data map keys: {list(category_data_map.keys())}")
    
    # If we have page groups, use them to organize the layout
    if page_groups and len(page_groups) > 0:
        # Process each page group - EACH GROUP GETS ITS OWN PAGE
        for group_index, group in enumerate(page_groups):
            group_categories = group.get('categories', [])
            
            # Add page break before each new page group (except the first)
            if group_index > 0:
                html += '<div class="page-break"></div>'
            
            # Wrap the entire page group in a container to keep it together
            html += '<div class="page-group-container">'
            
            # Process each category in this page group
            for cat_index, category_id in enumerate(group_categories):
                if category_id in category_data_map:
                    data = category_data_map[category_id]
                    category = data['category']
                    items = data['items']
                    
                    # Add category title
                    html += f'<h2 class="category-title">{category.name_he}</h2>'
                    
                    # Create 2-column table for items
                    if items:
                        # Split items into 2 columns
                        mid_point = (len(items) + 1) // 2
                        left_column = items[:mid_point]
                        right_column = items[mid_point:]
                        
                        html += '<table class="two-column-table"><tr>'
                        
                        # Left column
                        html += '<td>'
                        for item in left_column:
                            html += format_menu_item(item, show_prices, show_descriptions)
                        html += '</td>'
                        
                        # Right column  
                        html += '<td>'
                        for item in right_column:
                            html += format_menu_item(item, show_prices, show_descriptions)
                        html += '</td>'
                        
                        html += '</tr></table>'
            
            # Close page group container
            html += '</div>'
    else:
        # Fallback to old logic if no page groups defined
        for category_index, (category_id, data) in enumerate(categories_with_items):
            category = data['category']
            items = data['items']
            
            # Add page break only if this category is in the page break list
            should_break = category_id in page_break_categories
            
            if should_break and category_index > 0:
                html += '<div class="page-break"></div>'
            
            # Add category title
            html += f'<h2 class="category-title">{category.name_he}</h2>'
            
            # Create 2-column table for items
            if items:
                # Split items into 2 columns
                mid_point = (len(items) + 1) // 2
                left_column = items[:mid_point]
                right_column = items[mid_point:]
                
                html += '<table class="two-column-table"><tr>'
                
                # Left column
                html += '<td>'
                for item in left_column:
                    html += format_menu_item(item, show_prices, show_descriptions)
                html += '</td>'
                
                # Right column  
                html += '<td>'
                for item in right_column:
                    html += format_menu_item(item, show_prices, show_descriptions)
                html += '</td>'
                
                html += '</tr></table>'
    
    # Collect all active dietary properties from all items
    all_properties = set()
    for category_id, data in categories_with_items:
        for item in data['items']:
            if item.dietary_properties:
                for prop in item.dietary_properties:
                    if prop.is_active:
                        all_properties.add((prop.id, prop.name_he, prop.icon, prop.color, prop.description_he))
    
    # Add menu description if provided
    if menu_description and menu_description.strip():
        html += f'''
    <div class="menu-description-section">
        <p class="menu-description">{menu_description}</p>
    </div>
        '''
    
    # Add icon legend if there are any dietary properties
    if all_properties:
        html += '''
    <div class="icon-legend">
        <h3 class="legend-title">מקרא סימונים:</h3>
        <div class="legend-items">
        '''
        # Sort properties by name
        sorted_properties = sorted(all_properties, key=lambda x: x[1])
        for prop_id, name_he, icon, color, description_he in sorted_properties:
            # Normalize icon name
            icon_name = icon if icon and icon.startswith('fa-') else f'fa-{icon}'
            icon_color = color or '#666'
            prop_desc = f' - {description_he}' if description_he else ''
            html += f'''
            <div class="legend-item">
                <i class="fas {icon_name}" style="color: {icon_color};"></i>
                <span>{name_he}{prop_desc}</span>
            </div>
            '''
        html += '''
        </div>
    </div>
        '''
    
    html += '''
    </body>
    </html>
    '''
    
    return html
def generate_menu_print_html(menu_name, branch, categories_with_items, print_settings, layout_settings, style_settings=None, page_settings=None, menu_description=None):
    """Generate simple 2-column table-based print HTML with proper page breaks"""
    
    # Default settings
    style_settings = style_settings or {}
    page_settings = page_settings or {}
    
    # Layout settings
    show_prices = layout_settings.get('show_prices', True)
    show_descriptions = layout_settings.get('show_descriptions', True)
    
    # Print settings
    paper_size = print_settings.get('paper_size', 'A4')
    show_branch_info = print_settings.get('show_branch_info', True)
    show_date = print_settings.get('show_date', True)
    
    # Style settings
    primary_color = style_settings.get('primaryColor', '#1B2951')
    secondary_color = style_settings.get('secondaryColor', '#C75450')
    
    # Page settings
    page_break_categories = page_settings.get('pageBreakCategories', [])
    
    from datetime import datetime
    current_date = datetime.now().strftime('%d/%m/%Y')
    
    # Create HTML with proper 2-column table layout and page breaks
    html = f'''
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>{menu_name}</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;700&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Heebo', Arial, sans-serif;
                font-size: 12pt;
                line-height: 1.4;
                color: {primary_color};
                direction: rtl;
                text-align: right;
            }}
            
            @page {{
                size: {paper_size};
                margin: 15mm 0mm 15mm 15mm;
            }}
            
            .page-break {{
                page-break-before: always;
                break-before: page;
            }}
            
            .menu-header {{
                text-align: center;
                margin-bottom: 20px;
                border-bottom: 3px solid {secondary_color};
                padding-bottom: 15px;
            }}
            
            .menu-title {{
                font-size: 24pt;
                font-weight: 700;
                color: {primary_color};
                margin-bottom: 8px;
            }}
            
            .branch-info {{
                font-size: 14pt;
                color: {primary_color};
                margin-bottom: 5px;
            }}
            
            .print-date {{
                font-size: 11pt;
                color: #666;
            }}
            
            .page-group-container {{
                page-break-inside: avoid;
                break-inside: avoid;
                page-break-after: avoid;
                break-after: avoid;
            }}
            
            .category-title {{
                font-size: 18pt;
                font-weight: 600;
                color: {secondary_color};
                text-align: center;
                margin: 20px 0 15px 0;
                padding-bottom: 10px;
                border-bottom: 2px solid {secondary_color};
                page-break-after: avoid;
                break-after: avoid;
            }}
            
            .two-column-table {{
                width: 100%;
                table-layout: fixed;
                border-collapse: collapse;
                margin-bottom: 15px;
            }}
            
            .two-column-table td {{
                width: 50%;
                vertical-align: top;
                padding: 0 10px;
                border: none;
            }}
            
            .menu-item {{
                margin-bottom: 8px;
                padding: 3px 0;
                page-break-inside: avoid;
                break-inside: avoid;
            }}
            
            .item-header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 2px;
            }}
            
            .item-name {{
                font-size: 13pt;
                font-weight: 500;
                color: {primary_color};
                flex: 1;
                margin-left: 5px;
            }}
            
            .item-price {{
                font-size: 13pt;
                font-weight: 600;
                color: {secondary_color};
                white-space: nowrap;
            }}
            
            .item-description {{
                font-size: 10pt;
                color: #666;
                margin-top: 2px;
                font-style: italic;
            }}
            
            .dietary-icons {{
                display: flex;
                gap: 6px;
                margin-top: 4px;
                align-items: center;
            }}
            
            .dietary-icon {{
                font-size: 11pt;
                display: inline-flex;
                align-items: center;
            }}
            
            .dietary-icon i {{
                margin: 0;
            }}
            
            /* Menu description section */
            .menu-description-section {{
                margin-top: 30px;
                padding: 15px 20px;
                background: #f8f9fa;
                border-radius: 8px;
                text-align: center;
            }}
            
            .menu-description {{
                font-size: 11pt;
                color: #666;
                font-style: italic;
                margin: 0;
                line-height: 1.6;
            }}
            
            /* Icon legend section */
            .icon-legend {{
                margin-top: 25px;
                padding: 15px 20px;
                border-top: 2px solid {secondary_color};
                page-break-inside: avoid;
            }}
            
            .legend-title {{
                font-size: 14pt;
                font-weight: 600;
                color: {primary_color};
                margin-bottom: 12px;
                text-align: center;
            }}
            
            .legend-items {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 8px;
            }}
            
            .legend-item {{
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 10pt;
                color: #666;
            }}
            
            .legend-item i {{
                font-size: 12pt;
                width: 20px;
                text-align: center;
            }}
            
            /* Print optimizations */
            @media print {{
                .page-break {{
                    page-break-before: always !important;
                    break-before: page !important;
                }}
                
                .page-group-container {{
                    page-break-inside: avoid !important;
                    break-inside: avoid !important;
                    page-break-after: auto !important;
                    break-after: auto !important;
                }}
                
                .two-column-table {{
                    width: 100% !important;
                    table-layout: fixed !important;
                }}
                
                .two-column-table td {{
                    width: 50% !important;
                    padding: 0 8px !important;
                }}
                
                .menu-item {{
                    page-break-inside: avoid !important;
                    break-inside: avoid !important;
                }}
                
                .category-title {{
                    page-break-after: avoid !important;
                    break-after: avoid !important;
                }}
            }}
        </style>
    </head>
    <body>
        <!-- Header -->
        <div class="menu-header">
            <h1 class="menu-title">{menu_name}</h1>
    '''
    
    if show_branch_info and branch:
        html += f'<div class="branch-info">{branch.name_he}</div>'
    
    if show_date:
        html += f'<div class="print-date">תאריך: {current_date}</div>'
    
    html += '</div>'
    
    # Process categories
    for category_index, (category_id, data) in enumerate(categories_with_items.items()):
        category = data['category']
        items = data['items']
        
        # Add page break for specified categories
        if int(category_id) in page_break_categories and category_index > 0:
            html += '<div class="page-break"></div>'
        
        # Add category title
        html += f'<h2 class="category-title">{category.name_he}</h2>'
        
        # Create 2-column table for items
        if items:
            # Split items into 2 columns
            mid_point = (len(items) + 1) // 2
            left_column = items[:mid_point]
            right_column = items[mid_point:]
            
            html += '<table class="two-column-table"><tr>'
            
            # Left column
            html += '<td>'
            for item in left_column:
                html += format_menu_item(item, show_prices, show_descriptions, primary_color, secondary_color)
            html += '</td>'
            
            # Right column
            html += '<td>'
            for item in right_column:
                html += format_menu_item(item, show_prices, show_descriptions, primary_color, secondary_color)
            html += '</td>'
            
            html += '</tr></table>'
    
    # Collect all active dietary properties from all items
    all_properties = set()
    for category_id, data in categories_with_items.items():
        for item in data['items']:
            if hasattr(item, 'dietary_properties') and item.dietary_properties:
                for prop in item.dietary_properties:
                    if prop.is_active:
                        all_properties.add((prop.id, prop.name_he, prop.icon, prop.color, prop.description_he))
    
    # Add menu description if provided
    if menu_description and menu_description.strip():
        html += f'''
    <div class="menu-description-section">
        <p class="menu-description">{menu_description}</p>
    </div>
        '''
    
    # Add icon legend if there are any dietary properties
    if all_properties:
        html += '''
    <div class="icon-legend">
        <h3 class="legend-title">מקרא סימונים:</h3>
        <div class="legend-items">
        '''
        # Sort properties by name
        sorted_properties = sorted(all_properties, key=lambda x: x[1])
        for prop_id, name_he, icon, color, description_he in sorted_properties:
            # Normalize icon name
            icon_name = icon if icon and icon.startswith('fa-') else f'fa-{icon}'
            icon_color = color or '#666'
            prop_desc = f' - {description_he}' if description_he else ''
            html += f'''
            <div class="legend-item">
                <i class="fas {icon_name}" style="color: {icon_color};"></i>
                <span>{name_he}{prop_desc}</span>
            </div>
            '''
        html += '''
        </div>
    </div>
        '''
    
    html += '''
    </body>
    </html>
    '''
    
    return html

def format_menu_item(item, show_prices, show_descriptions, primary_color, secondary_color):
    """Format a single menu item for display"""
    item_html = '<div class="menu-item">'
    
    # Item header with name and price
    item_html += '<div class="item-header">'
    item_html += f'<span class="item-name">{item.name_he}</span>'
    
    if show_prices and item.base_price:
        try:
            price_value = int(float(item.base_price))
            item_html += f'<span class="item-price">₪ {price_value}</span>'
        except (ValueError, TypeError):
            pass
    
    item_html += '</div>'
    
    # Item description
    if show_descriptions and item.description_he:
        item_html += f'<div class="item-description">{item.description_he}</div>'
    
    # Dietary property icons
    if hasattr(item, 'dietary_properties') and item.dietary_properties:
        active_properties = [prop for prop in item.dietary_properties if prop.is_active]
        if active_properties:
            item_html += '<div class="dietary-icons">'
            for prop in active_properties:
                # Normalize icon name - add 'fa-' prefix if not present
                icon_class = prop.icon or 'fa-circle'
                if icon_class and not icon_class.startswith('fa-'):
                    icon_class = f'fa-{icon_class}'
                color_style = f'color: {prop.color};' if prop.color else ''
                item_html += f'<span class="dietary-icon" style="{color_style}" title="{prop.name_he}"><i class="fas {icon_class}"></i></span>'
            item_html += '</div>'
    
    item_html += '</div>'
    return item_html

# Messages Management
@admin_bp.route('/messages')
@login_required
def messages():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)

@admin_bp.route('/messages/mark-read/<int:id>', methods=['POST'])
@login_required
def mark_message_read(id):
    message = ContactMessage.query.get_or_404(id)
    message.is_read = True
    db.session.commit()
    return jsonify({'success': True})

# Reservations Management
@admin_bp.route('/reservations')
@login_required
def reservations():
    reservations = Reservation.query.order_by(Reservation.created_at.desc()).all()
    branches = Branch.query.filter_by(is_active=True).all()
    return render_template('admin/reservations.html', reservations=reservations, branches=branches)

@admin_bp.route('/reservations/update-status/<int:id>', methods=['POST'])
@login_required
def update_reservation_status(id):
    reservation = Reservation.query.get_or_404(id)
    status = request.json.get('status')
    
    if status in ['pending', 'confirmed', 'cancelled']:
        reservation.status = status
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'error': 'Invalid status'}), 400

# API Endpoints for Frontend
@admin_bp.route('/api/settings')
def api_settings():
    settings = SiteSettings.query.first()
    if not settings:
        return jsonify({})
    
    return jsonify({
        'site_name_he': settings.site_name_he,
        'site_name_en': settings.site_name_en,
        'hero_title_he': settings.hero_title_he,
        'hero_title_en': settings.hero_title_en,
        'hero_subtitle_he': settings.hero_subtitle_he,
        'hero_subtitle_en': settings.hero_subtitle_en,
        'hero_description_he': settings.hero_description_he,
        'hero_description_en': settings.hero_description_en,
        'about_title_he': settings.about_title_he,
        'about_title_en': settings.about_title_en,
        'about_content_he': settings.about_content_he,
        'about_content_en': settings.about_content_en,
        'facebook_url': settings.facebook_url,
        'instagram_url': settings.instagram_url,
        'whatsapp_number': settings.whatsapp_number
    })

@admin_bp.route('/api/branches')
def api_branches():
    branches = Branch.query.filter_by(is_active=True).order_by(Branch.display_order).all()
    result = []
    
    for branch in branches:
        working_hours = []
        for wh in branch.working_hours:
            working_hours.append({
                'day_of_week': wh.day_of_week,
                'day_name_he': wh.day_name_he,
                'day_name_en': wh.day_name_en,
                'open_time': wh.open_time,
                'close_time': wh.close_time,
                'is_closed': wh.is_closed
            })
        
        result.append({
            'id': branch.id,
            'name_he': branch.name_he,
            'name_en': branch.name_en,
            'address_he': branch.address_he,
            'address_en': branch.address_en,
            'phone': branch.phone,
            'email': branch.email,
            'waze_link': branch.waze_link,
            'google_maps_link': branch.google_maps_link,
            'working_hours': working_hours
        })
    
    return jsonify(result)

@admin_bp.route('/api/gallery')
def api_gallery():
    photos = GalleryPhoto.query.filter_by(is_active=True).order_by(GalleryPhoto.display_order).all()
    return jsonify([{
        'id': p.id,
        'file_path': p.file_path,
        'caption_he': p.caption_he,
        'caption_en': p.caption_en
    } for p in photos])

@admin_bp.route('/api/menu')
def api_menu():
    categories = MenuCategory.query.filter_by(is_active=True).order_by(MenuCategory.display_order).all()
    result = []
    
    for cat in categories:
        items = []
        # Get items ordered by display_order
        menu_items = MenuItem.query.filter_by(category_id=cat.id, is_available=True).order_by(MenuItem.display_order).all()
        
        for item in menu_items:
            # Get dietary properties for this item
            dietary_properties = []
            for prop in item.dietary_properties:
                if prop.is_active:
                    dietary_properties.append({
                        'id': prop.id,
                        'name_he': prop.name_he,
                        'name_en': prop.name_en,
                        'icon': prop.icon,
                        'color': prop.color,
                        'description_he': prop.description_he,
                        'description_en': prop.description_en
                    })
            
            items.append({
                'id': item.id,
                'name_he': item.name_he,
                'name_en': item.name_en,
                'description_he': item.description_he,
                'description_en': item.description_en,
                'ingredients_he': item.ingredients_he,
                'ingredients_en': item.ingredients_en,
                'base_price': item.base_price or item.price,  # Fallback to old price column
                'image_path': item.image_path,
                'dietary_properties': dietary_properties,
                'display_order': item.display_order
            })
        
        result.append({
            'id': cat.id,
            'name_he': cat.name_he,
            'name_en': cat.name_en,
            'description_he': cat.description_he,
            'description_en': cat.description_en,
            'items': items,
            'display_order': cat.display_order
        })
    
    return jsonify(result)

# Microservices Dashboard Routes
@admin_bp.route('/microservices')
@login_required
def microservices_dashboard():
    """Main microservices dashboard"""
    from services.order.order_service import Order
    from services.delivery.delivery_service import Driver
    from services.kitchen.kitchen_service import KitchenQueue
    
    # Get stats
    active_orders = Order.query.filter(Order.status.in_(['confirmed', 'preparing', 'ready'])).count()
    available_drivers = Driver.query.filter_by(status='available', is_active=True).count()
    kitchen_queue = KitchenQueue.query.filter(KitchenQueue.status.in_(['pending', 'preparing'])).count()
    
    # Calculate today's sales
    from datetime import datetime, date
    today = date.today()
    today_orders = Order.query.filter(
        db.func.date(Order.created_at) == today,
        Order.payment_status == 'paid'
    ).all()
    today_sales = sum(order.total_amount for order in today_orders if order.total_amount)
    
    return render_template('admin/modern_dashboard.html',
                         active_orders=active_orders,
                         available_drivers=available_drivers,
                         kitchen_queue=kitchen_queue,
                         today_sales=today_sales)

@admin_bp.route('/system-config')
@login_required
def system_config():
    """System configuration page"""
    return render_template('admin/system_config.html')

# Role and Permission Management Routes
@admin_bp.route('/roles')
@login_required
@require_permission('roles.view')
def roles():
    """List all roles"""
    roles = Role.query.all()
    return render_template('admin/roles.html', roles=roles)

@admin_bp.route('/roles/create', methods=['GET', 'POST'])
@login_required
@require_permission('roles.create')
def create_role():
    """Create new role"""
    if request.method == 'POST':
        name = request.form.get('name')
        display_name = request.form.get('display_name')
        description = request.form.get('description')
        permission_ids = request.form.getlist('permissions')
        
        if not name or not display_name:
            flash('שם התפקיד ושם התצוגה נדרשים', 'error')
            return redirect(request.url)
        
        # Check if role already exists
        if Role.query.filter_by(name=name).first():
            flash('תפקיד עם השם הזה כבר קיים', 'error')
            return redirect(request.url)
        
        # Create new role
        role = Role(
            name=name,
            display_name=display_name,
            description=description
        )
        
        # Add permissions
        if permission_ids:
            permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()
            role.permissions = permissions
        
        db.session.add(role)
        db.session.commit()
        
        flash(f'התפקיד "{display_name}" נוצר בהצלחה', 'success')
        return redirect(url_for('admin.roles'))
    
    # Get all permissions grouped by category
    permissions = Permission.query.order_by(Permission.category, Permission.display_name).all()
    permissions_by_category = {}
    for perm in permissions:
        if perm.category not in permissions_by_category:
            permissions_by_category[perm.category] = []
        permissions_by_category[perm.category].append(perm)
    
    return render_template('admin/create_role.html', permissions_by_category=permissions_by_category)

@admin_bp.route('/roles/<int:role_id>/edit', methods=['GET', 'POST'])
@login_required
@require_permission('roles.edit')
def edit_role(role_id):
    """Edit existing role"""
    role = Role.query.get_or_404(role_id)
    
    if request.method == 'POST':
        display_name = request.form.get('display_name')
        description = request.form.get('description')
        permission_ids = request.form.getlist('permissions')
        
        if not display_name:
            flash('שם התצוגה נדרש', 'error')
            return redirect(request.url)
        
        role.display_name = display_name
        role.description = description
        
        # Update permissions
        if permission_ids:
            permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()
            role.permissions = permissions
        else:
            role.permissions = []
        
        db.session.commit()
        
        flash(f'התפקיד "{display_name}" עודכן בהצלחה', 'success')
        return redirect(url_for('admin.roles'))
    
    # Get all permissions grouped by category
    permissions = Permission.query.order_by(Permission.category, Permission.display_name).all()
    permissions_by_category = {}
    for perm in permissions:
        if perm.category not in permissions_by_category:
            permissions_by_category[perm.category] = []
        permissions_by_category[perm.category].append(perm)
    
    return render_template('admin/edit_role.html', role=role, permissions_by_category=permissions_by_category)

@admin_bp.route('/roles/<int:role_id>/delete', methods=['DELETE'])
@login_required
@require_permission('roles.delete')
def delete_role(role_id):
    """Delete role"""
    role = Role.query.get_or_404(role_id)
    
    # Prevent deletion of system roles
    if role.is_system_role:
        return jsonify({'success': False, 'error': 'לא ניתן למחוק תפקיד מערכת'}), 400
    
    # Check if role has users
    if role.users:
        return jsonify({'success': False, 'error': f'לא ניתן למחוק תפקיד עם {len(role.users)} משתמשים'}), 400
    
    role_name = role.display_name
    db.session.delete(role)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'התפקיד "{role_name}" נמחק בהצלחה'})

@admin_bp.route('/permissions')
@login_required
@require_permission('roles.view')
def permissions():
    """List all permissions"""
    permissions = Permission.query.order_by(Permission.category, Permission.display_name).all()
    permissions_by_category = {}
    for perm in permissions:
        if perm.category not in permissions_by_category:
            permissions_by_category[perm.category] = []
        permissions_by_category[perm.category].append(perm)
    
    return render_template('admin/permissions.html', permissions_by_category=permissions_by_category)

@admin_bp.route('/kitchen-config')
@login_required
def kitchen_config():
    """Kitchen and printer configuration"""
    from services.kitchen.kitchen_service import PrinterConfig, KitchenStation
    
    printers = PrinterConfig.query.all()
    stations = KitchenStation.query.all()
    
    return render_template('admin/kitchen_config.html',
                         printers=printers,
                         stations=stations)

@admin_bp.route('/payment-config')
@login_required
def payment_config():
    """Payment gateway configuration"""
    from services.payment.payment_service import PaymentConfig
    
    configs = PaymentConfig.query.all()
    return render_template('admin/system_config.html', configs=configs)

@admin_bp.route('/drivers-management')
@login_required
def drivers_management():
    """Driver management page"""
    from services.delivery.delivery_service import Driver
    
    drivers = Driver.query.all()
    return render_template('admin/system_config.html', drivers=drivers)

@admin_bp.route('/orders-management')
@login_required
def orders_management():
    """Orders management page"""
    from services.order.order_service import Order
    
    orders = Order.query.order_by(Order.created_at.desc()).limit(100).all()
    return render_template('admin/system_config.html', orders=orders)

@admin_bp.route('/customers-management')
@login_required
def customers_management():
    """Customer management page"""
    from services.auth.auth_service import Customer
    
    customers = Customer.query.all()
    return render_template('admin/system_config.html', customers=customers)

@admin_bp.route('/printer-guide')
@login_required
def printer_guide():
    """SNBC Printer setup guide"""
    return render_template('admin/printer_setup_guide.html')

# ===== STOCK MANAGEMENT MICROSERVICE ROUTES =====

@admin_bp.route('/stock-management')
@login_required
@require_permission('stock.view')
def stock_management():
    """Main stock management dashboard"""
    from models import StockItem, StockLevel, Branch, StockAlert, Supplier, StockCategory
    
    # Get current branch or default to first branch
    branch_id = request.args.get('branch_id', type=int)
    if not branch_id:
        branch = Branch.query.filter_by(is_active=True).first()
        branch_id = branch.id if branch else None
    
    branches = Branch.query.filter_by(is_active=True).all()
    
    # Get all stock items, suppliers, and categories
    stock_items = StockItem.query.filter_by(is_active=True).order_by(StockItem.name_he).all()
    suppliers = Supplier.query.filter_by(is_active=True).order_by(Supplier.name).all()
    stock_categories = StockCategory.query.filter_by(is_active=True).order_by(StockCategory.name_he).all()
    
    # Get stock statistics for the selected branch
    stats = {}
    if branch_id:
        total_items = StockItem.query.filter_by(is_active=True).count()
        low_stock_alerts = StockAlert.query.filter_by(
            branch_id=branch_id, 
            alert_type='low_stock', 
            is_resolved=False
        ).count()
        out_of_stock = StockLevel.query.filter_by(
            branch_id=branch_id
        ).filter(StockLevel.current_quantity <= 0).count()
        expiring_soon = StockAlert.query.filter_by(
            branch_id=branch_id, 
            alert_type='expiring_soon', 
            is_resolved=False
        ).count()
        
        stats = {
            'total_items': total_items,
            'low_stock_alerts': low_stock_alerts,
            'out_of_stock': out_of_stock,
            'expiring_soon': expiring_soon
        }
    
    return render_template('admin/stock_management.html', 
                         branches=branches, 
                         current_branch_id=branch_id,
                         stats=stats,
                         stock_items=stock_items,
                         suppliers=suppliers,
                         stock_categories=stock_categories)

@admin_bp.route('/stock/item/add', methods=['POST'])
@login_required
@require_permission('stock.manage')
def add_stock_item():
    """Add new stock item"""
    from models import StockItem
    
    try:
        name_he = request.form.get('name_he')
        name_en = request.form.get('name_en', '')
        category_id = request.form.get('category_id', type=int)
        supplier_id = request.form.get('supplier_id', type=int)
        unit = request.form.get('unit', 'יחידות')
        minimum_stock = request.form.get('minimum_stock', 0, type=float)
        reorder_point = request.form.get('reorder_point', 0, type=float)
        cost_per_unit = request.form.get('cost_per_unit', 0, type=float)
        
        item = StockItem(
            name_he=name_he,
            name_en=name_en,
            category_id=category_id if category_id else None,
            supplier_id=supplier_id if supplier_id else None,
            unit=unit,
            minimum_stock=minimum_stock,
            reorder_point=reorder_point,
            cost_per_unit=cost_per_unit,
            is_active=True
        )
        
        db.session.add(item)
        db.session.commit()
        
        flash('פריט נוסף בהצלחה!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'שגיאה בהוספת הפריט: {str(e)}', 'danger')
    
    return redirect(url_for('admin.stock_management'))

@admin_bp.route('/stock/category/add', methods=['POST'])
@login_required
@require_permission('stock.manage')
def add_stock_category():
    """Add new stock category"""
    from models import StockCategory
    
    try:
        name_he = request.form.get('name_he')
        name_en = request.form.get('name_en', '')
        description = request.form.get('description', '')
        
        category = StockCategory(
            name_he=name_he,
            name_en=name_en,
            description=description,
            is_active=True
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash('קטגוריה נוספה בהצלחה!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'שגיאה בהוספת הקטגוריה: {str(e)}', 'danger')
    
    return redirect(url_for('admin.stock_management'))

@admin_bp.route('/stock/reports/monthly-costs')
@login_required
@require_permission('stock.view')
def monthly_cost_reports():
    """Monthly cost and expense reports"""
    from models import StockTransaction, StockItem
    from sqlalchemy import func, extract
    from datetime import datetime, timedelta
    import calendar
    
    # Get year and month from query params or default to current
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    # Calculate date range for the selected month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    # Get transactions for the month
    transactions = db.session.query(
        StockTransaction.transaction_type,
        StockItem.name_he,
        StockItem.category_id,
        func.sum(StockTransaction.quantity).label('total_quantity'),
        func.sum(StockTransaction.total_cost).label('total_cost')
    ).join(
        StockItem, StockTransaction.item_id == StockItem.id
    ).filter(
        StockTransaction.transaction_date >= start_date,
        StockTransaction.transaction_date < end_date
    ).group_by(
        StockTransaction.transaction_type,
        StockItem.name_he,
        StockItem.category_id
    ).all()
    
    # Calculate summary
    purchases = sum(t.total_cost or 0 for t in transactions if t.transaction_type == 'delivery')
    usage = sum(t.total_cost or 0 for t in transactions if t.transaction_type == 'usage')
    waste = sum(t.total_cost or 0 for t in transactions if t.transaction_type == 'waste')
    total_expenses = purchases + usage + waste
    
    # Get monthly comparison (last 6 months)
    monthly_data = []
    for i in range(5, -1, -1):
        target_date = datetime.now() - timedelta(days=30*i)
        target_month = target_date.month
        target_year = target_date.year
        
        month_start = datetime(target_year, target_month, 1)
        if target_month == 12:
            month_end = datetime(target_year + 1, 1, 1)
        else:
            month_end = datetime(target_year, target_month + 1, 1)
        
        month_total = db.session.query(
            func.sum(StockTransaction.total_cost)
        ).filter(
            StockTransaction.transaction_date >= month_start,
            StockTransaction.transaction_date < month_end
        ).scalar() or 0
        
        monthly_data.append({
            'month': calendar.month_name[target_month],
            'year': target_year,
            'total': month_total
        })
    
    return render_template('admin/monthly_cost_reports.html',
                         year=year,
                         month=month,
                         month_name=calendar.month_name[month],
                         transactions=transactions,
                         summary={
                             'purchases': purchases,
                             'usage': usage,
                             'waste': waste,
                             'total': total_expenses
                         },
                         monthly_data=monthly_data)

@admin_bp.route('/stock-items')
@login_required
@require_permission('stock.view')
def stock_items():
    """Stock items management"""
    from models import StockItem, StockCategory, Supplier
    
    # Get filter parameters
    category_id = request.args.get('category_id', type=int)
    item_type = request.args.get('item_type')
    search_query = request.args.get('search', '')
    
    # Build query
    query = StockItem.query.filter_by(is_active=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    if item_type:
        query = query.filter_by(item_type=item_type)
    if search_query:
        query = query.filter(
            db.or_(
                StockItem.name_he.contains(search_query),
                StockItem.name_en.contains(search_query),
                StockItem.sku.contains(search_query)
            )
        )
    
    items = query.order_by(StockItem.name_he).all()
    categories = StockCategory.query.filter_by(is_active=True).all()
    suppliers = Supplier.query.filter_by(is_active=True).all()
    
    return render_template('admin/stock_items.html', 
                         items=items, 
                         categories=categories,
                         suppliers=suppliers,
                         filters={
                             'category_id': category_id,
                             'item_type': item_type,
                             'search': search_query
                         })

@admin_bp.route('/stock-levels')
@login_required
@require_permission('stock.view')
def stock_levels():
    """Stock levels by branch"""
    from models import StockLevel, Branch, StockItem
    
    branch_id = request.args.get('branch_id', type=int)
    if not branch_id:
        branch = Branch.query.filter_by(is_active=True).first()
        branch_id = branch.id if branch else None
    
    if branch_id:
        levels = StockLevel.query.join(StockItem).filter(
            StockLevel.branch_id == branch_id,
            StockItem.is_active == True
        ).order_by(StockItem.name_he).all()
    else:
        levels = []
    
    branches = Branch.query.filter_by(is_active=True).all()
    
    return render_template('admin/stock_levels.html', 
                         levels=levels, 
                         branches=branches,
                         current_branch_id=branch_id)

@admin_bp.route('/stock-transactions')
@login_required
@require_permission('stock.view')
def stock_transactions():
    """Stock transaction history"""
    from models import StockTransaction, Branch, StockItem
    
    branch_id = request.args.get('branch_id', type=int)
    transaction_type = request.args.get('type')
    page = request.args.get('page', 1, type=int)
    
    query = StockTransaction.query.join(StockItem)
    
    if branch_id:
        query = query.filter(StockTransaction.branch_id == branch_id)
    if transaction_type:
        query = query.filter(StockTransaction.transaction_type == transaction_type)
    
    transactions = query.order_by(StockTransaction.created_at.desc()).limit(50).all()
    
    branches = Branch.query.filter_by(is_active=True).all()
    
    return render_template('admin/stock_transactions.html', 
                         transactions=transactions, 
                         branches=branches,
                         current_branch_id=branch_id,
                         current_type=transaction_type)

@admin_bp.route('/shopping-lists')
@login_required
@require_permission('stock.view')
def shopping_lists():
    """Shopping lists management"""
    from models import ShoppingList, Branch, Supplier
    
    branch_id = request.args.get('branch_id', type=int)
    status = request.args.get('status')
    
    query = ShoppingList.query
    
    if branch_id:
        query = query.filter_by(branch_id=branch_id)
    if status:
        query = query.filter_by(status=status)
    
    lists = query.order_by(ShoppingList.created_at.desc()).all()
    branches = Branch.query.filter_by(is_active=True).all()
    suppliers = Supplier.query.filter_by(is_active=True).all()
    
    return render_template('admin/shopping_lists.html', 
                         shopping_lists=lists, 
                         branches=branches,
                         suppliers=suppliers,
                         current_branch_id=branch_id,
                         current_status=status)

@admin_bp.route('/stock-alerts')
@login_required
@require_permission('stock.view')
def stock_alerts():
    """Stock alerts dashboard"""
    from models import StockAlert, Branch, StockItem
    
    branch_id = request.args.get('branch_id', type=int)
    alert_type = request.args.get('type')
    show_resolved = request.args.get('resolved', False, type=bool)
    
    query = StockAlert.query.join(StockItem)
    
    if branch_id:
        query = query.filter(StockAlert.branch_id == branch_id)
    if alert_type:
        query = query.filter(StockAlert.alert_type == alert_type)
    if not show_resolved:
        query = query.filter(StockAlert.is_resolved == False)
    
    alerts = query.order_by(StockAlert.created_at.desc()).all()
    branches = Branch.query.filter_by(is_active=True).all()
    
    # Calculate alert statistics
    alert_stats = {
        'critical': StockAlert.query.filter_by(severity='critical', is_resolved=False).count(),
        'medium': StockAlert.query.filter_by(severity='medium', is_resolved=False).count(), 
        'low': StockAlert.query.filter_by(severity='low', is_resolved=False).count(),
        'resolved': StockAlert.query.filter_by(is_resolved=True).count()
    }
    
    return render_template('admin/stock_alerts.html', 
                         alerts=alerts, 
                         branches=branches,
                         current_branch_id=branch_id,
                         current_type=alert_type,
                         show_resolved=show_resolved,
                         alert_stats=alert_stats)

@admin_bp.route('/stock-suppliers')
@login_required
@require_permission('stock.manage')
def stock_suppliers():
    """Suppliers management"""
    from models import Supplier
    
    suppliers = Supplier.query.order_by(Supplier.name).all()
    
    return render_template('admin/stock_suppliers.html', suppliers=suppliers)

@admin_bp.route('/stock-suppliers/add', methods=['GET', 'POST'])
@login_required
@require_permission('stock.manage')
def add_supplier():
    """Add new supplier"""
    if request.method == 'POST':
        from models import Supplier
        
        try:
            supplier = Supplier(
                name=request.form['name'].strip(),
                contact_person=request.form.get('contact_person', '').strip(),
                phone=request.form.get('phone', '').strip(),
                email=request.form.get('email', '').strip(),
                address=request.form.get('address', '').strip(),
                delivery_days=request.form.get('delivery_days', '1111111'),
                delivery_time=request.form.get('delivery_time', '').strip(),
                minimum_order=float(request.form.get('minimum_order', 0) or 0),
                payment_terms=request.form.get('payment_terms', '').strip(),
                notes=request.form.get('notes', '').strip()
            )
            
            db.session.add(supplier)
            db.session.commit()
            
            flash('ספק חדש נוסף בהצלחה', 'success')
            return redirect(url_for('admin.stock_suppliers'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'שגיאה בהוספת ספק: {str(e)}', 'error')
    
    return render_template('admin/add_supplier.html')

@admin_bp.route('/stock-suppliers/<int:supplier_id>/edit', methods=['GET', 'POST'])
@login_required
@require_permission('stock.manage')
def edit_supplier(supplier_id):
    """Edit supplier"""
    from models import Supplier
    
    supplier = Supplier.query.get_or_404(supplier_id)
    
    if request.method == 'POST':
        try:
            supplier.name = request.form['name'].strip()
            supplier.contact_person = request.form.get('contact_person', '').strip()
            supplier.phone = request.form.get('phone', '').strip()
            supplier.email = request.form.get('email', '').strip()
            supplier.address = request.form.get('address', '').strip()
            supplier.delivery_days = request.form.get('delivery_days', '1111111')
            supplier.delivery_time = request.form.get('delivery_time', '').strip()
            supplier.minimum_order = float(request.form.get('minimum_order', 0) or 0)
            supplier.payment_terms = request.form.get('payment_terms', '').strip()
            supplier.notes = request.form.get('notes', '').strip()
            
            db.session.commit()
            
            flash('פרטי ספק עודכנו בהצלחה', 'success')
            return redirect(url_for('admin.stock_suppliers'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'שגיאה בעדכון ספק: {str(e)}', 'error')
    
    return render_template('admin/edit_supplier.html', supplier=supplier)

@admin_bp.route('/stock-suppliers/<int:supplier_id>/toggle', methods=['POST'])
@login_required
@require_permission('stock.manage')
def toggle_supplier(supplier_id):
    """Toggle supplier active status"""
    from models import Supplier
    
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        supplier.is_active = not supplier.is_active
        
        db.session.commit()
        
        status = 'הופעל' if supplier.is_active else 'הושבת'
        flash(f'ספק {supplier.name} {status} בהצלחה', 'success')
        
        return redirect(url_for('admin.stock_suppliers'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'שגיאה בשינוי סטטוס ספק: {str(e)}', 'error')
        return redirect(url_for('admin.stock_suppliers'))

@admin_bp.route('/stock-suppliers/<int:supplier_id>/items')
@login_required
@require_permission('stock.view')
def supplier_items(supplier_id):
    """View items from specific supplier"""
    from models import Supplier, SupplierItem, StockItem
    
    supplier = Supplier.query.get_or_404(supplier_id)
    
    # Get items associated with this supplier
    supplier_items = db.session.query(SupplierItem, StockItem).join(
        StockItem, SupplierItem.item_id == StockItem.id
    ).filter(SupplierItem.supplier_id == supplier_id).all()
    
    return render_template('admin/supplier_items.html', 
                         supplier=supplier, 
                         supplier_items=supplier_items)

@admin_bp.route('/stock-suppliers/<int:supplier_id>/delete', methods=['POST'])
@login_required
@require_permission('stock.manage')
def delete_supplier(supplier_id):
    """Delete supplier (soft delete by setting is_active=False)"""
    from models import Supplier
    
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        
        # Check if supplier has any associated items or receipts
        from models import SupplierItem, Receipt
        has_items = SupplierItem.query.filter_by(supplier_id=supplier_id).first() is not None
        has_receipts = Receipt.query.filter_by(supplier_id=supplier_id).first() is not None
        
        if has_items or has_receipts:
            # Soft delete - just deactivate
            supplier.is_active = False
            flash(f'ספק {supplier.name} הושבת (יש לו נתונים משויכים)', 'warning')
        else:
            # Hard delete if no associated data
            db.session.delete(supplier)
            flash(f'ספק {supplier.name} נמחק לחלוטין', 'success')
        
        db.session.commit()
        return redirect(url_for('admin.stock_suppliers'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'שגיאה במחיקת ספק: {str(e)}', 'error')
        return redirect(url_for('admin.stock_suppliers'))

@admin_bp.route('/stock-settings')
@login_required
@require_permission('stock.settings')
def stock_settings():
    """Stock management settings"""
    from models import StockSettings, Branch
    
    branch_id = request.args.get('branch_id', type=int)
    
    # Get or create settings for the branch
    if branch_id:
        settings = StockSettings.query.filter_by(branch_id=branch_id).first()
        if not settings:
            settings = StockSettings(branch_id=branch_id)
            db.session.add(settings)
            db.session.commit()
    else:
        # Global settings
        settings = StockSettings.query.filter_by(branch_id=None).first()
        if not settings:
            settings = StockSettings()
            db.session.add(settings)
            db.session.commit()
    
    branches = Branch.query.filter_by(is_active=True).all()
    
    return render_template('admin/stock_settings.html', 
                         settings=settings, 
                         branches=branches,
                         current_branch_id=branch_id)

@admin_bp.route('/stock-analytics')
@login_required
@require_permission('stock.view')
def stock_analytics():
    """Stock analytics and reports"""
    from models import StockTransaction, StockLevel, Branch, StockItem
    from datetime import datetime, timedelta
    
    branch_id = request.args.get('branch_id', type=int)
    period = request.args.get('period', '30')  # days
    
    if not branch_id:
        branch = Branch.query.filter_by(is_active=True).first()
        branch_id = branch.id if branch else None
    
    analytics_data = {}
    
    if branch_id:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=int(period))
        
        # Get transaction data for charts
        transactions = StockTransaction.query.filter(
            StockTransaction.branch_id == branch_id,
            StockTransaction.created_at >= start_date
        ).all()
        
        # Get current stock levels
        stock_levels = StockLevel.query.join(StockItem).filter(StockLevel.branch_id == branch_id).all()
        
        # Calculate additional analytics
        total_items = StockItem.query.filter_by(is_active=True).count()
        low_stock_items = len([level for level in stock_levels if level.available_quantity <= level.item.minimum_stock])
        out_of_stock_items = len([level for level in stock_levels if level.available_quantity <= 0])
        full_stock_items = len([level for level in stock_levels if level.available_quantity >= level.item.maximum_stock])
        total_value = sum([level.available_quantity * level.item.cost_per_unit for level in stock_levels])
        
        analytics_data = {
            'total_transactions': len(transactions),
            'transactions': transactions,
            'stock_levels': stock_levels[:10],  # Limit for display
            'period': period,
            'start_date': start_date,
            'end_date': end_date,
            'active_items': total_items,
            'low_stock_items': low_stock_items,
            'out_of_stock_items': out_of_stock_items,
            'full_stock_items': full_stock_items,
            'total_value': total_value
        }
    
    branches = Branch.query.filter_by(is_active=True).all()
    
    return render_template('admin/stock_analytics.html', 
                         analytics=analytics_data, 
                         branches=branches,
                         current_branch_id=branch_id,
                         period=period)

# ===== RECEIPT MANAGEMENT & OCR PROCESSING =====

@admin_bp.route('/receipts')
@login_required
@require_permission('stock.manage')
def receipts():
    """Receipt management dashboard"""
    from models import Receipt, Branch, Supplier
    
    branch_id = request.args.get('branch_id', type=int)
    status = request.args.get('status')
    supplier_id = request.args.get('supplier_id', type=int)
    
    query = Receipt.query
    
    if branch_id:
        query = query.filter_by(branch_id=branch_id)
    if status:
        query = query.filter_by(ocr_status=status)
    if supplier_id:
        query = query.filter_by(supplier_id=supplier_id)
    
    receipts = query.order_by(Receipt.created_at.desc()).limit(50).all()
    branches = Branch.query.filter_by(is_active=True).all()
    suppliers = Supplier.query.filter_by(is_active=True).all()
    
    return render_template('admin/receipts.html',
                         receipts=receipts,
                         branches=branches,
                         suppliers=suppliers,
                         current_branch_id=branch_id,
                         current_status=status,
                         current_supplier_id=supplier_id)

@admin_bp.route('/receipts/upload', methods=['GET', 'POST'])
@login_required
@require_permission('stock.manage')
def upload_receipt():
    """Upload and process receipt image"""
    if request.method == 'POST':
        from models import Receipt, Branch, Supplier
        from ocr_service import ReceiptOCRService
        import os
        from werkzeug.utils import secure_filename
        from datetime import datetime
        
        try:
            # Get form data
            file = request.files.get('receipt_image')
            branch_id = request.form.get('branch_id', type=int)
            supplier_id = request.form.get('supplier_id', type=int) if request.form.get('supplier_id') else None
            
            if not file or file.filename == '':
                flash('לא נבחר קובץ', 'error')
                return redirect(request.url)
            
            if not branch_id:
                flash('חובה לבחור סניף', 'error')
                return redirect(request.url)
            
            # Validate file type
            allowed_extensions = {'jpg', 'jpeg', 'png', 'pdf'}
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            
            if file_extension not in allowed_extensions:
                flash('סוג קובץ לא נתמך. אנא העלה JPG, PNG או PDF', 'error')
                return redirect(request.url)
            
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join('static', 'uploads', 'receipts')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(upload_dir, new_filename)
            
            # Save file
            file.save(file_path)
            
            # Create receipt record
            receipt = Receipt(
                image_path=file_path,
                original_filename=filename,
                file_size=os.path.getsize(file_path),
                branch_id=branch_id,
                supplier_id=supplier_id,
                ocr_status='pending'
            )
            
            db.session.add(receipt)
            db.session.commit()
            
            # Process OCR in background (for now, process immediately)
            try:
                ocr_service = ReceiptOCRService()
                result = ocr_service.process_receipt_image(file_path)
                
                # Update receipt with OCR results
                receipt.ocr_status = result['status'] if result['status'] == 'success' else 'failed'
                receipt.ocr_data = result.get('data', {})
                receipt.ocr_confidence = result.get('confidence', 0.0)
                receipt.processed_at = datetime.utcnow()
                
                # Extract basic information
                if result['status'] == 'success' and result.get('data'):
                    data = result['data']
                    if 'total_amount' in data:
                        receipt.total_amount = data['total_amount']
                    if 'tax_amount' in data:
                        receipt.tax_amount = data['tax_amount']
                    if 'receipt_number' in data:
                        receipt.receipt_number = data['receipt_number']
                    if 'receipt_date' in data:
                        receipt.receipt_date = datetime.fromisoformat(data['receipt_date']).date()
                
                db.session.commit()
                
                if result['status'] == 'success':
                    flash(f'קבלה הועלתה בהצלחה! נמצאו {len(result.get("data", {}).get("items", []))} פריטים', 'success')
                else:
                    flash('קבלה הועלתה אך עיבוד OCR נכשל', 'warning')
                    
            except Exception as ocr_error:
                receipt.ocr_status = 'failed'
                receipt.processing_errors = str(ocr_error)
                db.session.commit()
                flash('קבלה הועלתה אך עיבוד הטקסט נכשל', 'warning')
            
            return redirect(url_for('admin.receipts'))
            
        except Exception as e:
            flash(f'שגיאה בהעלאת הקבלה: {str(e)}', 'error')
            return redirect(request.url)
    
    # GET request - show upload form
    from models import Branch, Supplier
    branches = Branch.query.filter_by(is_active=True).all()
    suppliers = Supplier.query.filter_by(is_active=True).all()
    
    return render_template('admin/upload_receipt.html',
                         branches=branches,
                         suppliers=suppliers)

# ===== FILE IMPORT/EXPORT SYSTEM =====

@admin_bp.route('/stock/import', methods=['GET', 'POST'])
@login_required
@require_permission('stock.manage')
def import_stock_data():
    """Import stock data from Excel/CSV files"""
    if request.method == 'POST':
        import pandas as pd
        import os
        from werkzeug.utils import secure_filename
        from datetime import datetime
        from models import StockItem, Supplier, Category, Branch, StockLevel
        
        try:
            # Get form data
            file = request.files.get('import_file')
            branch_id = request.form.get('branch_id', type=int)
            import_type = request.form.get('import_type')  # 'items', 'stock_levels', 'suppliers'
            
            if not file or file.filename == '':
                flash('לא נבחר קובץ', 'error')
                return redirect(request.url)
            
            if not branch_id and import_type in ['stock_levels']:
                flash('חובה לבחור סניף עבור יבוא רמות מלאי', 'error')
                return redirect(request.url)
            
            # Validate file type
            allowed_extensions = {'csv', 'xlsx', 'xls'}
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            
            if file_extension not in allowed_extensions:
                flash('סוג קובץ לא נתמך. אנא העלה CSV או Excel', 'error')
                return redirect(request.url)
            
            # Save file temporarily
            upload_dir = os.path.join('static', 'uploads', 'import')
            os.makedirs(upload_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            temp_filename = f"{timestamp}_{filename}"
            temp_path = os.path.join(upload_dir, temp_filename)
            file.save(temp_path)
            
            # Read file
            try:
                if file_extension == 'csv':
                    df = pd.read_csv(temp_path)
                else:
                    df = pd.read_excel(temp_path)
            except Exception as e:
                os.remove(temp_path)
                flash(f'שגיאה בקריאת הקובץ: {str(e)}', 'error')
                return redirect(request.url)
            
            success_count = 0
            error_count = 0
            errors = []
            
            if import_type == 'items':
                # Import stock items
                for index, row in df.iterrows():
                    try:
                        # Get or create category
                        category = None
                        if pd.notna(row.get('category')):
                            category = Category.query.filter_by(name=str(row['category'])).first()
                            if not category:
                                category = Category(name=str(row['category']), description='Imported category')
                                db.session.add(category)
                                db.session.flush()
                        
                        # Get or create supplier
                        supplier = None
                        if pd.notna(row.get('supplier')):
                            supplier = Supplier.query.filter_by(name=str(row['supplier'])).first()
                            if not supplier:
                                supplier = Supplier(name=str(row['supplier']), contact_info='Imported supplier')
                                db.session.add(supplier)
                                db.session.flush()
                        
                        # Create stock item
                        item = StockItem(
                            name=str(row['name']),
                            description=str(row.get('description', '')),
                            sku=str(row.get('sku', '')),
                            unit_of_measure=str(row.get('unit', 'יחידה')),
                            cost_per_unit=float(row.get('cost', 0)),
                            minimum_stock=int(row.get('min_stock', 0)),
                            maximum_stock=int(row.get('max_stock', 100)),
                            category_id=category.id if category else None
                        )
                        
                        db.session.add(item)
                        db.session.flush()
                        
                        # Add supplier relationship if exists
                        if supplier:
                            from models import SupplierItem
                            supplier_item = SupplierItem(
                                supplier_id=supplier.id,
                                item_id=item.id,
                                supplier_sku=str(row.get('supplier_sku', '')),
                                cost_per_unit=float(row.get('supplier_cost', row.get('cost', 0)))
                            )
                            db.session.add(supplier_item)
                        
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        errors.append(f"שורה {index + 2}: {str(e)}")
                        
            elif import_type == 'stock_levels':
                # Import stock levels
                for index, row in df.iterrows():
                    try:
                        # Find item by name or SKU
                        item = None
                        if pd.notna(row.get('sku')):
                            item = StockItem.query.filter_by(sku=str(row['sku'])).first()
                        if not item and pd.notna(row.get('name')):
                            item = StockItem.query.filter_by(name=str(row['name'])).first()
                        
                        if not item:
                            error_count += 1
                            errors.append(f"שורה {index + 2}: פריט לא נמצא")
                            continue
                        
                        # Update or create stock level
                        stock_level = StockLevel.query.filter_by(
                            item_id=item.id,
                            branch_id=branch_id
                        ).first()
                        
                        quantity = int(row.get('quantity', 0))
                        
                        if stock_level:
                            stock_level.current_quantity = quantity
                            stock_level.available_quantity = quantity - stock_level.reserved_quantity
                            stock_level.last_updated = datetime.utcnow()
                        else:
                            stock_level = StockLevel(
                                item_id=item.id,
                                branch_id=branch_id,
                                current_quantity=quantity,
                                reserved_quantity=0,
                                available_quantity=quantity
                            )
                            db.session.add(stock_level)
                        
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        errors.append(f"שורה {index + 2}: {str(e)}")
            
            elif import_type == 'suppliers':
                # Import suppliers
                for index, row in df.iterrows():
                    try:
                        # Check if supplier already exists
                        existing = Supplier.query.filter_by(name=str(row['name'])).first()
                        if existing:
                            error_count += 1
                            errors.append(f"שורה {index + 2}: ספק כבר קיים")
                            continue
                        
                        supplier = Supplier(
                            name=str(row['name']),
                            contact_info=str(row.get('contact', '')),
                            email=str(row.get('email', '')),
                            phone=str(row.get('phone', '')),
                            address=str(row.get('address', ''))
                        )
                        
                        db.session.add(supplier)
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        errors.append(f"שורה {index + 2}: {str(e)}")
            
            # Commit changes
            db.session.commit()
            
            # Clean up temp file
            os.remove(temp_path)
            
            # Show results
            if success_count > 0:
                flash(f'יובאו בהצלחה {success_count} רשומות', 'success')
            if error_count > 0:
                flash(f'{error_count} שגיאות בייבוא. ראה פרטים למטה.', 'warning')
                for error in errors[:10]:  # Show first 10 errors
                    flash(error, 'error')
            
            return redirect(url_for('admin.stock_management'))
            
        except Exception as e:
            flash(f'שגיאה בייבוא: {str(e)}', 'error')
            return redirect(request.url)
    
    # GET request - show import form
    from models import Branch
    branches = Branch.query.filter_by(is_active=True).all()
    
    return render_template('admin/import_stock.html', branches=branches)

@admin_bp.route('/stock/export')
@login_required
@require_permission('stock.view')
def export_stock_data():
    """Export stock data to Excel"""
    import pandas as pd
    from io import BytesIO
    from flask import send_file
    from models import StockItem, StockLevel, Supplier, Category, Branch
    from datetime import datetime
    
    try:
        export_type = request.args.get('type', 'items')
        branch_id = request.args.get('branch_id', type=int)
        
        # Create Excel writer
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if export_type == 'items' or export_type == 'all':
                # Export stock items
                items_query = db.session.query(
                    StockItem.id,
                    StockItem.name,
                    StockItem.description,
                    StockItem.sku,
                    StockItem.unit_of_measure.label('unit'),
                    StockItem.cost_per_unit.label('cost'),
                    StockItem.minimum_stock.label('min_stock'),
                    StockItem.maximum_stock.label('max_stock'),
                    Category.name.label('category')
                ).outerjoin(Category).filter(StockItem.is_active == True)
                
                items_df = pd.read_sql(items_query.statement, db.engine)
                items_df.to_excel(writer, sheet_name='Stock Items', index=False)
            
            if export_type == 'levels' or export_type == 'all':
                # Export stock levels
                levels_query = db.session.query(
                    StockItem.name,
                    StockItem.sku,
                    StockLevel.current_quantity.label('quantity'),
                    StockLevel.available_quantity.label('available'),
                    StockLevel.reserved_quantity.label('reserved'),
                    Branch.name_he.label('branch'),
                    StockLevel.last_updated
                ).join(StockItem).join(Branch)
                
                if branch_id:
                    levels_query = levels_query.filter(StockLevel.branch_id == branch_id)
                
                levels_df = pd.read_sql(levels_query.statement, db.engine)
                levels_df.to_excel(writer, sheet_name='Stock Levels', index=False)
            
            if export_type == 'suppliers' or export_type == 'all':
                # Export suppliers
                suppliers_query = db.session.query(
                    Supplier.name,
                    Supplier.contact_info.label('contact'),
                    Supplier.email,
                    Supplier.phone,
                    Supplier.address
                ).filter(Supplier.is_active == True)
                
                suppliers_df = pd.read_sql(suppliers_query.statement, db.engine)
                suppliers_df.to_excel(writer, sheet_name='Suppliers', index=False)
        
        output.seek(0)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"stock_export_{export_type}_{timestamp}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        flash(f'שגיאה בייצוא: {str(e)}', 'error')
        return redirect(url_for('admin.stock_management'))

@admin_bp.route('/stock/template/<template_type>')
@login_required
@require_permission('stock.view')
def download_import_template(template_type):
    """Download import template files"""
    import pandas as pd
    from io import BytesIO
    from flask import send_file
    
    try:
        # Create template based on type
        if template_type == 'items':
            data = {
                'name': ['פריט דוגמה 1', 'פריט דוגמה 2'],
                'description': ['תיאור פריט 1', 'תיאור פריט 2'],
                'sku': ['SKU001', 'SKU002'],
                'unit': ['יחידה', 'ק"ג'],
                'cost': [10.50, 25.00],
                'min_stock': [5, 2],
                'max_stock': [100, 50],
                'category': ['קטגוריה א', 'קטגוריה ב'],
                'supplier': ['ספק א', 'ספק ב'],
                'supplier_sku': ['SUP_SKU001', 'SUP_SKU002'],
                'supplier_cost': [9.50, 23.00]
            }
        elif template_type == 'levels':
            data = {
                'name': ['פריט דוגמה 1', 'פריט דוגמה 2'],
                'sku': ['SKU001', 'SKU002'],
                'quantity': [50, 25]
            }
        elif template_type == 'suppliers':
            data = {
                'name': ['ספק דוגמה 1', 'ספק דוגמה 2'],
                'contact': ['איש קשר 1', 'איש קשר 2'],
                'email': ['supplier1@example.com', 'supplier2@example.com'],
                'phone': ['050-1234567', '050-7654321'],
                'address': ['כתובת 1', 'כתובת 2']
            }
        else:
            flash('סוג תבנית לא ידוע', 'error')
            return redirect(url_for('admin.import_stock_data'))
        
        # Create DataFrame and Excel file
        df = pd.DataFrame(data)
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Template', index=False)
        
        output.seek(0)
        
        filename = f"import_template_{template_type}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        flash(f'שגיאה ביצירת תבנית: {str(e)}', 'error')
        return redirect(url_for('admin.import_stock_data'))

# ===== PRINT TEMPLATE MANAGEMENT ROUTES =====

@admin_bp.route('/api/print-templates', methods=['GET'])
@login_required
@require_permission('checklist.manage')
def get_print_templates():
    """Get all print templates"""
    from models import PrintTemplate
    
    templates = PrintTemplate.query.order_by(PrintTemplate.is_default.desc(), PrintTemplate.name).all()
    
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'description': t.description,
        'branch_id': t.branch_id,
        'shift_type': t.shift_type,
        'is_default': t.is_default,
        'config': t.config,
        'created_at': t.created_at.isoformat() if t.created_at else None,
        'updated_at': t.updated_at.isoformat() if t.updated_at else None
    } for t in templates])

@admin_bp.route('/api/print-templates/<int:template_id>', methods=['GET'])
@login_required
@require_permission('checklist.manage')
def get_print_template(template_id):
    """Get a specific print template"""
    from models import PrintTemplate
    
    template = PrintTemplate.query.get_or_404(template_id)
    
    return jsonify({
        'id': template.id,
        'name': template.name,
        'description': template.description,
        'branch_id': template.branch_id,
        'shift_type': template.shift_type,
        'is_default': template.is_default,
        'config': template.config,
        'created_at': template.created_at.isoformat() if template.created_at else None,
        'updated_at': template.updated_at.isoformat() if template.updated_at else None
    })

@admin_bp.route('/api/print-templates', methods=['POST'])
@login_required
@require_permission('checklist.manage')
def create_print_template():
    """Create a new print template"""
    from models import PrintTemplate
    
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'שם התבנית חובה'}), 400
    
    # Check if name already exists
    existing = PrintTemplate.query.filter_by(name=data['name']).first()
    if existing:
        return jsonify({'error': 'תבנית עם שם זה כבר קיימת'}), 400
    
    # Validate config structure
    config = data.get('config', {})
    if not config.get('page') or not config.get('columns'):
        return jsonify({'error': 'תצורת תבנית לא תקינה'}), 400
    
    template = PrintTemplate(
        name=data['name'],
        description=data.get('description'),
        branch_id=data.get('branch_id'),
        shift_type=data.get('shift_type'),
        is_default=data.get('is_default', False),
        created_by=current_user.id,
        config=config
    )
    
    # If setting as default, unset other defaults
    if template.is_default:
        PrintTemplate.query.update({'is_default': False})
    
    db.session.add(template)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'id': template.id,
        'message': 'התבנית נוצרה בהצלחה'
    }), 201

@admin_bp.route('/api/print-templates/<int:template_id>', methods=['PUT'])
@login_required
@require_permission('checklist.manage')
def update_print_template(template_id):
    """Update a print template"""
    from models import PrintTemplate
    
    template = PrintTemplate.query.get_or_404(template_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'נתונים חסרים'}), 400
    
    # Check if renaming to existing name
    if 'name' in data and data['name'] != template.name:
        existing = PrintTemplate.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': 'תבנית עם שם זה כבר קיימת'}), 400
    
    # Update fields
    if 'name' in data:
        template.name = data['name']
    if 'description' in data:
        template.description = data['description']
    if 'branch_id' in data:
        template.branch_id = data['branch_id']
    if 'shift_type' in data:
        template.shift_type = data['shift_type']
    if 'config' in data:
        template.config = data['config']
    
    # Handle default setting
    if 'is_default' in data:
        if data['is_default'] and not template.is_default:
            # Unset other defaults
            PrintTemplate.query.filter(PrintTemplate.id != template_id).update({'is_default': False})
        template.is_default = data['is_default']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'התבנית עודכנה בהצלחה'
    })

@admin_bp.route('/api/print-templates/<int:template_id>', methods=['DELETE'])
@login_required
@require_permission('checklist.manage')
def delete_print_template(template_id):
    """Delete a print template"""
    from models import PrintTemplate
    
    template = PrintTemplate.query.get_or_404(template_id)
    
    # Don't delete the default template
    if template.is_default:
        return jsonify({'error': 'לא ניתן למחוק תבנית ברירת מחדל'}), 400
    
    db.session.delete(template)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'התבנית נמחקה בהצלחה'
    })

@admin_bp.route('/api/print-templates/<int:template_id>/duplicate', methods=['POST'])
@login_required
@require_permission('checklist.manage')
def duplicate_print_template(template_id):
    """Duplicate a print template"""
    from models import PrintTemplate
    import copy
    
    original = PrintTemplate.query.get_or_404(template_id)
    
    # Find unique name
    base_name = f"{original.name} - העתק"
    name = base_name
    counter = 1
    while PrintTemplate.query.filter_by(name=name).first():
        counter += 1
        name = f"{base_name} {counter}"
    
    # Create duplicate
    duplicate = PrintTemplate(
        name=name,
        description=original.description,
        branch_id=original.branch_id,
        shift_type=original.shift_type,
        is_default=False,
        created_by=current_user.id,
        config=copy.deepcopy(original.config)
    )
    
    db.session.add(duplicate)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'id': duplicate.id,
        'message': 'התבנית שוכפלה בהצלחה'
    }), 201

