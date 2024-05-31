from flask_wtf import FlaskForm
from wtforms import StringField,IntegerField, SelectField, TextAreaField,SubmitField,SelectMultipleField,DateTimeField,TelField
from wtforms.validators import DataRequired,Optional,NumberRange,Length,InputRequired,Regexp,ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired
from datetime import datetime
from gtts import lang

languages=lang.tts_langs()


class BookForm(FlaskForm):
    storage = FileField('Book File',validators=[FileRequired(),FileAllowed(['pdf'], 'PDF only!')])
    thumbnail = FileField('Book Thumbnail',validators=[FileRequired(),FileAllowed(['png','jpeg','jpg'], 'Images only!')])
    language = SelectField('Language Selection',choices=[(i,lang.tts_langs()[i]) for i in lang.tts_langs()],coerce=str,validators=[DataRequired()])
    name= StringField('Book Name', validators=[DataRequired()])
    author= StringField('Author Name', validators=[DataRequired()])
    section_id = SelectField('Section Selection',coerce=int,validators=[DataRequired()])
    content = TextAreaField('Content',validators=[Optional()])
    noofcopies= IntegerField('Number of Copies available',validators=[InputRequired(),NumberRange(min=0)])
    price =IntegerField("Price",validators=[InputRequired(),NumberRange(min=0)])
    submit=SubmitField("Submit",validators=[DataRequired()])

class SectionForm(FlaskForm):
    name= StringField('Section Name', validators=[DataRequired()])
    description = TextAreaField('Description',validators=[Optional()])
    submit=SubmitField("Submit",validators=[DataRequired()])

class IssueRevokeForm(FlaskForm):
    issue = SelectMultipleField('Grant Access',coerce=int,validators=[Optional()])
    revoke = SelectMultipleField('Revoke Access',coerce=int,validators=[Optional()])
    submit=SubmitField("Submit",validators=[DataRequired()])

class PaymentDetailsForm(FlaskForm):
    cardno=TelField("Card number",validators=[DataRequired(),Length(min=12,max=19),Regexp("^[0-9]{12,19}$")])
    cardname=StringField('Name on the card', validators=[DataRequired(),Regexp("^[a-zA-Z]*$")])
    expirydate=DateTimeField("Expiry Date",format='%Y-%m',validators=[DataRequired()])
    def validate_expirydate(form, field):
        if field.data < datetime.now():
            raise ValidationError('The card should not be expired.')
    submit=SubmitField("Submit",validators=[DataRequired()])

class RatingForm(FlaskForm):
    rating =IntegerField("Rating",validators=[DataRequired(),NumberRange(min=1,max=5)])
    feedback=TextAreaField('Feedback',validators=[Optional()])
    submit=SubmitField("Submit",validators=[DataRequired()])