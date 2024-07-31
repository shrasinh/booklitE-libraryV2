from application.setup import (
    app,
    tstorage,
    CustomResponse,
    cache,
    user_datastore,
    security_username,
    security_password,
    security_mail,
)
from application.models import db, Books, Ratings, Sections, IssuedBook, PurchasedBook
from flask import abort, json, send_from_directory, request
from werkzeug.exceptions import HTTPException
from string import digits, ascii_letters
from random import SystemRandom
from flask_security import (
    current_user,
    logout_user,
)
from flask_security.utils import (
    hash_password,
    send_mail,
)
from flask_security.confirmable import (
    generate_confirmation_token,
    confirm_email_token_status,
    confirm_user,
)


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


@app.route("/user/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    # Validate presence of email, username, and password
    if not email or not username or not password:
        abort(400, "Email, username, and password are required.")

    # Validate password, email and username
    try:
        security_mail.validate(email)
        msg, normalized = security_username.validate(username)
        if msg:
            raise ValueError(msg)
        msg, normalized = security_password.validate(password, True)
        if msg:
            abort(400, msg)

    except ValueError as e:
        abort(400, str(e))

    # normalize password,email,username
    password = security_password.normalize(password)
    email = security_mail.normalize(email)
    username = security_username.normalize(username)

    # Check if the user already exists by email or username
    if user_datastore.find_user(email=email) or user_datastore.find_user(
        username=username
    ):
        abort(400, "User already exists.")

    # Create a new user
    user = user_datastore.create_user(
        email=email,
        username=username,
        password=hash_password(password),
    )
    user_datastore.add_role_to_user(user, "User")
    db.session.commit()

    # Send a confirmation email
    token = generate_confirmation_token(user)
    confirmation_link = f"http://localhost:5173?token={token}"
    send_mail(
        "Please confirm your email address",
        user.email,
        "confirmation_instructions",
        user=user,
        confirmation_link=confirmation_link,
        confirmation_token=token,
    )

    return '"You have successfully registered.Please check and confirm your email before login."'


@app.route("/user/confirm/<token>", methods=["GET"])
def confirm_email(token):
    expired, invalid, user = confirm_email_token_status(token)
    if not user or invalid:
        abort(400, "Invalid confirmation token")
    if expired and not user.confirmed_at:
        # Send a confirmation email
        token = generate_confirmation_token(user)
        confirmation_link = f"http://localhost:5173?token={token}"
        send_mail(
            "Please confirm your email address",
            user.email,
            "confirmation_instructions",
            user=user,
            confirmation_link=confirmation_link,
            confirmation_token=token,
        )
        abort(400, "Confirmation token has expired. Confirmation email is send again.")
    if user.confirmed_at:
        abort(400, "Account already confirmed")

    # Confirm the user
    confirm_user(user)
    db.session.commit()

    return '"Account confirmed successfully. You can now login to your account."'


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
