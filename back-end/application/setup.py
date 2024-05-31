from flask import Flask
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore,hash_password
from flask_restful import Api
from application.models import Users,Roles,db,IssuedBook
import os
from functools import wraps
from gtts import gTTS
from pypdf import PdfReader
from datetime import datetime


# instantiate the flask application
app = Flask("BookLit")

# for app configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.sqlite3'
app.config['SECRET_KEY'] =os.environ.get("SECRET_KEY", 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')
app.config['SECURITY_TRACKABLE']=True
app.config['SECURITY_REGISTERABLE']=True
app.config['SECURITY_SEND_REGISTER_EMAIL']=False
app.config['SECURITY_USERNAME_ENABLE']=True
app.config['SECURITY_USERNAME_REQUIRED']=True
app.config['SECURITY_PASSWORD_COMPLEXITY_CHECKER']="zxcvbn"
app.config['SECURITY_PASSWORD_CHECK_BREACHED']="best-effort"
app.config['SECURITY_PASSWORD_BREACHED_COUNT']=5
app.config['SECURITY_POST_LOGIN_VIEW']="/user/roleassign"
app.config['SECURITY_POST_LOGOUT_VIEW']="/post/logout"
app.config['SECURITY_POST_REGISTER_VIEW']="/user/roleassign"
app.config['SECURITY_POST_VERIFY_URL']="/user/roleassign"


# for db migration i.e to change the database schema
migrate=Migrate(app,db)

# instantiate the application's api
api = Api(app)

# for flask security setup
user_datastore = SQLAlchemyUserDatastore(db, Users, Roles)
app.security = Security(app, user_datastore)

# pushing the app context
with app.app_context():
  db.init_app(app)# database integration to the application
  db.create_all() # create the tables if not created
  if not app.security.datastore.find_user(email="librarian@gmail.com"):
      row1=Roles(name="User",description="To get user priviliges")
      row2= Roles(name="Member",description="To get the member privileges")
      row3=Roles(name="Admin",description="To get admin priviliges")
      db.session.add(row1)
      db.session.add(row2)
      db.session.add(row3)
      app.security.datastore.create_user(username="librarian",email="librarian@gmail.com",password=hash_password("pass#word12"),roles=[row3])
  db.session.commit()

# the function checks if any issued book access needs to be revoked due to return date expiration
def issuedbooktime(funct):
    @wraps(funct)
    def wrapper(*args,**kwargs):
        ibook=IssuedBook.query.all()
        for book in ibook:
            if datetime.now()>book.return_date and book.return_status==0:
                book.return_status=1
                book.book.noofcopies+=1
        db.session.commit()
        return funct(*args,**kwargs)
    return wrapper

# for text to speech convertering
def texttospeech(fileloc,soundloc,l):
    reader = PdfReader(fileloc)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    sound = gTTS(text=text,tld="co.in", lang=l, slow=False)
    sound.save(soundloc)

# to get the path of book pdf
def bstorage(l):
    return os.path.join("static","books",l)

# to get the path of book sound
def sstorage(l):
    return os.path.join("static","sound",l)

# to get the path of book thumbnail
def tstorage(l):
    return os.path.join("static","thumbnail",l)

# to check whether the user card details expired or not
def cardexpired(p):
    if datetime.now()>p.expirydate:
        return True
    return False