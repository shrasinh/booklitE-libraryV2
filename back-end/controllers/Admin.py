from application.setup import app, bstorage, tstorage, languages, CustomResponse, cache
from application.models import (
    db,
    Users,
    Sections,
    IssuedBook,
    Books,
    PurchasedBook,
    Roles,
)
import os
from flask import abort, request
from application.forms import BookForm, SectionForm, IssueRevokeForm
from controllers.Async import create_csv
from flask_security import roles_required
from datetime import datetime, timedelta
import base64
from time import sleep


@cache.cached(timeout=30, key_prefix="all_sections")
def get_sections():
    return Sections.query.all()


@cache.cached(timeout=60, key_prefix="all_books")
def get_books():
    return Books.query.all()


@cache.cached(timeout=60, key_prefix="all_users")
def get_users():
    return Users.query.all()


@app.route("/admin/dashboard")
@roles_required("Admin")
@cache.cached(timeout=60)
def adminstats():
    user = len(get_users()) - 1
    Members = len(db.session.query(Roles).filter(Roles.name == "Member").first().users)
    Normal_Users = user - Members
    section = len(get_sections())
    book = len(get_books())
    ibook = len(db.session.query(IssuedBook.book_id).all())
    pbook = len(db.session.query(PurchasedBook.book_id).all())
    return {
        "graph": [["Normal users", Normal_Users], ["Members", Members]],
        "user_count": user,
        "section_count": section,
        "book_count": book,
        "purchased_book_count": pbook,
        "issued_book_count": ibook,
    }


@app.route("/admin/sections")
@roles_required("Admin")
def adminsections():
    sections = []
    for s in get_sections():
        sections.append(
            {
                "section_id": s.id,
                "section_name": s.name,
                "description": s.description,
                "created_on": s.date_created,
                "books": [{"book_id": b.id, "book_name": b.name} for b in s.book],
            }
        )
    return {"sections": sections}


@app.route("/admin/sections/create", methods=["POST"])
@roles_required("Admin")
def adminsectioncreate():
    form = SectionForm()
    if form.validate_on_submit():
        row = Sections(
            name=form.name.data,
            description=form.description.data,
        )
        db.session.add(row)
        db.session.commit()
        return '"The section is successfully created."'
    else:
        errors = [
            f"{field} : {error}"
            for field in form.errors
            for error in form.errors[field]
        ]
        abort(400, errors)


@app.route("/admin/sections/edit/<int:id>", methods=["PUT"])
@roles_required("Admin")
def adminsectionedit(id):
    section = db.session.query(Sections).filter(Sections.id == id).first()
    if section:
        form = SectionForm()
        if form.validate_on_submit():
            form.populate_obj(section)
            db.session.commit()
            return '"The section is successfully updated."'
        else:
            errors = [
                f"{field} : {error}"
                for field in form.errors
                for error in form.errors[field]
            ]
            abort(400, errors)
    else:
        abort(404)


@app.route("/admin/sections/delete", methods=["DELETE"])
@roles_required("Admin")
def adminsectiondelete():
    section_ids = request.form.get("section_ids", "").split(",")
    res = {"response": {"errors": []}}
    for id in section_ids:
        section = db.session.query(Sections).filter(Sections.id == id).first()
        if section:
            for book in section.book:
                bookloc = bstorage(book.storage)
                thumbnailloc = tstorage(book.thumbnail)
                if os.path.exists(bookloc):
                    os.remove(bookloc)
                if os.path.exists(thumbnailloc):
                    os.remove(thumbnailloc)
            db.session.delete(section)
            db.session.commit()
        else:
            res["response"]["errors"].append(f"Section with Id {id} does not exist!")
    return res


@app.route("/admin/books")
@roles_required("Admin")
def adminbooks():
    books = []
    sections = [{"section_id": s.id, "section_name": s.name} for s in get_sections()]
    for b in get_books():
        books.append(
            {
                "book_id": b.id,
                "book_name": b.name,
                "no_of_copies_available": b.noofcopies,
                "no_of_issues": len(b.issue),
                "no_of_purchase": len(b.purchase),
                "language": b.language,
                "price": b.price,
                "author": b.author,
                "description": b.content,
                "section": {
                    "section_id": b.section_id,
                    "section_name": b.section.name,
                },
                "currently_issued_by": [
                    {"user_id": i.user_id, "username": i.user.username}
                    for i in b.issue
                    if i.return_status == 0
                ],
                "book_storage": bstorage(stype="retrieval", id=b.id),
                "thumbnail": tstorage(
                    b.thumbnail,
                    stype="retrieval",
                ),
            }
        )
    return {"books": books, "sections": sections, "languages": languages}


@app.route("/admin/books/create", methods=["POST"])
@roles_required("Admin")
def bookcreate():
    form = BookForm()
    form.section_id.choices = [(s.id, s.name) for s in get_sections()]
    if form.validate_on_submit():
        tnail = form.thumbnail.data
        thumbnail = datetime.now().strftime("%Y%m%d%H%M%S") + ".png"
        tnail.save(tstorage(thumbnail))
        book = form.storage.data
        storage = datetime.now().strftime("%Y%m%d%H%M%S") + ".pdf"
        storageloc = bstorage(storage)
        book.save(storageloc)
        row = Books(
            name=form.name.data,
            content=form.content.data,
            noofcopies=form.noofcopies.data,
            author=form.author.data,
            price=form.price.data,
            section_id=form.section_id.data,
            language=form.language.data,
            storage=storage,
            thumbnail=thumbnail,
        )
        db.session.add(row)
        db.session.commit()
        return '"The book is successfully created."'
    else:
        errors = [
            f"{field} : {error}"
            for field in form.errors
            for error in form.errors[field]
        ]
        abort(400, errors)


@app.route("/admin/books/edit/<int:id>", methods=["PUT"])
@roles_required("Admin")
def adminbookdetails(id):
    book = db.session.query(Books).filter(Books.id == id).first()
    if book:
        form = BookForm()
        del form.storage
        del form.thumbnail
        form.section_id.choices = [(s.id, s.name) for s in get_sections()]
        if form.validate_on_submit():
            form.populate_obj(book)
            book.language = form.language.data
            db.session.commit()
            return '"The book is successfully updated."'
        else:
            errors = [
                f"{field} : {error}"
                for field in form.errors
                for error in form.errors[field]
            ]
            abort(400, errors)
    else:
        abort(404)


@app.route("/admin/books/delete", methods=["DELETE"])
@roles_required("Admin")
def adminbookdelete():
    book_ids = request.form.get("book_ids", "").split(",")
    res = {"response": {"errors": []}}
    for id in book_ids:
        book = db.session.query(Books).filter(Books.id == id).first()
        if book:
            bookloc = bstorage(book.storage)
            if os.path.exists(bookloc):
                os.remove(bookloc)
            thumbnailloc = tstorage(book.thumbnail)
            if os.path.exists(thumbnailloc):
                os.remove(thumbnailloc)
            db.session.delete(book)
            db.session.commit()
        else:
            res["response"]["errors"].append(f"Section with Id {id} does not exist!")
    return res


@app.route("/admin/users")
@roles_required("Admin")
def adminusers():
    users = []
    books = {b.id: b.name for b in get_books() if b.noofcopies > 0}
    for u in get_users():
        if not u.has_role("Admin"):
            users.append(
                {
                    "user_id": u.id,
                    "username": u.username,
                    "no_of_issues": len(u.issue),
                    "no_of_purchase": len(u.purchase),
                    "roles": "Member" if u.has_role("Member") else "Normal",
                    "issue_limit": 10 if u.has_role("Member") else 5,
                    "currently_issued_books": [
                        {
                            "book_id": i.book_id,
                            "book_name": i.book.name,
                            "return_date": i.return_date,
                        }
                        for i in u.issue
                        if i.return_status == 0
                    ],
                }
            )

    return {"users": users, "books": books}


@app.route("/admin/users/<int:id>", methods=["PUT"])
@roles_required("Admin")
def adminusersissuerevoke(id):
    u = db.session.query(Users).filter(Users.id == id).first()
    if u.has_role("Admin"):
        abort(400, "You can not issue books to the admin.")
    elif u:
        form = IssueRevokeForm()
        form.revoke.choices = [
            (i.book_id, i.book.name)
            for i in db.session.query(IssuedBook)
            .filter(IssuedBook.user_id == id, IssuedBook.return_status == 0)
            .all()
        ]
        form.issue.choices = [
            (i.id, i.name)
            for i in db.session.query(Books)
            .filter(
                Books.id.not_in(
                    [
                        r[0]
                        for r in db.session.query(IssuedBook.book_id)
                        .filter(
                            IssuedBook.user_id == id,
                            IssuedBook.return_status == 0,
                        )
                        .all()
                    ]
                )
            )
            .all()
        ]
        if not form.issue.choices:
            del form.issue
        if not form.revoke.choices:
            del form.revoke
        if form.validate_on_submit():
            return_date = 14 if u.has_role("Member") else 7
            book_limit = 10 if return_date == 7 else 5
            if (
                form.issue
                and form.revoke
                and len(form.revoke.choices)
                - len(form.revoke.data)
                + len(form.issue.data)
                > book_limit
            ) or (form.issue and not form.revoke and len(form.issue.data) > book_limit):
                abort(
                    400,
                    f"The user can not have access to more than {book_limit} issued book at any time.",
                )
            else:
                res = {"response": {"errors": []}}
                if form.revoke:
                    for i in form.revoke.data:
                        issue = (
                            db.session.query(IssuedBook)
                            .filter(
                                IssuedBook.user_id == id,
                                IssuedBook.book_id == i,
                                IssuedBook.return_status == 0,
                            )
                            .first()
                        )
                        issue.book.noofcopies += 1
                        issue.return_status = 1
                        issue.return_date = datetime.now()
                if form.issue:
                    for i in form.issue.data:
                        b = db.session.query(Books).filter(Books.id == i).first()
                        if b.noofcopies > 0:
                            db.session.add(
                                IssuedBook(
                                    user_id=id,
                                    book_id=i,
                                    return_date=datetime.now()
                                    + timedelta(days=return_date),
                                )
                            )
                            b.noofcopies -= 1
                        else:
                            res["response"]["errors"].append(
                                f"{b.name} could not be issued as the number of copies available for issue is 0."
                            )
                db.session.commit()
                res["no_of_issues"] = len(u.issue)
                res["currently_issued_books"] = [
                    {
                        "book_id": i.book_id,
                        "book_name": i.book.name,
                        "return_date": i.return_date,
                    }
                    for i in u.issue
                    if i.return_status == 0
                ]
                return res
        else:
            errors = [
                f"{field} : {error}"
                for field in form.errors
                for error in form.errors[field]
            ]
            abort(400, errors)

    else:
        abort(404)


@app.route("/admin/export")
@roles_required("Admin")
def export():
    etype = request.args.get("etype", "section")
    task = create_csv.apply_async(args=[etype])
    return {"task_id": task.id}


@app.route("/admin/export/notify/<id>")
@roles_required("Admin")
def notify(id):
    def eventStream():
        while True:
            task = create_csv.AsyncResult(id)
            if task.state == "FAILURE":
                return "data:Task failed to be completed!"
            elif task.state == "SUCCESS":
                with open(f"files/reports/{task.get()['result']}", "rb") as csv_file:
                    csv_data = csv_file.read()
                    encoded_csv = base64.b64encode(csv_data).decode("utf-8")
                os.remove(f"files/reports/{task.get()['result']}")
                return f"data:{encoded_csv}\n\n"
            sleep(1)

    return CustomResponse(eventStream(), mimetype="text/event-stream")
