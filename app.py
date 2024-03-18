"""
ITAS 256 Web Development II
Assignment 2 - Web Server
Samjot Singh
Topic- Create a functional web server using either the Bottle or Flask python library

Took some help from chatgpt 3.5 for syntax/runtime errors and reformatting the code.
Used lab05 Flask server for reference.
Used https://flask.palletsprojects.com/en/3.0.x/quickstart/ for reference.
Used https://www.geeksforgeeks.org/how-to-run-a-flask-application/ for reference.
Used https://www.geeksforgeeks.org/flask-creating-first-simple-application/ for reference.
"""

from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, SelectField, IntegerField, FloatField, DateField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length
import json
from datetime import datetime
from jinja2.exceptions import UndefinedError

app = Flask(__name__)
app.secret_key = "Hello there "

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CreateForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = RadioField('Role', choices=[('c', 'Customer'), ('s', 'Staff')], default='c')
    submit = SubmitField('Create Account')

class PizzaForm(FlaskForm):
    type = SelectField('Type', choices=[], validators=[DataRequired()])
    crust = SelectField('Crust', choices=[], validators=[DataRequired()])
    size = SelectField('Size', choices=[], validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    price_per = FloatField('Price per Pizza', validators=[DataRequired()])
    order_date = DateField('Order Date', validators=[DataRequired()], format='%Y-%m-%d')
    id = HiddenField()
    submit = SubmitField('Submit')

def load_init_data():
    with open('data/init.json', 'r') as f:
        init_data = json.load(f)
    return init_data

def load_user_data():
    with open('data/users.json', 'r') as f:
        users_data = json.load(f)
    return users_data

def load_pizza_data():
    with open('data/pizzaorders.json', 'r') as f:
        pizza_data = json.load(f)
    return pizza_data

def write_pizza_data(pizza_data):
    with open('data/pizzaorders.json', 'w') as f:
        json.dump(pizza_data, f, indent=4)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        users_data = load_user_data()
        for user in users_data:
            if user['email'] == email and user['password'] == password:
                session['email'] = email
                session['role'] = user['role']
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
        flash('Invalid email or password. Please try again.', 'danger')
    return render_template('login.html', form=form)

@app.route('/create', methods=['GET', 'POST'])
def create():
    form = CreateForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        role = form.role.data
        users_data = load_user_data()
        users_data.append({'email': email, 'password': password, 'role': role})
        with open('data/users.json', 'w') as f:
            json.dump(users_data, f, indent=4)
        flash('Account created successfully! You can now login.', 'success')
        return redirect(url_for('login'))
    return render_template('create.html', form=form)

@app.route('/')
def index():
    if 'email' not in session:
        flash('Please login to view this page.', 'danger')
        return redirect(url_for('login'))
    pizza_data = load_pizza_data()
    return render_template('index.html', pizza_data=pizza_data)

@app.route('/pizza', methods=['GET', 'POST'])
def pizza():
    if 'email' not in session:
        flash('Please login to view this page.', 'danger')
        return redirect(url_for('login'))

    form = PizzaForm()
    init_data = load_init_data()
    form.type.choices = [(t, t) for t in init_data['type']]
    form.crust.choices = [(c, c) for c in init_data['crust']]
    form.size.choices = [(s, s) for s in init_data['size']]

    if request.method == 'POST':
        if form.validate_on_submit():
            pizza_data = load_pizza_data()
            pizza_order = {
                'id': len(pizza_data) + 1,
                'type': form.type.data,
                'crust': form.crust.data,
                'size': form.size.data,
                'quantity': form.quantity.data,
                'price_per': form.price_per.data,
                'order_date': datetime.strptime(form.order_date.data, '%Y-%m-%d').strftime('%Y-%m-%d')
            }
            pizza_data.append(pizza_order)
            write_pizza_data(pizza_data)
            flash('Pizza order placed successfully!', 'success')
            return redirect(url_for('index'))

    return render_template('pizza.html', form=form)

@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('role', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/confirm_delete/<int:order_id>', methods=['GET', 'POST'])
def confirm_delete(order_id):
    if 'email' not in session:
        flash('Please login to view this page.', 'danger')
        return redirect(url_for('login'))

    pizza_data = load_pizza_data()
    order_to_delete = next((order for order in pizza_data if order['id'] == order_id), None)

    if order_to_delete is None:
        flash('Order not found.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        pizza_data = load_pizza_data()
        updated_pizza_data = [order for order in pizza_data if order['id'] != order_id]
        write_pizza_data(updated_pizza_data)
        flash('Order deleted successfully!', 'success')
        return redirect(url_for('index'))

    try:
        return render_template('confirm_delete.html', form=None, order=order_to_delete)
    except UndefinedError:
        return render_template('confirm_delete.html', order=order_to_delete)


@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    if 'email' not in session:
        flash('Please login to view this page.', 'danger')
        return redirect(url_for('login'))
    
    form = PizzaForm()
    init_data = load_init_data()
    form.type.choices = [(t, t) for t in init_data['type']]
    form.crust.choices = [(c, c) for c in init_data['crust']]
    form.size.choices = [(s, s) for s in init_data['size']]
    
    pizza_data = load_pizza_data()
    order_to_edit = [order for order in pizza_data if order['id'] == order_id][0]

    if request.method == 'POST':
        if form.validate_on_submit():
            pizza_data = load_pizza_data()
            updated_orders = []
            for order in pizza_data:
                if order['id'] == order_id:
                    order['type'] = form.type.data
                    order['crust'] = form.crust.data
                    order['size'] = form.size.data
                    order['quantity'] = form.quantity.data
                    order['price_per'] = form.price_per.data
                    order['order_date'] = form.order_date.data.strftime('%Y-%m-%d')  # Ensure correct date format
                updated_orders.append(order)
            write_pizza_data(updated_orders)
            flash('Order updated successfully!', 'success')
            return redirect(url_for('index'))

    form.type.data = order_to_edit['type']
    form.crust.data = order_to_edit['crust']
    form.size.data = order_to_edit['size']
    form.quantity.data = order_to_edit['quantity']
    form.price_per.data = order_to_edit['price_per']
   
    try:
        form.order_date.data = datetime.strptime(order_to_edit['order_date'], '%Y-%m-%d')  
    except ValueError:
        form.order_date.data = datetime.strptime(order_to_edit['order_date'], '%Y/%m/%d')  

    return render_template('edit_order.html', form=form, order=order_to_edit)
if __name__ == '__main__':
    app.run(debug=True, port=8888)

