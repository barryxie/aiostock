from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length,Email
from wtforms import StringField, PasswordField, EmailField, IntegerField

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[ InputRequired(), Length(min=1,max=20)])
    password = PasswordField("Password", validators=[ InputRequired(), Length(min=6,max=55)])
    email = EmailField("Email", validators=[Email(),  InputRequired()])
    phone = IntegerField("Phone", validators=[ InputRequired()])
    first_name = StringField("First name")
    last_name = StringField("Last name")


class UpdatePasswordForm(FlaskForm):
    password = PasswordField("Current Password", validators=[ InputRequired(), Length(min=6,max=55)])
    new_password = PasswordField("New Password", validators=[ InputRequired(), Length(min=6,max=55)])
    confirm_password = PasswordField("Confirm Password", validators=[ InputRequired(), Length(min=6,max=55)])    
       

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[ InputRequired(), Length(min=1,max=20)])
    password = PasswordField("Password", validators=[ InputRequired(), Length(min=6,max=55)])

class addWatchlist(FlaskForm):
    symbol = StringField("symbol", validators=[InputRequired(), Length(min=1,max=20)])
