from application.setup import api,bstorage,tstorage,sstorage,texttospeech
from application.models import db,Users,Roles,Sections,Books
import os
from datetime import datetime
from application.forms import languages
from flask import request
from flask_restful import Resource, fields, marshal, reqparse

class Graph(Resource):
  def get(self):
    user=len(db.session.query(Users.id).all())-1
    Member=db.session.query(Roles).filter(Roles.name=="Member").first()
    Members=len(Member.users)
    Normal_Users=user-Members
    return [["Normal Users","Members"],[Normal_Users,Members]]
api.add_resource(Graph,'/api/graph')


book_output = {
    "id": fields.Integer,
    "name": fields.String,
    "section_id": fields.String,
    "author": fields.String,
    "language": fields.String,
    "price":fields.Float,
    "content":fields.String,
    "noofcopies":fields.Integer,
    "storage":fields.String,
    "sound":fields.String,
    "thumbnail":fields.String
}
book_parser = reqparse.RequestParser()
book_parser.add_argument('name',type=str,required=True,location="form")
book_parser.add_argument('section_id',type=int,required=True,location="form")
book_parser.add_argument('author',type=str,required=True,location="form")
book_parser.add_argument('language',type=str,location="form")
book_parser.add_argument('price',type=int,required=True,location="form")
book_parser.add_argument('content',type=str,location="form")
book_parser.add_argument('noofcopies',type=int,required=True,location="form")

class BookCRUD(Resource):
  def get(self,id):
    book=db.session.query(Books).filter(Books.id==id).first()
    if book:
      return marshal(book,book_output),200
    else:
      return "Not Found",404
  def post(self):
    book_args = book_parser.parse_args()
    l=book_args.get('language')
    tnail = request.files["thumbnail"]
    thumbnail=datetime.now().strftime("%Y%m%d%H%M%S")+".png"
    tnail.save(tstorage(thumbnail))
    book = request.files["storage"]
    storage=datetime.now().strftime("%Y%m%d%H%M%S")+".pdf"
    storageloc=bstorage(storage)
    book.save(storageloc)
    sound=datetime.now().strftime("%Y%m%d%H%M%S")+".mp3"
    texttospeech(storageloc,sstorage(sound),l)
    row=Books(name=book_args.get('name'),content=book_args.get('content'),
              noofcopies=book_args.get('noofcopies'),author=book_args.get('author'),
              price=book_args.get('price'),section_id=book_args.get('section_id'),
              language=languages[l],storage=storage,sound=sound,thumbnail=thumbnail)
    db.session.add(row)
    db.session.commit()
    return "Successfully Created!!",201
  def put(self,id):
    book_args = book_parser.parse_args()
    b=db.session.query(Books).filter(Books.id==id).first()
    if b:
      b.name=book_args.get('name')
      b.content=book_args.get('content')
      b.noofcopies=book_args.get('noofcopies')
      b.author=book_args.get('author')
      b.price=book_args.get('price')
      b.section_id=book_args.get('section_id')
      db.session.commit()
      return "Successfully updated!!",200
    else:
      return "Not Found",404
  def delete(self,id):
    book=db.session.query(Books).filter(Books.id==id).first()
    if book:
        bookloc=bstorage(book.storage)
        if os.path.exists(bookloc):
          os.remove(bookloc)
        thumbnailloc=tstorage(book.thumbnail)
        if os.path.exists(thumbnailloc):
          os.remove(thumbnailloc)
        soundloc=sstorage(book.sound)
        if os.path.exists(soundloc):
          os.remove(soundloc)
        db.session.delete(book)
        db.session.commit()
        return 204
    else:
      return "Not Found",404

api.add_resource(BookCRUD,'/api/book/<int:id>',"/api/book")


section_output = {
    "id": fields.Integer,
    "name": fields.String,
    "description": fields.String
}
section_parser = reqparse.RequestParser()
section_parser.add_argument('name',type=str,required=True,location="form")
section_parser.add_argument('description',type=str,location="form")


class SectionCRUD(Resource):
  def get(self,id):
    section=db.session.query(Sections).filter(Sections.id==id).first()
    if section:
      return marshal(section,section_output),200
    else:
      return "Not Found",404
  def post(self):
    section_args = section_parser.parse_args()
    row=Sections(name=section_args.get('name'),description=section_args.get('description'))
    db.session.add(row)
    db.session.commit()
    return "Successfully Created!!",201
  def put(self,id):
    s=db.session.query(Sections).filter(Sections.id==id).first()
    section_args = section_parser.parse_args()
    if s:
      s.name=section_args.get('name')
      s.description=section_args.get('description')
      db.session.commit()
      return "Successfully updated!!",200
    else:
      return "Not Found",404
  def delete(self,id):
    section=db.session.query(Sections).filter(Sections.id==id).first()
    if section:
        for book in section.book:
          bookloc=bstorage(book.storage)
          thumbnailloc=tstorage(book.thumbnail)
          soundloc=sstorage(book.sound)
          if os.path.exists(bookloc):
            os.remove(bookloc)
          if os.path.exists(thumbnailloc):
            os.remove(thumbnailloc)
          if os.path.exists(soundloc):
            os.remove(soundloc)
        db.session.delete(section)
        db.session.commit()
        return "Successfully deleted!!",204
    else:
      return "Not Found",404

api.add_resource(SectionCRUD,'/api/section/<int:id>',"/api/section")