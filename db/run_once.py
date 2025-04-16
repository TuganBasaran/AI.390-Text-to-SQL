from db import add_order, delete_all, session, Order
from datetime import datetime
from pathlib import Path
import csv

''' UYARI: BU KISMI SADECE BİR KERE RUNLA!!!!!
    YOKSA AYNI DATADAN BİRDEN FAZLA OLACAK 

    CODE AÇIKLAMASI 
    --------------
    1- Database'i oluşturduktan sonra csv file'ı read'lemen lazım 
    2- Her csv row'unu tek tek run'ladıktan 
    sonra her bir row'un attribute'larını tek tek alıyorsun.
    3- Bundan sonra her bir row'u tek tek database'e ekliyorsun 
    4- Detaylı açıklama aşağıda
'''

# 1. CSV yolunu dinamik şekilde ayarla
csv_path = Path(__file__).resolve().parent.parent / "data" / "orders.csv"

# 2. Veritabanını sıfırla
delete_all()

# 3. CSV'yi aç ve işle
with open(csv_path, 'r') as file:
    csv_reader = csv.reader(file)

    headers = next(csv_reader)
    count = 0

    for row in csv_reader:
        order_id, customer_name, order_date_str, amount = row
        order_date = datetime.strptime(order_date_str, '%Y-%m-%d')

        add_order(customer_name, amount, order_date)
        count += 1

    print(f'{count} order imported!')

# 4. Tüm verileri ekranda göster
all_orders = session.query(Order).all()
for order in all_orders:
    print(f"Id: {order.order_id} | Name: {order.customer_name} | Amount: {order.amount}")