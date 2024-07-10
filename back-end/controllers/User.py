from application.setup import (
    app,
    cardexpired,
    bstorage,
)
from application.models import (
    db,
    Books,
    IssuedBook,
    PurchasedBook,
    Ratings,
    PaymentDetails,
)
from flask import abort
from flask_security import roles_required, current_user
from application.forms import RatingForm, PaymentDetailsForm
from datetime import datetime, timedelta


@app.route("/user/dashboard")
@roles_required("User")
# caching
def userdashboard():
    ibook = db.session.query(IssuedBook).filter(IssuedBook.user_id == current_user.id)
    pbook = db.session.query(PurchasedBook).filter(
        PurchasedBook.user_id == current_user.id
    )
    return {
        "graph": [
            {
                "book_name": i.book.name,
                "issue_date": i.issue_date,
                "return_date": i.return_date,
            }
            for i in ibook
        ],
        "purchased_book_count": len(pbook),
        "issued_book_count": len(ibook),
    }


@app.route("/account")
@roles_required("User")
def account():
    return {
        "username": current_user.username,
        "email": current_user.email,
        "last_login_at": current_user.last_login_at,
        "last_login_ip": current_user.last_login_ip,
        "membership": (
            "Member" if current_user.has_role("Member") else "Normal member"
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


@app.route("/paymentdetails", methods=["PUT"])
@roles_required("User")
def paymentdetails():
    p = current_user.payment
    form = PaymentDetailsForm()
    if form.validate_on_submit():
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
            j.lower().replace("this field", i)
            for i in form.errors
            for j in form.errors[i]
        ]
        abort(400, errors)


@app.route("/user/confirmation/delete", methods=["DELETE"])
# caching
@roles_required("User")
def userconfirmdelete():
    app.security.datastore.delete_user(current_user)
    db.session.commit()
    return '"The user account is successfully deleted."'


@app.route("/membership")
@roles_required("User")
def member():
    if not current_user.has_role("Member"):
        if not current_user.payment:
            abort(400, "Enter the payment details before purchasing.")
        elif cardexpired(current_user.payment):
            abort(400, "Your card has expired. Please update your payment details.")
        else:
            app.security.datastore.add_role_to_user(current_user, "Member")
            db.session.commit()
            return '"The membership registration is completed."'
    else:
        abort(403)


@app.route("/book/issue/<int:id>")
@roles_required("User")
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


@app.route("/book/purchase/<int:id>")
@roles_required("User")
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
            return "'The book is successfully purchased.'"
    else:
        abort(404)


@app.route("/user/issuedbooks")
@roles_required("User")
def issue():
    issues = []
    for i in (
        db.session.query(IssuedBook).filter(IssuedBook.user_id == current_user.id).all()
    ):
        issues.append(
            {
                "issue_id": i.id,
                "book_id": i.book_id,
                "book_name": i.book.name,
                "section_name": i.book.section.name,
                "author_name": i.book.author,
                "issue_date": i.issue_date,
                "return_date": i.return_date,
                "storage": (
                    bstorage(stype="retrieval", id=i.book_id)
                    if i.return_status == 0
                    else ""
                ),
            }
        )
    return {"issues": issues}


@app.route("/user/issuedbooks/return/<int:id>")
@roles_required("User")
def returnbook(id):
    issuedetails = (
        db.session.query(IssuedBook)
        .filter(
            IssuedBook.user_id == current_user.id,
            IssuedBook.return_status == 0,
            IssuedBook.book_id == id,
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


@app.route("/user/purchasedbooks")
@roles_required("User")
def purchase():
    purchases = []
    for p in (
        db.session.query(PurchasedBook)
        .filter(PurchasedBook.user_id == current_user.id)
        .all()
    ):
        purchases.append(
            {
                "book_id": p.book_id,
                "book_name": p.book.name,
                "section_name": p.book.section.name,
                "author_name": p.book.author,
                "purchase_date": p.purchase_date,
                "price": p.price,
                "storage": bstorage(stype="retrieval", id=p.book_id),
            }
        )
    return {"purchases": purchases}


@app.route("/user/ratings")
@roles_required("User")
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
            }
        )
    for p in (
        db.session.query(PurchasedBook.book_id)
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
                }
            )
    for i in (
        db.session.query(IssuedBook.book_id)
        .filter(IssuedBook.user_id == current_user.id)
        .all()
    ):
        if i.book_id not in book_id:
            book_id.add(i.book_id)
            not_rated.append(
                {
                    "book_id": i.book_id,
                    "book_name": i.book.name,
                    "section_name": i.book.section.name,
                    "author_name": i.book.author,
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
            j.lower().replace("this field", i)
            for i in form.errors
            for j in form.errors[i]
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
        return '"The rating is successfully created."'
    else:
        errors = [
            j.lower().replace("this field", i)
            for i in form.errors
            for j in form.errors[i]
        ]
        abort(400, errors)


@app.route("/user/ratings/delete/<int:id>", methods=["DELETE"])
# caching
@roles_required("User")
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
