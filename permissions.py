"""
Permission decorators and utilities for role-based access control.
This module provides decorators to protect routes based on user permissions.
"""
from functools import wraps
from flask import abort, flash, redirect, url_for, request
from flask_login import current_user


def require_permission(permission_name, message=None):
    """
    Decorator to require a specific permission to access a route.
    
    Args:
        permission_name (str): Name of the required permission (e.g., 'users.create')
        message (str): Custom error message to show if permission denied
    
    Returns:
        decorator: Permission checking decorator
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('אנא התחבר למערכת', 'error')
                return redirect(url_for('admin.login'))
            
            if not current_user.has_permission(permission_name):
                if message:
                    flash(message, 'error')
                else:
                    flash(f'אין לך הרשאה לבצע פעולה זו', 'error')
                
                # Redirect to dashboard or return 403
                if request.is_json:
                    abort(403)
                else:
                    return redirect(url_for('admin.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_role(role_name, message=None):
    """
    Decorator to require a specific role to access a route.
    
    Args:
        role_name (str): Name of the required role (e.g., 'admin')
        message (str): Custom error message to show if role not found
    
    Returns:
        decorator: Role checking decorator
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('אנא התחבר למערכת', 'error')
                return redirect(url_for('admin.login'))
            
            if not current_user.has_role(role_name) and not current_user.is_superadmin:
                if message:
                    flash(message, 'error')
                else:
                    flash(f'אין לך הרשאת {role_name} לביצוע פעולה זו', 'error')
                
                if request.is_json:
                    abort(403)
                else:
                    return redirect(url_for('admin.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_any_permission(*permission_names, message=None):
    """
    Decorator to require at least one of the specified permissions.
    
    Args:
        *permission_names: Variable number of permission names
        message (str): Custom error message to show if no permissions found
    
    Returns:
        decorator: Permission checking decorator
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('אנא התחבר למערכת', 'error')
                return redirect(url_for('admin.login'))
            
            # Check if user has any of the required permissions
            has_permission = any(current_user.has_permission(perm) for perm in permission_names)
            
            if not has_permission:
                if message:
                    flash(message, 'error')
                else:
                    flash('אין לך הרשאה מתאימה לבצע פעולה זו', 'error')
                
                if request.is_json:
                    abort(403)
                else:
                    return redirect(url_for('admin.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_all_permissions(*permission_names, message=None):
    """
    Decorator to require all of the specified permissions.
    
    Args:
        *permission_names: Variable number of permission names
        message (str): Custom error message to show if missing permissions
    
    Returns:
        decorator: Permission checking decorator
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('אנא התחבר למערכת', 'error')
                return redirect(url_for('admin.login'))
            
            # Check if user has all required permissions
            missing_perms = [perm for perm in permission_names if not current_user.has_permission(perm)]
            
            if missing_perms:
                if message:
                    flash(message, 'error')
                else:
                    flash(f'חסרות לך הרשאות: {", ".join(missing_perms)}', 'error')
                
                if request.is_json:
                    abort(403)
                else:
                    return redirect(url_for('admin.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def superadmin_required(message=None):
    """
    Decorator to require superadmin privileges.
    
    Args:
        message (str): Custom error message
    
    Returns:
        decorator: Superadmin checking decorator
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('אנא התחבר למערכת', 'error')
                return redirect(url_for('admin.login'))
            
            if not current_user.is_superadmin:
                if message:
                    flash(message, 'error')
                else:
                    flash('פעולה זו מותרת למנהל מערכת בלבד', 'error')
                
                if request.is_json:
                    abort(403)
                else:
                    return redirect(url_for('admin.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Utility functions for templates and views
def has_permission(permission_name):
    """
    Template utility function to check if current user has a permission.
    
    Args:
        permission_name (str): Permission to check
    
    Returns:
        bool: True if user has permission
    """
    if not current_user.is_authenticated:
        return False
    return current_user.has_permission(permission_name)


def has_role(role_name):
    """
    Template utility function to check if current user has a role.
    
    Args:
        role_name (str): Role to check
    
    Returns:
        bool: True if user has role
    """
    if not current_user.is_authenticated:
        return False
    return current_user.has_role(role_name)


def has_any_permission(*permission_names):
    """
    Template utility function to check if current user has any of the permissions.
    
    Args:
        *permission_names: Variable number of permission names
    
    Returns:
        bool: True if user has any permission
    """
    if not current_user.is_authenticated:
        return False
    return any(current_user.has_permission(perm) for perm in permission_names)


def get_user_permissions():
    """
    Get all permissions for the current user.
    
    Returns:
        list: List of permission objects
    """
    if not current_user.is_authenticated:
        return []
    return current_user.get_permissions()


def is_superadmin():
    """
    Check if current user is superadmin.
    
    Returns:
        bool: True if user is superadmin
    """
    if not current_user.is_authenticated:
        return False
    return current_user.is_superadmin