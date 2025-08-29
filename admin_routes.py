from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from database import db
from models import *
import os
from datetime import datetime
import json

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    categories = MenuCategory.query.order_by(MenuCategory.display_order).all()
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
    if id:
        item = MenuItem.query.get_or_404(id)
    else:
        item = MenuItem()
    
    categories = MenuCategory.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
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
        
        # Dietary & Special Properties
        item.is_vegetarian = request.form.get('is_vegetarian') == 'on'
        item.is_vegan = request.form.get('is_vegan') == 'on'
        item.is_gluten_free = request.form.get('is_gluten_free') == 'on'
        item.is_dairy_free = request.form.get('is_dairy_free') == 'on'
        item.is_nut_free = request.form.get('is_nut_free') == 'on'
        item.is_spicy = request.form.get('is_spicy') == 'on'
        item.is_halal = request.form.get('is_halal') == 'on'
        item.is_kosher = request.form.get('is_kosher') == 'on'
        item.is_organic = request.form.get('is_organic') == 'on'
        item.is_signature = request.form.get('is_signature') == 'on'
        item.is_new = request.form.get('is_new') == 'on'
        item.is_popular = request.form.get('is_popular') == 'on'
        
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
        flash('Menu item saved successfully!', 'success')
        return redirect(url_for('admin.menu'))
    
    return render_template('admin/enhanced_menu_item.html', item=item, categories=categories)

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
        for item in cat.menu_items:
            if item.is_available:
                items.append({
                    'id': item.id,
                    'name_he': item.name_he,
                    'name_en': item.name_en,
                    'description_he': item.description_he,
                    'description_en': item.description_en,
                    'price': item.price,
                    'image_path': item.image_path,
                    'is_vegetarian': item.is_vegetarian,
                    'is_vegan': item.is_vegan,
                    'is_gluten_free': item.is_gluten_free,
                    'is_spicy': item.is_spicy
                })
        
        result.append({
            'id': cat.id,
            'name_he': cat.name_he,
            'name_en': cat.name_en,
            'description_he': cat.description_he,
            'description_en': cat.description_en,
            'items': items
        })
    
    return jsonify(result)