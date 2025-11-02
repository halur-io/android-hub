from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, DateField, TimeField, BooleanField
from wtforms.validators import DataRequired, Email, Length, NumberRange

class ContactForm(FlaskForm):
    name = StringField('שם מלא', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('אימייל', validators=[DataRequired(), Email()])
    phone = StringField('טלפון', validators=[DataRequired(), Length(min=9, max=15)])
    message = TextAreaField('הודעה', validators=[DataRequired(), Length(min=10, max=500)])

class ReservationForm(FlaskForm):
    name = StringField('שם מלא', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('אימייל', validators=[DataRequired(), Email()])
    phone = StringField('טלפון', validators=[DataRequired(), Length(min=9, max=15)])
    date = DateField('תאריך', validators=[DataRequired()])
    time = TimeField('שעה', validators=[DataRequired()])
    guests = SelectField('מספר סועדים', 
                        choices=[('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8+')],
                        validators=[DataRequired()])
    special_requests = TextAreaField('בקשות מיוחדות', validators=[Length(max=300)])

class NewsletterForm(FlaskForm):
    email = StringField('אימייל', validators=[DataRequired(), Email()])
    name = StringField('שם', validators=[Length(max=100)])
    accept_terms = BooleanField('אני מסכים לתנאי השימוש', validators=[DataRequired()])
