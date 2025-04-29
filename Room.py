from baseObject import baseObject

class Room(baseObject):
    def __init__(self):
        self.setup()  # Initialize the object with table structure

    def add_room(self, name, room_type, price, description=None, availability_status='available'):
        """Add a new room to the database."""
        self.data = [{
            'name': name,
            'room_type': room_type,
            'price': price,
            'description': description,
            'availability_status': availability_status
        }]
        self.insert()  # Insert the room into the database

    def update_room(self, room_id, name=None, room_type=None, price=None, description=None, availability_status=None):
        """Update an existing room in the database."""
        self.getById(room_id)
        if name:
            self.data[0]['name'] = name
        if room_type:
            self.data[0]['room_type'] = room_type
        if price:
            self.data[0]['price'] = price
        if description:
            self.data[0]['description'] = description
        if availability_status:
            self.data[0]['availability_status'] = availability_status
        self.update()  # Update the room record in the database

    def get_available_rooms(self, room_type, check_in_date, check_out_date):
        sql = """
        SELECT * FROM rooms
        WHERE room_type = %s
        AND id NOT IN (
            SELECT room_id FROM bookings
            WHERE room_id IS NOT NULL
            AND NOT (
                check_out_date <= %s OR check_in_date >= %s
            )
            AND status != 'canceled'
        )
        """
        self.cur.execute(sql, (
            room_type,
            check_in_date, check_out_date
        ))
        return self.cur.fetchall()



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
        
        AND NOT (
    check_out_date <= %s OR check_in_date >= %s
)
        
        AND status != 'canceled'
        """
        self.cur.execute(sql_bookings, (room_type, check_in_date, check_out_date))
        overlapping_bookings_count = self.cur.fetchone()['COUNT(*)']
    
        available_rooms_count = total_rooms - overlapping_bookings_count
    
   
        return available_rooms_count > 0 
     
    

