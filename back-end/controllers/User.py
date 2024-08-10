from application.setup import app, cardexpired, bstorage, languages, tstorage, cache
from application.models import (
    db,
    Books,
    IssuedBook,
    PurchasedBook,
    Ratings,
    PaymentDetails,
)
from flask import abort, request
from flask_security import roles_required, current_user
from application.forms import RatingForm, PaymentDetailsForm
from datetime import datetime, timedelta


def make_key(id=None):
    # make user specific and path specific key
    return current_user.fs_uniquifier + request.full_path


@app.route("/user/dashboard")
@roles_required("User")
@cache.cached(timeout=60, make_cache_key=make_key)
def account():
    ibook = (
        db.session.query(IssuedBook).filter(IssuedBook.user_id == current_user.id).all()
    )

    return {
        "username": current_user.username,
        "email": current_user.email,
        "last_login_at": current_user.last_login_at,
        "last_login_ip": current_user.last_login_ip,
        "membership": (
            "Subscribed member" if current_user.has_role("Member") else "Normal member"
        ),
        "daily_remainders": current_user.daily_remainders,
        "graph": [
            [i.book.name, i.issue_date, i.return_date]
            for i in ibook
            if i.return_status == 0
        ],
        "login_count": current_user.login_count,
        "purchased_book_count": len(current_user.purchase),
        "issued_book_count": len(ibook),
        "rating_count": len(current_user.rating),
        "payment": (
            {
                "card_number": current_user.payment.cardno,
                "card_name": current_user.payment.cardname,
                "expiry_date": current_user.payment.expirydate,
            }
            if current_user.payment
            else {}
        ),
        "membership_date": (
            f'"{current_user.membership_date.strftime("%Y-%m-%d %H:%M:%S")}"'
            if current_user.membership_date
            else '""'
        ),
    }


@app.route("/user/dailymails")
@roles_required("User")
def dailymails():
    options = request.args.get("options")
    if options == "out":
        current_user.daily_remainders = 0
    else:
        current_user.daily_remainders = 1
    db.session.commit()
    return '"The operation is successful"'


@app.route("/user/paymentdetails", methods=["PUT"])
@roles_required("User")
def paymentdetails():
    form = PaymentDetailsForm()
    if form.validate_on_submit():
        p = current_user.payment
        if p:
            form.populate_obj(p)
        else:
            row = PaymentDetails(
                cardno=form.cardno.data,
                expirydate=form.expirydate.data,
                cardname=form.cardname.data,
                user_id=current_user.id,
            )
            db.session.add(row)
        db.session.commit()
        return '"The payment details is successfully updated."'
    else:
        errors = [
            f"{field} : {error}"
            for field in form.errors
            for error in form.errors[field]
        ]
        abort(400, errors)


@app.route("/user/membership", methods=["POST"])
@roles_required("User")
def member():
    if not current_user.has_role("Member"):
        if not current_user.payment:
            abort(400, "Enter the payment details before purchasing.")
        elif cardexpired(current_user.payment):
            abort(400, "Your card has expired. Please update your payment details.")
        else:
            app.security.datastore.add_role_to_user(current_user, "Member")
            current_user.membership_date = datetime.now()
            db.session.commit()
            return '"The membership registration is completed."'
    else:
        abort(403)


@app.route("/user/delete", methods=["DELETE"])
@roles_required("User")
@cache.cached(timeout=200, make_cache_key=make_key)
def userdelete():
    for i in (
        db.session.query(IssuedBook)
        .filter(IssuedBook.user_id == current_user.id, IssuedBook.return_status == 0)
        .all()
    ):
        i.book.noofcopies += 1
    app.security.datastore.delete_user(current_user)
    db.session.commit()
    return '"The user account is successfully deleted."'


@app.route("/user/book/issue/<int:id>")
@roles_required("User")
@cache.cached(timeout=60, make_cache_key=make_key)
def bookissue(id):
    bookdetails = db.session.query(Books).filter(Books.id == id).first()
    if bookdetails:
        issuedbook = (
            db.session.query(IssuedBook)
            .filter(
                IssuedBook.user_id == current_user.id,
                IssuedBook.return_status == 0,
            )
            .all()
        )
        ibook = (
            db.session.query(IssuedBook)
            .filter(
                IssuedBook.user_id == current_user.id,
                IssuedBook.book_id == id,
                IssuedBook.return_status == 0,
            )
            .all()
        )
        if ibook:
            abort(
                400,
                "You have already issued the book!! You can again re-issue after you return the book.",
            )
        elif bookdetails.noofcopies > 0:
            bookdetails.noofcopies -= 1
            insert = False
            if current_user.has_role("Member"):
                if len(issuedbook) <= 10:
                    row = IssuedBook(
                        return_date=datetime.now() + timedelta(days=14),
                        book_id=bookdetails.id,
                        user_id=current_user.id,
                    )
                    insert = True
            else:
                if len(issuedbook) <= 5:
                    row = IssuedBook(
                        return_date=datetime.now() + timedelta(days=7),
                        book_id=bookdetails.id,
                        user_id=current_user.id,
                    )
                    insert = True
            if insert:
                db.session.add(row)
                db.session.commit()
                return '"The book is successfully issued."'
            else:
                abort(400, "You exceed the issue limit. Try to return some books.")
        else:
            abort(
                400,
                """There is no more copies of the book. Wait for someone to return the book.
            Else You can purchase the book to get unlimited access.""",
            )
    else:
        abort(404)


@app.route("/user/book/purchase/<int:id>")
@roles_required("User")
@cache.cached(timeout=60, make_cache_key=make_key)
def bookpurchase(id):
    bookdetails = db.session.query(Books).filter(Books.id == id).first()
    if bookdetails:
        pbook = (
            db.session.query(PurchasedBook)
            .filter(
                PurchasedBook.user_id == current_user.id,
                PurchasedBook.book_id == id,
            )
            .all()
        )
        if pbook:
            abort(
                400,
                "You have already purchased the book. You can not purchase it more than once.",
            )
        elif not current_user.payment:
            abort(400, "Enter the payment details before purchasing.")
        elif cardexpired(current_user.payment):
            abort(400, "Your card has expired. Update your payment details.")
        else:
            row = PurchasedBook(
                price=bookdetails.price,
                book_id=bookdetails.id,
                user_id=current_user.id,
            )
            db.session.add(row)
            db.session.commit()
            return '"The book is successfully purchased."'
    else:
        abort(404)


@app.route("/user/issue")
@roles_required("User")
@cache.cached(timeout=60, make_cache_key=make_key)
def issue():
    previous_issue = []
    current_issue = []
    for i in (
        db.session.query(IssuedBook).filter(IssuedBook.user_id == current_user.id).all()
    ):
        if i.return_status == 0:
            current_issue.append(
                {
                    "issue_id": i.id,
                    "book_id": i.book_id,
                    "book_name": i.book.name,
                    "section_name": i.book.section.name,
                    "author_name": i.book.author,
                    "issue_date": i.issue_date,
                    "return_date": i.return_date,
                    "storage": bstorage(stype="retrieval", id=i.book_id),
                    "language": languages[i.book.language],
                    "thumbnail": tstorage(i.book.thumbnail, "retrieval"),
                }
            )
        else:
            previous_issue.append(
                {   
                    "issue_id": i.id,
                    "book_id": i.book_id,
                    "book_name": i.book.name,
                    "section_name": i.book.section.name,
                    "author_name": i.book.author,
                    "issue_date": i.issue_date,
                    "return_date": i.return_date,
                    "thumbnail": tstorage(i.book.thumbnail, "retrieval"),
                }
            )

    return {"previous_issue": previous_issue, "current_issue": current_issue}


@app.route("/user/issue/return/<int:id>")
@roles_required("User")
@cache.cached(timeout=60, make_cache_key=make_key)
def returnbook(id):
    issuedetails = (
        db.session.query(IssuedBook)
        .filter(
            IssuedBook.user_id == current_user.id,
            IssuedBook.return_status == 0,
            IssuedBook.id == id,
        )
        .first()
    )
    if issuedetails:
        issuedetails.return_status = 1
        issuedetails.book.noofcopies += 1
        issuedetails.return_date = datetime.now()
        db.session.commit()
        return '"The book is successfully returned."'
    else:
        abort(400, "You have not yet issued the book.")


@app.route("/user/purchase")
@roles_required("User")
@cache.cached(timeout=60, make_cache_key=make_key)
def purchase():
    purchases = []
    for p in (
        db.session.query(PurchasedBook)
        .filter(PurchasedBook.user_id == current_user.id)
        .all()
    ):
        purchases.append(
            {
                "purchase_id": p.id,
                "book_id": p.book_id,
                "book_name": p.book.name,
                "section_name": p.book.section.name,
                "author_name": p.book.author,
                "purchase_date": p.purchase_date,
                "price": p.price,
                "storage": bstorage(stype="retrieval", id=p.book_id),
                "thumbnail": tstorage(p.book.thumbnail, "retrieval"),
            }
        )
    return {"purchases": purchases}


@app.route("/user/ratings")
@roles_required("User")
@cache.cached(timeout=60, make_cache_key=make_key)
def rating():
    rated = []
    not_rated = []
    book_id = set()
    for r in db.session.query(Ratings).filter(Ratings.user_id == current_user.id).all():
        book_id.add(r.book_id)
        rated.append(
            {
                "rating_id": r.id,
                "book_id": r.book_id,
                "book_name": r.book.name,
                "section_name": r.book.section.name,
                "author_name": r.book.author,
                "rating": r.rating,
                "rating_date": r.rating_date,
                "feedback": r.feedback,
                "thumbnail": tstorage(r.book.thumbnail, "retrieval"),
            }
        )
    for p in (
        db.session.query(PurchasedBook)
        .filter(PurchasedBook.user_id == current_user.id)
        .all()
    ):
        if p.book_id not in book_id:
            book_id.add(p.book_id)
            not_rated.append(
                {
                    "book_id": p.book_id,
                    "book_name": p.book.name,
                    "section_name": p.book.section.name,
                    "author_name": p.book.author,
                    "thumbnail": tstorage(p.book.thumbnail, "retrieval"),
                }
            )
    for i in (
        db.session.query(IssuedBook).filter(IssuedBook.user_id == current_user.id).all()
    ):
        if i.book_id not in book_id:
            book_id.add(i.book_id)
            not_rated.append(
                {
                    "book_id": i.book_id,
                    "book_name": i.book.name,
                    "section_name": i.book.section.name,
                    "author_name": i.book.author,
                    "thumbnail": tstorage(i.book.thumbnail, "retrieval"),
                }
            )
    return {"rated": rated, "not_rated": not_rated}


@app.route("/user/ratings/edit/<int:id>", methods=["PUT"])
@roles_required("User")
def ratingedit(id):
    userrating = (
        db.session.query(Ratings)
        .filter(Ratings.user_id == current_user.id, Ratings.id == id)
        .first()
    )
    if not userrating:
        abort(400, "You have not rated the book.")
    form = RatingForm()
    if form.validate_on_submit():
        form.populate_obj(userrating)
        db.session.commit()
        return '"The rating is successfully updated."'
    else:
        errors = [
            f"{field} : {error}"
            for field in form.errors
            for error in form.errors[field]
        ]
        abort(400, errors)


@app.route("/user/ratings/create/<int:book_id>", methods=["POST"])
@roles_required("User")
def ratingcreate(book_id):
    userrating = (
        db.session.query(Ratings)
        .filter(Ratings.user_id == current_user.id, Ratings.book_id == book_id)
        .first()
    )
    if userrating:
        abort(400, "You already rated the book!!Try to update it.")
    ibook = (
        db.session.query(IssuedBook)
        .filter(IssuedBook.user_id == current_user.id, IssuedBook.book_id == book_id)
        .first()
    )
    pbook = (
        db.session.query(PurchasedBook)
        .filter(
            PurchasedBook.user_id == current_user.id,
            PurchasedBook.book_id == book_id,
        )
        .first()
    )
    if not ibook and not pbook:
        abort(400, "You have not purchased or issued the book.")
    form = RatingForm()
    if form.validate_on_submit():
        row = Ratings(
            user_id=current_user.id,
            book_id=book_id,
            rating=form.rating.data,
            feedback=form.feedback.data,
        )
        db.session.add(row)
        db.session.commit()
        return {"rating_id": row.id}
    else:
        errors = [
            f"{field} : {error}"
            for field in form.errors
            for error in form.errors[field]
        ]
        abort(400, errors)


@app.route("/user/ratings/delete/<int:id>", methods=["DELETE"])
@roles_required("User")
@cache.cached(timeout=200, make_cache_key=make_key)
def ratingdelete(id):
    userrating = (
        db.session.query(Ratings)
        .filter(Ratings.user_id == current_user.id, Ratings.id == id)
        .first()
    )
    if userrating:
        db.session.delete(userrating)
        db.session.commit()
        return '"The rating is successfully deleted."'
    else:
        abort(400, "You have not rated for the book!")
