import csv
import psycopg2 as pg
import os

conn = pg.connect(
    host="localhost", #localhost or IP Address (127.0.0.1) can be used as well
    port="5432",
    user="postgres",
    password=os.environ['PGSQL_BASE_PW'],
    database="test1") #specify the DB tables are in
if(conn):
    print("Connected")
else:
    print("Error connecting")

cur = conn.cursor()

"""Table Creation"""
# cur.execute('CREATE TABLE IF NOT EXISTS nutreftable (id INT PRIMARY KEY, fdc_id INT, nutrient_id SMALLINT, amount FLOAT4, '\
#             'data_points SMALLINT NULL,  derivation_id SMALLINT NULL,  min FLOAT4 NULL,  max FLOAT4 NULL,  median FLOAT4 NULL,  '
#             'loq FLOAT4 NULL,  footnote TEXT NULL,  min_year_acquired SMALLINT NULL,  percent_daily_value FLOAT4 NULL);')
# with open('/Users/ericabbott/Desktop/FoodData_Central_csv_2025-12-18/food_nutrient.csv', 'r', encoding='utf-8') as f:
#     sql = """COPY nutreftable FROM STDIN WITH (FORMAT CSV, FORCE_NULL*, HEADER true, DELIMITER ','); """
#     cur.copy_expert(sql, f)
# cur.execute("ALTER TABLE nutreftable "
#             "DROP COLUMN IF EXISTS data_points, "
#             "DROP COLUMN IF EXISTS derivation_id, "
#             "DROP COLUMN IF EXISTS min, "
#             "DROP COLUMN IF EXISTS max, "
#             "DROP COLUMN IF EXISTS median, "
#             "DROP COLUMN IF EXISTS loq, "
#             "DROP COLUMN IF EXISTS footnote, "
#             "DROP COLUMN IF EXISTS min_year_acquired, "
#             "DROP COLUMN IF EXISTS percent_daily_value;")
# cur.execute("SELECT * FROM nutreftable WHERE fdc_id = 1105904;")
# check = cur.fetchmany(15) # <--- can also use fetchmany(#), fetchone()
# print(check)
''' ^ WORKS ; Created ^ '''
# cur.execute('CREATE TABLE IF NOT EXISTS nutrients (nutrient_id INT PRIMARY KEY, name VARCHAR(250), unit_name VARCHAR(10), nutrient_nbr FLOAT, rank FLOAT);')
# with open('/Users/ericabbott/Desktop/FoodData_Central_csv_2025-12-18/nutrientsupdated.csv', 'r', encoding='utf-8') as f:
#     sql = """COPY nutrients (nutrient_id, name, unit_name, nutrient_nbr, rank) FROM STDIN WITH (FORMAT CSV, HEADER true, DELIMITER ',');"""
#     cur.copy_expert(sql, f)
# cur.execute("SELECT * FROM nutrients")
# check = cur.fetchall() # <--- can also use fetchmany(#), fetchone()
# print(check)
''' ^ WORKS ; Created ^ '''
# cur.execute('CREATE TABLE IF NOT EXISTS inputs (id INT PRIMARY KEY, fdc_id INT, fdc_id_of_input_food INT NULL, seq_num SMALLINT NULL, '
#             'amount FLOAT4 NULL,  sr_code INT NULL,  sr_description VARCHAR(250) NULL,  unit VARCHAR(10) NULL, '
#             'portion_code INT NULL, portion_description VARCHAR(50) NULL, gram_weight FLOAT4 NULL, retention_code SMALLINT NULL) ;')
# with open('/Users/ericabbott/Desktop/FoodData_Central_csv_2025-12-18/input_food.csv', 'r', encoding='utf-8') as f:
#     sql = """
#     COPY inputs (id, fdc_id, fdc_id_of_input_food, seq_num, amount, sr_code, sr_description, unit, portion_code, portion_description, gram_weight, retention_code)
#     FROM STDIN WITH (FORMAT CSV, HEADER true, DELIMITER ',', FORCE_NULL*);"""
#     cur.copy_expert(sql, f)
# cur.execute("SELECT * FROM inputs WHERE fdc_id = 2706414")
# cur.execute("SELECT fdc_id_of_input_food FROM inputs WHERE fdc_id_of_input_food IS NOT NULL")
# check = cur.fetchall() # <--- can also use fetchmany(#), fetchone()
# print(check)
''' ^ WORKS ^ '''
cur.execute('CREATE TABLE IF NOT EXISTS foods (fdc_id INT PRIMARY KEY, data_type VARCHAR(50) NULL, description VARCHAR NULL, food_category_id VARCHAR NULL, publication_date VARCHAR NULL);')
with open('/Users/ericabbott/Desktop/FoodData_Central_csv_2025-12-18/food.csv', 'r', encoding='utf-8') as f:
    sql = """COPY foods (fdc_id, data_type, description, food_category_id, publication_date) FROM STDIN WITH (FORMAT CSV, HEADER true, DELIMITER ',', FORCE_NULL*);"""
    cur.copy_expert(sql, f)
cur.execute("SELECT * FROM foods WHERE fdc_id = 2705448")
check = cur.fetchall() # <--- can also use fetchmany(#), fetchone()
print(check)
''' ^ WORKS ^ '''

# conn.commit()

cur.close()
conn.close()