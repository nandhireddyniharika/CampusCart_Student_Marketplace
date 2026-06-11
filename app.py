from flask import Flask, render_template, request, redirect, session, flash, send_from_directory
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from config import Config
import os
import re

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)

# Create uploads folder if not exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# ---------------- HOME REDIRECT ----------------

@app.route('/')
def index():
    return """
    <html>
    <head>
        <meta http-equiv="refresh" content="3;url=/login">
    </head>
    <body style="text-align:center;margin-top:100px;">
        <h1>CampusCart 🛒</h1>
        <h3>Loading...</h3>
    </body>
    </html>
    """

# ---------------- REGISTER ----------------

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if not email.endswith("@sastra.ac.in"):
            flash("Only SASTRA email allowed")
            return redirect('/register')

        username = email.split('@')[0]

        if not re.fullmatch(r'\d{9}', username):
            flash("Email must be 9 digits followed by @sastra.ac.in")
            return redirect('/register')

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        existing = cur.fetchone()

        if existing:
            flash("User already exists")
            return redirect('/register')

        cur.execute(
            """
            INSERT INTO users(name,email,password)
            VALUES(%s,%s,%s)
            """,
            (name, email, password)
        )

        mysql.connection.commit()

        return """
        <html>
        <head>
            <meta http-equiv="refresh" content="3;url=/login">
        </head>
        <body style="text-align:center;margin-top:100px;">
            <h2>Registration Successful ✅</h2>
            <p>Redirecting to Login...</p>
        </body>
        </html>
        """

    return render_template("register.html")

# ---------------- LOGIN ----------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute(
            """
            SELECT * FROM users
            WHERE email=%s AND password=%s
            """,
            (email, password)
        )

        user = cur.fetchone()

        if user:

            session['user'] = email

            return """
            <html>
            <head>
                <meta http-equiv="refresh" content="3;url=/home">
            </head>
            <body style="text-align:center;margin-top:100px;">
                <h2>Login Successful 🚀</h2>
                <p>Redirecting to Home...</p>
            </body>
            </html>
            """

        flash("Invalid Credentials")
        return redirect('/login')

    return render_template("login.html")

# ---------------- HOME ----------------

@app.route('/home')
def home():

    if 'user' not in session:
        return redirect('/login')

    search = request.args.get('search')

    cur = mysql.connection.cursor()

    if search:

        cur.execute(
            """
            SELECT * FROM products
            WHERE title LIKE %s
            """,
            ('%' + search + '%',)
        )

    else:

        cur.execute(
            """
            SELECT * FROM products
            ORDER BY id DESC
            """
        )

    products = cur.fetchall()

    # Notification Count

    cur.execute(
        """
        SELECT COUNT(*)
        FROM notifications
        WHERE user_email=%s
        AND status='UNREAD'
        """,
        (session['user'],)
    )

    notification_count = cur.fetchone()[0]

    return render_template(
        'home.html',
        products=products,
        user=session['user'],
        notification_count=notification_count
    )


# ---------------- DASHBOARD ----------------

@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT * FROM products
        WHERE user_email=%s
        ORDER BY id DESC
        """,
        (session['user'],)
    )

    products = cur.fetchall()

    return render_template(
        'dashboard.html',
        products=products
    )

# ---------------- ADD PRODUCT ----------------

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():

    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':

        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        price = request.form['price']

        image = request.files['image']

        filename = secure_filename(image.filename)

        image.save(
            os.path.join(
                app.config['UPLOAD_FOLDER'],
                filename
            )
        )

        cur = mysql.connection.cursor()

        cur.execute(
            """
            INSERT INTO products
            (
                user_email,
                title,
                description,
                category,
                price,
                image
            )
            VALUES(%s,%s,%s,%s,%s,%s)
            """,
            (
                session['user'],
                title,
                description,
                category,
                price,
                filename
            )
        )

        mysql.connection.commit()

        return redirect('/home')

    return render_template("add_product.html")

# ---------------- EDIT PRODUCT ----------------

@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit_product(id):

    if 'user' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    if request.method == 'POST':

        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        price = request.form['price']

        image = request.files['image']

        if image.filename != "":

            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )

            cur.execute("""
            UPDATE products
            SET title=%s,
                description=%s,
                category=%s,
                price=%s,
                image=%s
            WHERE id=%s
            """,
            (
                title,
                description,
                category,
                price,
                filename,
                id
            ))

        else:

            cur.execute("""
            UPDATE products
            SET title=%s,
                description=%s,
                category=%s,
                price=%s
            WHERE id=%s
            """,
            (
                title,
                description,
                category,
                price,
                id
            ))

        mysql.connection.commit()

        return redirect('/dashboard')

    cur.execute(
        "SELECT * FROM products WHERE id=%s",
        (id,)
    )

    product = cur.fetchone()

    return render_template(
        'edit_product.html',
        product=product
    )

# ---------------- DELETE PRODUCT ----------------

@app.route('/delete/<int:id>')
def delete_product(id):

    if 'user' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        DELETE FROM products
        WHERE id=%s
        """,
        (id,)
    )

    mysql.connection.commit()

    return redirect('/dashboard')

# ---------------- SOLD OUT ----------------

@app.route('/soldout/<int:id>')
def soldout(id):

    if 'user' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT title,user_email
        FROM products
        WHERE id=%s
        """,
        (id,)
    )

    product = cur.fetchone()

    cur.execute(
        """
        UPDATE products
        SET status='SOLD'
        WHERE id=%s
        """,
        (id,)
    )

    cur.execute(
        """
        INSERT INTO notifications
        (
            user_email,
            message
        )
        VALUES(%s,%s)
        """,
        (
            product[1],
            f"Product Sold: {product[0]}"
        )
    )

    mysql.connection.commit()

    return redirect('/dashboard')


# ---------------- PROFILE ----------------

@app.route('/profile')
def profile():

    if 'user' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT * FROM users WHERE email=%s",
        (session['user'],)
    )

    user = cur.fetchone()

    cur.execute(
        "SELECT COUNT(*) FROM products WHERE user_email=%s",
        (session['user'],)
    )

    total_products = cur.fetchone()[0]

    cur.execute(
        """
        SELECT COUNT(*)
        FROM products
        WHERE user_email=%s
        AND status='SOLD'
        """,
        (session['user'],)
    )

    sold_products = cur.fetchone()[0]

    return render_template(
        "profile.html",
        user=user,
        total_products=total_products,
        sold_products=sold_products
    )

# ---------------- IMAGE ROUTE ----------------

@app.route('/uploads/<filename>')
def uploaded_file(filename):

    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename
    )


# ---------------- CHAT ROUTE -----------------
@app.route('/chat/<seller_email>', methods=['GET','POST'])
def chat(seller_email):

    if 'user' not in session:
        return redirect('/login')

    buyer = session['user']

    cur = mysql.connection.cursor()

    if request.method == 'POST':

        msg = request.form['message']

        cur.execute(
            """
            INSERT INTO messages
            (
                sender_email,
                receiver_email,
                message
            )
            VALUES(%s,%s,%s)
            """,
            (
                buyer,
                seller_email,
                msg
            )
        )

       
        cur.execute(
            """
            INSERT INTO notifications
            (
                user_email,
                message
            )
            VALUES(%s,%s)
            """,
            (
                seller_email,
                f"New message from {buyer}"
            )
        )

        mysql.connection.commit()

    cur.execute(
        """
        SELECT *
        FROM messages
        WHERE
        (sender_email=%s AND receiver_email=%s)
        OR
        (sender_email=%s AND receiver_email=%s)
        ORDER BY sent_at
        """,
        (
            buyer,
            seller_email,
            seller_email,
            buyer
        )
    )

    chats = cur.fetchall()

    return render_template(
        "chat.html",
        chats=chats,
        seller=seller_email
    )

# ---------------- INBOX -----------------
@app.route('/inbox')
def inbox():

    if 'user' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT DISTINCT sender_email
        FROM messages
        WHERE receiver_email=%s
        """,
        (session['user'],)
    )

    users = cur.fetchall()

    return render_template(
        "inbox.html",
        users=users
    )


# ---------------- ADD Admin -----------------
@app.route('/admin')
def admin():

    if 'user' not in session:
        return redirect('/login')

    if session['user'] != 'admin@sastra.ac.in':
        return "Access Denied"

    cur = mysql.connection.cursor()

    # Total Users
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    # Total Products
    cur.execute("SELECT COUNT(*) FROM products")
    total_products = cur.fetchone()[0]

    # Sold Products
    cur.execute(
        "SELECT COUNT(*) FROM products WHERE status='SOLD'"
    )
    sold_products = cur.fetchone()[0]

    # All Users
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    # All Products
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()

    return render_template(
        'admin.html',
        total_users=total_users,
        total_products=total_products,
        sold_products=sold_products,
        users=users,
        products=products
    )

# ---------------- DELETE ADMIN ----------
@app.route('/admin_delete/<int:id>')
def admin_delete(id):

    if 'user' not in session:
        return redirect('/login')

    if session['user'] != 'admin@sastra.ac.in':
        return "Access Denied"

    cur = mysql.connection.cursor()

    cur.execute(
        "DELETE FROM products WHERE id=%s",
        (id,)
    )

    mysql.connection.commit()

    return redirect('/admin')


# ---------------- ADD WISHLIST ----------
@app.route('/wishlist/<int:product_id>')
def add_wishlist(product_id):

    if 'user' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        INSERT INTO wishlist
        (user_email, product_id)
        VALUES(%s,%s)
        """,
        (
            session['user'],
            product_id
        )
    )

    mysql.connection.commit()

    flash("Added to Wishlist ❤️")

    return redirect('/home')

# ---------------- WISHLIST --------------
@app.route('/wishlist')
def wishlist():

    if 'user' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT p.*
        FROM products p
        JOIN wishlist w
        ON p.id = w.product_id
        WHERE w.user_email=%s
    """,
    (session['user'],))

    products = cur.fetchall()

    return render_template(
        'wishlist.html',
        products=products
    )

# --------------- NOTIFICATIONS ----------
@app.route('/notifications')
def notifications():

    if 'user' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT *
        FROM notifications
        WHERE user_email=%s
        ORDER BY created_at DESC
        """,
        (session['user'],)
    )

    data = cur.fetchall()

    return render_template(
        'notifications.html',
        notifications=data
    )



# ---------------- LOGOUT ----------------

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)