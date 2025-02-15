from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3  
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Folder for auction images

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Database
def init_db():
    with sqlite3.connect('archinova.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auctions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                price INTEGER NOT NULL,
                end_time TEXT NOT NULL,
                seller_name TEXT NOT NULL,
                seller_email TEXT NOT NULL,
                image TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bids (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                auction_id INTEGER NOT NULL,
                bidder TEXT NOT NULL,
                bid_amount INTEGER NOT NULL,
                FOREIGN KEY (auction_id) REFERENCES auctions (id)
            )
        ''')
        conn.commit()

init_db()

# Home Page (Requires Login)
@app.route('/')
def index():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session.get('username'))

# Auction Page (Requires Login)
@app.route('/auction')
def auction():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    with sqlite3.connect('archinova.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM auctions')
        auctions = [
            {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "price": row[3],
                "end_time": row[4],
                "seller_name": row[5],
                "seller_email": row[6],
                "image": row[7],
                "bids": []
            }
            for row in cursor.fetchall()
        ]

    # Read existing bids from the JSON file
    bids_file_path = os.path.join(os.getcwd(), 'bids.json')
    if os.path.exists(bids_file_path):
        with open(bids_file_path, 'r') as file:
            try:
                bids = json.load(file)
            except json.JSONDecodeError:
                bids = []
    else:
        bids = []

    # Add bids to the corresponding auctions
    for auction in auctions:
        auction['bids'] = [bid for bid in bids if bid['auction_id'] == auction['id']]

    return render_template('auction.html', auctions=auctions)

# Create Auction
@app.route('/create_auction', methods=['POST'])
def create_auction():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    name = request.form['work-name']
    description = request.form['work-description']
    price = request.form['work-price']
    end_time = request.form['auction-end-time']
    seller_name = request.form['seller-name']
    seller_email = request.form['seller-email']
    image = request.files['work-image']

    if image:
        image_filename = image.filename
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)

        with sqlite3.connect('archinova.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO auctions (name, description, price, end_time, seller_name, seller_email, image)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, price, end_time, seller_name, seller_email, image_filename))
            conn.commit()

    return redirect(url_for('auction'))

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect('archinova.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM accounts WHERE username = ? AND password = ?', (username, password))
            account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            session['email'] = account[3]
            return redirect(url_for('index'))
        else:
            msg = 'მომხმარებლის სახელი ან პაროლი არასწორია!'
    
    return render_template('login.html', msg=msg)

# Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        with sqlite3.connect('archinova.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM accounts WHERE username = ?', (username,))
            account = cursor.fetchone()

            if account:
                msg = 'მომხმარებელი უკვე არსებობს!'
            elif not username or not password or not email:
                msg = 'შეავსეთ ყველა ველი!'
            else:
                cursor.execute('INSERT INTO accounts (username, password, email) VALUES (?, ?, ?)', (username, password, email))
                conn.commit()
                return redirect(url_for('login'))

    return render_template('register.html', msg=msg)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/get_user', methods=['GET'])
def get_user():
    if 'loggedin' not in session:
        return jsonify({"error": "User not logged in"}), 401  # 🔴 No session found

    return jsonify({
        "name": session.get('username'),
        "email": session.get('email')
    })

@app.route('/place_bid', methods=['POST'])
def place_bid():
    if 'loggedin' not in session:
        return jsonify({"success": False, "error": "User not logged in"}), 401

    # Debug: Print request headers and body
    print(f"🧐 Debug Headers: {request.headers}")
    print(f"🧐 Debug Raw Data: {request.data}")

    try:
        data = request.get_json(force=True)  # ✅ Force parsing JSON (helps if Content-Type is incorrect)
        print(f"🧐 Debug Parsed JSON: {data}")
    except Exception as e:
        print(f"❌ Error parsing JSON: {e}")
        return jsonify({"success": False, "error": "Invalid JSON format", "details": str(e)}), 400

    auction_id = int(data.get("auction_id"))
    bid_amount = int(data.get("amount"))

    # Get username and email from session
    username = session.get("username")
    email = session.get("email")

    if not all([auction_id, bid_amount]):
        return jsonify({"success": False, "error": "Missing auction ID or bid amount"}), 400

    # Read existing bids from the JSON file
    bids_file_path = os.path.join(os.getcwd(), 'bids.json')
    if os.path.exists(bids_file_path):
        with open(bids_file_path, 'r') as file:
            try:
                bids = json.load(file)
            except json.JSONDecodeError:
                bids = []
    else:
        bids = []

    # Add the new bid to the list
    new_bid = {
        "auction_id": auction_id,
        "bidder": username,
        "bidder_email": email,
        "bid_amount": bid_amount
    }
    bids.append(new_bid)

    # Write the updated bids list back to the JSON file
    with open(bids_file_path, 'w') as file:
        json.dump(bids, file, indent=4)

    print(f"✅ Bid Placed: {username} ({email}) - {bid_amount}₾ on Auction {auction_id}")

    return jsonify({
        "success": True,
        "username": username,
        "email": email,
        "auction_id": auction_id,
        "amount": bid_amount
    })




@app.route('/delete_auction/<int:auction_id>', methods=['POST'])
def delete_auction(auction_id):
    if 'loggedin' not in session:
        return jsonify({"success": False, "error": "User not logged in"}), 401

    # Get username from session
    username = session.get("username")

    with sqlite3.connect('archinova.db') as conn:
        cursor = conn.cursor()
        # Check if the auction exists and if the logged-in user is the seller
        cursor.execute('SELECT seller_name FROM auctions WHERE id = ?', (auction_id,))
        auction = cursor.fetchone()

        if auction and auction[0] == username:
            # Delete the auction
            cursor.execute('DELETE FROM auctions WHERE id = ?', (auction_id,))
            conn.commit()
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Auction not found or you are not the seller"}), 403
# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)