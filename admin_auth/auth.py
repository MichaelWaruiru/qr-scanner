from flask import session, request, redirect, url_for, render_template, flash
import os
from functools import wraps

# Define admin credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "password")


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
def admin_logout():
  session.pop("admin_logged_in", None)
  flash("You have been logged out.", "info")
  return redirect(url_for("admin_login"))