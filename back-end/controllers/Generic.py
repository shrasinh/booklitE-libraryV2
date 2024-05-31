from application.setup import app,issuedbooktime
from application.models import db,Books,Ratings,Sections,PaymentDetails
from application.forms import PaymentDetailsForm
from flask import redirect, render_template,flash,request
from flask_security import auth_required,current_user
from application.forms import PaymentDetailsForm

@app.route('/')
def home():
    section=Sections.query.order_by(Sections.date_created.desc()).all()
    ratedbooks=db.session.query(db.func.avg(Ratings.rating),Ratings.book_id).group_by(Ratings.book_id).all()
    d={}
    for book in ratedbooks:
        d[book[1]]=book[0]
    return render_template('index.html',sections=section,rating=d)

@app.route('/policies')
def policies():
    return render_template('policies.html')

@app.route('/user/roleassign')
@auth_required()
def userroleassign():
    if current_user.roles==[]:
        app.security.datastore.add_role_to_user(current_user,"User")
    db.session.commit()
    flash("You are successfully logged in.")
    return redirect("/")

@app.route('/post/logout')
def postlogout():
    if current_user and current_user.is_authenticated:
        return redirect("/logout")
    flash("You are successfully logged out.")
    return redirect("/")

@app.route("/random")
def randombook():
    book=db.session.query(Books).order_by(db.func.random()).first()
    if book:
        return redirect(f"/book/{book.id}")
    flash("No books are currently present in the system.")
    return redirect("/")

@app.route('/book/<int:id>')
@issuedbooktime
def book(id):
    bookdetails=db.session.query(Books).filter(Books.id==id).first()
    rating=db.session.query(db.func.avg(Ratings.rating).label('average')).filter(Ratings.book_id==id).first()
    ratingc=db.session.query(db.func.count(Ratings.rating).label('count'),Ratings.rating).filter(Ratings.book_id==id).group_by(Ratings.rating).all()
    rate={i:0 for i in range(1,6)}
    if not bookdetails:
        flash("The book does not exists.")
        return redirect("/")
    total=0
    for c,r in ratingc:
        rate[r]=c
        total+=c
    if total:
        c={r:(rate[r]/total)*100 for r in rate}
    else:
        c=0
    return render_template('book.html',bookdetails=bookdetails,avg=rating,count=c)

@app.route('/search')
def textsearch():
    bybook=request.args.get("bybook","").strip()
    byauthor=request.args.get("byauthor","").strip()
    bysection=request.args.get("bysection","").strip()
    matchb=matchs=""
    if not byauthor and not bysection and bybook:
        matchb=db.session.query(Books).filter(Books.name.icontains(bybook,autoescape=True)).all()
    elif not byauthor and bysection and not bybook:
        matchs=db.session.query(Sections.name.label("sname"),Books.id.label("bid"),
                                Books.name.label("bname"),Books.author).filter(Sections.id == Books.section_id,
                                                       Sections.name.icontains(bysection,autoescape=True)
                                                       ).all()
    elif byauthor and not bysection and not bybook:
        matchb=db.session.query(Books).filter(Books.author.icontains(byauthor,autoescape=True)).all()
    elif not bysection and bybook and byauthor:
        matchb=db.session.query(Books).filter(Books.author.icontains(byauthor,autoescape=True),
                                              Books.name.icontains(bybook,autoescape=True)).all()
    elif bysection and not bybook and byauthor:
        matchs=db.session.query(Sections.name.label("sname"),Books.id.label("bid"),
                                Books.name.label("bname"),Books.author).filter(Sections.id == Books.section_id,
                                                       Sections.name.icontains(bysection,autoescape=True),
                                                       Books.author.icontains(byauthor,autoescape=True),
                                                       ).all()
    elif bysection and bybook and not byauthor:
        matchs=db.session.query(Sections.name.label("sname"),Books.id.label("bid"),
                                Books.name.label("bname"),Books.author).filter(Sections.id == Books.section_id,
                                                       Sections.name.icontains(bysection,autoescape=True),
                                                       Books.name.icontains(bybook,autoescape=True)
                                                       ).all()
    elif bysection and bybook and byauthor:
        matchs=db.session.query(Sections.name.label("sname"),Books.id.label("bid"),
                                Books.name.label("bname"),Books.author).filter(Sections.id == Books.section_id,
                                                       Sections.name.icontains(bysection,autoescape=True),
                                                       Books.author.icontains(byauthor,autoescape=True),
                                                       Books.name.icontains(bybook,autoescape=True)
                                                       ).all()
    return render_template('search.html',mb=matchb,ms=matchs,book=bybook,section=bysection,author=byauthor)

@app.route('/accountdetails',methods=["GET","POST"])
@auth_required()
def account():
    p=current_user.payment
    if p:
        form=PaymentDetailsForm(obj=p)
    else:
        form=PaymentDetailsForm()
    if form.validate_on_submit():
        if p:
            form.populate_obj(p)
            flash("Payment details successfully updated.")
        else:
            row=PaymentDetails(cardno=form.cardno.data,expirydate=form.expirydate.data,cardname=form.cardname.data,user_id=current_user.id)
            db.session.add(row)
            flash("Payment details successfully added.")
        db.session.commit()
        return redirect("/accountdetails")
    return render_template('account.html',form=form)