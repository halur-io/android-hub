"""
Audit logging utilities for stock management system.
Provides centralized functions for recording all stock entity changes.
"""

from database import db
from models import AuditLog
from flask import request
from flask_login import current_user
from sqlalchemy import inspect
from datetime import datetime


def get_entity_changes(entity, action='update'):
    """
    Extract changes from a SQLAlchemy entity.
    
    Args:
        entity: SQLAlchemy model instance
        action: 'create', 'update', or 'delete'
    
    Returns:
        dict: Changes in format {field: {old: value, new: value}}
    """
    if action == 'create':
        # For creates, return all non-null values
        mapper = inspect(entity.__class__)
        new_values = {}
        for column in mapper.columns:
            value = getattr(entity, column.key, None)
            if value is not None and column.key not in ['id', 'created_at', 'updated_at']:
                # Convert datetime to ISO string for JSON compatibility
                if isinstance(value, datetime):
                    value = value.isoformat()
                new_values[column.key] = value
        return {'new_values': new_values}
    
    elif action == 'delete':
        # For deletes, capture current state
        mapper = inspect(entity.__class__)
        old_values = {}
        for column in mapper.columns:
            value = getattr(entity, column.key, None)
            if value is not None and column.key not in ['id']:
                if isinstance(value, datetime):
                    value = value.isoformat()
                old_values[column.key] = value
        return {'old_values': old_values}
    
    else:  # update
        # Get modified attributes
        state = inspect(entity)
        changes = {}
        
        for attr in state.attrs:
            hist = attr.load_history()
            if hist.has_changes() and attr.key not in ['updated_at', 'last_updated']:
                old_value = hist.deleted[0] if hist.deleted else None
                new_value = hist.added[0] if hist.added else None
                
                # Convert datetime to ISO string
                if isinstance(old_value, datetime):
                    old_value = old_value.isoformat()
                if isinstance(new_value, datetime):
                    new_value = new_value.isoformat()
                
                changes[attr.key] = {
                    'old': old_value,
                    'new': new_value
                }
        
        return changes if changes else None


def record_audit(entity_type, entity_id, action, changes=None, user_id=None, context=None):
    """
    Record an audit log entry.
    
    Args:
        entity_type: Type of entity (stock_item, supplier, stock_category, etc.)
        entity_id: ID of the entity
        action: Action performed (create, update, delete)
        changes: Dict of changes (optional, will be computed if None)
        user_id: User who performed the action (defaults to current_user)
        context: Additional context dict (source, ip_address, etc.)
    """
    try:
        # Get user ID
        if user_id is None and current_user and current_user.is_authenticated:
            user_id = current_user.id
        
        # Build context
        if context is None:
            context = {}
        
        # Add request context if available
        if request:
            context['source'] = 'web'
            context['ip_address'] = request.remote_addr
            context['user_agent'] = request.headers.get('User-Agent', '')[:200]
            context['method'] = request.method
            context['endpoint'] = request.endpoint
        
        # Create audit log entry
        audit_entry = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            performed_by=user_id,
            performed_at=datetime.utcnow(),
            changes=changes,
            context=context
        )
        
        db.session.add(audit_entry)
        db.session.commit()
        
        return audit_entry
    
    except Exception as e:
        # Log error but don't fail the main operation
        print(f"Audit logging error: {e}")
        db.session.rollback()
        return None


def record_entity_audit(entity, action, user_id=None, context=None):
    """
    Convenience function to record audit for a SQLAlchemy entity.
    Automatically extracts entity type, ID, and changes.
    
    Args:
        entity: SQLAlchemy model instance
        action: Action performed (create, update, delete)
        user_id: User who performed the action (defaults to current_user)
        context: Additional context dict
    """
    # Map model class names to entity types
    entity_type_map = {
        'StockItem': 'stock_item',
        'Supplier': 'supplier',
        'StockCategory': 'stock_category',
        'StockLevel': 'stock_level',
        'Receipt': 'receipt',
        'StockTransaction': 'stock_transaction',
        'ReceiptItem': 'receipt_item',
    }
    
    entity_class_name = entity.__class__.__name__
    entity_type = entity_type_map.get(entity_class_name, entity_class_name.lower())
    entity_id = entity.id
    
    # Get changes if action is update
    changes = None
    if action in ['create', 'update', 'delete']:
        changes = get_entity_changes(entity, action)
    
    return record_audit(entity_type, entity_id, action, changes, user_id, context)


def get_audit_history(entity_type, entity_id, page=1, per_page=20):
    """
    Get audit history for a specific entity.
    
    Args:
        entity_type: Type of entity
        entity_id: ID of the entity
        page: Page number (1-indexed)
        per_page: Items per page
    
    Returns:
        dict: Paginated audit history with metadata
    """
    query = AuditLog.query.filter_by(
        entity_type=entity_type,
        entity_id=entity_id
    ).order_by(AuditLog.performed_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Format audit entries
    entries = []
    for entry in pagination.items:
        entries.append({
            'id': entry.id,
            'action': entry.action,
            'action_display_he': entry.get_action_display('he'),
            'action_display_en': entry.get_action_display('en'),
            'performed_by': entry.performed_by,
            'user_name': entry.get_user_display_name() if entry.user else 'מערכת',
            'performed_at': entry.performed_at.isoformat(),
            'performed_at_display': entry.performed_at.strftime('%d/%m/%Y %H:%M'),
            'changes': entry.changes,
            'context': entry.context
        })
    
    return {
        'entries': entries,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page,
        'has_prev': pagination.has_prev,
        'has_next': pagination.has_next
    }
