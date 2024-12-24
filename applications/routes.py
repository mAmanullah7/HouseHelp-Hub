from flask import Flask , render_template , request, flash, redirect, url_for, session, abort
from app import app
from applications.models import db, User, Service, ServiceRequest, UserActivity, Review, Report
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime
import os
from sqlalchemy import or_, desc, asc




@app.context_processor 
def inject_user():
    return dict(user=User)


# @auth_required
def auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'User_id' in session:
            return func(*args, **kwargs)
        else:
            flash('Please login to continue')
            return redirect(url_for('login'))
    return inner


# @admin_required
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
def index():
    if 'User_id' in session:
        user = User.query.get(session['User_id'])
        
        if user.is_admin:
            return redirect(url_for('admin'))
        
        if user.is_provider:
            return redirect(url_for('professional_dashboard'))
        
        return redirect(url_for('customer_dashboard'))
    
    return render_template('index.html')
    

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/professional_register')
def profRegister():
    services = Service.query.all()
    return render_template('prof.html', services=services)

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
    
    # Check if user is a professional and not verified
    if user.is_provider and not user.is_verified:
        flash('Your account is pending verification by admin')
        return redirect(url_for('login'))
    
    if user.is_blocked:
        flash('Your account has been blocked. Please contact admin.')
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
    
    

# @app.route('/professional_register', methods=['POST'])
# def profRegister_post():
#     username=request.form.get('email')
#     password=request.form.get('password')
#     confirm_password=request.form.get('confirm_password')
#     name = request.form.get('fullname')
#     service_type = request.form.get('service')
#     experience = request.form.get('experience')
#     document = request.files.get('documents')
#     adress=request.form.get('address')
#     pincode=request.form.get('pincode')


#     service = Service.query.filter_by(service_name=service_type).first()
#     if not service:
#         flash('Invalid service type')
#         return redirect(url_for('profRegister'))
    

#     if not  username or not password or not confirm_password or not name or not service_type or not experience or not adress or not pincode or not document:
#        flash('Please fill out all the feild', 'error')
#        return redirect(url_for('profRegister'))
    
#     if password != confirm_password:
#         return "Passwords do not match!", 400
    
#     user=User.query.filter_by(username=username).first()

#     if user:
#         flash('Username already exists', 'error')
#         return redirect(url_for('profRegister'))
    
#     password_hash=generate_password_hash(password)

#     file_name=secure_filename(document.filename)
    
#     if file_name!="":
#             file_exit=os.path.splitext(file_name)[1]
#             renamed_file_name=username+file_exit
#             if file_exit not in app.config['UPLOAD_EXTENSIONS']:
#                 abort(400)
#             document.save(os.path.join(app.config['UPLOAD_PATH'],renamed_file_name))

#     new_user = User(
#         username=username, 
#         passhash=password_hash, 
#         name=name, 
#         service_type=service_type,
#         service_id=service.id,  # Add service_id
#         experience=experience,
#         address=adress, 
#         pincode=pincode, 
#         is_provider=True
#     )

#     db.session.add(new_user)
#     db.session.commit()
#     return redirect(url_for('login'))

# routes.py

@app.route('/professional_register', methods=['POST'])
def profRegister_post():
    try:
        # Get form data
        username = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('fullname')
        service_type = request.form.get('service')
        experience = request.form.get('experience')
        document = request.files.get('documents')
        address = request.form.get('address')
        pincode = request.form.get('pincode')

        # Basic validation
        if not all([username, password, confirm_password, name, 
                   service_type, experience, address, pincode, document]):
            flash('All fields are required', 'error')
            return redirect(url_for('profRegister'))

        # Check password match
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('profRegister'))

        # Check username uniqueness
        if User.query.filter_by(username=username).first():
            flash('Email already registered', 'error')
            return redirect(url_for('profRegister'))

        # Validate service
        service = Service.query.filter_by(service_name=service_type).first()
        if not service:
            flash('Invalid service selected', 'error')
            return redirect(url_for('profRegister'))

        # Handle file upload
        if document:
            filename = secure_filename(document.filename)
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                flash('Invalid document format. Please upload PDF only', 'error')
                return redirect(url_for('profRegister'))

            new_filename = f"{username}{file_ext}"
            document.save(os.path.join(app.config['UPLOAD_PATH'], new_filename))

        # Create new user
        new_user = User(
            username=username,
            passhash=generate_password_hash(password),
            name=name,
            service_type=service_type,
            service_id=service.id,
            experience=experience,
            address=address,
            pincode=pincode,
            documents=new_filename,
            is_provider=True
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please wait for admin verification', 'success')
        return redirect(url_for('login'))

    except Exception as e:
        db.session.rollback()
        flash('Registration failed', 'error')
        return redirect(url_for('profRegister'))

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
    return redirect(url_for('index'))
    

    
#  --------------------------------------Admin Pages--------------------------------------------

@app.route('/admin')
# @auth_required
@admin_required
def admin():
    service=Service.query.order_by(Service.id).all()
    providers = User.query.filter_by(is_provider=True).all()
    customers = User.query.filter_by(is_client=True).all()
    requests = ServiceRequest.query.order_by(ServiceRequest.date_created.desc()).all()
    ord_service=list(enumerate(service,1))

    return render_template('admin.html', services=ord_service,providers=providers, customers=customers, requests=requests)


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
@admin_required
# @auth_required
def show_service(id):
    service = Service.query.get(id)
    return render_template('Services/show.html', service=service)


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


# ---------------------------- Professional Management Routes ----------------------------

@app.route('/professionals/<int:id>/verify')
@admin_required
def verify_professional(id):
    provider = User.query.filter_by(id=id).first()
    
    # Check if professional exists
    if not provider:
        flash('Professional not found')
        return redirect(url_for('admin'))
        
    return render_template('Professionals/verify.html', provider=provider)


@app.route('/professionals/<int:id>/verify', methods=['POST'])
@admin_required
def verify_professional_post(id):
    provider = User.query.filter_by(id=id).first()
    
    if not provider:
        flash('Professional not found')
        return redirect(url_for('admin'))
    
    provider.is_verified = True
    db.session.commit()
    flash('Professional verified successfully')
    return redirect(url_for('admin'))


@app.route('/professionals/<int:id>/delete') 
@admin_required
def delete_professional(id):
    provider = User.query.filter_by(id=id).first()
    
    if not provider:
        flash('Professional not found')
        return redirect(url_for('admin'))
        
    return render_template('Professionals/delete.html', provider=provider)

@app.route('/admin/toggle-block/<int:user_id>')
@admin_required
def toggle_block(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blocked = not user.is_blocked
    db.session.commit()
    flash(f"User {user.name} {'blocked' if user.is_blocked else 'unblocked'} successfully")
    return redirect(url_for('admin'))


@app.route('/professionals/<int:id>/delete', methods=['POST'])
@admin_required
def delete_professional_post(id):
    provider = User.query.filter_by(id=id).first()
    
    if not provider:
        flash('Professional not found')
        return redirect(url_for('admin'))
        
    # Delete professional
    db.session.delete(provider)
    db.session.commit()
    flash('Professional deleted successfully')
    return redirect(url_for('admin'))



# -----------------------Customer Management Routes------------------------

@app.route('/admin/customers')
@admin_required
def view_customers():
    customers = User.query.filter_by(is_client=True).all()
    return render_template('admin/customers.html', customers=customers)

@app.route('/admin/professionals') 
@admin_required
def view_professionals():
    professionals = User.query.filter_by(is_provider=True).all()
    return render_template('admin/professionals.html', professionals=professionals)

@app.route('/admin/users/<int:id>/toggle_block')
@admin_required
def toggle_user_block(id):
    user = User.query.get_or_404(id)
    user.toggle_block()
    flash(f"User {user.name} has been {'blocked' if user.is_blocked else 'unblocked'}")
    return redirect(request.referrer)

#  ----------------------------  Service Request Management Routes   ----------------------------



@app.route('/requests/<int:id>')
@admin_required
def show_request(id):

    
   
    service_request = ServiceRequest.query.get_or_404(id)

    if not service_request:
        flash('Service request not found')
        return redirect(url_for('admin'))
    
    # Get available verified providers for this service type
    available_providers = User.query.filter_by(
        is_provider=True, 
        is_verified=True,
        service_type=service_request.service.service_name  # Match by service name
    ).all()
    
    return render_template('Requests/show.html', request=service_request, providers=available_providers)



@app.route('/requests/<int:id>/assign', methods=['POST'])
@admin_required
def assign_request(id):
    # Get service request by ID
    service_request = ServiceRequest.query.filter_by(id=id).first()
    
    if not service_request:
        flash('Service request not found')
        return redirect(url_for('admin'))
    
    # Get provider ID from form
    provider_id = request.form.get('provider_id')
    
    if not provider_id:
        flash('Please select a provider')
        return redirect(url_for('show_request', id=id))
    
    # Update request with provider
    service_request.provider_id = provider_id
    service_request.status = 'Assigned'
    db.session.commit()
    flash('Service request assigned successfully')
    
    return redirect(url_for('admin'))




@app.route('/requests/<int:id>/update-status', methods=['POST'])
@admin_required
def update_request_status(id):
    service_request = ServiceRequest.query.filter_by(id=id).first()
    
    if not service_request:
        flash('Service request not found')
        return redirect(url_for('admin'))
    
    status = request.form.get('status')
    
    if not status:
        flash('Please select a status')
        return redirect(url_for('show_request', id=id))
    
    # Update request status
    service_request.status = status
    if status == 'Completed':
        service_request.date_closed = datetime.utcnow()
    db.session.commit()
    flash('Status updated successfully')
    
    return redirect(url_for('admin'))

@app.route('/professional/request/<int:request_id>/update-status', methods=['POST'])
@auth_required
def update_service_status(request_id):
    user = User.query.get(session['User_id'])
    if not user.is_provider:
        flash('Unauthorized access')
        return redirect(url_for('index'))
    
    update_request = ServiceRequest.query.get_or_404(request_id)
    if update_request.provider_id != user.id:
        flash('Unauthorized access')
        return redirect(url_for('professional_dashboard'))
    
    status = request.form.get('status')
    notes = request.form.get('notes')
    
    # Add activity log
    activity = UserActivity(
        user_id=user.id,
        activity_type='status_update',
        description=f"Updated request {request_id} status to {status}: {notes}"
    )
    
    request.status = status
    db.session.add(activity)
    db.session.commit()
    
    flash('Service status updated successfully')
    return redirect(url_for('professional_dashboard'))

@app.route('/professional/request/<int:request_id>/report', methods=['POST'])
@auth_required
def report_issue(request_id):
    user = User.query.get(session['User_id'])
    if not user.is_provider:
        flash('Unauthorized access')
        return redirect(url_for('index'))
    
    request = ServiceRequest.query.get_or_404(request_id)
    if request.provider_id != user.id:
        flash('Unauthorized access')
        return redirect(url_for('professional_dashboard'))
    
    issue_type = request.form.get('issue_type')
    description = request.form.get('description')
    
    report = Report(
        request_id=request_id,
        reported_by_id=user.id,
        issue_type=issue_type,
        description=description
    )
    
    db.session.add(report)
    db.session.commit()
    
    flash('Issue reported successfully')
    return redirect(url_for('professional_dashboard'))

@app.route('/customer/request/<int:request_id>/close', methods=['POST'])
@auth_required
def close_request(request_id):
    request = ServiceRequest.query.get_or_404(request_id)
    
    # Verify the request belongs to current user
    if request.client_id != session['User_id']:
        flash('Unauthorized access')
        return redirect(url_for('customer_dashboard'))
    
    # Only in-progress requests can be closed
    if request.status != 'In Progress':
        flash('Only in-progress requests can be closed')
        return redirect(url_for('customer_dashboard'))
    
    request.status = 'Completed'
    request.date_closed = datetime.utcnow()
    
    db.session.commit()
    flash('Service request closed successfully')
    return redirect(url_for('customer_dashboard'))



# routes.py - Update professional dashboard route
@app.route('/professional/dashboard')
@auth_required
def professional_dashboard():
    user = User.query.get(session['User_id'])
    if not user.is_provider:
        flash('Unauthorized access')
        return redirect(url_for('index'))
    
    # Get pending requests for provider's service type
    pending_requests = ServiceRequest.query.filter_by(
        req_type=user.service_type,
        status='Pending'
    ).order_by(ServiceRequest.date_created.desc()).all()

    active_requests = ServiceRequest.query.filter_by(
        provider_id=user.id,
        status='In Progress'
    ).order_by(ServiceRequest.date_created.desc()).all()
    
    
    # Get provider's assigned/completed requests
    completed_requests = ServiceRequest.query.filter_by(
        provider_id=user.id,
        status = 'Completed'
    ).order_by(ServiceRequest.date_created.desc()).all()
    
    # print(f"Found {len(pending_requests)} pending requests")
    # print(f"Found {len(completed_requests)} completed requests")
    
    return render_template('Professionals/dashboard.html',
                         user=user,
                         pending_requests=pending_requests,
                         active_requests=active_requests,
                         completed_requests=completed_requests)
    

@app.route('/professional/request/<int:id>', methods=['POST'])
@auth_required
def handle_request(id):
    user = User.query.get(session['User_id'])
    if not user.is_provider:
        flash('Unauthorized access')
        return redirect(url_for('index'))
    
    service_request = ServiceRequest.query.get_or_404(id)
    action = request.form.get('action')

    if action == 'accept':
        service_request.status = 'In Progress'
        service_request.provider_id = user.id

    elif action == 'reject':
        service_request.status = 'Rejected'
  

    db.session.commit()
    return redirect(url_for('professional_dashboard'))

@app.route('/professional/request/<int:id>/complete', methods=['POST'])
@auth_required
def complete_request(id):
    user = User.query.get(session['User_id'])
    if not user.is_provider:
        flash('Unauthorized access')
        return redirect(url_for('index'))
    
    request = ServiceRequest.query.get_or_404(id)
    request.status = 'Completed'
    request.date_closed = datetime.utcnow()
    
    db.session.commit()
    flash('Service request marked as completed')
    return redirect(url_for('professional_dashboard'))


# ------------------   Customer Routes    -------------------


# routes.py

@app.route('/customer/dashboard')
@auth_required
def customer_dashboard():
    user = User.query.get(session['User_id'])
    if not user.is_client:
        flash('Unauthorized access')
        return redirect(url_for('index'))
    
    # Get all services
    services = Service.query.all()
    
    # Get user's service requests
    service_requests = ServiceRequest.query.filter_by(client_id=user.id).order_by(ServiceRequest.date_created.desc()).all()
    
    return render_template('customer/dashboard.html', 
                         user=user,
                         services=services,
                         requests=service_requests)

@app.route('/customer/service/request/<int:service_id>', methods=['POST'])
@auth_required
def request_service(service_id):
    user = User.query.get(session['User_id'])
    if not user.is_client:
        flash('Unauthorized access')
        return redirect(url_for('index'))
    
    description = request.form.get('description')
    service = Service.query.get_or_404(service_id)
    
    new_request = ServiceRequest(
        service_id=service_id,
        client_id=user.id,
        req_type=service.service_name,
        description=description,
        status='Pending'
    )
    
    db.session.add(new_request)
    db.session.commit()
    
    flash('Service request submitted successfully')
    return redirect(url_for('customer_dashboard'))


@app.route('/customer/request/<int:request_id>/rate', methods=['POST'])
@auth_required
def rate_service(request_id):
    user = User.query.get(session['User_id'])
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    if service_request.client_id != user.id:
        flash('Unauthorized access')
        return redirect(url_for('customer_dashboard'))
    
    rating = float(request.form.get('rating'))
    review = request.form.get('review')
    
    service_request.rating_by_client = rating
    service_request.review_by_client = review
    
    provider = service_request.provider
    if provider:
        # Update provider's average rating
        total_ratings = provider.rating_count * provider.avg_rating + rating
        provider.rating_count += 1
        provider.avg_rating = total_ratings / provider.rating_count
    
    db.session.commit()
    flash('Thank you for your rating!')
    return redirect(url_for('customer_dashboard'))


@app.route('/customer/review/<int:review_id>/report', methods=['POST'])
@auth_required
def report_review(review_id):
    review = Review.query.get_or_404(review_id)
    review.reported = True
    db.session.commit()
    flash('Review reported successfully')
    return redirect(url_for('professional_dashboard'))



# ------------------   Searching   -------------------

@app.route('/admin/search')
@admin_required
def admin_search():
    search_type = request.args.get('search_type', 'all')
    keyword = request.args.get('keyword', '')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    status = request.args.get('status')
    rating = request.args.get('rating')
    sort_by = request.args.get('sort_by', 'name_asc')

    # Services search
    if search_type == 'services':
        query = Service.query.filter(
            or_(
                Service.service_name.ilike(f'%{keyword}%'),
                Service.description.ilike(f'%{keyword}%')
            )
        )
        # Sort services
        if sort_by == 'name_asc':
            query = query.order_by(Service.service_name.asc())
        elif sort_by == 'name_desc':
            query = query.order_by(Service.service_name.desc())
        elif sort_by == 'price_asc':
            query = query.order_by(Service.price.asc())
        elif sort_by == 'price_desc':
            query = query.order_by(Service.price.desc())

    # Professionals search
    elif search_type == 'professionals':
        query = User.query.filter_by(is_provider=True).filter(
            or_(
                User.name.ilike(f'%{keyword}%'),
                User.username.ilike(f'%{keyword}%'),
                User.service_type.ilike(f'%{keyword}%')
            )
        )
        if rating:
            query = query.filter(User.avg_rating >= float(rating))
        
        if sort_by == 'name_asc':
            query = query.order_by(User.name.asc())
        elif sort_by == 'name_desc':
            query = query.order_by(User.name.desc())
        elif sort_by in ['rating_desc', 'rating_asc']:
            direction = desc if sort_by == 'rating_desc' else asc
            query = query.order_by(direction(User.avg_rating))

    # Service requests search
    elif search_type == 'requests':
        query = ServiceRequest.query
        if keyword:
            query = query.join(Service).filter(
                or_(
                    Service.service_name.ilike(f'%{keyword}%'),
                    ServiceRequest.description.ilike(f'%{keyword}%')
                )
            )
        
        if date_from:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(ServiceRequest.date_created >= date_from)
        if date_to:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(ServiceRequest.date_created <= date_to)
        
        if status:
            query = query.filter(ServiceRequest.status == status)
        
        if sort_by in ['date_desc', 'date_asc']:
            direction = desc if sort_by == 'date_desc' else asc
            query = query.order_by(direction(ServiceRequest.date_created))

    # Customers search
    else:
        query = User.query.filter_by(is_client=True).filter(
            or_(
                User.name.ilike(f'%{keyword}%'),
                User.username.ilike(f'%{keyword}%')
            )
        )
        if sort_by in ['name_desc', 'name_asc']:
            direction = desc if sort_by == 'name_desc' else asc
            query = query.order_by(direction(User.name))

    results = query.all()
    return render_template('admin_search.html', 
                         results=results,
                         search_type=search_type,
                         keyword=keyword,
                         date_from=date_from,
                         date_to=date_to,
                         status=status,
                         rating=rating,
                         sort_by=sort_by)



@app.route('/professional/search')
@auth_required
def professional_search():
    # Get search parameters
    current_user = User.query.get(session['User_id'])
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    location = request.args.get('location', '')
    pincode = request.args.get('pincode', '')
    status = request.args.get('status')
    sort_by = request.args.get('sort_by', 'date_desc')

    # Base query with aliased joins
    query = ServiceRequest.query\
        .filter(ServiceRequest.provider_id == current_user.id)

    # Apply filters with proper table aliases
    if location or pincode:
        query = query.join(User, ServiceRequest.client_id == User.id)
        
        if location:
            query = query.filter(User.address.ilike(f'%{location}%'))
        if pincode:
            query = query.filter(User.pincode == pincode)

    if date_from:
        query = query.filter(ServiceRequest.date_created >= datetime.strptime(date_from, '%Y-%m-%d'))
    if date_to:
        query = query.filter(ServiceRequest.date_created <= datetime.strptime(date_to, '%Y-%m-%d'))
    if status:
        query = query.filter(ServiceRequest.status == status)

    # Apply sorting
    if sort_by == 'date_desc':
        query = query.order_by(ServiceRequest.date_created.desc())
    elif sort_by == 'date_asc':
        query = query.order_by(ServiceRequest.date_created.asc())
    elif sort_by == 'status':
        query = query.order_by(ServiceRequest.status)

    results = query.all()
    return render_template('professionals/professional_search.html', 
                         results=results,
                         date_from=date_from,
                         date_to=date_to,
                         location=location,
                         pincode=pincode,
                         status=status,
                         sort_by=sort_by)


# routes.py
@app.route('/customer/search')
@auth_required
def customer_search():
    # Get search parameters
    service_name = request.args.get('service_name', '')
    pincode = request.args.get('pincode', '')
    price_min = request.args.get('price_min', type=int)
    price_max = request.args.get('price_max', type=int)
    rating = request.args.get('rating', type=int)
    sort_by = request.args.get('sort_by', 'rating_desc')

    # Base query
    query = Service.query

    # Apply filters
    if service_name:
        query = query.filter(Service.service_name.ilike(f'%{service_name}%'))
    
    if price_min:
        query = query.filter(Service.price >= price_min)
    if price_max:
        query = query.filter(Service.price <= price_max)

    # Apply sorting
    if sort_by == 'price_asc':
        query = query.order_by(Service.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Service.price.desc())
    elif sort_by == 'name_asc':
        query = query.order_by(Service.service_name.asc())
    
    services = query.all()

    # Filter providers by pincode and rating if specified
    if pincode or rating:
        for service in services:
            filtered_providers = []
            for provider in service.providers:
                if provider.is_verified and not provider.is_blocked:
                    if pincode and str(provider.pincode) != str(pincode):
                        continue
                    if rating and provider.avg_rating < rating:
                        continue
                    filtered_providers.append(provider)
            service.filtered_providers = filtered_providers
    else:
        for service in services:
            service.filtered_providers = [p for p in service.providers if p.is_verified and not p.is_blocked]

    return render_template('customer/customer_search.html',
                         services=services,
                         service_name=service_name,
                         pincode=pincode,
                         price_min=price_min,
                         price_max=price_max,
                         rating=rating,
                         sort_by=sort_by)



# ----------------------- SUmmary ----------------------------

@app.route('/admin/summary')
@admin_required
def admin_summary():
    # Get statistics
    total_customers = User.query.filter_by(is_client=True).count()
    total_providers = User.query.filter_by(is_provider=True).count()
    total_services = Service.query.count()
    
    # Get service requests statistics
    total_requests = ServiceRequest.query.count()
    pending_requests = ServiceRequest.query.filter_by(status='Pending').count()
    active_requests = ServiceRequest.query.filter_by(status='In Progress').count()
    completed_requests = ServiceRequest.query.filter_by(status='Completed').count()
    
    # Get top rated professionals
    top_professionals = User.query.filter_by(is_provider=True)\
        .order_by(User.avg_rating.desc())\
        .limit(5).all()
    
    # Get most requested services
    service_stats = db.session.query(
        Service.service_name,
        db.func.count(ServiceRequest.id).label('request_count')
    ).join(ServiceRequest)\
     .group_by(Service.service_name)\
     .order_by(db.desc('request_count'))\
     .limit(5).all()
    
    return render_template('admin_summary.html',
                         total_customers=total_customers,
                         total_providers=total_providers,
                         total_services=total_services,
                         total_requests=total_requests,
                         pending_requests=pending_requests,
                         active_requests=active_requests,
                         completed_requests=completed_requests,
                         top_professionals=top_professionals,
                         service_stats=service_stats)


@app.route('/professional/summary')
@auth_required
def professional_summary():
    current_user = User.query.get(session['User_id'])
    
    # Basic stats with explicit status checks
    total_requests = ServiceRequest.query.filter_by(provider_id=current_user.id).count()
    completed_requests = ServiceRequest.query.filter_by(
        provider_id=current_user.id, 
        status='Completed'
    ).count()
    active_requests = ServiceRequest.query.filter_by(
        provider_id=current_user.id, 
        status='Assigned'
    ).count()
    pending_requests = ServiceRequest.query.filter_by(
        provider_id=current_user.id, 
        status='Pending'
    ).count()

    rejected_requests = ServiceRequest.query.filter_by(
        provider_id=current_user.id,
        status='Rejected'
    )
    
    # Calculate completion rate
    completion_rate = (completed_requests / total_requests * 100) if total_requests > 0 else 0
    
    # Get weekly stats using SQLite strftime
    weekly_stats = db.session.query(
        db.func.strftime('%W', ServiceRequest.date_created).label('week'),
        db.func.count(ServiceRequest.id).label('count')
    ).filter(
        ServiceRequest.provider_id == current_user.id,
        ServiceRequest.date_created >= db.func.datetime('now', '-8 weeks')
    ).group_by('week')\
     .order_by('week')\
     .all()
    
    # Format weeks for better display
    formatted_weekly_stats = [
        {'week': f"Week {stat.week}", 'count': stat.count}
        for stat in weekly_stats
    ]
    
    # Recent reviews with rating
    recent_reviews = ServiceRequest.query.filter(
        ServiceRequest.provider_id == current_user.id,
        ServiceRequest.rating_by_client > 0
    ).order_by(ServiceRequest.date_closed.desc())\
     .limit(5).all()
    
    return render_template('Professionals/summary.html',
                         total_requests=total_requests,
                         completed_requests=completed_requests,
                         active_requests=active_requests,
                         pending_requests=pending_requests,
                         completion_rate=completion_rate,
                         weekly_stats=formatted_weekly_stats,
                         recent_reviews=recent_reviews,
                         avg_rating=current_user.avg_rating,
                         rejected_requests=rejected_requests)


@app.route('/customer/summary')
@auth_required
def customer_summary():
    current_user = User.query.get(session['User_id'])
    
    # Basic request statistics
    total_requests = ServiceRequest.query.filter_by(client_id=current_user.id).count()
    pending_requests = ServiceRequest.query.filter_by(
        client_id=current_user.id,
        status='Pending'
    ).count()
    active_requests = ServiceRequest.query.filter_by(
        client_id=current_user.id,
        status='In Progress'
    ).count()
    completed_requests = ServiceRequest.query.filter_by(
        client_id=current_user.id,
        status='Completed'
    ).count()

    # Get most used services
    service_usage = db.session.query(
        Service.service_name,
        db.func.count(ServiceRequest.id).label('usage_count')
    ).join(ServiceRequest)\
     .filter(ServiceRequest.client_id == current_user.id)\
     .group_by(Service.service_name)\
     .order_by(db.desc('usage_count'))\
     .limit(5).all()

    # Recent service requests
    recent_requests = ServiceRequest.query.filter_by(client_id=current_user.id)\
        .order_by(ServiceRequest.date_created.desc())\
        .limit(5).all()

    # Get weekly request stats
    weekly_stats = db.session.query(
        db.func.strftime('%W', ServiceRequest.date_created).label('week'),
        db.func.count(ServiceRequest.id).label('count')
    ).filter(
        ServiceRequest.client_id == current_user.id,
        ServiceRequest.date_created >= db.func.datetime('now', '-8 weeks')
    ).group_by('week')\
     .order_by('week')\
     .all()

    formatted_weekly_stats = [
        {'week': f"Week {stat.week}", 'count': stat.count}
        for stat in weekly_stats
    ]

    return render_template('customer/summary.html',
                         total_requests=total_requests,
                         pending_requests=pending_requests,
                         active_requests=active_requests, 
                         completed_requests=completed_requests,
                         service_usage=service_usage,
                         recent_requests=recent_requests,
                         weekly_stats=formatted_weekly_stats)