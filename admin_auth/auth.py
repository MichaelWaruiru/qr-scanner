from flask import Response, request
import os

# Define admin credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "password")

def authenticate():
  """Send a 401 response for authorized access."""
  return Response(
    "Could not verify your access level for that URL. \n"
    "You have to login with proper credentials",
    401,
    {"WWW-Authenticate": "Basic realm='Login Required'"}
  )

def requires_auth(func):
  """Decorator to require authentication for specific routes."""
  from functools import wraps
  @wraps(func)
  def decorated(*args, **kwargs):
    auth = request.authorization
    if not auth or auth.username != ADMIN_USERNAME or auth.password != ADMIN_PASSWORD:
      return authenticate()
    return func(*args, **kwargs)
  return decorated