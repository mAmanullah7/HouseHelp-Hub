from flask import Flask , render_template
from app import app


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/professional_register')
def profRegister():
    return render_template('prof.html')

@app.route('/customer_register')
def custRegister():
    return render_template('customer.html')




