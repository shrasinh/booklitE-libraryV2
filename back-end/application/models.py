from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from flask_security import UserMixin, RoleMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

db = SQLAlchemy(metadata=MetaData(naming_convention=convention))

UsersRoles = db.Table(
    "UsersRoles",
    db.Column("id", db.Integer, primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id")),
)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean)
    last_login_at = db.Column(db.DateTime)
    current_login_at = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String)
    current_login_ip = db.Column(db.String)
    login_count = db.Column(db.Integer)
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)
    membership_date = db.Column(db.DateTime, nullable=True)
    daily_remainders = db.Column(db.Boolean, default=0, nullable=False)
    roles = db.relationship("Roles", secondary="UsersRoles", back_populates="users")
    rating = db.relationship("Ratings", cascade="all,delete", back_populates="user")
    issue = db.relationship("IssuedBook", cascade="all,delete", back_populates="user")
    purchase = db.relationship(
        "PurchasedBook", cascade="all,delete", back_populates="user"
    )
    payment = db.relationship(
        "PaymentDetails", uselist=False, cascade="all,delete", back_populates="user"
    )


class Sections(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    book = db.relationship("Books", cascade="all,delete", back_populates="section")


class Books(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    noofcopies = db.Column(db.Integer, nullable=False)
    author = db.Column(db.String, nullable=False)
    price = db.Column(
        db.Float(precision=2, asdecimal=True, decimal_return_scale=2), nullable=False
    )
    section_id = db.Column(db.Integer, db.ForeignKey("sections.id"), nullable=False)
    language = db.Column(db.String, nullable=False)
    storage = db.Column(db.String, nullable=False)
    thumbnail = db.Column(db.String, nullable=False)
    section = db.relationship("Sections", uselist=False, back_populates="book")
    rating = db.relationship("Ratings", cascade="all,delete", back_populates="book")
    issue = db.relationship("IssuedBook", cascade="all,delete", back_populates="book")
    purchase = db.relationship(
        "PurchasedBook", cascade="all,delete", back_populates="book"
    )


class Roles(db.Model, RoleMixin):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True)
    description = db.Column(db.String, nullable=False)
    users = db.relationship("Users", secondary="UsersRoles", back_populates="roles")


class PaymentDetails(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    cardno = db.Column(db.Integer, nullable=False)
    cardname = db.Column(db.String, nullable=False)
    expirydate = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False
    )
    user = db.relationship("Users", uselist=False, back_populates="payment")


class IssuedBook(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    issue_date = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    return_date = db.Column(db.DateTime, nullable=False)
    return_status = db.Column(db.Boolean, default=0, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("Users", uselist=False, back_populates="issue")
    book = db.relationship("Books", uselist=False, back_populates="issue")


class PurchasedBook(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    purchase_date = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    price = db.Column(
        db.Float(precision=2, asdecimal=True, decimal_return_scale=2), nullable=False
    )
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("Users", uselist=False, back_populates="purchase")
    book = db.relationship("Books", uselist=False, back_populates="purchase")


class Ratings(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    rating_date = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    feedback = db.Column(db.Text)
    __table_args__ = (db.UniqueConstraint("user_id", "book_id"),)
    user = db.relationship("Users", uselist=False, back_populates="rating")
    book = db.relationship("Books", uselist=False, back_populates="rating")
