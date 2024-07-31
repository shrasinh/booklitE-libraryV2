from application.setup import celery, db, app, mail
from application.models import (
    IssuedBook,
    Roles,
    Users,
    Sections,
    Books,
    PurchasedBook,
    IssuedBook,
)
from datetime import datetime, timedelta
from flask_mailman import EmailMessage
from celery.schedules import crontab
import pdfkit
import pandas as pd
from dateutil import tz
import os
from flask import render_template


@celery.on_after_finalize.connect
def setup_periodic_tasks(**kwargs):
    celery.add_periodic_task(
        crontab(hour=0, minute=0),
        revoke.s(),
        name="revoke access to overdue books every day",
    )

    celery.add_periodic_task(
        crontab(hour=18, minute=0),
        daily_remainders.s(),
        name="send users remainders to visit app and return the issued books that have return date approaching",
    )

    celery.add_periodic_task(
        crontab(day_of_month=1, hour=7, minute=0),
        monthly_status.s(),
        name="send monthly reports to admin",
    )


@celery.task()
def create_csv(etype):
    details = []
    if etype == "user":
        for u in db.session.query(Users).all():
            if not u.has_role("Admin"):
                details.append(
                    {
                        "user_id": u.id,
                        "username": u.username,
                        "no_of_issues": len(u.issue),
                        "no_of_purchase": len(u.purchase),
                        "roles": "Member" if u.has_role("Member") else "Normal",
                        "issue_limit": 10 if u.has_role("Member") else 5,
                        "no_of_current_issue": [
                            i for i in u.issue if i.return_status == 0
                        ],
                    }
                )
    elif etype == "book":
        for b in db.session.query(Books).all():
            details.append(
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
                    "section_id": b.section_id,
                    "section_name": b.section.name,
                    "no_of_current_issue": len(
                        [i for i in b.issue if i.return_status == 0]
                    ),
                }
            )
    else:
        etype = "section"
        for s in Sections.query.all():
            details.append(
                {
                    "section_id": s.id,
                    "section_name": s.name,
                    "description": s.description,
                    "created_on": s.date_created,
                    "no_of_books_present": len(s.book),
                }
            )
    date = datetime.now().strftime("%d-%m-%Y-%H-%M-%S-%f")
    pd.DataFrame.from_dict(details).to_csv(
        os.path.join("files", "reports", f"{etype}_details_{date}.csv"), index=False
    )
    return {
        "result": f"{etype}_details_{date}.csv",
    }


@celery.task
def revoke():
    with mail.get_connection() as conn:
        emails = []
        ibook = IssuedBook.query.all()
        now = datetime.now()
        for book in ibook:
            if now > book.return_date and book.return_status == 0:
                book.return_status = 1
                book.book.noofcopies += 1
                emails.append(
                    EmailMessage(
                        subject=f"Access for {book.book.name} is revoked",
                        body=f"""Dear {book.user.username}\n\nThis is to inform you that your access to {book.book.name} has been revoked as the access deadline has passed.\n\nIf you want you can again reissue the book by visiting Booklit.\n\nWarm regards,\nBooklit team""",
                        from_email=app.config["MAIL_USERNAME"],
                        to=[book.user.email],
                    )
                )
        db.session.commit()
        if emails:
            conn.send_messages(emails)


@celery.task
def daily_remainders():
    with mail.get_connection() as conn:
        format = "%d-%m-%Y"
        date = datetime.now().strftime(format)

        emails = []
        for user in db.session.query(Users).all():
            if (
                user.has_role("User")
                and user.daily_remainders == 1
                and datetime.strptime(
                    user.current_login_at.replace(tzinfo=tz.tzutc())
                    .astimezone(tz.tzlocal())
                    .strftime(format),
                    format,
                )
                < datetime.strptime(date, format)
            ):
                emails.append(
                    EmailMessage(
                        subject="Remainder to visit Booklit today!!",
                        body=f"""Dear {user.username}\n\nIt seems that you have yet to login to your Booklit account for today. Please make time to visit it.\n\nWarm regards,\nBooklit team""",
                        from_email=app.config["MAIL_USERNAME"],
                        to=[user.email],
                    )
                )
            books = ""
            for issue in user.issue:
                if (
                    issue.return_status == 0
                    and issue.return_date < datetime.now() + timedelta(days=1)
                ):
                    books += issue.book.name + "\n"
            if books:
                emails.append(
                    EmailMessage(
                        subject=f"Remainder to return the issued books",
                        body=f"""Dear {user.username}\n\nThis is to inform you that your access for the following books are soon going to be revoked:\n\n{books}\nYou can return the books before the deadline, else their access will be automatically revoked past deadline.\nIf you want you can again reissue the book by visiting Booklit.\n\nWarm regards,\nBooklit team""",
                        from_email=app.config["MAIL_USERNAME"],
                        to=[user.email],
                    )
                )
        if emails:
            conn.send_messages(emails)


@celery.task
def monthly_status():
    admin_role = db.session.query(Roles).filter(Roles.name == "Admin").first()
    admin = (admin_role.users[0] if admin_role.users else "") if admin_role else ""
    if admin:
        date = (
            datetime.now().replace(day=1) - timedelta(days=1, minutes=0, seconds=0)
        ).strftime("%B, %Y")
        name = f"Monthly report for {date}"
        section_created_total = db.session.query(Sections.date_created).all()
        section_created_this_month = format_date(section_created_total, date)
        book_issued_total = db.session.query(IssuedBook.issue_date).all()
        book_issued_this_month = format_date(book_issued_total, date)
        book_purchased_total = db.session.query(PurchasedBook.purchase_date).all()
        book_purchased_this_month = format_date(book_purchased_total, date)

        html = render_template(
            "monthly.html",
            name=name,
            section_created_this_month=section_created_this_month,
            book_issued_this_month=book_issued_this_month,
            book_purchased_this_month=book_purchased_this_month,
            section_created_total=len(section_created_total),
            book_issued_total=len(book_issued_total),
            book_purchased_total=len(book_purchased_total),
        )
        pdf = pdfkit.from_string(html, css=os.path.join("static", "monthly.css"))

        msg = EmailMessage(
            f"Monthly report for {date}",
            f"""Dear {admin.username}\n\nPlease find the below attached PDF, detailing out the Booklit's performance for {date}.\n\nRegards,\nSystem""",
            from_email=app.config["MAIL_USERNAME"],
            to=[admin.email],
        )
        msg.attach(name, pdf, "application/pdf")
        msg.send()


def format_date(l, date):
    c = 0
    for i in l:
        if i[0].strftime("%B, %Y") == date:
            c += 1
    return c
