from flask import Flask, render_template, request, jsonify, url_for
import requests
import json
import base64
from datetime import datetime
import qrcode
import io
import os
from flask import send_file
from dotenv import load_dotenv


app = Flask(__name__)

load_dotenv()

# Configure M-Pesa keys
MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE")
MPESA_PASSKEY = os.getenv("MPESA_PASSKEY")
MPESA_CALLBACK_URL = 'https://your-domain.com/mpesa_callback'


products = {
  1: {"name": "Phone", "price": 109000},
  2: {"name": "Laptop", "price": 256000},
}


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
    product = products.get(product_id)
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
        "Amount": product['price'],  # Use product price from QR code
        "PartyA": phone_number,  # Customer's phone number
        "PartyB": MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": MPESA_CALLBACK_URL,
        "AccountReference": str(product['id']),
        "TransactionDesc": f"Payment for {product['name']}"
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

@app.route("/")
def home_page():
  return render_template("home.html", products=products)

# QR generation
@app.route("/qr_code/<int:product_id>")
def generate_qr(product_id):
  product = products.get(product_id)
  if not product:
    return "Product not found", 404
  
  # Create a QR code with product info
  qr = qrcode.QRCode(version=1, box_size=10, border=5)
  qr_data = {
    "id": product_id,
    "name": product["name"],
    "price": product["price"]
  }

  qr.add_data(qr_data)
  qr.make(fit=True)

  img = qr.make_image(fill="black", back_color="white")
  buf = io.BytesIO()
  img.save(buf)
  buf.seek(0)
  return send_file(buf, mimetype="image/png")


if __name__ == "__main__":
  app.run(debug=True)