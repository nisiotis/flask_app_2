# -*- coding: utf-8 -*-
#!/usr/bin/env python

import g2, os
from flask import Flask, send_file, render_template
from flask import session, redirect, url_for, escape
from flask import request, Response, jsonify
from flask import make_response
from database import engine, db_session
from models import User
from cStringIO import StringIO

from reportlab.rl_config import TTFSearchPath
TTFSearchPath.append('/var/www/flaskapp/flaskapp/static')

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Image, Table
from reportlab.platypus.doctemplate import NextPageTemplate, SimpleDocTemplate
from reportlab.platypus.flowables import PageBreak


app = Flask(__name__)

@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
#    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.route("/")
def index():
    if 'username' in session:
        u = User.query.all()
        return render_template('index.html', users=u, loggeduser=session['username'])
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    ip = "Your ip is " + request.remote_addr
    return render_template('login.html', ipaddress=ip)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route("/name_sort")
def namesort():
    u = User.query.order_by('name asc').all()
    return render_template('index.html', users=u)

@app.route("/email_sort")
def emailsort():
    u = User.query.order_by('email asc').all()
    return render_template('index.html', users=u)

@app.route("/progress_sort")
def progresssort():
    u = User.query.order_by('progress asc').all()
    return render_template('index.html', users=u)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        r = do_save(request.form['name'], 
                    request.form['email'], 
                    request.form['progress'])
        u = User.query.all()
        return render_template('index.html', 
                               users=u, 
                               result=r)
    else:
        u = User.query.all()
        return render_template('add.html', users=u)

def do_save(name, email, progress):
    try:
        if name <> "" and email <> "":
            u = User(name, email, progress)
            db_session.add(u)
            db_session.commit()
            return "Added Successfully"
        else:
            return "Nothing to Add"
    except:
        return "Add Failed"

@app.route('/edit/<int:uid>', methods=['GET', 'POST'])
def edit(uid):
    if request.method == 'POST':
        r = do_update(uid, 
                      request.form['name'],
                      request.form['email'],
                      request.form['progress'])
        u = User.query.all()
        return render_template('index.html',
                               users=u,
                               result = r)
    else:
        u = User.query.get(uid)
        return render_template('edit.html', user=u)

def do_update(uid, name, email, progress):
    try:
        if name <> "" and email <> "":
            u = User.query.filter_by(id=uid).first()
            u.name = name
            u.email = email
            u.progress = progress
            db_session.commit()
            return "%s Updated Successfully" % name
        else:
            return "Nothing to Update"
    except:
        return "Update Failed"

@app.route('/delete/<int:uid>')
def delete(uid):
    try:
        d = User.query.get(uid)
        db_session.query(User).filter(User.id==uid).delete()
        db_session.commit()
        r = "%s Deleted" % d.name
    except:
        r = "Delete Failed"
    u = User.query.all()     
    return render_template('index.html',
                           users=u,
                           result = r)

@app.route("/print/<int:uid>")
def print_rep(uid):
    registerFont(TTFont('DroidSans', 'DroidSans.ttf'))

    pdf = StringIO()

    doc = SimpleDocTemplate(pdf, pagesize=A4)
    elements = []
    style = getSampleStyleSheet()
    style.add(ParagraphStyle(name='Header', alignment=TA_LEFT,
                             fontName='DroidSans',
                             fontSize=14, leading=16))
    style.add(ParagraphStyle(name='Left', alignment=TA_LEFT,
                             fontName='DroidSans',
                             fontSize=12))
    style.add(ParagraphStyle(name='Right', alignment=TA_RIGHT,
                             fontName='DroidSans',
                             fontSize=12))
    if uid == 0:
        elements.append(Paragraph(u'<u>Users List</u>', style['Header']))
        u = User.query.all()     
        for i, o in enumerate(u):
            elements.append(Paragraph(u'%s. %s %s %s' % (i+1, o.name, o.email, o.progress), style['Left']))
    else:
        u = User.query.get(uid)
        elements.append(Paragraph(u'%s %s %s' % (u.name, u.email, u.progress), style['Header']))

    doc.build(elements)
    pdf_file = pdf.getvalue()
    pdf.close()
    response = make_response(pdf_file)

    response.headers['Content-Disposition'] = "attachment; filename='pdf_user.pdf"
    response.mimetype = 'application/pdf'
    return response

@app.route("/stats")
def stats():
    u = User.query.all()
    return render_template('stats.html',
                           users=u)

@app.route("/stats_sort")
def statssort():
    u = User.query.order_by('progress asc').all()
    return render_template('stats.html',
                           users=u)
    

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == "__main__":
    app.run(debug=True)
