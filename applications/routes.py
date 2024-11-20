from flask import Flask , render_template , request, flash, redirect, url_for
from app import app
from applications.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash



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

@app.route('/login', methods=['POST'])
def login_post():
    username=request.form.get('email')
    password=request.form.get('password')
    
    if not username or not password:
        flash('Please fill out all the fields')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('User does not exist')
        return redirect(url_for('login'))
    
    if not check_password_hash(user.passhash, password):
        flash('Password is incorrect')
        return redirect(url_for('login'))
    
    return redirect(url_for('index'))

                        

@app.route('/customer_register', methods=['POST'])
def custRegister_post():
    username=request.form.get('email')
    password=request.form.get('password')
    confirm_password=request.form.get('confirm_password')
    name = request.form.get('fullname')
    adress=request.form.get('address')
    pincode=request.form.get('pincode')

    if not  username or not password or not confirm_password or not name or not adress or not pincode:
       flash('Please fill out the form', 'error')
       return redirect(url_for('custRegister'))

    if password != confirm_password:
        flash('Passwords do not match', 'error')
        return redirect(url_for('custRegister'))
    
    user = User.query.filter_by(username=username).first()

    if user:
        flash('Username already exists', )
        redirect(url_for('custRegister'))
    

    password_hash = generate_password_hash(password)

    new_user=User(username=username, email=username, passhash=password_hash, name=name)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('login'))
    
    


@app.route('/professional_register', methods=['POST'])
def profRegister_post():
    username=request.form.get('email')
    password=request.form.get('password')
    confirm_password=request.form.get('confirm_password')
    name = request.form.get('fullname')
    service_type = request.form.get('service')
    experience = request.form.get('experience')
    document = request.form.get('documents')
    adress=request.form.get('address')
    pincode=request.form.get('pincode')

    if not  username or not password or not confirm_password or not name or not service_type or not experience or not adress or not pincode or not document:
       flash('Please fill out all the feild', 'error')
       return redirect(url_for('profRegister'))
    
    if password != confirm_password:
        return "Passwords do not match!", 400
    
    user=User.query.filter_by(username=username).first()

    if user:
        flash('Username already exists', 'error')
        return redirect(url_for('profRegister'))
    
    password_hash=generate_password_hash(password)

    new_user=User(username=username, email=username, passhash=password_hash, name=name, service_type=service_type, experience=experience, document=document)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('login'))

    
    

