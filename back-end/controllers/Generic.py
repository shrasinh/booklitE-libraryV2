from application.setup import app, tstorage, CustomResponse, cache
from application.models import db, Books, Ratings, Sections, IssuedBook, PurchasedBook
from flask import abort, json, send_from_directory, request
from werkzeug.exceptions import HTTPException
from flask_security import current_user, logout_user
from string import digits, ascii_letters
from random import SystemRandom


@app.errorhandler(HTTPException)
def handle_exception(error):
    data = json.dumps(
        {
            "response": {
                "errors": (
                    [error.description]
                    if isinstance(error.description, str)
                    else error.description
                )
            }
        }
    )
    return CustomResponse(data, status=error.code)


@app.route("/")
@cache.cached(timeout=100)
def home():
    sections = []
    book_ids = []
    for s in Sections.query.order_by(Sections.date_created.desc()).all():
        if s.book:
            d = {
                "section_id": s.id,
                "section_name": s.name,
                "description": s.description,
                "created_on": s.date_created,
                "books": [],
            }
            for b in s.book:
                d["books"].append(
                    {
                        "book_id": b.id,
                        "book_name": b.name,
                        "thumbnail": tstorage(b.thumbnail, "retrieval"),
                        "author_name": b.author,
                        "language": b.language,
                        "rating": (
                            db.session.query(db.func.avg(Ratings.rating))
                            .filter(Ratings.book_id == b.id)
                            .first()[0]
                        ),
                    }
                )
                book_ids.append(b.id)
            sections.append(d)
    return {"sections": sections, "book_ids": book_ids}


@app.route("/user/role")
def userroleassign():
    if current_user.is_authenticated:
        if current_user.roles == []:
            app.security.datastore.add_role_to_user(current_user, "User")
        db.session.commit()
        return [r.name for r in current_user.roles]
    else:
        abort(401)


@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        # changing the fs_uniquifier so that all the authentication tokens of the current user gets invalidated
        current_user.fs_uniquifier = "".join(
            SystemRandom().choice(ascii_letters + digits) for _ in range(64)
        )
        db.session.commit()
        logout_user()
        return '"You have successfully logged out."'
    else:
        abort(401)


@app.route("/book/<int:id>")
@cache.memoize(timeout=200)
def book(id):
    book = db.session.query(Books).filter(Books.id == id).first()
    if not book:
        abort(404)
    else:
        return {
            "book_id": id,
            "book_name": book.name,
            "thumbnail": tstorage(book.thumbnail, "retrieval"),
            "author_name": book.author,
            "language": book.language,
            "price": book.price,
            "no_of_copies_available": book.noofcopies,
            "description": book.content,
            "ratings": [
                {
                    "username": r.user.username,
                    "feedback": r.feedback,
                    "rating": r.rating,
                    "rating_date": r.rating_date,
                }
                for r in db.session.query(Ratings).filter(Ratings.book_id == id).all()
            ],
        }


@app.route("/book/pdf/<int:id>")
def bookview(id):
    if current_user.is_authenticated:
        q = request.args.get("type")
        book = db.session.query(Books).filter(Books.id == id).first()
        if book:
            issued = purchased = False
            if current_user.has_role("User"):
                issued = (
                    db.session.query(IssuedBook)
                    .filter(
                        IssuedBook.book_id == id,
                        IssuedBook.user_id == current_user.id,
                        IssuedBook.return_status == 0,
                    )
                    .first()
                )
                if not issued:
                    purchased = (
                        db.session.query(PurchasedBook)
                        .filter(
                            PurchasedBook.book_id == id,
                            PurchasedBook.user_id == current_user.id,
                        )
                        .first()
                    )
            if current_user.has_role("Admin") or issued or purchased:
                if purchased and q == "download":
                    return send_from_directory(
                        "files/books",
                        book.storage,
                        as_attachment=True,
                        download_name=book.name,
                    )
                return send_from_directory("files/books", book.storage)
            else:
                abort(403)
        else:
            abort(404)
    else:
        abort(401)
