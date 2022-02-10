from flask_wtf import Form 
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class SignupForm(Form):
  # accountid
  account_id_3commas = StringField('3commas Account ID', validators=[DataRequired("Please enter your 3commas account id")])
  #accountkey
  api_key_3commas = StringField('3commas Account API KEY', validators=[DataRequired("Please enter your 3commas account API KEY")])
  #accountsecret
  api_secret_3commas = StringField('3commas Account API Secret', validators=[DataRequired("Please enter your 3commas account API Secret")])
  api_key_ftx = StringField('FTX API KEY', validators=[DataRequired("Please enter your FTX account API Secret")])
  api_secret_ftx = StringField('FTX API SECRET', validators=[DataRequired("Please enter your FTX account API Secret")])

  submit = SubmitField('Run')
