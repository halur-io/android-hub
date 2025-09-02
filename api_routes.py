from flask import Blueprint, jsonify, request
from models import (SiteSettings, Branch, WorkingHours, MenuCategory, 
                   MenuItem, MediaFile, DietaryProperty, ChecklistTask,
                   GeneratedChecklist, db)
from datetime import datetime
import logging

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Site Settings API
@api_bp.route('/settings', methods=['GET'])
def get_site_settings():
    """Get site settings for the website"""
    try:
        settings = SiteSettings.query.first()
        if not settings:
            # Create default settings if none exist
            settings = SiteSettings()
            db.session.add(settings)
            db.session.commit()
        
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
    except Exception as e:
        logging.error(f"Error fetching site settings: {e}")
        return jsonify({'error': 'Failed to fetch settings'}), 500

# Branches API
@api_bp.route('/branches', methods=['GET'])
def get_branches():
    """Get all active branches with working hours"""
    try:
        branches = Branch.query.filter_by(is_active=True).order_by(Branch.display_order).all()
        
        branches_data = []
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
            
            branches_data.append({
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
        
        return jsonify(branches_data)
    except Exception as e:
        logging.error(f"Error fetching branches: {e}")
        return jsonify({'error': 'Failed to fetch branches'}), 500

# Menu API
@api_bp.route('/menu', methods=['GET'])
def get_menu():
    """Get complete menu with categories and items"""
    try:
        categories = MenuCategory.query.filter_by(is_active=True).order_by(MenuCategory.display_order).all()
        
        menu_data = []
        for category in categories:
            items = []
            for item in category.menu_items:
                if item.is_available:
                    # Calculate effective price
                    effective_price = item.base_price
                    if item.discount_percentage:
                        effective_price = item.base_price * (1 - item.discount_percentage / 100)
                    
                    # Get dietary properties
                    dietary_props = [{'id': dp.id, 'name_he': dp.name_he, 'name_en': dp.name_en, 
                                     'icon': dp.icon, 'color': dp.color} 
                                    for dp in item.dietary_properties]
                    
                    items.append({
                        'id': item.id,
                        'name_he': item.name_he,
                        'name_en': item.name_en,
                        'description_he': item.description_he,
                        'description_en': item.description_en,
                        'base_price': item.base_price,
                        'effective_price': effective_price,
                        'discount_percentage': item.discount_percentage,
                        'image_path': item.image_path,
                        'is_vegetarian': item.is_vegetarian,
                        'is_vegan': item.is_vegan,
                        'is_gluten_free': item.is_gluten_free,
                        'is_spicy': item.is_spicy,
                        'is_signature': item.is_signature,
                        'is_new': item.is_new,
                        'is_popular': item.is_popular,
                        'spice_level': item.spice_level,
                        'dietary_properties': dietary_props,
                        'special_offer_text_he': item.special_offer_text_he,
                        'special_offer_text_en': item.special_offer_text_en
                    })
            
            if items:  # Only include categories with items
                menu_data.append({
                    'id': category.id,
                    'name_he': category.name_he,
                    'name_en': category.name_en,
                    'description_he': category.description_he,
                    'description_en': category.description_en,
                    'icon': category.icon,
                    'color': category.color,
                    'items': items
                })
        
        return jsonify(menu_data)
    except Exception as e:
        logging.error(f"Error fetching menu: {e}")
        return jsonify({'error': 'Failed to fetch menu'}), 500

# Gallery/Media API
@api_bp.route('/gallery', methods=['GET'])
def get_gallery():
    """Get gallery images"""
    try:
        section = request.args.get('section', 'gallery')
        media_files = MediaFile.query.filter_by(
            section=section, 
            is_active=True,
            file_type='image'
        ).order_by(MediaFile.display_order).all()
        
        gallery_data = []
        for media in media_files:
            gallery_data.append({
                'id': media.id,
                'file_path': media.file_path,
                'caption_he': media.caption_he,
                'caption_en': media.caption_en
            })
        
        return jsonify(gallery_data)
    except Exception as e:
        logging.error(f"Error fetching gallery: {e}")
        return jsonify({'error': 'Failed to fetch gallery'}), 500

# Dietary Properties API
@api_bp.route('/dietary-properties', methods=['GET'])
def get_dietary_properties():
    """Get all dietary properties"""
    try:
        properties = DietaryProperty.query.filter_by(is_active=True).order_by(DietaryProperty.display_order).all()
        
        props_data = []
        for prop in properties:
            props_data.append({
                'id': prop.id,
                'name_he': prop.name_he,
                'name_en': prop.name_en,
                'icon': prop.icon,
                'color': prop.color,
                'description_he': prop.description_he,
                'description_en': prop.description_en
            })
        
        return jsonify(props_data)
    except Exception as e:
        logging.error(f"Error fetching dietary properties: {e}")
        return jsonify({'error': 'Failed to fetch dietary properties'}), 500

# Featured Items API
@api_bp.route('/featured', methods=['GET'])
def get_featured_items():
    """Get featured menu items"""
    try:
        featured = MenuItem.query.filter(
            (MenuItem.is_signature == True) | 
            (MenuItem.is_popular == True) |
            (MenuItem.is_new == True)
        ).filter_by(is_available=True).limit(6).all()
        
        featured_data = []
        for item in featured:
            featured_data.append({
                'id': item.id,
                'name_he': item.name_he,
                'name_en': item.name_en,
                'description_he': item.short_description_he or item.description_he,
                'description_en': item.short_description_en or item.description_en,
                'price': item.base_price,
                'image_path': item.image_path,
                'is_signature': item.is_signature,
                'is_new': item.is_new,
                'is_popular': item.is_popular
            })
        
        return jsonify(featured_data)
    except Exception as e:
        logging.error(f"Error fetching featured items: {e}")
        return jsonify({'error': 'Failed to fetch featured items'}), 500

# Checklist Tasks API
@api_bp.route('/checklist-tasks', methods=['GET'])
def get_checklist_tasks():
    """Get all active checklist tasks"""
    try:
        tasks = ChecklistTask.query.filter_by(is_active=True).order_by(ChecklistTask.display_order).all()
        
        tasks_list = []
        for task in tasks:
            tasks_list.append({
                'id': task.id,
                'name': task.name,
                'description': task.description,
                'shift_type': task.shift_type,
                'category': task.category,
                'priority': task.priority,
                'frequency': task.frequency,
                'display_order': task.display_order
            })
        
        return jsonify(tasks_list)
    except Exception as e:
        logging.error(f"Error fetching checklist tasks: {e}")
        return jsonify({'error': 'Failed to fetch tasks'}), 500

@api_bp.route('/checklist-tasks', methods=['POST'])
def create_checklist_task():
    """Create a new checklist task"""
    try:
        data = request.json
        
        task = ChecklistTask(
            name=data.get('name'),
            description=data.get('description'),
            shift_type=data.get('shift_type'),
            category=data.get('category'),
            priority=data.get('priority', 'medium'),
            frequency=data.get('frequency', 'daily')
        )
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify({'success': True, 'id': task.id})
    except Exception as e:
        logging.error(f"Error creating checklist task: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create task'}), 500

@api_bp.route('/checklist-tasks/<int:task_id>', methods=['PUT'])
def update_checklist_task(task_id):
    """Update an existing checklist task"""
    try:
        task = ChecklistTask.query.get_or_404(task_id)
        data = request.json
        
        task.name = data.get('name', task.name)
        task.description = data.get('description', task.description)
        task.shift_type = data.get('shift_type', task.shift_type)
        task.category = data.get('category', task.category)
        task.priority = data.get('priority', task.priority)
        task.frequency = data.get('frequency', task.frequency)
        
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Error updating checklist task: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update task'}), 500

@api_bp.route('/checklist-tasks/<int:task_id>', methods=['DELETE'])
def delete_checklist_task(task_id):
    """Delete (soft delete) a checklist task"""
    try:
        task = ChecklistTask.query.get_or_404(task_id)
        task.is_active = False
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Error deleting checklist task: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete task'}), 500