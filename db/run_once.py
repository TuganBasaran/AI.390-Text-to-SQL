from db import add_order, delete_all, session, Order
from datetime import datetime
import csv

''' UYARI: BU KISMI SADECE BİR KERE RUNLA!!!!!
    YOKSA AYNI DATADAN BİRDEN FAZLA OLACAK 
    
    CODE AÇKLAMASI 
    --------------
    1- Database'i oluşturdaktan sonra csv file'ı read'lemen lazım 
    2- Her csv row'unu tek tek run'ladıktan 
    sonra her bir row'un attribute'larını tek tek alıyorsun.
    3- Bundan sonra her bir row'u tek tek database'e ekliyorsun 
    4- Detaylı açıklama aşağıda
    '''

delete_all()

# Datayı csv'den çekiyorsun sırayla attribute'ları alıyorsun
# Ondan sonra her biri ile add_order() methodu'nu çalıştırıyorsun 
with open('data/orders.csv', 'r') as file: 
    csv_reader = csv.reader(file)

    # Header'ları geçiyorsun 
    headers = next(csv_reader)

    # Tek bir row'u al (List gibi düşünebilirsin bu for'u)
    for row in csv_reader:
        # Kaç tane data eklendiğini bilmek için 
        count = 0 
        # Dataları row'dan alımı
        order_id, customer_name, order_date_str, amount = row 
        order_date = datetime.strptime(order_date_str, '%Y-%m-%d')

        # Burada order'ı database'e ekliyorsun
        add_order(customer_name, amount, order_date)
        count += 1 
    
    print(f'{count} order imported!')

    
all_orders = session.query(Order).all()
for order in all_orders: 
    print(f"Id: {order.order_id} | Name: {order.customer_name} | Amount: {order.amount}")