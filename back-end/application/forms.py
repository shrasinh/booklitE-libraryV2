from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    IntegerField,
    FloatField,
    SelectField,
    TextAreaField,
    SelectMultipleField,
    DateTimeField,
    TelField,
)
from wtforms.validators import (
    DataRequired,
    Optional,
    NumberRange,
    Length,
    InputRequired,
    Regexp,
    ValidationError,
)
from flask_wtf.file import FileField, FileAllowed, FileRequired
from datetime import datetime
from application.setup import languages


class BookForm(FlaskForm):
    storage = FileField(
        "Book File", validators=[FileRequired(), FileAllowed(["pdf"], "PDF only!")]
    )
    thumbnail = FileField(
        "Book Thumbnail",
        validators=[
            FileRequired(),
            FileAllowed(["png", "jpeg", "jpg"], "Images only!"),
        ],
    )
    language = SelectField(
        "Language Selection",
        choices=[(i, languages[i]) for i in languages],
        coerce=str,
        validators=[DataRequired()],
    )
    name = StringField("Book Name", validators=[DataRequired()])
    author = StringField("Author Name", validators=[DataRequired()])
    section_id = SelectField(
        "Section Selection", coerce=int, validators=[DataRequired()]
    )
    content = TextAreaField("Content", validators=[DataRequired()])
    noofcopies = IntegerField(
        "Number of Copies available", validators=[InputRequired(), NumberRange(min=0)]
    )
    price = FloatField("Price", validators=[InputRequired(), NumberRange(min=0)])

    def validate_price(form, field):
        if (not field.data % 1 == 0) and len(str(field.data).split(".")[1]) > 2:
            raise ValidationError(
                "The price should not have more than 2 decimal precision."
            )


class SectionForm(FlaskForm):
    name = StringField("Section Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])


class IssueRevokeForm(FlaskForm):
    issue = SelectMultipleField("Grant Access", coerce=int, validators=[Optional()])
    revoke = SelectMultipleField("Revoke Access", coerce=int, validators=[Optional()])


class PaymentDetailsForm(FlaskForm):
    cardno = TelField(
        "Card number",
        validators=[DataRequired(), Length(min=12, max=19), Regexp("^[0-9]{12,19}$")],
    )
    cardname = StringField(
        "Name on the card", validators=[DataRequired(), Regexp("^[a-zA-Z]*$")]
    )
    expirydate = DateTimeField(
        "Expiry Date", format="%Y-%m", validators=[DataRequired()]
    )

    def validate_expirydate(form, field):
        if field.data < datetime.now():
            raise ValidationError("The card should not be expired.")


class RatingForm(FlaskForm):
    rating = IntegerField(
        "Rating", validators=[DataRequired(), NumberRange(min=1, max=5)]
    )
    feedback = TextAreaField("Feedback", validators=[Optional()])
