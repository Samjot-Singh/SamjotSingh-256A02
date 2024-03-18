# app.py

from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, SelectField, IntegerField, FloatField, DateField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length
import json
import os

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
    order_date = DateField('Order Date', validators=[DataRequired()])
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
    if form.validate_on_submit():
        pizza_data = load_pizza_data()
        pizza_order = {
            'id': len(pizza_data) + 1,
            'type': form.type.data,
            'crust': form.crust.data,
            'size': form.size.data,
            'quantity': form.quantity.data,
            'price_per': form.price_per.data,
            'order_date': form.order_date.data.strftime('%Y/%m/%d')
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

if __name__ == '__main__':
    app.run(debug=True, port=8888)
