from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, InputRequired


class SignupForm(FlaskForm):
    """User Signup Form."""
    first_name = StringField('',
                       validators=[DataRequired()])
    last_name = StringField('',
                       validators=[DataRequired()])
    email = StringField('',
                        validators=[Length(min=6),
                                    Email(message='Please enter a valid email, e.g. username@example.com'),
                                    DataRequired()])
    password = PasswordField('',
                             validators=[InputRequired(),
                                         Length(min=6, message='Password should have at least 6 characters'),
                                         Regexp('(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])', message='Select a password with at least a number, an upper-case letter, a lower-case letter, and a special character')])
    confirm = PasswordField('',
                            validators=[InputRequired(),
                                        EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """User Login Form."""
    email = StringField('Email',
                        validators=[Email(message='Enter a valid email.'),
                                    DataRequired()])
    password = PasswordField('Password',
                             validators=[InputRequired()])
    submit = SubmitField('Login')