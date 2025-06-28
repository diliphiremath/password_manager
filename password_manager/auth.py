import functools

from flask import (
    Blueprint, flash, g, make_response, redirect, render_template, request, url_for, session
)
from werkzeug.security import check_password_hash, generate_password_hash
from password_manager.sqlite_db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route("/hello")
def hello_user():
    return "Welcome to User"

@bp.route("/register", methods=("GET", "POST"))
def register_user():
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        # TODO: add confirm password field
        password = request.form.get("password")
        error = None
        db = get_db()

        if not email:
            error = "Email is required"
        elif not name:
            error = "Name is required"
        elif not password:
            error = "Password is required"
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (email, name, password) Values (?,?,?)",
                    (email, name, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                error = f"{email} is already registered."
            else:
                return redirect(url_for("auth.login"))
            
        flash(error)
    
    return render_template("auth/register.html")

@bp.route("/login", methods=("GET","POST"))
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        db = get_db()
        error = None

        user = db.execute(
            "SELECT * FROM user WHERE email = ?",
            (email,)
        ).fetchone()

        if user is None:
            error = "Incorrect email"
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password"
        
        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("manager.welcome_manager"))
        
        flash(error)
    
    return render_template("auth/login.html")

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('manager.welcome_manager'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
        

