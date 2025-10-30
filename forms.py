from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email ,EqualTo, ValidationError
from models import User  # For uniqueness checks

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=200)])
    excerpt = StringField('Excerpt', validators=[Length(max=300)])
    content = TextAreaField('Content', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired(), Length(max=100)])
    image_url = StringField('Image URL', validators=[Length(max=500)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    tags = StringField('Tags (comma-separated)')
    featured = BooleanField('Featured Post')
    published = BooleanField('Published', default=True)
    submit = SubmitField('Save Post')
# grok code

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=80),
        # FIXED: Lambda now takes (form, field)
        lambda form, field: ValidationError('Username already taken.') if User.query.filter_by(username=field.data).first() else None
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120),
        # FIXED: Lambda now takes (form, field)
        lambda form, field: ValidationError('Email already registered.') if User.query.filter_by(email=field.data).first() else None
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6),
        EqualTo('confirm_password', message='Passwords must match.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    is_admin = BooleanField('Admin User?', default=False)
    submit = SubmitField('Sign Up')