from database import db
from datetime import datetime

class Printer(db.Model):
    __tablename__ = 'printers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='CASCADE'), nullable=False)
    printer_type = db.Column(db.String(50), default='snbc-btp-r880npv')
    ip_address = db.Column(db.String(45), nullable=False)
    port = db.Column(db.Integer, default=9100)
    encoding = db.Column(db.String(30), default='iso-8859-8')
    codepage_num = db.Column(db.Integer, default=36)
    cut_feed_lines = db.Column(db.Integer, default=6)
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    checker_copies = db.Column(db.Integer, default=2)
    payment_copies = db.Column(db.Integer, default=1)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    branch = db.relationship('Branch', backref=db.backref('printers', lazy=True, cascade='all, delete-orphan'))
    stations = db.relationship('PrinterStation', backref='printer', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'printer_type': self.printer_type or 'escpos',
            'branch_id': self.branch_id,
            'ip_address': self.ip_address,
            'port': self.port,
            'encoding': self.encoding,
            'codepage_num': self.codepage_num,
            'cut_feed_lines': self.cut_feed_lines,
            'is_active': self.is_active,
            'display_order': self.display_order,
            'checker_copies': self.checker_copies,
            'payment_copies': self.payment_copies,
            'is_default': self.is_default,
            'stations': [s.station_name for s in self.stations],
        }

    def __repr__(self):
        return f'<Printer {self.name} @ {self.ip_address}>'


class PrintStation(db.Model):
    __tablename__ = 'print_stations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PrintStation {self.name}>'


class PrinterStation(db.Model):
    __tablename__ = 'printer_stations'
    __table_args__ = (
        db.UniqueConstraint('printer_id', 'station_name', name='uq_printer_station'),
    )
    id = db.Column(db.Integer, primary_key=True)
    printer_id = db.Column(db.Integer, db.ForeignKey('printers.id', ondelete='CASCADE'), nullable=False)
    station_name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<PrinterStation {self.station_name} -> Printer#{self.printer_id}>'


class PrintDevice(db.Model):
    __tablename__ = 'print_devices'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(128), unique=True, nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    device_name = db.Column(db.String(100), nullable=False)
    last_heartbeat = db.Column(db.DateTime, nullable=True)
    is_online = db.Column(db.Boolean, default=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    config_json = db.Column(db.Text, nullable=True)

    branch = db.relationship('Branch', backref=db.backref('print_devices', lazy=True))

    def to_dict(self):
        import json as _json
        config = {}
        if self.config_json:
            try:
                config = _json.loads(self.config_json)
            except Exception:
                pass
        return {
            'id': self.id,
            'device_id': self.device_id,
            'branch_id': self.branch_id,
            'device_name': self.device_name,
            'last_heartbeat': self.last_heartbeat.isoformat() + 'Z' if self.last_heartbeat else None,
            'is_online': self.is_online,
            'registered_at': self.registered_at.isoformat() + 'Z' if self.registered_at else None,
            'config': config,
        }

    def __repr__(self):
        return f'<PrintDevice {self.device_name} ({self.device_id})>'


class ApiKey(db.Model):
    __tablename__ = 'api_keys'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    branch = db.relationship('Branch', backref=db.backref('api_keys', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'name': self.name,
            'branch_id': self.branch_id,
            'branch_name': self.branch.name_he if self.branch else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'last_used_at': self.last_used_at.isoformat() + 'Z' if self.last_used_at else None,
            'created_by': self.created_by,
            'notes': self.notes,
        }

    def __repr__(self):
        return f'<ApiKey {self.name} ({"active" if self.is_active else "revoked"})>'


class PendingPrintJob(db.Model):
    __tablename__ = 'pending_print_jobs'
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    branch_id = db.Column(db.Integer, nullable=False, index=True)
    job_type = db.Column(db.String(30), nullable=False, default='check_print')
    payload_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    claimed_at = db.Column(db.DateTime, nullable=True)
    claimed_by = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        return f'<PendingPrintJob {self.job_id} branch={self.branch_id} type={self.job_type}>'


class PrintSyncLog(db.Model):
    __tablename__ = 'print_sync_log'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, nullable=True)
    job_id = db.Column(db.String(32), nullable=True)
    device_id = db.Column(db.String(128), nullable=True)
    branch_id = db.Column(db.Integer, nullable=True)
    action = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(30), nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
