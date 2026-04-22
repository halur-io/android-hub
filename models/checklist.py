from database import db
from datetime import datetime

class TaskGroup(db.Model):
    __tablename__ = 'task_groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    shift_type = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20), default='#007bff')
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<TaskGroup {self.name}>'

class ChecklistTask(db.Model):
    __tablename__ = 'checklist_tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    shift_type = db.Column(db.String(50))
    category = db.Column(db.String(50))
    priority = db.Column(db.String(20), default='medium')
    frequency = db.Column(db.String(20), default='daily')
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    group_id = db.Column(db.Integer, db.ForeignKey('task_groups.id'), nullable=True)
    group = db.relationship('TaskGroup', backref='tasks')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GeneratedChecklist(db.Model):
    __tablename__ = 'generated_checklists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    shift_type = db.Column(db.String(50))
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    manager_name = db.Column(db.String(100))
    tasks_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    branch = db.relationship('Branch', backref='checklists')

class TaskTemplate(db.Model):
    __tablename__ = 'task_templates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text)
    shift_type = db.Column(db.String(50), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    tasks_config = db.Column(db.JSON)
    assigned_groups = db.Column(db.JSON)
    branch = db.relationship('Branch', backref='templates')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<TaskTemplate {self.name}>'

class PrintTemplate(db.Model):
    __tablename__ = 'print_templates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    shift_type = db.Column(db.String(50), nullable=True)
    is_default = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    config = db.Column(db.JSON, nullable=False, default=lambda: {
        'page': {
            'size': 'A4',
            'margins': {'top': 10, 'right': 10, 'bottom': 10, 'left': 10},
            'rtl': True,
            'rowHeight': 'auto',
            'gridlines': True,
            'headerRepeat': True,
            'fontFamily': 'Arial Hebrew, Arial',
            'fontSize': 12
        },
        'layout': 'table',
        'columns': [
            {
                'id': 'checkbox',
                'key': 'checkbox',
                'label': '',
                'type': 'checkbox',
                'width': {'value': 20, 'unit': 'px'},
                'align': 'center',
                'order': 0,
                'visible': True
            },
            {
                'id': 'taskname',
                'key': 'taskname',
                'label': 'משימה',
                'type': 'text',
                'dataPath': 'name',
                'width': {'value': 'auto', 'unit': 'auto'},
                'align': 'right',
                'order': 1,
                'visible': True
            }
        ]
    })
    branch = db.relationship('Branch', backref='print_templates')
    creator = db.relationship('AdminUser', backref='created_print_templates')

class MenuTemplate(db.Model):
    __tablename__ = 'menu_templates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True)
    categories_config = db.Column(db.JSON)
    items_config = db.Column(db.JSON)
    layout_config = db.Column(db.JSON)
    print_config = db.Column(db.JSON)
    style_config = db.Column(db.JSON)
    page_config = db.Column(db.JSON)
    icon_config = db.Column(db.JSON)
    branch = db.relationship('Branch', backref='menu_templates')
    creator = db.relationship('AdminUser', backref='created_menu_templates')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<MenuTemplate {self.name}>'

class GeneratedMenu(db.Model):
    __tablename__ = 'generated_menus'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('menu_templates.id'), nullable=True)
    date_created = db.Column(db.Date, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True)
    menu_content = db.Column(db.JSON)
    print_settings = db.Column(db.JSON)
    style_settings = db.Column(db.JSON)
    page_settings = db.Column(db.JSON)
    icon_settings = db.Column(db.JSON)
    branch = db.relationship('Branch', backref='generated_menus')
    template = db.relationship('MenuTemplate', backref='generated_menus')
    creator = db.relationship('AdminUser', backref='created_menus')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    printed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<GeneratedMenu {self.name}>'

class MenuPrintConfiguration(db.Model):
    __tablename__ = 'menu_print_configurations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    is_default = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True)
    config = db.Column(db.JSON, nullable=False, default=lambda: {
        'page': {
            'size': 'A4',
            'orientation': 'portrait',
            'margins': {'top': 15, 'right': 0, 'bottom': 15, 'left': 15},
            'rtl': True,
            'fontFamily': 'Heebo, Arial Hebrew, Arial',
            'fontSize': 12,
            'lineHeight': 1.4
        },
        'header': {
            'show_branch_name': True,
            'show_date': True,
            'show_page_numbers': True,
            'custom_text': '',
            'logo_enabled': False
        },
        'categories': {
            'show_category_titles': True,
            'category_font_size': 16,
            'category_style': 'bold',
            'spacing_after': 10
        },
        'items': {
            'show_descriptions': True,
            'show_prices': True,
            'price_alignment': 'left',
            'description_max_length': 100,
            'item_spacing': 8
        },
        'layout': {
            'columns': 1,
            'column_gap': 20,
            'section_spacing': 25,
            'border_style': 'none'
        }
    })
    branch = db.relationship('Branch', backref='menu_print_configs')
    creator = db.relationship('AdminUser', backref='created_menu_print_configs')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<MenuPrintConfiguration {self.name}>'
