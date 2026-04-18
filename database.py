import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from werkzeug.middleware.proxy_fix import ProxyFix

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

def _run_safe_migrations(db):
    migrations = [
        ("food_orders", "coupon_code", "ALTER TABLE food_orders ADD COLUMN coupon_code VARCHAR(50)"),
        ("food_orders", "coupon_discount", "ALTER TABLE food_orders ADD COLUMN coupon_discount FLOAT DEFAULT 0"),
        ("food_orders", "payment_provider", "ALTER TABLE food_orders ADD COLUMN payment_provider VARCHAR(20)"),
        ("branches", "payment_provider", "ALTER TABLE branches ADD COLUMN payment_provider VARCHAR(20) DEFAULT 'hyp'"),
        ("branches", "hyp_terminal", "ALTER TABLE branches ADD COLUMN hyp_terminal VARCHAR(100)"),
        ("branches", "hyp_api_key", "ALTER TABLE branches ADD COLUMN hyp_api_key VARCHAR(255)"),
        ("branches", "hyp_passp", "ALTER TABLE branches ADD COLUMN hyp_passp VARCHAR(255)"),
        ("branches", "max_api_url", "ALTER TABLE branches ADD COLUMN max_api_url VARCHAR(500)"),
        ("branches", "max_api_key", "ALTER TABLE branches ADD COLUMN max_api_key VARCHAR(255)"),
        ("branches", "max_merchant_id", "ALTER TABLE branches ADD COLUMN max_merchant_id VARCHAR(100)"),
        ("manager_pins", "ops_permissions", "ALTER TABLE manager_pins ADD COLUMN ops_permissions JSON"),
        ("manager_pins", "is_ops_superadmin", "ALTER TABLE manager_pins ADD COLUMN is_ops_superadmin BOOLEAN DEFAULT FALSE"),
        ("branches", "enable_delivery", "ALTER TABLE branches ADD COLUMN enable_delivery BOOLEAN DEFAULT TRUE"),
        ("branches", "enable_pickup", "ALTER TABLE branches ADD COLUMN enable_pickup BOOLEAN DEFAULT TRUE"),
        ("enrolled_devices", "pending_request_token", "ALTER TABLE enrolled_devices ADD COLUMN pending_request_token VARCHAR(64) UNIQUE"),
        ("menu_items", "print_name", "ALTER TABLE menu_items ADD COLUMN print_name VARCHAR(100)"),
        ("menu_items", "image_hero_path", "ALTER TABLE menu_items ADD COLUMN image_hero_path VARCHAR(500)"),
        ("manager_pins", "branch_id", "ALTER TABLE manager_pins ADD COLUMN branch_id INTEGER REFERENCES branches(id)"),
        ("branch_menu_items", "print_station", "ALTER TABLE branch_menu_items ADD COLUMN print_station VARCHAR(50)"),
        ("deals", "deal_type", "ALTER TABLE deals ADD COLUMN deal_type VARCHAR(20) DEFAULT 'fixed'"),
        ("deals", "source_category_id", "ALTER TABLE deals ADD COLUMN source_category_id INTEGER"),
        ("deals", "pick_count", "ALTER TABLE deals ADD COLUMN pick_count INTEGER DEFAULT 0"),
        ("deals", "source_category_ids", "ALTER TABLE deals ADD COLUMN source_category_ids JSON DEFAULT '[]'"),
        ("global_option_group_links", "linked_option_group_id", "ALTER TABLE global_option_group_links ADD COLUMN linked_option_group_id INTEGER REFERENCES menu_item_option_groups(id) ON DELETE SET NULL"),
        ("food_orders", "bon_acked_at", "ALTER TABLE food_orders ADD COLUMN bon_acked_at TIMESTAMP"),
        ("food_orders", "bon_acked_device_id", "ALTER TABLE food_orders ADD COLUMN bon_acked_device_id VARCHAR(128)"),
        ("food_orders", "bon_print_error", "ALTER TABLE food_orders ADD COLUMN bon_print_error TEXT"),
        ("food_orders", "bon_print_attempts", "ALTER TABLE food_orders ADD COLUMN bon_print_attempts INTEGER DEFAULT 0"),
        ("food_orders", "bon_print_options", "ALTER TABLE food_orders ADD COLUMN bon_print_options TEXT"),
        ("food_orders", "source", "ALTER TABLE food_orders ADD COLUMN source VARCHAR(20) DEFAULT 'online'"),
        ("food_orders", "created_by_name", "ALTER TABLE food_orders ADD COLUMN created_by_name VARCHAR(120)"),
        ("branches", "ordering_status", "ALTER TABLE branches ADD COLUMN ordering_status VARCHAR(20) NOT NULL DEFAULT 'open'"),
        ("payment_configuration", "test_mode", "ALTER TABLE payment_configuration ADD COLUMN test_mode BOOLEAN DEFAULT TRUE"),
        ("payment_configuration", "webhook_url", "ALTER TABLE payment_configuration ADD COLUMN webhook_url VARCHAR(500)"),
        ("payment_configuration", "webhook_secret", "ALTER TABLE payment_configuration ADD COLUMN webhook_secret VARCHAR(500)"),
        ("food_orders", "table_number", "ALTER TABLE food_orders ADD COLUMN table_number VARCHAR(20)"),
        ("food_orders", "dine_in_session_id", "ALTER TABLE food_orders ADD COLUMN dine_in_session_id INTEGER REFERENCES dine_in_sessions(id)"),
        ("dine_in_sessions", "payment_callback_token", "ALTER TABLE dine_in_sessions ADD COLUMN payment_callback_token VARCHAR(64)"),
        ("dine_in_tables", "area", "ALTER TABLE dine_in_tables ADD COLUMN area VARCHAR(50) DEFAULT ''"),
        ("food_orders", "void_log", "ALTER TABLE food_orders ADD COLUMN void_log TEXT"),
        ("dine_in_sessions", "pending_void_approvals", "ALTER TABLE dine_in_sessions ADD COLUMN pending_void_approvals TEXT"),
        ("dine_in_tables", "pos_x", "ALTER TABLE dine_in_tables ADD COLUMN pos_x FLOAT"),
        ("dine_in_tables", "pos_y", "ALTER TABLE dine_in_tables ADD COLUMN pos_y FLOAT"),
        ("dine_in_tables", "width", "ALTER TABLE dine_in_tables ADD COLUMN width FLOAT DEFAULT 100"),
        ("dine_in_tables", "height", "ALTER TABLE dine_in_tables ADD COLUMN height FLOAT DEFAULT 80"),
        ("dine_in_tables", "shape", "ALTER TABLE dine_in_tables ADD COLUMN shape VARCHAR(10) DEFAULT 'rect'"),
        ("dine_in_sessions", "tip_amount", "ALTER TABLE dine_in_sessions ADD COLUMN tip_amount FLOAT DEFAULT 0"),
        ("dine_in_sessions", "cash_received", "ALTER TABLE dine_in_sessions ADD COLUMN cash_received FLOAT"),
        ("dine_in_sessions", "cancel_reason", "ALTER TABLE dine_in_sessions ADD COLUMN cancel_reason VARCHAR(100)"),
        ("dine_in_sessions", "cancel_note", "ALTER TABLE dine_in_sessions ADD COLUMN cancel_note TEXT"),
        ("dine_in_sessions", "split_config", "ALTER TABLE dine_in_sessions ADD COLUMN split_config TEXT"),
        ("food_orders", "payment_url", "ALTER TABLE food_orders ADD COLUMN payment_url VARCHAR(500)"),
        ("food_orders", "payment_callback_token", "ALTER TABLE food_orders ADD COLUMN payment_callback_token VARCHAR(64)"),
        ("food_orders", "display_number", "ALTER TABLE food_orders ADD COLUMN display_number VARCHAR(20)"),
        ("food_orders", "operating_day_id", "ALTER TABLE food_orders ADD COLUMN operating_day_id INTEGER"),
    ]
    for table, column, sql in migrations:
        try:
            result = db.session.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name=:t AND column_name=:c"
            ), {"t": table, "c": column})
            if result.fetchone() is None:
                db.session.execute(text(sql))
                db.session.commit()
                logging.info(f"Migration: added {column} to {table}")
        except Exception as e:
            db.session.rollback()
            logging.warning(f"Migration skipped for {table}.{column}: {e}")

    try:
        result = db.session.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_name='dine_in_payment_splits'"
        ))
        if result.fetchone() is None:
            db.session.execute(text("""
                CREATE TABLE dine_in_payment_splits (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL REFERENCES dine_in_sessions(id),
                    portion_index INTEGER NOT NULL,
                    amount FLOAT NOT NULL,
                    payment_method VARCHAR(20),
                    payment_status VARCHAR(20) DEFAULT 'pending',
                    payer_label VARCHAR(100),
                    tip_amount FLOAT DEFAULT 0,
                    cash_received FLOAT,
                    paid_at TIMESTAMP,
                    payment_callback_token VARCHAR(64)
                )
            """))
            db.session.commit()
            logging.info("Migration: created dine_in_payment_splits table")
    except Exception as e:
        db.session.rollback()
        logging.warning(f"Migration skipped for dine_in_payment_splits: {e}")

    try:
        result = db.session.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name='dine_in_payment_splits' AND column_name='payment_callback_token'"
        ))
        if result.fetchone() is None:
            db.session.execute(text("ALTER TABLE dine_in_payment_splits ADD COLUMN payment_callback_token VARCHAR(64)"))
            db.session.commit()
            logging.info("Migration: added payment_callback_token to dine_in_payment_splits")
    except Exception as e:
        db.session.rollback()
        logging.warning(f"Migration skipped for dine_in_payment_splits.payment_callback_token: {e}")

    try:
        result = db.session.execute(text(
            "UPDATE printers SET codepage_num = 36 WHERE id = 2 AND codepage_num = 15"
        ))
        if result.rowcount:
            db.session.commit()
            logging.info("Migration: updated SNBC printer (id=2) codepage_num from 15 to 36")
    except Exception as e:
        db.session.rollback()
        logging.warning(f"Migration skipped for printers.codepage_num fix: {e}")

    try:
        from models import PrintStation, PrinterStation, MenuItem
        existing_names = set(r[0] for r in db.session.query(PrintStation.name).all())
        legacy_names = set()
        for (name,) in db.session.query(PrinterStation.station_name).distinct().all():
            if name and name not in existing_names:
                legacy_names.add(name)
        for (name,) in db.session.query(MenuItem.print_station).filter(MenuItem.print_station.isnot(None), MenuItem.print_station != '').distinct().all():
            if name and name not in existing_names:
                legacy_names.add(name)
        for name in legacy_names:
            db.session.add(PrintStation(name=name, display_name=name))
            logging.info(f"Backfill: created PrintStation '{name}' from legacy data")
        if legacy_names:
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.warning(f"PrintStation backfill skipped: {e}")

def init_db(app):
    """Initialize database with the Flask app"""
    # Configure database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    
    with app.app_context():
        # Import models to create tables
        import models
        
        # Import microservices models
        from services.config.config_service import SystemConfig, BranchConfig
        from services.auth.auth_service import Customer, CustomerAddress, PhoneVerification
        from services.order.order_service import Order, OrderItem, DeliveryZone
        from services.delivery.delivery_service import Driver, DeliveryAssignment, DriverShift
        from services.kitchen.kitchen_service import KitchenStation, KitchenQueue, PrinterConfig
        from services.payment.payment_service import PaymentTransaction, PaymentConfig
        
        db.create_all()

        _run_safe_migrations(db)

def create_default_roles_and_permissions():
    """Create default roles and permissions for the system"""
    from models import Role, Permission
    
    # Define default permissions by category
    permissions_data = [
        # User Management
        ('users.view', 'View Users', 'users', 'View user list and details'),
        ('users.create', 'Create Users', 'users', 'Create new users'),
        ('users.edit', 'Edit Users', 'users', 'Edit user information'),
        ('users.delete', 'Delete Users', 'users', 'Delete users from system'),
        
        # Role Management
        ('roles.view', 'View Roles', 'roles', 'View roles and permissions'),
        ('roles.create', 'Create Roles', 'roles', 'Create new roles'),
        ('roles.edit', 'Edit Roles', 'roles', 'Edit role permissions'),
        ('roles.delete', 'Delete Roles', 'roles', 'Delete roles'),
        
        # Orders
        ('orders.view', 'View Orders', 'orders', 'View order list and details'),
        ('orders.create', 'Create Orders', 'orders', 'Create new orders'),
        ('orders.edit', 'Edit Orders', 'orders', 'Modify order status and details'),
        ('orders.delete', 'Delete Orders', 'orders', 'Cancel/delete orders'),
        
        # Kitchen Management
        ('kitchen.view', 'View Kitchen', 'kitchen', 'Access kitchen display system'),
        ('kitchen.manage', 'Manage Kitchen', 'kitchen', 'Update order status in kitchen'),
        
        # Delivery Management
        ('delivery.view', 'View Deliveries', 'delivery', 'View delivery assignments'),
        ('delivery.manage', 'Manage Deliveries', 'delivery', 'Assign drivers and manage deliveries'),
        
        # Payment Management
        ('payments.view', 'View Payments', 'payments', 'View payment transactions'),
        ('payments.manage', 'Manage Payments', 'payments', 'Process refunds and manage payments'),
        
        # Menu Management
        ('menu.view', 'View Menu', 'menu', 'View menu items and categories'),
        ('menu.edit', 'Edit Menu', 'menu', 'Edit menu items and categories'),
        
        # Settings
        ('settings.view', 'View Settings', 'settings', 'View system settings'),
        ('settings.edit', 'Edit Settings', 'settings', 'Modify system settings'),
        
        # Branches
        ('branches.view', 'View Branches', 'branches', 'View branch information'),
        ('branches.edit', 'Edit Branches', 'branches', 'Edit branch settings'),
        
        # Checklists
        ('checklists.view', 'View Checklists', 'checklists', 'View task checklists'),
        ('checklists.edit', 'Edit Checklists', 'checklists', 'Manage task checklists'),
        
        # Stock Management
        ('stock.view', 'View Stock', 'stock', 'View stock levels and items'),
        ('stock.manage', 'Manage Stock', 'stock', 'Add/edit stock items and levels'),
        ('stock.transactions', 'Stock Transactions', 'stock', 'Record stock transactions'),
        ('stock.alerts', 'Stock Alerts', 'stock', 'Manage stock alerts and notifications'),
        ('stock.shopping_lists', 'Shopping Lists', 'stock', 'Create and manage shopping lists'),
        ('stock.suppliers', 'Manage Suppliers', 'stock', 'Manage supplier information'),
        ('stock.settings', 'Stock Settings', 'stock', 'Configure stock management settings'),
        ('stock.analytics', 'Stock Analytics', 'stock', 'View stock reports and analytics'),
        
        # Reports
        ('reports.view', 'View Reports', 'reports', 'View system reports'),
        
        # System Administration
        ('system.admin', 'System Administration', 'system', 'Full system administration access'),
    ]
    
    # Create permissions
    for perm_name, display_name, category, description in permissions_data:
        try:
            existing = Permission.query.filter_by(name=perm_name).first()
            if not existing:
                permission = Permission(
                    name=perm_name,
                    display_name=display_name,
                    category=category,
                    description=description
                )
                db.session.add(permission)
        except Exception as e:
            print(f"Error checking permission {perm_name}: {e}")
            permission = Permission(
                name=perm_name,
                display_name=display_name,
                category=category,
                description=description
            )
            db.session.add(permission)
    
    # Define default roles
    roles_data = [
        ('superadmin', 'Super Administrator', 'Full system access with all permissions', True),
        ('admin', 'Administrator', 'Full administrative access to most features', True),
        ('manager', 'Manager', 'Management access to operations and reports', False),
        ('kitchen', 'Kitchen Staff', 'Kitchen operations and order management', False),
        ('delivery', 'Delivery Manager', 'Delivery and driver management', False),
        ('cashier', 'Cashier', 'Order taking and payment processing', False),
        ('viewer', 'Viewer', 'Read-only access to reports and data', False),
    ]
    
    # Create roles
    for role_name, display_name, description, is_system in roles_data:
        try:
            existing = Role.query.filter_by(name=role_name).first()
            if not existing:
                role = Role(
                    name=role_name,
                    display_name=display_name,
                    description=description,
                    is_system_role=is_system
                )
                db.session.add(role)
        except Exception as e:
            print(f"Error checking role {role_name}: {e}")
            role = Role(
                name=role_name,
                display_name=display_name,
                description=description,
                is_system_role=is_system
            )
            db.session.add(role)
    
    db.session.commit()
    
    # Assign permissions to roles
    superadmin_role = Role.query.filter_by(name='superadmin').first()
    admin_role = Role.query.filter_by(name='admin').first()
    manager_role = Role.query.filter_by(name='manager').first()
    kitchen_role = Role.query.filter_by(name='kitchen').first()
    delivery_role = Role.query.filter_by(name='delivery').first()
    cashier_role = Role.query.filter_by(name='cashier').first()
    viewer_role = Role.query.filter_by(name='viewer').first()
    
    # Superadmin gets all permissions
    if superadmin_role:
        superadmin_role.permissions = Permission.query.all()
    
    # Admin gets most permissions except system admin
    if admin_role:
        admin_perms = Permission.query.filter(Permission.name != 'system.admin').all()
        admin_role.permissions = admin_perms
    
    # Manager gets operational permissions including stock management
    if manager_role:
        manager_perms = Permission.query.filter(Permission.category.in_([
            'orders', 'kitchen', 'delivery', 'menu', 'branches', 'checklists', 'reports', 'stock'
        ])).all()
        manager_role.permissions = manager_perms
    
    # Kitchen staff gets kitchen permissions and basic stock viewing
    if kitchen_role:
        kitchen_perms = Permission.query.filter(Permission.category.in_(['kitchen', 'orders'])).all()
        # Add stock viewing permissions for kitchen staff
        stock_view_perms = Permission.query.filter(Permission.name.in_([
            'stock.view', 'stock.transactions'
        ])).all()
        kitchen_role.permissions = kitchen_perms + stock_view_perms
    
    # Delivery gets delivery permissions
    if delivery_role:
        delivery_perms = Permission.query.filter(Permission.category.in_(['delivery', 'orders'])).all()
        delivery_role.permissions = delivery_perms
    
    # Cashier gets order and payment permissions
    if cashier_role:
        cashier_perms = Permission.query.filter(Permission.category.in_(['orders', 'payments'])).all()
        cashier_role.permissions = cashier_perms
    
    # Viewer gets view-only permissions
    if viewer_role:
        viewer_perms = Permission.query.filter(Permission.name.like('%.view')).all()
        viewer_role.permissions = viewer_perms
    
    db.session.commit()
    print("Created default roles and permissions")

def init_default_data():
    """Initialize default data - called lazily after app startup"""
    with db.engine.begin() as conn:
        from models import AdminUser, SiteSettings, Role, Permission
        
        # Initialize default roles and permissions
        try:
            create_default_roles_and_permissions()
        except Exception as e:
            print(f"Error creating default roles/permissions: {e}")
        
        # Create default admin user if not exists
        try:
            admin = AdminUser.query.filter_by(username='khalilshiban').first()
            if not admin:
                admin = AdminUser(
                    username='khalilshiban',
                    email='khalil@sumo.com',
                    is_superadmin=True,
                    is_active=True
                )
                admin.set_password('Winston35!')
                db.session.add(admin)
                db.session.commit()
                print("Created superadmin user: khalilshiban")
        except Exception as e:
            print(f"Error creating admin user: {e}")
        
        # Create default site settings if not exists
        try:
            settings = SiteSettings.query.first()
            if not settings:
                settings = SiteSettings()
                db.session.add(settings)
                db.session.commit()
                print("Created default site settings")
        except Exception as e:
            print(f"Error creating default site settings: {e}")

@login_manager.user_loader
def load_user(user_id):
    from models import AdminUser
    return AdminUser.query.get(int(user_id))