from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_from_directory
from application.database import db
from application.models import *
import os
from werkzeug.utils import secure_filename
from datetime import datetime


app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///household_services.db'

app.app_context().push()
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/', methods = ["GET"])
def hello():
    return render_template("home-login-page.html")

@app.route('/logout')
def logout():
    return redirect(url_for('hello'))  

## -------------------------------------------------------------------------------------------------------------------------

# ------------------------------------------------------- ADMIN PAGES ------------------------------------------------------

@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'GET':
        return render_template("adminlogin.html")
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        print(f"Received username: {username}, password: {password}")

        if username == 'admin-sada' and password == '1234':
            print("Login successful")
            return redirect(url_for("admindashboard"))
        else:
            print("Login failed")
            return render_template("loginerror.html")

@app.route('/admindashboard', methods= ['GET'])
def admindashboard():
    if request.method == 'GET':
        services = Service.query.all()
        professionals = ServiceProfessional.query.all()
        service_requests = ServiceRequest.query.all()
        customers = Customer.query.all()
        return render_template("admindashboard.html", services = services, professionals = professionals, service_requests = service_requests, customers = customers)

@app.route('/service/new',methods = ['POST'])
def add_new_service():
    new_name = request.form.get('new_name').title()
    new_base_price = request.form.get('new_base_price')
    new_time_required = request.form.get('new_time_required')
    new_description = request.form['new_description']
    new_service = Service(
        name = new_name,
        base_price= new_base_price,
        time_required = new_time_required,
        descriptions = new_description
        )

    db.session.add(new_service)
    db.session.commit()
    return redirect(url_for('admindashboard'))


@app.route('/service/<int:id>/edit', methods=['POST'])
def edit_service(id):
    service = Service.query.get(id)
     
    if service:
        new_name = request.form.get('name')
        new_base_price = request.form.get('base_price')
        new_time_required = request.form.get('time_required')

        service.name = new_name
        service.base_price = new_base_price
        service.time_required = new_time_required

        try:
            db.session.commit()
            return redirect(url_for('admindashboard'))
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Service Not Found'}), 404

@app.route('/service/<int:id>/delete', methods = ['POST'])
def delete_service(id):
    service = Service.query.get(id)

    if service:
        db.session.delete(service)
        db.session.commit()
        return redirect(url_for('admindashboard'))
    return jsonify({'error': 'Service not found'}), 404

@app.route('/customer/<int:id>/delete', methods = ['POST', 'GET'])
def block_customer(id):
    customer = Customer.query.get(id)

    if customer:
        db.session.delete(customer)
        db.session.commit()
        return redirect(url_for('admindashboard'))
    return jsonify({'error': 'Customer not found'}), 404

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/professional/<int:id>/approve', methods = ['POST'])
def approve_professional(id):
    professional = ServiceProfessional.query.get(id)
    if professional:
        professional.status = 'accepted'

        try:
            db.session.commit()
            return redirect(url_for('admindashboard'))
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    return jsonify({'error': 'Professional not found'}), 401


@app.route('/professional/<int:id>/reject', methods = ['POST'])
def reject_professional(id):
    professional = ServiceProfessional.query.get(id)
    if professional:
        professional.status = 'rejected'

        try:
            db.session.commit()
            return redirect(url_for('admindashboard'))
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    return jsonify({'error': 'Professional not found'}), 401

@app.route('/professional/<int:id>/delete', methods = ['POST'])
def delete_professional(id):
    professional = ServiceProfessional.query.get(id)
    if professional:
        try:
            db.session.delete(professional)
            db.session.commit()
            return redirect(url_for('admindashboard'))
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    return jsonify({'error': 'Professional not found'}), 401

@app.route('/assign_professional/<int:request_id>', methods = ['GET', 'POST'])
def assign_professional(request_id):
    service_request = ServiceRequest.query.get(request_id)
    service_id = service_request.service_id
    professionals = ServiceProfessional.query.filter_by(service_id = service_id).all()

    return render_template('assign_professional.html', professionals = professionals, service_request = service_request)

@app.route('/assign_to_request/<int:request_id>', methods = ['POST'])
def assign_to_request(request_id):
    professional_id = request.form.get('professional_id')
    service_request = ServiceRequest.query.get(request_id)

    service_request.professional_id = professional_id
    service_request.service_status = 'assigned'

    db.session.commit()

    return redirect(url_for('admindashboard'))

@app.route('/admindashboard/viewcustomerprofile/<int:id>', methods=["GET"])
def viewcustomerprofile(id):
    customer = Customer.query.get(id)
    if customer:
        return render_template("viewcustomerprofile.html", customer=customer, customer_id=id)
    else:
        return "Customer Not Found", 404

@app.route('/admindashboard/viewprofessionalprofile/<int:id>', methods=["GET"])
def viewprofessionalprofile(id):
    professional = ServiceProfessional.query.get(id)
    ratings = Rating.query.filter_by(professional_id = id).all()
    if ratings:
        average_rating = sum(rating.rating for rating in ratings) / len(ratings)
    else:
        average_rating = None
    if professional:
        return render_template("viewprofessionalprofile.html", professional=professional, professional_id=id, ratings = ratings, average_rating = average_rating)
    else:
        return "Professional Not Found", 404
    
@app.route('/admindashboard/adminsearchpage', methods=['GET', 'POST'])
def adminsearchpage():
    services = Service.query.all()  
    professionals = [] 

    if request.method == 'POST':
        search_query = request.form.get('search_query', '').strip() 
        service_filter = request.form.get('service_filter', '').strip()  

        query = ServiceProfessional.query

        if search_query:
            query = query.filter(ServiceProfessional.full_name.contains(search_query))

        if service_filter:

            try:
                service_filter_id = int(service_filter)
                query = query.filter(ServiceProfessional.service_id == service_filter_id)
            except ValueError:
                print("Invalid service filter ID")

        professionals = query.all()

    return render_template('adminsearchpage.html', professionals=professionals, services=services)

@app.route('/api/adminsummary', methods=['GET'])
def admin_summary():
    try:
        summary_data = {
            'services': get_total_services(),
            'customers': get_total_customers(),
            'professionals': get_total_professionals(),
            'service_requests': get_total_service_requests()
        }
        return jsonify(summary_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/adminsummary', methods=['GET'])
def render_admin_summary():
    return render_template('adminsummary.html')

@app.route('/delete_professional/<int:id>', methods=['POST'])
def admin_delete_professional(id):
    professional = ServiceProfessional.query.get_or_404(id)
    
    # Ensure that the professional can be safely deleted (optional checks)
    if professional.status == 'accepted':
        return redirect(url_for('admindashboard'))
    
    try:
        db.session.delete(professional)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
    
    return redirect(url_for('admindashboard'))



#-------------------------------------------- END OF ADMIN PAGES --------------------------------------------

# -------------------------------------------- CUSTOMER PAGES --------------------------------------------

@app.route('/customersignup', methods = ['GET', 'POST'])
def customer_signup_page():
    if request.method == 'GET':
        return render_template("customersignup.html")
    elif request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        address = request.form.get('address')
        pincode = request.form.get('pincode')

        customer = Customer(
            email = email,
            password = password,
            full_name = full_name,
            address = address,
            pincode = pincode
        )

        try:
            db.session.add(customer)
            db.session.commit()
            return redirect(url_for('customerlogin'))
        except Exception as e:
            return f"An error occurred: {e}"   
        
@app.route('/customerlogin', methods=["GET", "POST"])
def customerlogin():
    if request.method == 'GET':
        return render_template("customerlogin.html")
    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        customer = Customer.query.filter_by(email=email).first()
    
        if customer is None:
            return jsonify({'error': 'Customer not found'}), 404
        if customer.password == password:
            return redirect(url_for('customerhomepage', id = customer.id))
        else:
            return render_template("loginerror.html")
        

@app.route('/customerhomepage/<int:id>', methods=['GET'])
def customerhomepage(id):
    customer = Customer.query.get(id)
    services = Service.query.all()
    service_requests = ServiceRequest.query.filter_by(cust_id=id).all()

    return render_template("customerhomepage.html", customer=customer, services=services, service_requests=service_requests)

@app.route('/customerhomepage/customerprofile/<int:id>', methods=["GET"])
def customerprofile(id):
    customer = Customer.query.get(id)
    if customer:
        return render_template("customerprofile.html", customer=customer, customer_id=id)
    else:
        return "Customer Not Found", 404

@app.route('/customerhomepage/editcustomerprofile/<int:id>', methods=['GET', 'POST'])
def editcustomerprofile(id):
    customer = Customer.query.get(id)
    if not customer:
        return "Customer Not Found", 404

    if request.method == 'POST':
        customer.full_name = request.form['full_name']
        customer.email = request.form['email']
        customer.password = request.form['password']
        customer.address = request.form['address']
        customer.pincode = request.form['pincode']
        
        db.session.commit()
        return redirect(url_for('customerprofile', id=customer.id))

    return render_template('editcustomerprofile.html', customer=customer)


@app.route('/service/<int:service_id>/<int:customer_id>', methods=['GET', 'POST'])
def servicedetails(service_id, customer_id):
    service = Service.query.get(service_id)
    customer = Customer.query.get(customer_id)
    
    if not service or not customer:
        return "Service or Customer Not Found", 404
    
    if request.method == 'POST':
        service_description = request.form.get('service_description')
        address = request.form.get('address')
        service_now = datetime.now()
        service_date = service_now.date()

        new_request = ServiceRequest(
            service_id=service_id,
            cust_id=customer_id,
            date_of_req=service_date,
            service_status="requested",
            remarks=service_description
        )
        db.session.add(new_request)
        db.session.commit()

        return redirect(url_for('servicedetails', service_id=service_id, customer_id=customer_id))

    return render_template('servicedetails.html', service=service, customer=customer)

@app.route('/rate_service/<int:serv_req_id>', methods=['GET', 'POST'])
def rate_service(serv_req_id):
    service_request = ServiceRequest.query.get(serv_req_id)
    if service_request is None:
        return "Service Request not found", 404

    professional = service_request.professional

    if request.method == 'POST':
        rating_value = float(request.form['rating'])
        review_text = request.form.get('review', '')

        existing_rating = Rating.query.filter_by(
            service_id=service_request.service_id,
            professional_id=service_request.professional_id,
            customer_id=service_request.cust_id,
            serv_req_id=serv_req_id
        ).first()

        if not existing_rating:
            new_rating = Rating(
                service_id=service_request.service_id,
                professional_id=service_request.professional_id,
                customer_id=service_request.cust_id,
                serv_req_id=serv_req_id, 
                rating=rating_value,
                review=review_text,
                rating_status='True' 
            )
            db.session.add(new_rating)
            db.session.commit()
        else:
            existing_rating.rating = rating_value
            existing_rating.review = review_text
            existing_rating.rating_status = 'True'
            db.session.commit()

        return redirect(url_for('customerhomepage', id=service_request.cust_id))

    return render_template('rate_service.html', service_request=service_request)

@app.route('/customerhomepage/<int:customer_id>/search_services', methods=['GET', 'POST'])
def search_services(customer_id):
    if request.method == 'POST':
        pincode = request.form.get('pincode')
        professionals = ServiceProfessional.query.filter_by(pincode=pincode).all()
        return render_template('customer_search_results.html', professionals=professionals, customer_id=customer_id)
    return render_template('customer_search_services.html', customer_id=customer_id)

@app.route('/edit_service_request/<int:serv_req_id>', methods=['GET', 'POST'])
def edit_service_request(serv_req_id):
    service_request = ServiceRequest.query.get(serv_req_id)
    if not service_request:
        return "Service Request not found", 404

    if request.method == 'POST':
        # Update fields
        new_date = request.form.get('new_date')
        remarks = request.form.get('remarks')

        try:
            if new_date:
                service_request.date_of_req = datetime.strptime(new_date, '%Y-%m-%d').date()
            if remarks:
                service_request.remarks = remarks

            db.session.commit()
            return redirect(url_for('customerhomepage', id=service_request.cust_id))
        except Exception as e:
            return f"An error occurred: {e}"

    return render_template('edit_service_request.html', service_request=service_request)



#-------------------------------------------- END OF CUSTOMER PAGES --------------------------------------------

# -------------------------------------------- SERVICE PROFESSIONAL PAGES --------------------------------------------
@app.route('/spsignup', methods = ['GET', 'POST'])
def spsignup():
    if request.method == 'GET':
        services = Service.query.all()
        return render_template('spsignup.html', services = services)
    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        experience = request.form.get('experience')
        file = request.files.get('file_upload')
        service_id = request.form.get('service_id')
        status = "requested"
        
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            profile_doc = filename
        else:
            profile_doc = None
        professional = ServiceProfessional(
            email = email,
            password = password,
            full_name = full_name,
            service_id = service_id,
            experience = experience,
            profile_doc = profile_doc,
            address = address,
            pincode = pincode,
            status = status
        )

        try:
            db.session.add(professional)
            db.session.commit()
            
            return redirect(url_for('reviewpage'))
        except Exception as e:
            return f"An error occurred: {e}"

@app.route('/reviewpage', methods = ['GET'])
def reviewpage():
    return render_template("reviewpage.html")
        
@app.route('/splogin', methods = ['GET', 'POST'])
def splogin():
    if request.method == 'GET':
        return render_template("splogin.html")
    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        professional = ServiceProfessional.query.filter_by(email = email).first()
        print(professional.password)
        if professional is None:
            return jsonify({"Error": "Professional does not exist"}), 404

        if professional.password == password:
            if professional.status == 'accepted':
                return redirect(url_for('sphomepage', id = professional.id))
            elif professional.status == 'rejected':
                return redirect(url_for('rejectedsp'))
            else:
                return jsonify({"Error": f"Your account is in {professional.status} status"}), 403
        else:
            return render_template("loginerror.html")

@app.route('/splogin/rejectedsp', methods = ['GET'])
def rejectedsp():
    return render_template("rejectedsp.html")

@app.route('/sphomepage/<int:id>', methods = ['GET'])
def sphomepage(id):
    professional = ServiceProfessional.query.get(id)
    service_requests = ServiceRequest.query.filter_by(professional_id = id)
    return render_template("sphomepage.html", professional = professional, service_requests = service_requests)

@app.route('/sphomepage/professionalprofile/<int:id>', methods=["GET"])
def professionalprofile(id):
    professional = ServiceProfessional.query.get(id)
    ratings = Rating.query.filter_by(professional_id = id).all()
    if ratings:
        average_rating = sum(rating.rating for rating in ratings) / len(ratings)
    else:
        average_rating = None
    if professional:
        return render_template("spprofile.html", professional=professional, professional_id=id, ratings = ratings, average_rating = average_rating)
    else:
        return "Professional Not Found", 404

@app.route('/sphomepage/editspprofile/<int:id>', methods=['GET', 'POST'])
def editspprofile(id):
    professional = ServiceProfessional.query.get(id)
    if not professional:
        return "Professional Not Found", 404

    if request.method == 'POST':
        professional.full_name = request.form['full_name']
        professional.email = request.form['email']
        professional.password = request.form['password']
        professional.address = request.form['address']
        professional.pincode = request.form['pincode']
        
        db.session.commit()
        return redirect(url_for('professionalprofile', id=professional.id))

    return render_template('editspprofile.html', professional=professional)

@app.route('/complete_service/<int:request_id>', methods = ['GET'])
def complete_service(request_id):
    service_request = ServiceRequest.query.get(request_id)
    service_request.service_status = 'completed'
    professional_id = service_request.professional_id
    dt = datetime.now()
    service_request.date_of_completion = dt.date()

    db.session.commit()

    return redirect(url_for('sphomepage', id = professional_id))

#-------------------------------------------- END OF SERVICE PROFESSIONAL PAGES --------------------------------------------



if __name__ == '__main__':
    app.run(debug=True)