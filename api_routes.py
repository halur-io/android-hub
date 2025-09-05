from flask import Blueprint, jsonify, request
from models import (SiteSettings, Branch, WorkingHours, MenuCategory, 
                   MenuItem, MediaFile, DietaryProperty, ChecklistTask,
                   GeneratedChecklist, TaskTemplate, TaskGroup, db)
from datetime import datetime
import logging
import json

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
                'display_order': task.display_order,
                'group_id': task.group_id  # Fix: Include group_id to prevent duplicates
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
            frequency=data.get('frequency', 'daily'),
            group_id=data.get('group_id')  # Allow group assignment during creation
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
        
        # Handle group assignment - explicitly check for group_id field
        if 'group_id' in data:
            task.group_id = data.get('group_id')
        
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

# Task Templates API
@api_bp.route('/task-templates', methods=['GET'])
def get_task_templates():
    """Get all task templates"""
    try:
        templates = TaskTemplate.query.order_by(TaskTemplate.created_at.desc()).all()
        
        templates_list = []
        for template in templates:
            templates_list.append({
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'shift_type': template.shift_type,
                'branch_id': template.branch_id,
                'is_default': template.is_default,
                'tasks_config': template.tasks_config,
                'assigned_groups': template.assigned_groups or [],
                'created_at': template.created_at.isoformat() if template.created_at else None
            })
        
        return jsonify(templates_list)
    except Exception as e:
        logging.error(f"Error fetching task templates: {e}")
        return jsonify({'error': 'Failed to fetch templates'}), 500

@api_bp.route('/task-templates', methods=['POST'])
def create_task_template():
    """Create a new task template from current tasks"""
    try:
        data = request.json
        
        # Get current tasks for the shift type
        current_tasks = ChecklistTask.query.filter_by(
            shift_type=data.get('shift_type'), 
            is_active=True
        ).all()
        
        # Convert tasks to config format
        tasks_config = []
        for task in current_tasks:
            tasks_config.append({
                'name': task.name,
                'description': task.description,
                'category': task.category,
                'priority': task.priority,
                'frequency': task.frequency
            })
        
        template = TaskTemplate(
            name=data.get('name'),
            description=data.get('description'),
            shift_type=data.get('shift_type'),
            branch_id=data.get('branch_id'),
            is_default=data.get('is_default', False),
            tasks_config=tasks_config,
            assigned_groups=data.get('assigned_groups', [])
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({'success': True, 'id': template.id})
    except Exception as e:
        logging.error(f"Error creating task template: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create template'}), 500

@api_bp.route('/task-templates/<int:template_id>/load', methods=['POST'])
def load_task_template(template_id):
    """Load tasks from a template (creates new tasks)"""
    try:
        template = TaskTemplate.query.get_or_404(template_id)
        
        if not template.tasks_config:
            return jsonify({'error': 'Template has no tasks configured'}), 400
        
        # Delete existing tasks for this shift type (optional - based on user preference)
        if request.json.get('replace_existing', False):
            ChecklistTask.query.filter_by(
                shift_type=template.shift_type,
                is_active=True
            ).update({'is_active': False})
        
        # Create new tasks from template
        created_tasks = []
        for task_data in template.tasks_config:
            new_task = ChecklistTask(
                name=task_data.get('name'),
                description=task_data.get('description'),
                shift_type=template.shift_type,
                category=task_data.get('category'),
                priority=task_data.get('priority', 'medium'),
                frequency=task_data.get('frequency', 'daily')
            )
            db.session.add(new_task)
            created_tasks.append(new_task)
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'created_count': len(created_tasks),
            'template_name': template.name
        })
    except Exception as e:
        logging.error(f"Error loading task template: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to load template'}), 500

@api_bp.route('/task-templates/<int:template_id>', methods=['DELETE'])
def delete_task_template(template_id):
    """Delete a task template"""
    try:
        template = TaskTemplate.query.get_or_404(template_id)
        db.session.delete(template)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Error deleting task template: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete template'}), 500

# Generated Checklists API
@api_bp.route('/generated-checklists', methods=['POST'])
def create_generated_checklist():
    """Create and save a generated checklist"""
    try:
        data = request.json
        
        # Create new generated checklist
        checklist = GeneratedChecklist(
            name=data.get('name'),
            date=datetime.strptime(data.get('date'), '%Y-%m-%d').date(),
            shift_type=data.get('shift_type'),
            branch_id=data.get('branch_id'),
            manager_name=data.get('manager_name'),
            tasks_json=json.dumps(data.get('tasks_data', []))
        )
        
        db.session.add(checklist)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'id': checklist.id,
            'message': 'Checklist saved successfully'
        })
    except Exception as e:
        logging.error(f"Error creating generated checklist: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to save checklist'}), 500

@api_bp.route('/generated-checklists', methods=['GET'])
def get_generated_checklists():
    """Get all generated checklists"""
    try:
        checklists = GeneratedChecklist.query.order_by(GeneratedChecklist.created_at.desc()).all()
        
        checklists_list = []
        for checklist in checklists:
            checklists_list.append({
                'id': checklist.id,
                'name': checklist.name,
                'date': checklist.date.isoformat() if checklist.date else None,
                'shift_type': checklist.shift_type,
                'branch_id': checklist.branch_id,
                'branch_name': checklist.branch.name_he if checklist.branch else None,
                'manager_name': checklist.manager_name,
                'tasks_data': json.loads(checklist.tasks_json) if checklist.tasks_json else [],
                'created_at': checklist.created_at.isoformat() if checklist.created_at else None,
                'completed_at': checklist.completed_at.isoformat() if checklist.completed_at else None
            })
        
        return jsonify(checklists_list)
    except Exception as e:
        logging.error(f"Error fetching generated checklists: {e}")
        return jsonify({'error': 'Failed to fetch checklists'}), 500

@api_bp.route('/generated-checklists/<int:checklist_id>', methods=['GET'])
def get_generated_checklist(checklist_id):
    """Get a specific generated checklist"""
    try:
        checklist = GeneratedChecklist.query.get_or_404(checklist_id)
        
        return jsonify({
            'id': checklist.id,
            'name': checklist.name,
            'date': checklist.date.isoformat() if checklist.date else None,
            'shift_type': checklist.shift_type,
            'branch_id': checklist.branch_id,
            'branch_name': checklist.branch.name_he if checklist.branch else None,
            'manager_name': checklist.manager_name,
            'tasks_data': json.loads(checklist.tasks_json) if checklist.tasks_json else [],
            'created_at': checklist.created_at.isoformat() if checklist.created_at else None,
            'completed_at': checklist.completed_at.isoformat() if checklist.completed_at else None
        })
    except Exception as e:
        logging.error(f"Error fetching generated checklist: {e}")
        return jsonify({'error': 'Failed to fetch checklist'}), 500

@api_bp.route('/generated-checklists/<int:checklist_id>', methods=['DELETE'])
def delete_generated_checklist(checklist_id):
    """Delete a generated checklist"""
    try:
        checklist = GeneratedChecklist.query.get_or_404(checklist_id)
        db.session.delete(checklist)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Error deleting generated checklist: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete checklist'}), 500

# Task Groups API
@api_bp.route('/task-groups', methods=['GET'])
def get_task_groups():
    """Get all task groups with their tasks"""
    try:
        groups = TaskGroup.query.filter_by(is_active=True).order_by(TaskGroup.display_order, TaskGroup.name).all()
        
        groups_list = []
        for group in groups:
            group_tasks = [
                {
                    'id': task.id,
                    'name': task.name,
                    'description': task.description,
                    'shift_type': task.shift_type,
                    'category': task.category,
                    'priority': task.priority,
                    'frequency': task.frequency,
                    'group_id': task.group_id,  # Include group_id for consistency
                    'created_at': task.created_at.isoformat() if task.created_at else None
                }
                for task in group.tasks if task.is_active
            ]
            
            groups_list.append({
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'shift_type': group.shift_type,
                'category': group.category,
                'color': group.color,
                'task_count': len(group_tasks),
                'tasks': group_tasks,
                'created_at': group.created_at.isoformat() if group.created_at else None
            })
        
        return jsonify(groups_list)
    except Exception as e:
        logging.error(f"Error fetching task groups: {e}")
        return jsonify({'error': 'Failed to fetch groups'}), 500

@api_bp.route('/task-groups', methods=['POST'])
def create_task_group():
    """Create a new task group and optionally add tasks to it"""
    try:
        data = request.json
        
        # Create the group
        group = TaskGroup(
            name=data.get('name'),
            description=data.get('description'),
            shift_type=data.get('shift_type'),
            category=data.get('category'),
            color=data.get('color', '#007bff')
        )
        
        db.session.add(group)
        db.session.flush()  # To get the group ID
        
        # Add tasks to the group if provided
        tasks_data = data.get('tasks', [])
        created_tasks = []
        
        for task_data in tasks_data:
            task = ChecklistTask(
                name=task_data.get('name'),
                description=task_data.get('description', ''),
                shift_type=group.shift_type,
                category=group.category,
                priority=task_data.get('priority', 'medium'),
                frequency=task_data.get('frequency', 'daily'),
                group_id=group.id
            )
            db.session.add(task)
            created_tasks.append(task)
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'group_id': group.id,
            'tasks_created': len(created_tasks)
        })
    except Exception as e:
        logging.error(f"Error creating task group: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create group'}), 500

@api_bp.route('/task-groups/<int:group_id>', methods=['PUT'])
def update_task_group(group_id):
    """Update a task group"""
    try:
        group = TaskGroup.query.get_or_404(group_id)
        data = request.json
        
        if 'name' in data:
            group.name = data['name']
        if 'description' in data:
            group.description = data['description']
        if 'color' in data:
            group.color = data['color']
        if 'category' in data:
            group.category = data['category']
            
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Error updating task group: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update group'}), 500

@api_bp.route('/task-groups/<int:group_id>', methods=['DELETE'])
def delete_task_group(group_id):
    """Delete a task group and optionally its tasks"""
    try:
        group = TaskGroup.query.get_or_404(group_id)
        
        # Option to delete tasks with group or just remove group assignment
        delete_tasks = request.json.get('delete_tasks', False) if request.json else False
        
        if delete_tasks:
            # Delete all tasks in the group
            ChecklistTask.query.filter_by(group_id=group_id).update({'is_active': False})
        else:
            # Just remove group assignment from tasks
            ChecklistTask.query.filter_by(group_id=group_id).update({'group_id': None})
        
        db.session.delete(group)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Error deleting task group: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete group'}), 500