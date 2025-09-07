from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from database import db
from models import *
from permissions import require_permission, require_role, superadmin_required, has_permission
import os
from datetime import datetime
import json
import pandas as pd
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, URL, Optional

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
    submit = SubmitField('שמור')

UPLOAD_FOLDER = 'static/uploads'
CSV_UPLOAD_FOLDER = 'static/csv_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
ALLOWED_CSV_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin.settings'))
    
    return render_template('admin/settings.html', settings=settings)

# Media Management
@admin_bp.route('/media')
@login_required
def media():
    media_files = MediaFile.query.order_by(MediaFile.section, MediaFile.display_order).all()
    return render_template('admin/media.html', media_files=media_files)

@admin_bp.route('/media/upload', methods=['POST'])
@login_required
def upload_media():
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
    
    return jsonify({'error': 'Invalid file type'}), 400

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
        category.display_order = int(request.form.get('display_order', 0))
        category.is_active = request.form.get('is_active') == 'on'
        category.icon = request.form.get('icon')
        category.color = request.form.get('color')
        
        if not id:
            db.session.add(category)
        
        db.session.commit()
        flash('Category saved successfully!', 'success')
        return redirect(url_for('admin.menu'))
    
    return render_template('admin/enhanced_category.html', category=category)

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
        
        # Operations
        item.is_available = request.form.get('is_available') == 'on'
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

# Gallery Management
@admin_bp.route('/gallery')
@login_required
def gallery():
    photos = GalleryPhoto.query.order_by(GalleryPhoto.display_order).all()
    return render_template('admin/gallery.html', photos=photos)

@admin_bp.route('/gallery/upload', methods=['POST'])
@login_required
def upload_gallery():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files[]')
    uploaded = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"gallery_{timestamp}_{filename}"
            
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            photo = GalleryPhoto(
                file_path=f'/static/uploads/{filename}',
                caption_he=request.form.get('caption_he', ''),
                caption_en=request.form.get('caption_en', ''),
                display_order=GalleryPhoto.query.count()
            )
            db.session.add(photo)
            uploaded.append(photo.file_path)
    
    db.session.commit()
    return jsonify({'success': True, 'uploaded': uploaded})

# Checklist Management
@admin_bp.route('/checklist')
@login_required
def checklist():
    return render_template('admin/checklist_tasks.html')

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
    from models import StockItem, StockLevel, Branch, StockAlert
    
    # Get current branch or default to first branch
    branch_id = request.args.get('branch_id', type=int)
    if not branch_id:
        branch = Branch.query.filter_by(is_active=True).first()
        branch_id = branch.id if branch else None
    
    branches = Branch.query.filter_by(is_active=True).all()
    
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
                         stats=stats)

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
        levels = db.session.query(StockLevel, StockItem).join(
            StockItem, StockLevel.item_id == StockItem.id
        ).filter(
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
    
    query = db.session.query(StockTransaction, StockItem).join(
        StockItem, StockTransaction.item_id == StockItem.id
    )
    
    if branch_id:
        query = query.filter(StockTransaction.branch_id == branch_id)
    if transaction_type:
        query = query.filter(StockTransaction.transaction_type == transaction_type)
    
    transactions = query.order_by(StockTransaction.transaction_date.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
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
    
    query = db.session.query(StockAlert, StockItem).join(
        StockItem, StockAlert.item_id == StockItem.id
    )
    
    if branch_id:
        query = query.filter(StockAlert.branch_id == branch_id)
    if alert_type:
        query = query.filter(StockAlert.alert_type == alert_type)
    if not show_resolved:
        query = query.filter(StockAlert.is_resolved == False)
    
    alerts = query.order_by(StockAlert.created_at.desc()).all()
    branches = Branch.query.filter_by(is_active=True).all()
    
    return render_template('admin/stock_alerts.html', 
                         alerts=alerts, 
                         branches=branches,
                         current_branch_id=branch_id,
                         current_type=alert_type,
                         show_resolved=show_resolved)

@admin_bp.route('/stock-suppliers')
@login_required
@require_permission('stock.manage')
def stock_suppliers():
    """Suppliers management"""
    from models import Supplier
    
    suppliers = Supplier.query.order_by(Supplier.name).all()
    
    return render_template('admin/stock_suppliers.html', suppliers=suppliers)

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
            StockTransaction.transaction_date >= start_date
        ).all()
        
        # Get current stock levels
        stock_levels = db.session.query(StockLevel, StockItem).join(
            StockItem, StockLevel.item_id == StockItem.id
        ).filter(StockLevel.branch_id == branch_id).all()
        
        analytics_data = {
            'transactions': transactions,
            'stock_levels': stock_levels,
            'period': period,
            'start_date': start_date,
            'end_date': end_date
        }
    
    branches = Branch.query.filter_by(is_active=True).all()
    
    return render_template('admin/stock_analytics.html', 
                         analytics=analytics_data, 
                         branches=branches,
                         current_branch_id=branch_id)

