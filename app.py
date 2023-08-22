from flask import Flask, render_template, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import Unauthorized

from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///flask-feedback"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'abc123'
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route("/")
def homepage():
    """Homepage + redirect to register"""
    return redirect("/register")

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a user; produce form and handle form submission"""

    if "username" in session:
        return redirect(f"/users/{session['username']}")
    
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data

        user = User.register(username, password, first_name, last_name, email)

        db.session.commit()
        session['username'] = user.username
        
        return redirect(f"/users/{user.username}")
    
    else:
        return render_template("users/register.html", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Produce login form or handle login"""

    if "username" in session:
        return redirect(f"/users/{session['username']}")
    
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Invalid username/password"]
            return render_template("users/login.html", form=form)
        
    return render_template("users/login.html", form=form)

@app.route("/logout")
def logout():
    """User logout"""

    session.pop("username")
    return redirect("/login")

@app.route("/users/<username>")
def show_user(username):
    """Example page for logged in users"""

    if "username" not in session or username != session['username']:
        raise Unauthorized()
    
    user = User.query.get(username)
    form = DeleteForm()

    return render_template("users/show.html", user=user, form=form)

@app.route("/users/<username>/delete", methods=["POST"])
def remove_user(username):
    """Remove user and redirect to login"""

    if "username" not in session or username != session['username']:
        raise Unauthorized()
    
    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")

    return redirect("/login")



