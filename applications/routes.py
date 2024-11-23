from flask import Flask , render_template , request, flash, redirect, url_for, session, abort
from app import app
from applications.models import db, User, Service, ServiceRequest
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os



def auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'User_id' in session:
            return func(*args, **kwargs)
        else:
            flash('Please login to continue')
            return redirect(url_for('login'))
    return inner

def admin_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'User_id' not in session:
            flash('Please login to continue')
            return redirect(url_for('login'))
        user=User.query.get(session['User_id'])
        if not user.is_admin:
            flash('You are not authorized to view this page')
            return redirect(url_for('index'))
        else:
            return func(*args, **kwargs)
    return inner

@app.route('/')
@auth_required     #decorator
def index():
    user=User.query.get(session['User_id'])
    if user.is_admin:
        return redirect(url_for('admin'))
    
    return render_template('index.html')
    #NOTE: This is the done by auth required decorator
    #user_id exist in session
    # if 'User_id' in session:
    #     return render_template('index.html')
    # else:
    #     flash('Please login to continue')
    

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
    
    session['User_id']=user.id
    flash('Login successful')
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
    new_user=User(username=username, passhash=password_hash, name=name, address=adress, pincode=pincode, is_client=True)

    
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
    document = request.files.get('documents')
    adress=request.form.get('address')
    pincode=request.form.get('pincode')
    is_provider=True

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

    file_name=secure_filename(document.filename)
    
    if file_name!="":
            file_exit=os.path.splitext(file_name)[1]
            renamed_file_name=username+file_exit
            if file_exit not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            document.save(os.path.join(app.config['UPLOAD_PATH'],renamed_file_name))

    new_user=User(username=username, passhash=password_hash, name=name, service_type=service_type, experience=experience,address=adress, pincode=pincode, is_provider=True)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('login'))

@app.route('/profile')
@auth_required
def profile():

    user=User.query.get(session['User_id'])
    return render_template('profile.html', user=user)
    # if 'User_id' in session:
    #     user=User.query.get(session['User_id'])
    #     return render_template('profile.html', user=user)
    # else:
    #     flash('Please login to continue')
    

@app.route('/profile', methods=['POST'])
@auth_required
def profile_post():
    username = request.form.get('email')
    curr_password = request.form.get('currentpassword')
    password = request.form.get('newpassword')
    name=request.form.get('name')

    if not username or not curr_password or not password or not name:
        flash('Please fill out all the fields')
        return redirect(url_for('profile'))  
    
    user = User.query.get(session['User_id'])
    if not check_password_hash(user.passhash, curr_password):
        flash('Current password is incorrect')
        return redirect(url_for('profile'))
    
    if username != user.username:
        new_username = User.query.filter_by(username=username).first()
        if new_username:
            flash('Username already exisits')
            return redirect(url_for('profile'))
    
    new_password_hash = generate_password_hash(password)
    user.username = username
    user.passhash = new_password_hash
    user.name = name
    # print(user.username)
    # print(user.name)
    db.session.commit()
    flash('Profile updated successfully')
    return redirect(url_for('profile'))


    

@app.route('/logout')
@auth_required
def logout():
    session.pop('User_id')
    return redirect(url_for('login'))
    

    
#  --------------------------------------Admin Pages--------------------------------------------

@app.route('/admin')
# @auth_required
@admin_required
def admin():
    service=Service.query.all()
    return render_template('admin.html', services=service)

@app.route('/services/add')
# @auth_required
@admin_required
def add_service():
    return render_template('Services/add_services.html')

@app.route('/services/add', methods=['POST'])
def add_service_post():
    name=request.form.get('name')
    price=request.form.get('price')
    description = request.form.get('description')

    if not name or not price or not description:
        flash('Please fill out the feild')
        return redirect(url_for('add_service'))

    new_Service = Service(service_name=name, price=price, description=description)
    db.session.add(new_Service)
    db.session.commit()
    flash('Service added successfully')
    return redirect(url_for('admin'))







@app.route('/services/<int:id>/')
# @admin_required
@auth_required
def show_service(id):
    return "show_service"


@app.route('/services/<int:id>/edit')
# @auth_required
@admin_required
def edit_service(id):
    service=Service.query.get(id)
    if not service:
        flash('Service does not exist')
        return redirect(url_for('admin'))
    
    return render_template('Services/edit_service.html', service=service)

@app.route('/services/<int:id>/edit', methods=['POST'])
@admin_required
def edit_service_post(id):
    service=Service.query.get(id)
    if not service:
        flash('Service does not exist')
        return redirect(url_for('admin'))
    service_name=request.form.get('name')
    price=request.form.get('price')
    description=request.form.get('description')
    if not service_name or not price or not description:
        flash('Please fill out all the fields')

    service.service_name=service_name
    service.price=price
    service.description=description
    db.session.commit()
    flash('Service updated successfully')
    return redirect(url_for('admin'))

@app.route('/services/<int:id>/delete')
# @auth_required
@admin_required
def delete_service(id):
    service = Service.query.get(id)

    return render_template('Services/delete.html', service=service)


@app.route('/services/<int:id>/delete', methods=['POST'])
@admin_required
def delete_service_post(id):
    service = Service.query.get(id)
    if not service:
        flash('Service does not exist')
        return redirect(url_for('admin'))
    db.session.delete(service)
    db.session.commit()
    flash('Service deleted successfully')
    return redirect(url_for('admin'))



    
