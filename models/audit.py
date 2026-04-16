from database import db
from datetime import datetime

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(20), nullable=False)
    performed_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=True)
    performed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    changes = db.Column(db.JSON)
    context = db.Column(db.JSON)

    user = db.relationship('AdminUser', backref='audit_actions')

    __table_args__ = (
        db.Index('idx_audit_entity', 'entity_type', 'entity_id', 'performed_at'),
        db.Index('idx_audit_user', 'performed_by', 'performed_at'),
        db.Index('idx_audit_date', 'performed_at'),
    )

    def __repr__(self):
        return f'<AuditLog {self.action} {self.entity_type}:{self.entity_id} by User {self.performed_by}>'

    def get_user_display_name(self):
        if not self.user:
            return 'מערכת' if hasattr(self, '_is_rtl') else 'System'
        return self.user.username

    def get_action_display(self, lang='he'):
        actions_he = {'create': 'נוצר', 'update': 'עודכן', 'delete': 'נמחק'}
        actions_en = {'create': 'Created', 'update': 'Updated', 'delete': 'Deleted'}
        return actions_he.get(self.action, self.action) if lang == 'he' else actions_en.get(self.action, self.action)
