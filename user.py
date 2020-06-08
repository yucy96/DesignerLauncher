from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField, RadioField, TextAreaField
from wtforms.validators import EqualTo, Length, Regexp, InputRequired, Optional


gender_mapping = [(0, 'Female'), (1, 'Male'), (2, 'Other')]
identification_mapping = [(0, 'Student'), (1, 'Fashion Lover'), (2, 'Professional Designer'), (3, 'New Designer'), (4, 'Buyer'), (5, 'Other')]

class ChangeSettingForm(FlaskForm):
    """Setting change Form."""
    old_password = PasswordField('',
                             validators=[InputRequired()])
    new_password = PasswordField('',
                             validators=[InputRequired(),
                                         Length(min=6, message='Password should have at least 6 characters'),
                                         Regexp('(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])', message='Select a password with at least a number, an upper-case letter, a lower-case letter, and a special character')])
    confirm = PasswordField('',
                            validators=[InputRequired(),
                                        EqualTo('new_password', message='Passwords must match.')])
    submit = SubmitField('Submit')


class ProfileForm(FlaskForm):
    """User Signup Form."""
    first_name = StringField('',
                       validators=[InputRequired()])
    last_name = StringField('',
                       validators=[InputRequired()])
    birthday = StringField('')
    gender = SelectField('', coerce=int, choices=gender_mapping)
    company = StringField('')
    position = StringField('')
    identification = RadioField('', coerce=int, choices=identification_mapping)
    description = TextAreaField('')
    submit = SubmitField('Save Info')


