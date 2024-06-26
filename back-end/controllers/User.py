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
from flask import request, abort
from flask_security import current_user
from application.forms import RatingForm, PaymentDetailsForm
from datetime import datetime, timedelta


@app.route("/user/dashboard")
def userdashboard():
    if current_user.is_authenticated:
        if current_user.has_role("User"):
            ibook = db.session.query(IssuedBook).filter(
                IssuedBook.user_id == current_user.id
            )
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
        else:
            abort(403)
    else:
        abort(401)


@app.route("/paymentdetails", methods=["PUT"])
def paymentdetails():
    if current_user.is_authenticated:
        if current_user.has_role("User"):
            p = current_user.payment
            form = PaymentDetailsForm(request.form)
            if form.validate():
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
                return 204
            else:
                print(form.errors)
                abort(400, "invalidate")
        else:
            abort(403)
    else:
        abort(401)


@app.route("/user/confirmation/delete", methods=["DELETE"])
def userconfirmdelete():
    if current_user.is_authenticated:
        if current_user.has_role("User"):
            app.security.datastore.delete_user(current_user)
            db.session.commit()
            return 204
        else:
            abort(403)
    else:
        abort(401)


@app.route("/membership")
def member():
    if current_user.is_authenticated:
        if current_user.has_role("User") and not current_user.has_role("Member"):
            if not current_user.payment:
                abort(400, "Enter the payment details before purchasing.")
            elif cardexpired(current_user.payment):
                abort(400, "Your card has expired. Update your payment details.")
            else:
                app.security.datastore.add_role_to_user(current_user, "Member")
                db.session.commit()
                return 201
        else:
            abort(403)
    else:
        abort(401)


@app.route("/book/issue/<int:id>")
def bookissue(id):
    if current_user.is_authenticated:
        if current_user.has_role("User"):
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
                        return 201
                    else:
                        abort(
                            400, "You exceed the issue limit. Try to return some books."
                        )
                else:
                    abort(
                        400,
                        """There is no more copies of the book. Wait for someone to return the book.
                    Else You can purchase the book to get unlimited access.""",
                    )
            else:
                abort(404)
        else:
            abort(403)
    else:
        abort(401)


@app.route("/book/purchase/<int:id>")
def bookpurchase(id):
    if current_user.is_authenticated:
        if current_user.has_role("User"):
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
                    return 201
            else:
                abort(404)
        else:
            abort(403)
    else:
        abort(401)


@app.route("/user/issuedbooks")
def issue():
    if current_user.is_authenticated:
        if current_user.has_role("User"):
            issues = []
            for i in (
                db.session.query(IssuedBook)
                .filter(IssuedBook.user_id == current_user.id)
                .all()
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
                            bstorage(i.book.storage) if i.return_status == 0 else ""
                        ),
                    }
                )
            return {"issues": issues}, 200
        else:
            abort(403)
    else:
        abort(401)


@app.route("/user/issuedbooks/return/<int:id>")
def returnbook(id):
    if current_user.is_authenticated:
        if current_user.has_role("User"):
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
                return 201
            else:
                abort(400, "You have not yet issued the book.")
        else:
            abort(403)
    else:
        abort(401)


@app.route("/user/purchasedbooks")
def purchase():
    if current_user.is_authenticated:
        if current_user.has_role("User"):
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
                        "storage": bstorage(p.book.storage),
                    }
                )
            return {"purchases": purchases}
        else:
            abort(403)
    else:
        abort(401)


@app.route("/user/ratings")
def rating():
    if current_user.is_authenticated:
        if current_user.has_role("User"):
            rated = []
            not_rated = []
            book_id = set()
            for r in (
                db.session.query(Ratings)
                .filter(Ratings.user_id == current_user.id)
                .all()
            ):
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
        else:
            abort(403)
    else:
        abort(401)


@app.route("/user/ratings/edit/<int:id>", methods=["PUT"])
def ratingedit(id):
    if current_user.is_authenticated:
        if current_user.has_role("User"):
            userrating = (
                db.session.query(Ratings)
                .filter(Ratings.user_id == current_user.id, Ratings.id == id)
                .first()
            )
            if not userrating:
                abort(400, "You have not rated the book.")
            form = RatingForm(request.form)
            if form.validate():
                form.populate_obj(userrating)
                db.session.commit()
                return 204
            else:
                print(form.errors)
                abort(400, "invalidate")
        else:
            abort(403)
    else:
        abort(401)


@app.route("/user/ratings/create/<int:book_id>", methods=["POST"])
def ratingcreate(book_id):
    if current_user.is_authenticated:
        if current_user.has_role("User"):
            userrating = (
                db.session.query(Ratings)
                .filter(Ratings.user_id == current_user.id, Ratings.book_id == book_id)
                .first()
            )
            if userrating:
                abort(400, "You already rated the book!!Try to update it.")
            ibook = (
                db.session.query(IssuedBook)
                .filter(
                    IssuedBook.user_id == current_user.id, IssuedBook.book_id == book_id
                )
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
            form = RatingForm(request.form)
            if form.validate():
                row = Ratings(
                    user_id=current_user.id,
                    book_id=book_id,
                    rating=form.rating.data,
                    feedback=form.feedback.data,
                )
                db.session.add(row)
                db.session.commit()
                return 201
        else:
            abort(403)
    else:
        abort(401)


@app.route("/user/ratings/delete/<int:id>", methods=["DELETE"])
def ratingdelete(id):
    if current_user.is_authenticated:
        if current_user.has_role("User"):
            userrating = (
                db.session.query(Ratings)
                .filter(Ratings.user_id == current_user.id, Ratings.id == id)
                .first()
            )
            if userrating:
                db.session.delete(userrating)
                db.session.commit()
                return 204
            else:
                abort(400, "You have not rated for the book!")
        else:
            abort(403)
    else:
        abort(401)
