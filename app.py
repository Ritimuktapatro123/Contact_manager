from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Used for flashing messages

# --- Initialize DB ---
def init_db():
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            address TEXT,
            email TEXT UNIQUE,
            phone TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

# --- Home Page: Display All Contacts ---
@app.route('/')
def index():
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts")
    contacts = cursor.fetchall()
    conn.close()
    return render_template('index.html', contacts=contacts)

# --- Add New Contact ---
@app.route('/add', methods=['GET', 'POST'])
def add_contact():
    if request.method == 'POST':
        first = request.form['first_name'].strip()
        last = request.form['last_name'].strip()
        address = request.form['address'].strip()
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email format.', 'danger')
            return redirect(url_for('add_contact'))

        try:
            conn = sqlite3.connect('contacts.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO contacts (first_name, last_name, address, email, phone)
                VALUES (?, ?, ?, ?, ?)
            ''', (first, last, address, email, phone))
            conn.commit()
            flash('Contact added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Email or phone number already exists.', 'danger')
        finally:
            conn.close()
        return redirect(url_for('index'))
    return render_template('add_contact.html')

# --- Update Contact ---
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_contact(id):
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts WHERE id=?", (id,))
    contact = cursor.fetchone()
    conn.close()

    if request.method == 'POST':
        first = request.form['first_name'].strip()
        last = request.form['last_name'].strip()
        address = request.form['address'].strip()
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email format.', 'danger')
            return redirect(url_for('edit_contact', id=id))

        try:
            conn = sqlite3.connect('contacts.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE contacts
                SET first_name=?, last_name=?, address=?, email=?, phone=?
                WHERE id=?
            ''', (first, last, address, email, phone, id))
            conn.commit()
            flash('Contact updated successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Email or phone already exists.', 'danger')
        finally:
            conn.close()
        return redirect(url_for('index'))

    return render_template('update_contact.html', contact=contact)

# --- Delete Contact ---
@app.route('/delete/<int:id>')
def delete_contact(id):
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contacts WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash('Contact deleted successfully!', 'success')
    return redirect(url_for('index'))

# --- Run App ---
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
