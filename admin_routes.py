from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from database import db
from models import *
import os
from datetime import datetime
import json
import pandas as pd

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

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