import pymysql
import yaml
from pathlib import Path


class baseObject:
    def setup(self):
        config = yaml.safe_load(Path("config.yml").read_text())
        self.config = config
        self.tn = self.config['tables'][type(self).__name__]
        self.conn = None
        self.cur = None
        self.pk = None
        self.fields = []
        self.errors = []
        self.data = []
        self.establishConnection()
        self.getFields()
    def establishConnection(self):
        config = self.config
        #print(config)
        self.conn = pymysql.connect(host=config['db']['host'], port=config['db']['port'], user=config['db']['user'],
                       passwd=config['db']['passwd'], db=config['db']['db'], autocommit=True)
        self.cur = self.conn.cursor(pymysql.cursors.DictCursor) 
    def set(self,d):
        self.data.append(d)
    def getFields(self):
        sql = f'''DESCRIBE `{self.tn}`;'''
        self.cur.execute(sql)
        for row in self.cur:
            if row['Extra'] == 'auto_increment':
                self.pk  = row['Field']
            elif row['Field'] != 'created_at':
                self.fields.append(row['Field'])
    def insert(self,n=0):
        count = 0
        vals = []
        sql = f"INSERT INTO `{self.tn}` ("
        for field in self.fields:
            sql += f"`{field}`,"
            vals.append(self.data[n][field])
            count +=1
        sql = sql[0:-1] + ') VALUES ('
        tokens = ("%s," * count)[0:-1]
        sql += tokens + ');'
        #print(sql,vals)
        self.cur.execute(sql,vals)
        self.data[n][self.pk] = self.cur.lastrowid
    def createBlank(self):
        d = {}
        for field in self.fields:
            d[field] = ''
        self.set(d)
    def getById(self,id):
        sql = f"Select * from `{self.tn}` where `{self.pk}` = %s" 
        #print(sql,id)
        self.cur.execute(sql,(id,))
        self.data = []
        for row in self.cur:
            self.data.append(row)
    def getAll(self):
        sql = f"Select * from `{self.tn}`" 
        self.cur.execute(sql)
        self.data = []
        for row in self.cur:
            self.data.append(row)
    def truncate(self):
        sql = f"TRUNCATE TABLE `{self.tn}`" 
        self.cur.execute(sql)
    def getByField(self,field,val):
        sql = f"Select * from `{self.tn}` where `{field}` = %s" 
        #print(sql,val)
        self.cur.execute(sql,(val))
        self.data = []
        for row in self.cur:
            self.data.append(row)
    def update(self,n=0):
        vals=[]
        fvs=''
        for field in self.fields:
            if field in self.data[n].keys():
                fvs += f"`{field}`=%s,"
                vals.append(self.data[n][field])
        fvs=fvs[:-1]
        sql=f"UPDATE `{self.tn}` SET {fvs} WHERE `{self.pk}` = %s"
        vals.append(self.data[n][self.pk])
        #print(sql,vals)
        self.cur.execute(sql,vals)
    def deleteById(self,id):
        sql = f"Delete from `{self.tn}` where `{self.pk}` = %s" 
        self.cur.execute(sql,(id))
    def get_distinct(self, column_name):
        """Get distinct values from a specified column."""
        sql = f"SELECT DISTINCT `{column_name}` FROM `{self.tn}`"
        self.cur.execute(sql)
        return self.cur.fetchall() 
    def get_bookings_by_room_type(self):
        self.cur.execute("""
            SELECT room_type, COUNT(*) AS count
            FROM bookings
            GROUP BY room_type
        """)
        return self.cur.fetchall()

    def get_revenue_by_room_type(self):
        self.cur.execute("""
            SELECT 
                b.room_type,
                COUNT(*) AS bookings,
                ROUND(COUNT(*) * AVG(r.price), 2) AS revenue
            FROM bookings b
            JOIN rooms r ON b.room_type = r.room_type
            WHERE b.status = 'confirmed'
            GROUP BY b.room_type
        """)
        return self.cur.fetchall()


    def get_bookings_over_time(self):
        self.cur.execute("""
            SELECT DATE(check_in_date) AS date, COUNT(*) AS count
            FROM bookings
            GROUP BY DATE(check_in_date)
            ORDER BY date
        """)
        return self.cur.fetchall()


    def get_top_5_guests(self):
        self.cur.execute("""
            SELECT u.name, COUNT(*) AS bookings
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            GROUP BY u.id
            ORDER BY bookings DESC
            LIMIT 5
        """)
        return self.cur.fetchall()
    def get_daily_revenue(self):
        self.cur.execute("""
                    SELECT 
            DATE(b.check_in_date) AS date,
            ROUND(SUM(r.price), 2) AS revenue
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        WHERE b.status = 'confirmed'
        AND b.room_id IS NOT NULL
        GROUP BY DATE(b.check_in_date)
        ORDER BY DATE(b.check_in_date)

        """)
        return self.cur.fetchall()
    def close(self):
        if self.cur:
            self.cur.close()
            self.cur = None
        if self.conn:
            self.conn.close()
            self.conn = None
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


    