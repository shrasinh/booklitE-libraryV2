from application.setup import app, tstorage
from application.models import db, Books, Ratings, Sections
from flask import abort, json
from werkzeug.exceptions import HTTPException
from flask_security import current_user, logout_user
from string import digits, ascii_letters
from random import SystemRandom


@app.errorhandler(HTTPException)
def handle_exception(error):
    response = error.get_response()
    response.data = json.dumps({"response": {"errors": [error.description]}})
    return response


@app.route("/")
def home():
    sections = []
    for s in Sections.query.order_by(Sections.date_created.desc()).all():
        if s.book:
            sections.append(
                {
                    "section_id": s.id,
                    "section_name": s.name,
                    "description": s.description,
                    "created_on": s.date_created,
                    "books": [
                        {
                            "book_id": b.id,
                            "book_name": b.name,
                            "thumbnail": tstorage(b.thumbnail),
                            "author_name": b.author,
                            "language": b.language,
                            "rating": db.session.query(db.func.avg(Ratings.rating))
                            .filter(Ratings.book_id == b.id)
                            .first(),
                        }
                        for b in s.book
                    ],
                }
            )
    return {"sections": sections}


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
        return "Logout successful."
    else:
        abort(401)


@app.route("/book/<int:id>")
def book(id):
    book = db.session.query(Books).filter(Books.id == id).first()
    if not book:
        abort(404)
    else:
        return {
            "book_id": id,
            "book_name": book.name,
            "thumbnail": tstorage(book.thumbnail),
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


@app.route("/accountdetails")
def accountdetails():
    if current_user.is_authenticated:
        return {
            "username": current_user.username,
            "email": current_user.email,
            "last_login_at": current_user.last_login_at,
            "last_login_ip": current_user.last_login_ip,
            "membership": (
                "Admin"
                if current_user.has_role("Admin")
                else ("Member" if current_user.has_role("Member") else "Normal member")
            ),
            "payment_details": (
                {
                    "card_no": current_user.payment.card_no,
                    "cardname": current_user.payment.card_no,
                    "expirydate": current_user.payment.expirydate,
                }
                if current_user.payment
                else {}
            ),
        }
    else:
        abort(401)
