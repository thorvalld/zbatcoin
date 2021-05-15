from wtforms import Form, StringField, DecimalField, IntegerField, TextAreaField, PasswordField, validators


class RegisterForm(Form):
    name = StringField('Fullname', [validators.Length(min=3, max=32)])
    username = StringField('Username', [validators.Length(min=4, max=32)])
    email = StringField('Email', [validators.Length(min=6, max=32)])
    password = PasswordField('Password', [validators.DataRequired(), validators.EqualTo('confirm', message="Passwords must match")])
    confirm = PasswordField('Confirm password')


class TransferFundsForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=32)])
    amount = StringField('Amount', [validators.Length(min=1, max=50)])


class BuyFundsForm(Form):
    amount = StringField('Amount', [validators.Length(min=1, max=50)])