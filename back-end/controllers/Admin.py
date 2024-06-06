from application.setup import app,issuedbooktime
from application.models import db,Users,Sections,IssuedBook,Books,PurchasedBook
from flask import redirect, render_template,flash
from flask_security import auth_required,roles_required
from application.forms import BookForm,SectionForm,IssueRevokeForm
from requests import get,post,put,delete
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime,timedelta

matplotlib.use("Agg")

@app.route('/admin/dashboard')
@auth_required()
@roles_required("Admin")
def dashboard():
    b=get("http://localhost:5500/api/graph")
    plt.bar(b.json()[0],b.json()[1])
    plt.title("Number of Normal users vs Members")
    plt.ylabel("Numbers")
    plt.savefig("static/graph.png")
    user=len(db.session.query(Users.id).all())-1
    section=len(db.session.query(Sections.id).all())
    book=len(db.session.query(Books.id).all())
    ibook=len(db.session.query(IssuedBook.book_id).all())
    pbook=len(db.session.query(PurchasedBook.book_id).all())
    return render_template('admin/dashboard.html',user=user,section=section,book=book,ibook=ibook,pbook=pbook)

@app.route('/admin/books')
@auth_required()
@roles_required('Admin')
@issuedbooktime
def adminbooks():
    book=db.session.query(Books).all()
    ibook=db.session.query(IssuedBook.book_id,db.func.count(IssuedBook.book_id)).filter(IssuedBook.return_status==0).group_by(IssuedBook.book_id).all()
    cissue={}
    for i,b in ibook:
        cissue[i]=b
    return render_template('admin/books.html',book=book,cissue=cissue)

@app.route('/admin/books/create', methods=['GET', 'POST'])
@auth_required()
@roles_required('Admin')
def bookcreate():
    form = BookForm()
    form.section_id.choices = [(s.id, s.name) for s in Sections.query.order_by(Sections.name).all()]
    if form.validate_on_submit():
        post(f"http://localhost:5500/api/book",data={"name":form.name.data,"content":form.content.data,
                                                              "noofcopies":form.noofcopies.data,"author":form.author.data,
                                                              "price":form.price.data,"section_id":form.section_id.data,
                                                              "language":form.language.data},files={"storage":form.storage.data,"thumbnail":form.thumbnail.data})
        flash("The Book is successfully added.")
        return redirect("/admin/books")
    return render_template('admin/bookscreate.html', form=form)

@app.route('/admin/books/<int:id>',methods=["GET","POST"])
@auth_required()
@roles_required('Admin')
@issuedbooktime
def adminbookdetails(id):
    book=get(f"http://localhost:5500/api/book/{id}")
    if book.ok:
        i=db.session.query(IssuedBook).filter(IssuedBook.book_id==id,IssuedBook.return_status==0).all()
        form = BookForm(data=book.json())
        del form.storage; del form.thumbnail; del form.language
        form.section_id.choices = [(s.id, s.name) for s in Sections.query.order_by(Sections.name).all()]
        if form.validate_on_submit():
            put(f"http://localhost:5500/api/book/{id}",data={"name":form.name.data,"content":form.content.data,
                                                                      "noofcopies":form.noofcopies.data,"author":form.author.data,
                                                                      "price":form.price.data,"section_id":form.section_id.data})
            flash("The Book is successfully updated.")
            return redirect("/admin/books")
        return render_template("admin/bookupdate.html",issue=i,form=form,id=id)
    flash("Book not found!")
    return redirect("/admin/books")

@app.route('/admin/books/view/<int:id>')
@auth_required()
@roles_required('Admin')
def adminbookview(id):
    b=get(f"http://localhost:5500/api/book/{id}")
    if b.ok:
        book=b.json()
        return render_template("bookview.html",name=book["name"],file=book["storage"],sound=book["sound"])
    flash("Book not found!")
    return redirect("/admin/books")

@app.route('/admin/books/<int:id>/delete')
@auth_required()
@roles_required('Admin')
def adminbookdelete(id): 
    book=delete(f"http://localhost:5500/api/book/{id}")
    if book.ok:
        flash("The book is successfully deleted.")
    else:
        flash("Book not found!")
    return redirect("/admin/books")

@app.route('/admin/sections')
@auth_required()
@roles_required('Admin')
def adminsections():
    section=Sections.query.all() 
    return render_template('admin/sections.html',sections=section)

@app.route('/admin/sections/create',methods=["GET","POST"])
@auth_required()
@roles_required('Admin')
def adminsectioncreate():
    form = SectionForm()
    if form.validate_on_submit():
        post(f"http://localhost:5500/api/section",data={"name":form.name.data,"description":form.description.data})
        flash("Section successfully created!!")
        return redirect('/admin/sections')
    return render_template('admin/sectionscreate.html',form=form)

@app.route('/admin/sections/<int:id>',methods=["GET","POST"])
@auth_required()
@roles_required('Admin')
def adminsectiondetails(id):
    s=get(f"http://localhost:5500/api/section/{id}")
    if s.ok:
        form = SectionForm(data=s.json())
        b=db.session.query(Books).filter(Books.section_id==id).all()
        if form.validate_on_submit():
            put(f"http://localhost:5500/api/section/{id}",data={"name":form.name.data,"description":form.description.data})
            flash("Section successfully updated!!")
            return redirect('/admin/sections')
        return render_template('admin/sectionupdate.html',form=form,book=b)
    flash("Section does not exist!!")
    return redirect("/admin/sections")
    
@app.route('/admin/sections/<int:id>/delete')
@auth_required()
@roles_required('Admin')
def adminsectiondelete(id):
    s=delete(f"http://localhost:5500/api/section/{id}")
    if s.ok:
        flash("The section is successfully deleted.")
    else:
        flash("Section not found!")
    return redirect("/admin/sections")

@app.route('/admin/users')
@auth_required()
@roles_required('Admin')
@issuedbooktime
def adminusers():
    user=Users.query.all()
    ibook=db.session.query(IssuedBook.user_id,db.func.count(IssuedBook.book_id)).filter(IssuedBook.return_status==0).group_by(IssuedBook.user_id).all()
    cissue={}
    for i,b in ibook:
        cissue[i]=b
    return render_template('admin/users.html',user=user,cissue=cissue)

@app.route('/admin/users/<int:id>',methods=["GET","POST"])
@auth_required()
@roles_required('Admin')
@issuedbooktime
def adminusersdetails(id):
    u=db.session.query(Users).filter(Users.id==id).first()
    if u.has_role("Admin"):
        flash("You can not issue book to the admin.")
    elif u:
        form=IssueRevokeForm()
        form.revoke.choices=[(i.id,i.book.name) for i in db.session.query(IssuedBook).filter(IssuedBook.user_id==id,
                                                                                             IssuedBook.return_status==0).all()]
        form.issue.choices=[(i.id,i.name) for i in db.session.query(Books).filter(Books.id.not_in([r[0] for 
                                                                                                   r in db.session.query(IssuedBook.book_id).filter(IssuedBook.user_id==id,
                                                                                                   IssuedBook.return_status==0).all()])).all()]
        if not form.issue.choices:
            del form.issue
        if not form.revoke.choices:
            del form.revoke
        if form.validate_on_submit():
            return_date= 14 if u.has_role("Member") else 7
            book_limit= 10 if return_date==7 else 5
            if (form.issue and form.revoke and len(form.revoke.choices)-len(form.revoke.data)+len(form.issue.data)>book_limit) or (form.issue and not form.revoke and len(form.issue.data)>book_limit):
                flash(f'The user can not have access to more than {book_limit} issued book at any time.')
            else:
                if form.revoke:
                    for i in form.revoke.data:
                        issue=db.session.query(IssuedBook).filter(IssuedBook.id==i).first()
                        issue.book.noofcopies+=1
                        issue.return_status=1
                        issue.return_date=datetime.now()
                        flash(f"The access to {issue.book.name} is successfully revoked from the user.")
                if form.issue:
                    for i in form.issue.data:
                        issue=db.session.query(IssuedBook).filter(IssuedBook.user_id==id,IssuedBook.book_id==i,IssuedBook.return_status==0).first()
                        b=db.session.query(Books).filter(Books.id==i).first()
                        if b.noofcopies>0:
                            db.session.add(IssuedBook(user_id=id,book_id=i,return_date=datetime.now()+timedelta(days=return_date)))
                            b.noofcopies-=1
                            flash(f"{b.name} is successfully issued to the user.")
                        else:
                            flash(f"{b.name} could not be issued as the number of copies available for issue is 0.")
                db.session.commit()
            return redirect("/admin/users")
        return render_template('admin/usersir.html',u=u,form=form)
    else:
        flash("User not found!")
    return redirect("/admin/users")
