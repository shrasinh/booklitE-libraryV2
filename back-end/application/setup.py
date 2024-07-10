from flask import Flask, Response, jsonify
from flask.sessions import SecureCookieSessionInterface, SessionMixin
from flask_migrate import Migrate
from flask_security import (
    Security,
    SQLAlchemyUserDatastore,
    hash_password,
)
from application.models import Users, Roles, db, IssuedBook
import os
from datetime import datetime


# instantiate the flask application
app = Flask("BookLit")

# for app configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.sqlite3"
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw"
)
app.config["SECURITY_PASSWORD_SALT"] = os.environ.get(
    "SECURITY_PASSWORD_SALT", "146585145368132386173505678016728509634"
)
app.config["SECURITY_TRACKABLE"] = True
app.config["SECURITY_REGISTERABLE"] = True
app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
app.config["SECURITY_USERNAME_ENABLE"] = True
app.config["SECURITY_USERNAME_REQUIRED"] = True
app.config["SECURITY_PASSWORD_COMPLEXITY_CHECKER"] = "zxcvbn"
app.config["SECURITY_PASSWORD_CHECK_BREACHED"] = "best-effort"
app.config["SECURITY_PASSWORD_BREACHED_COUNT"] = 5
app.config["SECURITY_LOGOUT_METHODS"] = None
app.config["SECURITY_TOKEN_MAX_AGE"] = 60 * 60 * 24
app.config["WTF_CSRF_ENABLED"] = False


# disabling sending of cookie
class CustomSessionInterface(SecureCookieSessionInterface):
    def should_set_cookie(self, app: Flask, session: SessionMixin) -> bool:
        return False


app.session_interface = CustomSessionInterface()


class CustomResponse(Response):
    default_mimetype = "application/json"

    def __init__(self, response=None, **kwargs):
        # adding the headers that allow cross-origin requests
        kwargs["headers"] = {
            "Access-Control-Allow-Origin": "http://localhost:5173",
            "Access-Control-Allow-Headers": "Authentication-Token,content-type",
            "Access-Control-Allow-Methods": "*",
        }
        return super(CustomResponse, self).__init__(response, **kwargs)

    @classmethod
    def force_type(cls, rv, environ=None):
        # jsonifying the response
        if isinstance(rv, dict):
            rv = jsonify(rv)
        return super(CustomResponse, cls).force_type(rv, environ)


app.response_class = CustomResponse

# for db migration i.e to change the database schema
migrate = Migrate(app, db)

# for flask security setup
user_datastore = SQLAlchemyUserDatastore(db, Users, Roles)
app.security = Security(app, user_datastore)

# pushing the app context
with app.app_context():
    db.init_app(app)  # database integration to the application
    db.create_all()  # create the tables if not created
    if not app.security.datastore.find_user(email="librarian@gmail.com"):
        row1 = Roles(name="User", description="To get user priviliges")
        row2 = Roles(name="Member", description="To get the member privileges")
        row3 = Roles(name="Admin", description="To get admin priviliges")
        db.session.add(row1)
        db.session.add(row2)
        db.session.add(row3)
        app.security.datastore.create_user(
            username="librarian",
            email="librarian@gmail.com",
            password=hash_password("pass#word12"),
            roles=[row3],
        )
    db.session.commit()


# the function checks if any issued book access needs to be revoked due to return date expiration
def issuedbooktime():
    ibook = IssuedBook.query.all()
    now = datetime.now()
    for book in ibook:
        if now > book.return_date and book.return_status == 0:
            book.return_status = 1
            book.book.noofcopies += 1
    db.session.commit()


# to get the path of book pdf
def bstorage(l=None, stype="store", id=None):
    if stype == "retrieval":
        return f"http://localhost:5500/book/pdf/{id}"
    return os.path.join("files", "books", l)


# to get the path of book thumbnail
def tstorage(l, stype="store"):
    if stype == "retrieval":
        return "http://localhost:5500/static/thumbnail/" + l
    return os.path.join("static", "thumbnail", l)


# to check whether the user card details expired or not
def cardexpired(p):
    if datetime.now() > p.expirydate:
        return True
    return False


# languages in which the books can be
languages = {
    "English (United States)": "en-US",
    "Deutsch": "de-DE",
    "UK English": "en-GB",
    "español": "es-ES",
    "español de Estados Unidos": "es-US",
    "français": "fr-FR",
    "हिन्दी": "hi-IN",
    "Bahasa Indonesia": "id-ID",
    "italiano": "it-IT",
    "日本語": "ja-JP",
    "한국의": "ko-KR",
    "Nederlands": "nl-NL",
    "polski": "pl-PL",
    "português do Brasil": "pt-BR",
    "русский": "ru-RU",
    "普通话（中国大陆）": "zh-CN",
    "粤語（香港）": "zh-HK",
    "國語（臺灣）": "zh-TW",
}
