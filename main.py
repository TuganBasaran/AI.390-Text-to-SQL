import re
from gemini_utils import generate_sql
from db.db import Order, add_order, execute_query 

def clean_sql_query(sql_text):
    # Markdown formatını temizle (```sql ve ``` gibi kısımları kaldır)
    # ve gerçek SQL sorgusunu çıkar
    sql_pattern = re.search(r'```(?:sql)?\s*(.*?)```', sql_text, re.DOTALL)
    if sql_pattern:
        return sql_pattern.group(1).strip()
    return sql_text.strip()

def main(): 
    query = "Select all of the rows in orders table"
    sql_code = generate_sql(query)
    print(sql_code)

    try:
        cleaned_query = clean_sql_query(sql_code)
        execute_query(cleaned_query)
        print('Query successfully executed. Code: 1')
    except Exception as e: 
        print("Error occured. Code: 0 \n {}".format(e))


if __name__ == '__main__': 
    main()