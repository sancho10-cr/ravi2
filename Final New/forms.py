from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField
from wtforms.validators import DataRequired,Email,EqualTo,Length


class Signup(FlaskForm):
    name=StringField(
        label="Enter Name",
        validators=[DataRequired()],
        render_kw={'placeholder':'Full name'})
    email=StringField(
        label="Enter Email",
        validators=[DataRequired(),Email(message="Enter correct email")],
        render_kw={'placeholder':'E-mail'})
    password=PasswordField(
        label="Enter Password",
        validators=[DataRequired(),Length(min=6,message='Password must be 6 characters long')],
        render_kw={'placeholder':'Password'})
    confirm_password=PasswordField(
        label="Confirm Password",
        validators=[EqualTo('password',message='Password and confirm password must be same')],
        render_kw={'placeholder':'Confirm Password'})
    submit=SubmitField(label="Sign up")


class Signin(FlaskForm):
    email=StringField(
        'Email',
        validators=[DataRequired(),Email(message="Enter correct email")],
        render_kw={'placeholder':'E-mail','style':'width:300px;'})
    password=PasswordField(
        'Password',
        validators=[DataRequired()],
        render_kw={'placeholder':'Password'})
    # remember_me=BooleanField('Remember Me')
    submit=SubmitField('Sign in',
        render_kw={'style':'background-color:black'})