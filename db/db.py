import sqlalchemy as db
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime


'''
CODE AÇIKLAMASI
---------------
1- Mysql üzerinden yeni bir database yarat. Adını 'AI_390' koy
2- mysql+pymysql://{mysql_kullanıcı_adı}:{mysql_kullanıcı_şifren}@localhost/{database_adın}
3- Bu dosyayı bir kez run'layınca otomatik olarak table'ın AI_390 database'i içerisinde oluşturulacak 
4- run_once.py dosyasına geç 
5- Bir kez daha run'lamaya gerek kalmadı. 
'''

engine = db.create_engine('mysql+pymysql://root:password@localhost/AI_390')


Base = declarative_base()

class Order(Base): 
    __tablename__ = 'orders' 

    order_id = db.Column(db.Integer, primary_key= True)
    customer_name = db.Column(db.String(100), nullable= False)
    order_date = db.Column(db.DateTime, default= datetime.utcnow())
    amount = db.Column(db.Float, nullable= False)

    def __repr__(self): 
        return f"Order_id: {self.order_id} | customer_name: {self.customer_name} | Order Date: {self.order_date} | Amount: {self.amount}"
    

# Tabloları Oluşturma 
Base.metadata.create_all(engine)

Session = sessionmaker(bind= engine)
session = Session()

def add_order(customer_name, amount, order_date= None): 
    order = Order(
        customer_name = customer_name, 
        amount = amount, 
        order_date = order_date or datetime.utcnow()
    )

    session.add(order)
    session.commit()
    return order.order_id

def delete_all(): 
    deleted_count = session.query(Order).delete()
    session.execute(text("TRUNCATE TABLE orders"))
    session.commit()
    return deleted_count

#Önemli olan bu!!!!
def execute_query(query): 
    '''Raw SQL query executer method'''
    result = session.execute(text(query))
    for row in result: 
        print('ID: {} | Customer_Name: {} | Date: {} | Amount: {} '
              .format(row.order_id, row.customer_name, row.order_date, row.amount))