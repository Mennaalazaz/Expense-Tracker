from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField , DateField, SelectField,FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
        
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(),Length(min=6)])
    submit = SubmitField('Login')    

class EditExpenseForm(FlaskForm):
    category = SelectField('Category', validators=[DataRequired()], choices=[
        ('Food', 'Food'),
        ('Transport', 'Transport'),
        ('Bills', 'Bills'),
        ('Entertainment', 'Entertainment'),
        ('Travel', 'Travel'),
        ('Shopping', 'Shopping'),
        ('Dining Out', 'Dining Out'),
        ('Education', 'Education'),
        ('Health', 'Health'),
        ('Gifts', 'Gifts'),
        ('Donations', 'Donations'),
        ('Other', 'Other')
    ])
    amount = FloatField('Amount', validators=[DataRequired()])
    description = StringField('Description', validators=[Length(max=200)])
    date = DateField('Date', validators=[DataRequired()])
    submit = SubmitField('Update Expense')        