from flask import session, request, redirect, url_for, render_template, flash
import os
from functools import wraps
from datetime import datetime, timedelta

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

    # Check if session expired
    login_time_str = session.get("login_time")
    if login_time_str:
      login_time = datetime.strptime(login_time_str, "%Y-%m-%d %H:%M:%S")
      session_duration = datetime.utcnow() - login_time

      # If session is older than 15 minutes, log out the user
      if session_duration > timedelta(minutes=15):
        session.pop("admin_logged_in", None)
        session.pop("login_time", None)
        flash("Session expired. Please log in again.", "warning")
        return redirect(url_for("admin_login"))

    # Reset session login time (extend session by 15 minutes on activity)
    session["login_time"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    return func(*args, **kwargs)

  return decorated


def admin_login():
  if request.method == "POST":
    username = request.form.get("username")
    password = request.form.get("password")

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
      session["admin_logged_in"] = True
      session["login_time"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")  # Store the login time
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