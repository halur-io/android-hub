from database import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

class ManagerPIN(db.Model):
    __tablename__ = 'manager_pins'
    id = db.Column(db.Integer, primary_key=True)
    pin_hash = db.Column(db.String(256), nullable=False)
    pin_plain = db.Column(db.String(10), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime)
    ops_permissions = db.Column(db.JSON, default=list)
    is_ops_superadmin = db.Column(db.Boolean, default=False)

    branch = db.relationship('Branch', foreign_keys=[branch_id])

    OPS_MODULES = ['home', 'orders', 'tables', 'menu', 'stock', 'deals', 'branches', 'shifts', 'delivery', 'employees', 'history']

    def set_pin(self, pin):
        self.pin_hash = generate_password_hash(pin)

    def check_pin(self, pin):
        return check_password_hash(self.pin_hash, pin)

    def has_ops_permission(self, module):
        if self.is_ops_superadmin:
            return True
        perms = self.ops_permissions or []
        if module in perms:
            return True
        if module == 'tables' and 'orders' in perms:
            return True
        return False

    def get_ops_modules(self):
        if self.is_ops_superadmin:
            return self.OPS_MODULES[:]
        perms = self.ops_permissions or []
        result = []
        for m in self.OPS_MODULES:
            if m in perms:
                result.append(m)
            elif m == 'tables' and 'orders' in perms:
                result.append(m)
        return result

    def __repr__(self):
        return f'<ManagerPIN {self.name}>'


class EnrolledDevice(db.Model):
    __tablename__ = 'enrolled_devices'
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(100), nullable=False)
    device_token = db.Column(db.String(128), unique=True, nullable=False)
    enrollment_code = db.Column(db.String(32), unique=True)
    pending_request_token = db.Column(db.String(64), unique=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    enrolled_at = db.Column(db.DateTime)
    enrolled_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    last_seen = db.Column(db.DateTime)
    user_agent = db.Column(db.String(500))
    last_pin_id = db.Column(db.Integer, db.ForeignKey('manager_pins.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    branch = db.relationship('Branch', backref='enrolled_devices')
    last_pin = db.relationship('ManagerPIN', backref='enrolled_devices')
    enrolled_by_user = db.relationship('AdminUser', backref='enrolled_devices')

    def __repr__(self):
        return f'<EnrolledDevice {self.device_name}>'


class TimeLog(db.Model):
    __tablename__ = 'time_logs'
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('manager_pins.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    clock_in = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    clock_out = db.Column(db.DateTime, nullable=True)
    source = db.Column(db.String(20), default='kds')

    worker = db.relationship('ManagerPIN', backref='time_logs', foreign_keys=[worker_id])
    branch = db.relationship('Branch', foreign_keys=[branch_id])

    @property
    def duration_seconds(self):
        end = self.clock_out or datetime.utcnow()
        return max(0, int((end - self.clock_in).total_seconds()))

    @property
    def duration_display(self):
        s = self.duration_seconds
        h, remainder = divmod(s, 3600)
        m, _ = divmod(remainder, 60)
        return f'{h}:{m:02d}'

    @property
    def is_open(self):
        return self.clock_out is None

    def close_shift(self):
        if self.clock_out is None:
            self.clock_out = datetime.utcnow()

    @staticmethod
    def get_auto_close_hours():
        import os
        try:
            return float(os.environ.get('SHIFT_AUTO_CLOSE_HOURS', '12'))
        except (ValueError, TypeError):
            return 12.0

    @staticmethod
    def auto_close_stale(threshold_hours=None):
        if threshold_hours is None:
            threshold_hours = TimeLog.get_auto_close_hours()
        cutoff = datetime.utcnow() - timedelta(hours=threshold_hours)
        stale = TimeLog.query.filter(
            TimeLog.clock_out.is_(None),
            TimeLog.clock_in < cutoff,
        ).all()
        for tl in stale:
            tl.clock_out = tl.clock_in + timedelta(hours=threshold_hours)
        return len(stale)

    def __repr__(self):
        return f'<TimeLog worker={self.worker_id} in={self.clock_in} out={self.clock_out}>'
