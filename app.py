from flask import Flask, request, redirect, flash, session, url_for
from flask import render_template
from flask import request,session, redirect,send_from_directory,make_response 
from flask_session import Session
from datetime import timedelta
from user import user
from Room import Room
from Booking import Booking
import time
import datetime
from datetime import datetime
from flask import jsonify
#create Flask app instance
app = Flask(__name__,static_url_path='')

#Configure serverside sessions 
app.config['SECRET_KEY'] = '56hdtryhRTg'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
sess = Session()
sess.init_app(app)




@app.context_processor
def inject_user():
    return dict(me=session.get('user'))

'''
- DDL (init) script
- MyISAM engine
- no referential integrity in create statement

TODO:
-show login form
-check login on submit
    -set session if login ok
-redirect to menu
-check session on login required pages
'''
@app.route('/')

def home():
    
    return render_template('home.html')
@app.route('/about')

def about():
    
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = user()
        action = request.form.get('action')
        if action == 'login':
            name = request.form.get('name')
            password = request.form.get('password')
            if u.tryLogin(name, password):
                session['user'] = u.data[0]
                session['active'] = time.time()
                flash('Login successful!', 'success')
                return redirect(url_for('main'))
            else:
                flash('Incorrect username or password.', 'error')
                return redirect(url_for('login'))

        elif action == 'register':
            name = request.form.get('name')
            password = request.form.get('password')
            password2 = request.form.get('password2')
            role = 'guest'
            u.data = [{'name': name, 'password': password, 'password2': password2, 'role': role}]
            if u.verify_new():
                u.insert()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Registration failed. Please check the provided details.', 'error')
                return redirect(url_for('login'))

    else:
        return render_template('login.html')

 
    
@app.route('/logout',methods = ['GET','POST'])
def logout():
    if session.get('user') is not None:
        del session['user']
        del session['active']
    return render_template('login.html', title='Login', msg='You have logged out.')

@app.route('/mainAdmin')
def main():
    if checkSession() == False: 
        return redirect('/login')
    user = session.get('user')
    if session['user']['role'] == 'admin':
        return render_template('main.html', title='Main menu') 
    else:
        return render_template('guest_menu.html', title='Main menu',user=user ) 
@app.route('/users/manage', methods=['GET', 'POST'])
def manage_user():
    if not checkSession() or session['user']['role'] != 'admin': 
        return redirect('/login')

    o = user()

    try:
        action = request.args.get('action')
        pkval = request.args.get('pkval')

        if action == 'delete' and pkval:
            o.deleteById(pkval)
            return render_template('ok_dialog.html', msg="Deleted.")

        elif action == 'insert' and request.method == 'POST':
            d = {
                'name': request.form.get('name'),
                'role': request.form.get('role'),
                'password': request.form.get('password'),
                'password2': request.form.get('password2')
            }
            o.set(d)
            if o.verify_new():
                o.insert()
                return render_template('ok_dialog.html', msg="User added.")
            else:
                return render_template('users/add.html', obj=o)

        elif action == 'update' and request.method == 'POST' and pkval:
            o.getById(pkval)
            if not o.data:
                flash("User not found.", "danger")
                return redirect('/users/manage')

            o.data[0]['name'] = request.form.get('name')
            o.data[0]['role'] = request.form.get('role')
            o.data[0]['password'] = request.form.get('password')
            o.data[0]['password2'] = request.form.get('password2')

            if o.verify_update():
                o.update()
                return render_template('ok_dialog.html', msg="User updated.")
            else:
                return render_template('users/manage.html', obj=o)

        elif pkval == 'new':
            o.createBlank()
            return render_template('users/add.html', obj=o)

        elif pkval:
            o.getById(pkval)
            if not o.data:
                flash("User not found.", "danger")
                return redirect('/users/manage')
            return render_template('users/manage.html', obj=o)

        else:
            o.getAll()
            return render_template('users/list.html', objs=o)

    finally:
        o.close()

@app.route('/check_availability')
def check_availability():
    room_type = request.args.get('room_type')
    check_in_date = request.args.get('check_in_date')
    check_out_date = request.args.get('check_out_date')

    try:
        check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d')
        check_out_date = datetime.strptime(check_out_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    room = Room()
    is_available = room.check_room_availability(room_type, check_in_date, check_out_date)

    return jsonify({
        'available': is_available,
        'login_required': not checkSession(),  # or use current_user.is_authenticated
        'message': (
            "✅ Room is available, but please log in to proceed with booking."
            if not checkSession() else
            "✅ Room is available. You can proceed to booking."
        )
    })
@app.route("/availability")
def availability():
    room = Room()
    room_types = room.get_distinct('room_type')  
    print("ROOM TYPES BEING SENT:", [r['room_type'] for r in room_types])  

    return render_template("availability.html", room_types=room_types)

@app.route('/contact')
def contact_page():
    return render_template('contact.html')


@app.route('/check_in', methods=['GET', 'POST'])
def check_in():
    if  not checkSession() or 'user' not in session:
        flash('You must be logged in to make a booking.', 'danger')
        return redirect('/login')  

    room = Room()  
    booking = Booking()  
    
    if request.method == 'POST':
        
        room_type = request.form['room_type']
        check_in_date = request.form['check_in_date']
        check_out_date = request.form['check_out_date']
        
        
        try:
            check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d')
            check_out_date = datetime.strptime(check_out_date, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return redirect('/check_in')
        
        if check_in_date >= check_out_date:
            flash('Check-out date must be after check-in date.', 'danger')
            return redirect('/check_in')

        
        if not room.check_room_availability(room_type, check_in_date, check_out_date):
            flash('No rooms available for the selected dates and room type.', 'danger')
            return redirect('/check_in')
        
    
        booking.create_booking(
            user_id=session['user']['id'],
            room_type=room_type,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            room_id=None  
        )
        
        flash('Your booking request has been submitted for approval.', 'success')
        return render_template('customer_success.html', user=session['user'])
    
    
    distinct_room_types = room.get_distinct('room_type')

    return render_template('check_in.html', room_types=distinct_room_types)


@app.route('/rooms/manage', methods=['GET', 'POST'])
def manage_room():
    if not checkSession() or session['user']['role'] != 'admin':
        return redirect('/login')

    o = Room()
    action = request.args.get('action')
    pkval = request.args.get('pkval')

    # Delete a room
    if action and action == 'delete':
        o.deleteById(pkval)
        return render_template('ok_dialog.html', msg="Room deleted.")

    # Insert new room

    if action and action == 'insert':
        d = {
            'name': request.form.get('name'),
            'room_type': request.form.get('room_type'),  # fixed key
            'price': request.form.get('price'),
            'description': request.form.get('description'),
            'availability_status': request.form.get('availability_status')
        }
        o.set(d)
        o.insert()
        return render_template('ok_dialog.html', msg="Room added.")

# Update room
    if action and action == 'update':
        o.getById(pkval)
        o.data[0]['name'] = request.form.get('name')
        o.data[0]['room_type'] = request.form.get('room_type')  # fixed key
        o.data[0]['price'] = request.form.get('price')
        o.data[0]['description'] = request.form.get('description')
        o.data[0]['availability_status'] = request.form.get('availability_status')
        o.update()
        return render_template('ok_dialog.html', msg="Room updated.")            
    # List all rooms
    if pkval is None:
        o.getAll()
        return render_template('rooms/list.html', objs=o)


    if pkval == 'new':
        o.createBlank()
        return render_template('rooms/add.html', obj=o)

    
    o.getById(pkval)
    return render_template('rooms/manage.html', obj=o)

@app.route('/bookings/manage', methods=['GET', 'POST'])
def manage_booking():
    if not checkSession() or session['user']['role'] != 'admin':
        return redirect('/login')

    o = Booking()
    action = request.args.get('action')
    pkval = request.args.get('pkval')

    
    if action and action == 'delete':
        o.deleteById(pkval)
        return render_template('ok_dialog.html', msg="Booking deleted.")

    
    if action and action == 'insert':
        d = {
            'user_id': request.form.get('user_id'),
            'room_type': request.form.get('room_type'),
            'check_in_date': request.form.get('check_in_date'),
            'check_out_date': request.form.get('check_out_date'),
            'status': 'pending',
            'room_id':  "NULL"
        }
        o.set(d)
        if o.verify_new():
            o.insert()
            return render_template('ok_dialog.html', msg="Booking added.")
        else:
            return render_template('bookings/add.html', obj=o)

    
    if action and action == 'update':
        o.getById(pkval)
        o.data[0]['user_id'] = request.form.get('user_id')
        o.data[0]['room_type'] = request.form.get('room_type')
        o.data[0]['check_in_date'] = request.form.get('check_in_date')
        o.data[0]['check_out_date'] = request.form.get('check_out_date')
        o.data[0]['status'] = request.form.get('status')
        o.update()
        return render_template('ok_dialog.html', msg="Booking updated.")


    if pkval is None:
        o.getAll()
        return render_template('bookings/list.html', objs=o)

    
    if pkval == 'new':
        o.createBlank()
        return render_template('bookings/add.html', obj=o)

    
    o.getById(pkval)
    return render_template('bookings/manage.html', obj=o)



@app.route('/admin/confirm_booking', methods=['GET', 'POST'])
def admin_confirm_booking():
    if 'user' not in session or session['user']['role'] != 'admin':
        flash('You must be logged in as an admin to confirm bookings.', 'danger')
        return redirect('/login')

    booking = Booking()
    room = Room()

    # Load bookings and requests
    pending_bookings = booking.get_pending_bookings()
    guest_requests = booking.get_unresolved_requests()

    available_rooms_dict = {}
    for pending_booking in pending_bookings:
        room_type = pending_booking['room_type']
        check_in_date = pending_booking['check_in_date']
        check_out_date = pending_booking['check_out_date']
        available_rooms_dict[pending_booking['id']] = room.get_available_rooms(
            room_type, check_in_date, check_out_date
        )

    # Confirm room booking
    if request.form.get('action') == 'confirm_booking':
        booking_id = request.form['booking_id']
        room_id = request.form['room_id']
        booking.assign_room_to_booking(booking_id, room_id)
        flash('The booking has been confirmed and a room has been assigned.', 'success')
        return redirect('/admin/confirm_booking')

    # Mark request as resolved
    if request.form.get('action') == 'resolve_request':
        request_id = request.form['request_id']
        booking.mark_request_resolved(request_id)
        flash('Guest request marked as fulfilled.', 'success')
        return redirect('/admin/confirm_booking')

    return render_template('admin_confirm_booking.html',
                           pending_bookings=pending_bookings,
                           available_rooms_dict=available_rooms_dict,
                           guest_requests=guest_requests)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


def checkSession():
    if 'active' in session.keys():
        timeSinceAct = time.time() - session['active']
        print(timeSinceAct)
        if timeSinceAct > 500:
            session['msg'] = 'Your session has timed out.'
            return False
        else:
            session['active'] = time.time()
            return True
    else:
        return False   

@app.route('/guest/dashboard', methods=['GET', 'POST'])
def guest_dashboard():
    if not checkSession() or 'user' not in session or session['user']['role'] != 'guest':
        flash('Please log in as a guest to access the dashboard.', 'danger')
        return redirect('/login')

    user_id = session['user']['id']
    booking = Booking()
    bookings = booking.get_user_bookings(user_id)

    if request.method == 'POST':
        booking_id = request.form.get('booking_id')
        message = request.form.get('message')

        if booking_id and message.strip():
            booking.save_guest_request(user_id, booking_id, message.strip())
            flash("Your request has been submitted successfully!", "success")
        else:
            flash("Please enter a message before submitting.", "danger")

    return render_template('guest_dashboard.html', bookings=bookings)
@app.route('/admin/Adashboard')
def admin_dashboard():
    if not checkSession() or session['user']['role'] != 'admin':
        flash('Admin access required.', 'danger')
        return redirect('/login')

    booking = Booking()
    data = {
        "bookings_by_room_type": booking.get_bookings_by_room_type(),
        "revenue_by_room_type": booking.get_revenue_by_room_type(),
        "bookings_over_time": booking.get_bookings_over_time(),
        "top_guests": booking.get_top_5_guests(),
        "daily_revenue": booking.get_daily_revenue()
    }

    return render_template("Admin_dashboard.html", data=data)

     
  
if __name__ == '__main__':
   app.run(host='127.0.0.1',debug=True)   