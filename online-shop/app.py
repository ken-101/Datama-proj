from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = "replace_with_your_secret_key"  # Needed for session usage

# Supabase credentials
SUPABASE_URL = "https://cipzhvxtnmftxqamsicd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNpcHpodnh0bm1mdHhxYW1zaWNkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2MTg4NTYsImV4cCI6MjA1NTE5NDg1Nn0.zZmXXbIqigl8XmcsxBf2Rg_SXpLOyZxPKMI-ksx-Zgg"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route('/')
def home():
    # Simple home page, you can redirect to /login or show a landing page
    return "Welcome to the Flask + Supabase Demo"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Query the 'users' table to find matching user
        response = supabase.table("users").select("*").eq("user_email", email).execute()
        user_data = response.data

        if user_data:
            # user_data is a list of records, so we take the first one
            user = user_data[0]
            # Check password
            if user["user_password"] == password:
                # Save user info in session
                session["user_id"] = user["user_id"]
                session["user_role"] = user["user_role"]

                # Redirect based on user role
                if user["user_role"] == "buyer":
                    return redirect(url_for('buyer_dashboard'))
                elif user["user_role"] == "seller":
                    return redirect(url_for('seller_dashboard'))
                else:
                    return "Unknown role."
            else:
                return "Wrong password."
        else:
            return "User not found."
    else:
        # GET request -> show the login form
        return render_template('login.html')


@app.route('/buyer-dashboard')
def buyer_dashboard():
    # Check if user is logged in and is a buyer
    if "user_role" in session and session["user_role"] == "buyer":
        return render_template('buyer.html')
    else:
        return "Unauthorized access. Please log in as a buyer."


@app.route('/seller-dashboard')
def seller_dashboard():
    # Check if user is logged in and is a seller
    if "user_role" in session and session["user_role"] == "seller":
        return render_template('seller.html')
    else:
        return "Unauthorized access. Please log in as a seller."


@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
