from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField
from wtforms.validators import DataRequired,Length

class HelloForm(FlaskForm):
    name=StringField('名字',validators=[DataRequired(),Length(1,20)])
    body=TextAreaField('消息',validators=[DataRequired(),Length(1,200)])
    submit=SubmitField()