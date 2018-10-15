from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class MessageForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=1, max=20)])
    message = TextAreaField('Сообщение', validators=[DataRequired(), Length(min=1, max=200)])
    submit = SubmitField()
