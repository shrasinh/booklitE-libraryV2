from flask import Flask, Response, jsonify
from flask.sessions import SecureCookieSessionInterface, SessionMixin
from flask_migrate import Migrate
from flask_security import (
    Security,
    SQLAlchemyUserDatastore,
    hash_password,
    MailUtil,
    PasswordUtil,
    UsernameUtil,
)
from flask.json.provider import JSONProvider
from decimal import Decimal
from application.models import Users, Roles, db
import os
import json
from datetime import datetime
from celery import Celery
from flask_mailman import Mail
from flask_caching import Cache


# instantiate the flask application
app = Flask("BookLit")


# for app configuration

## for flask-sqlalchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.sqlite3"

## for flask-security-too
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw"
)
app.config["SECURITY_PASSWORD_SALT"] = os.environ.get(
    "SECURITY_PASSWORD_SALT", "146585145368132386173505678016728509634"
)
app.config["SECURITY_TRACKABLE"] = True
app.config["SECURITY_CONFIRMABLE"] = True
app.config["SECURITY_USERNAME_ENABLE"] = True
app.config["SECURITY_USERNAME_REQUIRED"] = True
app.config["SECURITY_PASSWORD_COMPLEXITY_CHECKER"] = "zxcvbn"
app.config["SECURITY_PASSWORD_CHECK_BREACHED"] = "best-effort"
app.config["SECURITY_PASSWORD_BREACHED_COUNT"] = 5
app.config["SECURITY_LOGOUT_METHODS"] = None
app.config["SECURITY_TOKEN_MAX_AGE"] = 60 * 60 * 24
app.config["WTF_CSRF_ENABLED"] = False

## for flask-mailman
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = os.getenv("MAIL_PORT")
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_USE_SSL"] = True

## for celery
app.config["broker_url"] = "redis://localhost:6379/1"
app.config["result_backend"] = "redis://localhost:6379/2"
app.config["broker_connection_retry_on_startup"] = True

## for flask-caching
app.config["CACHE_TYPE"] = "RedisCache"
app.config["CACHE_REDIS_HOST"] = "localhost"
app.config["CACHE_REDIS_PORT"] = 6379


# initializing celery
celery = Celery(
    app.name, broker=app.config["broker_url"], include=["controllers.Async"]
)
celery.conf.update(app.config)
celery.conf.enable_utc = False


# always run celery with app context
class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextTask

# initializing flask-mailman
mail = Mail(app)

# initializing flask-caching
cache = Cache(app)

# initializing flask-migrate
migrate = Migrate(app, db)

# initializing flask-security-too
user_datastore = SQLAlchemyUserDatastore(db, Users, Roles)
app.security = Security(app, user_datastore)
security_password = PasswordUtil(app)
security_mail = MailUtil(app)
security_username = UsernameUtil(app)


with app.app_context():

    db.init_app(app)  # initializing flask-sqlalchemy

    db.create_all()  # create the tables if not created

    if not app.security.datastore.find_user(
        email=os.environ.get("LIBRARIAN_EMAIL")
    ):  # if librarian is not created
        row1 = Roles(name="User", description="To get user priviliges")
        row2 = Roles(name="Member", description="To get the member privileges")
        row3 = Roles(name="Admin", description="To get admin priviliges")
        db.session.add(row1)
        db.session.add(row2)
        db.session.add(row3)
        app.security.datastore.create_user(
            username="librarian",
            email=os.environ.get("LIBRARIAN_EMAIL"),
            password=hash_password("pass#word12"),
            roles=[row3],
            confirmed_at=datetime.now(),
        )
    db.session.commit()


# changing the default implementation of some flask utils


## changing the datetime json format
class JSON_Improved(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime("%a %d %b %Y %H:%M:%S")
        if isinstance(o,Decimal):
            return str(o)
        else:
            return super(JSON_Improved, self).default(o)


class CustomJSONProvider(JSONProvider):

    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs , cls=JSON_Improved)
        
    def loads(self, s: str | bytes, **kwargs):
        return json.loads(s, **kwargs)


app.json = CustomJSONProvider(app)


## disabling sending of cookie
class CustomSessionInterface(SecureCookieSessionInterface):
    def should_set_cookie(self, app: Flask, session: SessionMixin) -> bool:
        return False


app.session_interface = CustomSessionInterface()


## adding the headers that allow cross-origin requests and jsonifying the response
class CustomResponse(Response):
    default_mimetype = "application/json"

    def __init__(self, response=None, *args, **kwargs):
        kwargs["headers"] = {
            "Access-Control-Allow-Origin": "http://localhost:5173",
            "Access-Control-Allow-Headers": "Authentication-Token,content-type",
            "Access-Control-Allow-Methods": "*",
        }
        return super(CustomResponse, self).__init__(response, *args, **kwargs)

    @classmethod
    def force_type(cls, rv, environ=None):
        if isinstance(rv, dict):
            rv = jsonify(rv)
        return super(CustomResponse, cls).force_type(rv, environ)


app.response_class = CustomResponse


# some functions and variable used all over the app


## to get the path of book pdf
def bstorage(l=None, stype="store", id=None):
    if stype == "retrieval":
        return f"http://localhost:5500/book/pdf/{id}"
    return os.path.join("files", "books", l)


## to get the path of book thumbnail
def tstorage(l, stype="store"):
    if stype == "retrieval":
        return "http://localhost:5500/static/thumbnail/" + l
    return os.path.join("static", "thumbnail", l)


## to check whether the user card details expired or not
def cardexpired(p):
    if datetime.now() > p.expirydate:
        return True
    return False


## languages in which the books can be
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
