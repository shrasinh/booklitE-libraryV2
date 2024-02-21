from application.setup import app,issuedbooktime,cardexpired,bstorage
from application.models import db,Books,IssuedBook,PurchasedBook,Ratings
from flask import redirect, render_template,flash,send_file,request
from flask_security import auth_required,roles_required,current_user,roles_accepted
from application.forms import RatingForm
from datetime import datetime,timedelta

@app.route('/book/<int:id>/issue')
@auth_required()
@roles_required("User")
@issuedbooktime
def bookissue(id):
    bookdetails=db.session.query(Books).filter(Books.id==id).first()
    issuedbook=db.session.query(IssuedBook).filter(IssuedBook.user_id==current_user.id, IssuedBook.return_status==0).all()
    ibook=db.session.query(IssuedBook).filter(IssuedBook.user_id==current_user.id,IssuedBook.book_id==id, IssuedBook.return_status==0).all()
    if ibook:
        flash("You have already issued the book!! You can again re-issue after you return the book.")
    elif bookdetails.noofcopies>0:
        bookdetails.noofcopies-=1
        insert=False
        if current_user.has_role("Member"):
            if len(issuedbook)<=10:
                row=IssuedBook(return_date=datetime.now()+timedelta(days=14),book_id=bookdetails.id,user_id=current_user.id)
                insert=True
        else:
            if len(issuedbook)<=5:
                row=IssuedBook(return_date=datetime.now()+timedelta(days=7),book_id=bookdetails.id,user_id=current_user.id)
                insert=True
        if insert:
            db.session.add(row)
            db.session.commit()
            flash("The book is issued.")
        else:
            flash("You exceed the issue limit. Try to return some books.")
    else:
        flash("""There is no more copies of the book. Wait for someone to return the book.
        Else You can purchase the book to get unlimited access.""")
        return redirect("/")   
    return redirect("/user/issuedbooks")

@app.route('/book/<int:id>/purchase')
@auth_required()
@roles_required("User")
def bookpurchase(id):
    bookdetails=db.session.query(Books).filter(Books.id==id).first()
    pbook=db.session.query(PurchasedBook).filter(PurchasedBook.user_id==current_user.id,PurchasedBook.book_id==id).all()
    if pbook:
        flash("You have already purchased the book. You can not purchase it more than once.")
        return redirect("/user/purchasedbooks")
    elif not current_user.payment:
        flash("Enter the payment details.")
    elif cardexpired(current_user.payment):
        flash("Your card has expired. Update your payment details.")
    else:
        row=PurchasedBook(price=bookdetails.price,book_id=bookdetails.id,user_id=current_user.id)
        db.session.add(row)
        db.session.commit()
        flash("The book is purchased.")
        return redirect("/user/purchasedbooks")
    return redirect("/accountdetails")

@app.route('/user/confirmation/delete')
@auth_required()
@roles_required('User')
def userconfirmdelete():
    a=request.args.get("choice")
    if a=="yes":
        db.session.delete(current_user)
        db.session.commit()
        flash("Your account is successfully deleted.")
        return redirect("/")
    return render_template("user/delete.html")

@app.route('/membership')
@auth_required()
@roles_accepted("User")
def member():
    if not current_user.payment:
        flash("Enter the payment details.")
    elif cardexpired(current_user.payment):
        flash("Your card has expired. Update your payment details.")
    else:
        app.security.datastore.add_role_to_user(current_user,"Member")
        db.session.commit()
        flash("Congrats!! Now you are a subscribed member of the library!")
    return redirect("/accountdetails")

@app.route('/user/issuedbooks')
@auth_required()
@roles_required("User")
@issuedbooktime
def issue():
    issuedetails=db.session.query(IssuedBook).filter(IssuedBook.user_id==current_user.id).all()
    cissue,pissue=[],[]
    for book in issuedetails:
        if book.return_status==1:
            pissue.append(book)
        else:
            cissue.append(book)
    return render_template('user/issue.html',cissue=cissue,pissue=pissue)

@app.route('/user/issuedbooks/return/<int:id>')
@auth_required()
@roles_required("User")
@issuedbooktime
def returnbook(id):
    issuedetails=db.session.query(IssuedBook).filter(IssuedBook.user_id==current_user.id,IssuedBook.return_status==0,IssuedBook.book_id==id).first()
    if issuedetails:
        issuedetails.return_status=1
        issuedetails.book.noofcopies+=1
        issuedetails.return_date=datetime.now()
        db.session.commit()
        flash("You have successfully returned the book.")
    else:
        flash("You have not yet issued the book.")
    return redirect("/user/issuedbooks")

@app.route('/user/issuedbooks/view/<int:id>')
@auth_required()
@roles_required("User")
@issuedbooktime
def issueview(id):
    ibook=db.session.query(IssuedBook).filter(IssuedBook.user_id==current_user.id,IssuedBook.return_status==0,IssuedBook.book_id==id).first()
    if ibook:
        return render_template("bookview.html",name=ibook.book.name,file=ibook.book.storage,sound=ibook.book.sound)
    else:
        flash("You have not currently issued the book. Issue it first to view the book.")
    return redirect("/user/issuedbooks")

@app.route('/user/purchasedbooks')
@auth_required()
@roles_required("User")
def purchase():
    purchasedetails=db.session.query(PurchasedBook).filter(PurchasedBook.user_id==current_user.id).all()
    return render_template('user/purchase.html',pdetails=purchasedetails)

@app.route('/user/purchasedbooks/download/<id>')
@auth_required()
@roles_required("User")
def purchasedownload(id):
    pbook=db.session.query(PurchasedBook).filter(PurchasedBook.user_id==current_user.id, PurchasedBook.book_id==id).first()
    if pbook:
        flash("You have successfully downloaded the file.")
        return send_file(bstorage(pbook.book.storage),as_attachment=True,download_name=pbook.book.name+".pdf",mimetype="application/pdf")
    else:
        flash("You have not purchased the book.")
        return redirect('/user/purchasedbooks')

@app.route('/user/rating')
@auth_required()
@roles_required("User")
def rating():
    userrating=db.session.query(Ratings).filter(Ratings.user_id==current_user.id).all()
    books=db.session.query(Books).all()
    ibook=db.session.query(IssuedBook.book_id).filter(IssuedBook.user_id==current_user.id).all()
    pbook=db.session.query(PurchasedBook.book_id).filter(PurchasedBook.user_id==current_user.id).all()
    ratedbookid,id_to_book=set(),{}
    for u in userrating:
        ratedbookid.add(u.book_id)
    notrated={i[0] for i in pbook+ibook if not i[0] in ratedbookid}
    for bk in books:
        id_to_book[bk.id]=bk
    return render_template('user/rating.html',urating=userrating,notrated=notrated,book=id_to_book)

@app.route('/user/rating/<int:id>',methods=["GET","POST"])
@auth_required()
@roles_required("User")
def ratingview(id):
    userrating=db.session.query(Ratings).filter(Ratings.user_id==current_user.id,Ratings.id==id).first()
    if not userrating:
        flash("You have not rated the book.")
        return redirect("/user/rating")
    form=RatingForm(obj=userrating)
    if form.validate_on_submit():
        form.populate_obj(userrating)
        db.session.commit()
        flash("The rating is successfully updated.")
        return redirect("/user/rating")
    return render_template("user/ratingupdatecreate.html",form=form,book=userrating.book)
    
@app.route('/user/rating/<int:book_id>/create',methods=["GET","POST"])
@auth_required()
@roles_required('User')
def ratingcreate(book_id):
    userrating=db.session.query(Ratings).filter(Ratings.user_id==current_user.id,Ratings.book_id==book_id).first()
    if userrating:
        flash("You already rated the book!!Try to update it.")
        return redirect(f"/user/rating/{userrating.id}")
    ibook=db.session.query(IssuedBook).filter(IssuedBook.user_id==current_user.id,IssuedBook.book_id==book_id).first()
    pbook=db.session.query(PurchasedBook).filter(PurchasedBook.user_id==current_user.id,PurchasedBook.book_id==book_id).first()
    if not ibook and not pbook:
        flash("You have not purchased or issued the book.")
        return redirect("/user/rating")
    if ibook:
        book=ibook.book 
    if pbook.book:
        book=pbook.book 
    form=RatingForm()
    if form.validate_on_submit():
        row=Ratings(user_id=current_user.id,book_id=book_id,rating=form.rating.data,feedback=form.feedback.data)
        db.session.add(row)
        db.session.commit()
        flash("The book rating is successfully submitted.")
        return redirect("/user/rating")
    return render_template("user/ratingupdatecreate.html",form=form,book=book,word="Giving")
    
@app.route('/user/rating/<int:id>/delete')
@auth_required()
@roles_required('User')
def ratingdelete(id):
    userrating=db.session.query(Ratings).filter(Ratings.user_id==current_user.id,Ratings.id==id).first()
    if userrating:
        db.session.delete(userrating)
        db.session.commit()
        flash("The rating is sucessfully deleted.")
    else:
        flash("You have not rated for the book!")
    return redirect("/user/rating")