from flask import session, request, redirect, url_for, render_template, flash, g, Flask # g is proxy Flask's object
import os
from functools import wraps

# Define admin credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "password")

app = Flask(__name__)
app.secret_key = os.urandom(24) # Set a secret key sessions

def login_required(func):
  """Decorator to require login for specific routes."""
  from functools import wraps
  @wraps(func)
  def decorated(*args, **kwargs):
    if not session.get("admin_logged_in"):
      flash("Please log in to access the admin page.", "warning")
      return redirect(url_for("admin_login"))
    return func(*args, **kwargs)
  return decorated


@app.before_request
def before_request():
  g.current_user = session.get("admin_logged_in")


@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
  if request.method == "POST":
    username = request.form.get("username")
    password = request.form.get("password")

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
      session["admin_logged_in"] = True
      flash("Logged in successfully.", "success")
      return redirect(url_for("add_product"))
    else:
      flash("Invalid username or password.", "danger")

  return render_template("login.html")


# Logout route
@app.route("/admin_logout")
def admin_logout():
  session.pop("admin_logged_in", None)
  flash("You have been logged out.", "info")
  return redirect(url_for("admin_login"))


# Ensure g.current_user is available in all templates
@app.context_processor
def inject_user():
  return dict(current_user=g.current_user)