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
@login_required
def dashboard():
    db = get_db()
    credentials = db.execute(
        'SELECT s.id, website, username, s.password, user_id'
        ' FROM store s JOIN user u ON s.user_id = u.id'
        ' ORDER BY website'
    ).fetchall()
    credentials_list = [dict(row) for row in credentials]
    return render_template("manager/dashboard.html", secrets=credentials_list)

def get_secret(id, check_user=True):
    secret = get_db().execute(
        "SELECT s.id, website, username, s.password, user_id"
        " FROM store s JOIN user u ON s.user_id = u.id"
        " WHERE s.id = ?",
        (id,)
    ).fetchone()

    if secret is None:
        abort(404, f"Secret for {id} doesn't exisit")
    
    if check_user and secret["user_id"] != g.user["id"]:
        abort(403)
    
    return secret

@bp.route("/<int:id>/update", methods=("GET","POST"))
@login_required
def update_record(id):
    secret = get_secret(id)

    if request.method == "POST":
        website = request.form["website"]
        username = request.form["username"]
        password = request.form["password"]
        error = None

        if not website:
            error = "Website is required"
        elif not username:
            error = "username is required"
        elif not password:
            error = "password is required"
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE store SET website = ?, username = ?, password = ?"
                " WHERE id = ?",
                (website, username, password, id)
            )
            db.commit()
            return redirect(url_for("manager.dashboard"))
    
    return render_template("manager/update.html", secret=secret)

@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete_record(id):
    get_secret(id)
    db = get_db()
    db.execute("DELETE FROM store WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("manager.dashboard"))
            


