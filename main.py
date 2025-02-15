from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import base64
from datetime import datetime
import qrcode
import io
import os
from flask import send_file
from dotenv import load_dotenv
from admin_auth.auth import login_required, admin_login, admin_logout
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
load_dotenv()

# Database configurations
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Configure upload folder
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# Allowed image extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Configure M-Pesa keys
MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE")
MPESA_PASSKEY = os.getenv("MPESA_PASSKEY")
MPESA_CALLBACK_URL = 'https://your-domain.com/mpesa_callback'


class Product(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(100), nullable=False)
   price = db.Column(db.Float, nullable=False)
   image_filename = db.Column(db.String(255), nullable=True)
   description = db.Column(db.String(255), nullable=True)


# Create database and table
with app.app_context():
   db.create_all()


# Home Page
@app.route("/")
def home_page():
  products = Product.query.all()
  return render_template("home.html", products=products)


# Admin login route
app.add_url_rule('/admin/login', 'admin_login', admin_login, methods=['GET', 'POST'])

# Admin logout route
app.add_url_rule('/admin/logout', 'admin_logout', admin_logout)


# Check if the image file is allowed
def allowed_image_file(filename):
   return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Admin endpoint to add Product
@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == "GET":
       return render_template("products.html")

    # Handle form submission
    name = request.form.get('name')
    price = request.form.get('price')
    image = request.files.get('image')
    description = request.form.get('description')

    print("Image uploaded", image)

    # Validate inputs
    if not name or not price:
        flash("Invalid product data.", "danger")
        return jsonify({"error": "Invalid product data"}), 400
    

    # Validate and save image file
    if image and allowed_image_file(image.filename):
       image_filename = secure_filename(image.filename)
       image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)

       # Ensure the upload directory exists
       if not os.path.exists(app.config['UPLOAD_FOLDER']):
           os.makedirs(app.config['UPLOAD_FOLDER'])

       try:
        print("Saving image to:", image_path)
        image.save(image_path)
       except Exception as e:
          app.logger.error(f"Error saving image: {e}")
          flash(f"Failed to save image: {str(e)}", "danger")
          return redirect(url_for("add_product"))
    else:
        flash("Invalid image file.", "danger")
        return redirect(url_for("add_product"))

    # Convert price to float
    # try:
    #    price = float(price)
    # except ValueError:
    #    flash("Price must be a number.", "danger")
    #    return jsonify({"error": "Price must be a number"}), 400
    
    # Add a product to database
    product = Product(name=name, price=price, description=description, image_filename=image_filename)
    db.session.add(product)
    db.session.commit()

    flash("Product added successfully!", "success")
    return redirect(url_for('add_product'))


# Edit product route
@app.route("/edit_product", methods=["POST"])
@login_required
def edit_product():
    product_id = request.form.get("product_id")
    product = Product.query.get(product_id)
    if not product:
        flash("Product not found", "danger")
        return redirect(url_for("home_page"))

    name = request.form.get("name")
    price = request.form.get("price")
    description = request.form.get("description")
    image = request.files.get("image")

    # Validate the inputs
    if not name or not price:
        flash("Invalid product data", "danger")
        return redirect(url_for("edit_product", product_id=product_id))

    # Validate and save image file
    if image and allowed_image_file(image.filename):
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)

        # Ensure the upload directory exists
        if not os.path.exists(app.config["UPLOAD_FOLDER"]):
            os.makedirs(app.config["UPLOAD_FOLDER"])

        try:
            image.save(image_path)
            product.image_filename = image_filename
        except Exception as e:
            app.logger.error(f"Error saving image: {e}")
            flash(f"Failed to save image: {str(e)}", "danger")
            return redirect(url_for("edit_product", product_id=product_id))

    # Convert price to float
    # try:
    #     price = float(price)
    # except ValueError:
    #     flash("Price must be a number.", "danger")
    #     return redirect(url_for('home_page'))

    # Update product details
    product.name = name
    product.price = price
    product.description = description
    db.session.commit()

    flash("Product updated successfully!", "success")
    return redirect(url_for("home_page"))


# Route to get product data
@app.route("/get_product/<int:product_id>", methods=["GET"])
@login_required
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    product_data = {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "description": product.description
    }
    return jsonify(product_data)

# Delete product
@app.route("/delete_product", methods=["POST"])
@login_required
def delete_product():
    product_id = request.form.get("product_id")
    product = Product.query.get(product_id)
    if not product:
        flash("Product not found", "danger")
        return redirect(url_for("home_page"))

    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully!", "success")
    return redirect(url_for("home_page"))


# QR generation for Product
@app.route("/qr_code/<int:product_id>")
def generate_qr(product_id):
  product = Product.query.get(product_id)
  if not product:
    return "Product not found", 404
  
  # Create a QR code with product info
  qr = qrcode.QRCode(version=1, box_size=10, border=5)
  qr_data = {
    "id": product_id,
    "name": product.name,
    "price": product.price
  }

  qr.add_data(qr_data)
  qr.make(fit=True)

  img = qr.make_image(fill="black", back_color="white")
  buf = io.BytesIO()
  img.save(buf)
  buf.seek(0)
  return send_file(buf, mimetype="image/png")


# Access token for MPesa API 
def generate_mpesa_access_token():
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(api_url, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET))
    json_response = response.json()
    return json_response['access_token']


# Initiate MPesa STK Push payment
@app.route('/initiate_payment', methods=['POST'])
def initiate_payment():
    access_token = generate_mpesa_access_token()
    
    # Get product and phone number from the request
    product_id = request.json.get('product_id')
    phone_number = request.json.get('phone_number')

    # Fetch the product details
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    # Generate password for STK Push
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode((MPESA_SHORTCODE + MPESA_PASSKEY + timestamp).encode()).decode('utf-8')
    
    payload = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": product.price,  # Use product price from QR code
        "PartyA": phone_number,  # Customer's phone number
        "PartyB": MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": MPESA_CALLBACK_URL,
        "AccountReference": str(product.id),
        "TransactionDesc": f"Payment for {product.name}"
    }

    headers = {"Authorization": f"Bearer {access_token}"}
    stk_push_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    response = requests.post(stk_push_url, json=payload, headers=headers)

    if response.status_code == 200:
        return jsonify({"message": "Payment initiated, check your phone to complete payment."})
    else:
        return jsonify({"error": "Failed to initiate payment"}), 500

# Handle MPesa payment callback
@app.route('/mpesa_callback', methods=['POST'])
def mpesa_callback():
    data = request.json

    # Log the payment result and status
    with open("mpesa_callback_log.txt", "a") as log_file:
        log_file.write(json.dumps(data) + "\n")
    
    # Check if payment is successful
    if data.get("Body").get("stkCallback").get("ResultCode") == 0:
        # Payment was successful, proceed with order fulfillment
        return jsonify({"message": "Payment successful!"})
    else:
        # Payment failed
        return jsonify({"error": "Payment failed"}), 400


if __name__ == "__main__":
  app.run(debug=True)