from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SignupForm(FlaskForm):
    account_id_3commas_signup = StringField('3commas Account ID:',
                                            validators=[DataRequired("Please enter your 3commas account id")])
    api_key_3commas_signup = StringField('3commas API KEY:',
                                         validators=[DataRequired("Please enter your 3commas account API KEY")])
    api_secret_3commas_signup = StringField('3commas API Secret:',
                                            validators=[
                                                DataRequired("Please enter your 3commas account API Secret")])
    api_key_ftx_signup = StringField('FTX API KEY:',
                                     validators=[DataRequired("Please enter your FTX account API key")])
    api_secret_ftx_signup = StringField('FTX API SECRET:',
                                        validators=[DataRequired("Please enter your FTX account API Secret")])

    run_button = SubmitField('Run')
    close_all_button = SubmitField('Close all')
    cleanup_button = SubmitField('Clean up')
    position_button = SubmitField('Position')
    tp_button = SubmitField('take profit')
