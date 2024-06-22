from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)

# Initialize the database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            order_item TEXT NOT NULL,
            item_price REAL NOT NULL,
            item_quantity INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Function to add the item_quantity column if it doesn't exist
def update_db_schema():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(orders)')
    columns = [col[1] for col in cursor.fetchall()]
    if 'item_quantity' not in columns:
        cursor.execute('ALTER TABLE orders ADD COLUMN item_quantity INTEGER DEFAULT 1')
    conn.commit()
    conn.close()

init_db()
update_db_schema()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/orders')
def orders():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    conn.close()
    return render_template('orders.html', orders=orders)

@app.route('/add', methods=['POST'])
def add():
    order_item = request.form['order_item']
    item_price = request.form['item_price']
    item_quantity = request.form['item_quantity']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (order_item, item_price, item_quantity) VALUES (?, ?, ?)", (order_item, item_price, item_quantity))
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    return jsonify({
        'order_item': order_item,
        'item_price': float(item_price),
        'item_quantity': int(item_quantity),
        'total_cost': float(item_price) * int(item_quantity)
    })

@app.route('/edit/<int:order_id>', methods=['GET', 'POST'])
def edit(order_id):
    if request.method == 'POST':
        order_item = request.form['order_item']
        item_price = request.form['item_price']
        item_quantity = request.form['item_quantity']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET order_item = ?, item_price = ?, item_quantity = ? WHERE id = ?", (order_item, item_price, item_quantity, order_id))
        conn.commit()
        conn.close()
        return redirect(url_for('orders'))
    else:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()
        conn.close()
        return render_template('edit_order.html', order=order)

@app.route('/delete/<int:order_id>')
def delete(order_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('orders'))

if __name__ == '__main__':
    app.run(debug=True)
