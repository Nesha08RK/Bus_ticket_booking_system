from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId, InvalidId
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = "your_secret_key"  # Required for session security

# Initialize MongoDB
mongo = PyMongo(app)
bus_collection = mongo.db.buses
user_collection = mongo.db.users  # Users collection for authentication

# ---------------------- HOME ROUTE ----------------------
@app.route('/')
def home():
    return render_template('index.html')

# ---------------------- BUS SEARCH ----------------------
@app.route('/search', methods=['POST'])
def search():
    source = request.form.get('source', '').strip().lower()
    destination = request.form.get('destination', '').strip().lower()
    
    results = list(bus_collection.find({"source": source, "destination": destination}))
    return render_template('search_results.html', buses=results, source=source, destination=destination)

# ---------------------- BOOKING SEAT ----------------------
@app.route('/book/<bus_id>')
def book_seat(bus_id):
    try:
        bus = bus_collection.find_one({"_id": ObjectId(bus_id)})
        if not bus:
            flash("Bus not found.", "danger")
            return redirect(url_for('home'))
    except (InvalidId, Exception) as e:
        flash(f"Invalid Bus ID: {str(e)}", "danger")
        return redirect(url_for('home'))
    return redirect(url_for('seat_selection', bus_id=bus_id))

# ---------------------- SEAT SELECTION ----------------------
@app.route('/seat_selection/<bus_id>')
def seat_selection(bus_id):
    try:
        bus = bus_collection.find_one({"_id": ObjectId(bus_id)})
        if not bus:
            flash("Bus not found.", "danger")
            return redirect(url_for('home'))
    except (InvalidId, Exception) as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('home'))
    
    return render_template('seat_selection.html', bus=bus)

# ---------------------- CONFIRM BOOKING ----------------------
@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    bus_id = request.form.get("bus_id")
    selected_seats = request.form.get("selected_seats", "").split(",") if request.form.get("selected_seats") else []

    if not bus_id:
        flash("Bus ID is missing!", "danger")
        return redirect(url_for('home'))
    
    if not selected_seats:
        flash("Please select at least one seat.", "danger")
        return redirect(url_for('seat_selection', bus_id=bus_id))

    try:
        bus = bus_collection.find_one({"_id": ObjectId(bus_id)})
        if not bus:
            flash("Bus not found.", "danger")
            return redirect(url_for('home'))
    except (InvalidId, Exception) as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('home'))

    total_cost = bus["price"] * len(selected_seats)

    # Store booking details in session
    session['booking_details'] = {
        'bus_id': str(bus_id),
        'selected_seats': selected_seats,
        'total_cost': total_cost
    }

    flash("Booking confirmed successfully!", "success")
    return redirect(url_for('confirmation'))

# ---------------------- CONFIRMATION PAGE ----------------------
@app.route('/confirmation')
def confirmation():
    if 'booking_details' not in session:
        flash("No booking details found!", "danger")
        return redirect(url_for("home"))

    booking_details = session['booking_details']
    
    try:
        bus = bus_collection.find_one({"_id": ObjectId(booking_details['bus_id'])})
        if not bus:
            flash("Bus not found.", "danger")
            return redirect(url_for('home'))
    except Exception as e:
        flash(f"Error retrieving booking details: {str(e)}", "danger")
        return redirect(url_for("home"))

    return render_template(
        'confirmation.html',
        bus=bus,
        selected_seats=booking_details['selected_seats'],
        total_cost=booking_details['total_cost']
    )

# ---------------------- USER AUTHENTICATION ----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        user = user_collection.find_one({"email": email})

        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['email'] = user['email']
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials. Please try again.", "danger")

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form.get('fullName').strip()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        existing_user = user_collection.find_one({"email": {"$regex": f"^{email}$", "$options": "i"}})

        if existing_user:
            flash("Email already exists. Please log in.", "warning")
            return redirect(url_for('login'))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        user_collection.insert_one({"full_name": full_name, "email": email, "password": hashed_password})

        flash("Signup successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

# ---------------------- RUN APP ----------------------
if __name__ == '__main__':
    app.run(debug=True)
