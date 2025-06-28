import json
from flask import (
    Blueprint, flash, g, make_response, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from password_manager.auth import login_required
from password_manager.sqlite_db import get_db

bp = Blueprint('manager', __name__)

@bp.route('/hello')
def welcome_manager():
    return 'Welcome to Manager!'

@bp.route("/insert", methods=("GET","POST"))
@login_required
def insert_record():
    if request.method == 'POST':
        website = request.form['website']
        username = request.form['username']
        password = request.form['password']
        user_id = g.user["id"]
        db = get_db()
        error = None

        if not website:
            error = "Website is required"
        elif not username:
            error = "username is required"
        elif not password:
            error = "password is required"
        
        if error is None:
            try:
                db.execute(
                    'INSERT INTO store (website, username, password, user_id)'
                    ' VALUES (?, ?, ?, ?)',
                    (website, username, password, user_id)
                )
                db.commit() 
            except db.IntegrityError:
                error = f"username {username} is already present."
            else:
                return redirect(url_for("manager.dashboard"))
        
        flash(error)

    return render_template("manager/insert.html")

@bp.route('/dashboard')
def dashboard():
    db = get_db()
    credentials = db.execute(
        'SELECT s.id, website, username, s.password, user_id'
        ' FROM store s JOIN user u ON s.user_id = u.id'
        ' ORDER BY website'
    ).fetchall()
    credentials_list = [dict(row) for row in credentials]
    return render_template("manager/dashboard.html", secrets=credentials_list)


