from baseObject import baseObject
from datetime import datetime

class Booking(baseObject):
    def __init__(self):
        self.setup()  # Setup base object, fetch table name and initialize the connection

    def create_booking(self, user_id, room_type, check_in_date, check_out_date, room_id=None, status='pending'):
        """Create a new booking request."""
        self.data = [{
            'user_id': user_id,
            'room_type': room_type,
            'check_in_date': check_in_date,
            'check_out_date': check_out_date,
            'status': status,
            'room_id': room_id  
        }]
        self.insert()
  # Insert the booking into the database

    def update_booking(self, booking_id, status):
        """Update the status of a booking."""
        self.getById(booking_id)
        self.data[0]['status'] = status
        self.update()  

    def get_user_bookings(self, user_id):
        """Fetch all bookings made by a specific user."""
        self.getByField('user_id', user_id)
        return self.data

    def get_pending_bookings(self):
        """Fetch all bookings that are pending approval."""
        sql = f"SELECT * FROM `{self.tn}` WHERE `status` = 'pending'"
        self.cur.execute(sql)
        return self.cur.fetchall()
     
    def assign_room_to_booking(self, booking_id, room_id):
        
        self.getById(booking_id)
        self.data[0]['room_id'] = room_id
        self.data[0]['status'] = 'confirmed'
        self.update() 
    def check_room_availability(self, room_type, check_in_date, check_out_date):
        
       
        sql_rooms = """
        SELECT COUNT(*) 
        FROM rooms 
        WHERE room_type = %s
        """
        self.cur.execute(sql_rooms, (room_type,))
        total_rooms = self.cur.fetchone()['COUNT(*)']
        
  
        sql_bookings = """
        SELECT COUNT(*) 
        FROM bookings 
        WHERE room_type = %s
        AND (
            (check_in_date BETWEEN %s AND %s) OR
            (check_out_date BETWEEN %s AND %s)
        )
        AND status != 'canceled'
        """
        self.cur.execute(sql_bookings, (room_type, check_in_date, check_out_date, check_in_date, check_out_date))
        overlapping_bookings_count = self.cur.fetchone()['COUNT(*)']
    
        available_rooms_count = total_rooms - overlapping_bookings_count
    
   
        return available_rooms_count > 0  
    
    def save_guest_request(self, user_id, booking_id, message):
        sql = """INSERT INTO requests (user_id, booking_id, message, created_at)
        VALUES (%s, %s, %s, NOW())
        """
        self.cur.execute(sql, (user_id, booking_id, message))
        self.conn.commit()
    def get_unresolved_requests(self):
        sql = """
        SELECT r.id, r.booking_id, r.user_id, r.message, r.created_at, u.name AS user_name
        FROM requests r
        JOIN users u ON r.user_id = u.id
        WHERE r.status IS NULL OR r.status != 'resolved'
        ORDER BY r.created_at DESC
        """
        self.cur.execute(sql)
        return self.cur.fetchall()
    def mark_request_resolved(self, request_id):
        sql = "UPDATE requests SET status = 'resolved' WHERE id = %s"
        self.cur.execute(sql, (request_id,))
        self.conn.commit()

