import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash
import config

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this in production

# Initialize Supabase Client
supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

@app.route('/')
def home():
    return render_template("login.html")

# SIGNUP ROUTE
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_email = request.form.get('email')
        user_password = request.form.get('password')
        user_role = request.form.get('role')

        # Hash password before storing
        hashed_password = generate_password_hash(user_password)

        # Check if email already exists
        existing_user = supabase.table("users").select("*").eq("user_email", user_email).execute()
        if existing_user.data:
            return jsonify({"error": "Email already registered!"}), 400

        # Insert user into Supabase
        supabase.table("users").insert({
            "user_email": user_email,
            "user_password": hashed_password,
            "user_role": user_role
        }).execute()

        return redirect(url_for("login"))

    return render_template('signup.html')

# LOGIN ROUTE
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_email = request.form.get('email')
        user_password = request.form.get('password')

        # Fetch user from Supabase
        user = supabase.table("users").select("*").eq("user_email", user_email).execute()
        if not user.data:
            return jsonify({"error": "User not found!"}), 400

        # Verify password
        user_data = user.data[0]
        if not check_password_hash(user_data["user_password"], user_password):
            return jsonify({"error": "Invalid password!"}), 400

        # Store session & redirect
        session["user_email"] = user_email
        session["user_role"] = user_data["user_role"]

        if user_data["user_role"] == "buyer":
            return redirect(url_for("buyer_dashboard"))
        else:
            return redirect(url_for("seller_dashboard"))

    return render_template("login.html")

# BUYER DASHBOARD
@app.route('/buyer')
def buyer_dashboard():
    if session.get("user_role") != "buyer":
        return redirect(url_for("login"))
    return render_template("buyer.html")

# SELLER DASHBOARD
@app.route('/seller')
def seller_dashboard():
    if session.get("user_role") != "seller":
        return redirect(url_for("login"))
    return render_template("seller.html")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use Railway-assigned port
    app.run(host='0.0.0.0', port=port)
