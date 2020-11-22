from wtforms import SubmitField, BooleanField, StringField, PasswordField, validators
from flask_wtf import Form

class RegForm(Form):
    name_first = StringField('First Name', [validators.DataRequired()])
    name_last = StringField('Last Name', [validators.DataRequired()])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Submit')