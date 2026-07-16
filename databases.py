# Use ON DELETE CASCADE for FKs (Recipes <-- Nutrients) ;  Just use Recipe Name as FK
    # Don't think I'll NEED any FKs to/for IngredientNutrients...

# Filtering Child Tables by a Specific Parent (Child table records that belong to that Parent)
    # use WHERE + parent's primary key value / join condition
    # select data from the child table directly by filtering on the foreign key column:
        # SELECT * FROM ChildTable WHERE parent_id = 1;
# DBs:
    # Recipes:
        # RecID, Name, URL, Servings, Cook_Time, Cuisine, Restriction
        #   "Ingredients" references ENTIRE TABLE ;  MAYBE DON'T NEED "Nutrients" is FK-related to sheet
    # RecNutrients:
        # RedID*, Nutrients-->
        #   "RecID is FK to Recipes
        #   filled in w/ Calcs using Ingredients + "Servings" from Recipes
    # Ingredients:
        #   Independent ;  created thru Recipe scraper and FDC API. Used for Nutrient Calcs

"""Arrays need '{}' inside '()' around the list of all items ; Or just ['',] lol """

recipe_list = [
    {"rec_id":1, "rec_name":'Shrimp', "url":'https://en.wikipedia.org/wiki/Shrimp',
                "servings":6, "cook_time":30, "cuisine":'', "calories":400, "restrictions":['shellfish'], "diet":'pescatarian'},
    {"rec_id":2, "rec_name":'Summer Udon Noodle Salad', "url":'https://www.blueapron.com/recipes/standard-meal-kit/summer-udon-noodle-salad-with-cherry-tomatoes-corn-summer-sweet-pepper?idp_intent=add-standard-product&product_id=7846af3a-6fa1-4ba0-bc5a-edfcc209befc&page_source=cookbook',
                "servings":4, "cook_time":15, "cuisine":'asian', "calories":1000, "restrictions":[''], "diet":'vegan'},
    {"rec_id":3, "rec_name": 'Chorizo Enchiladas', "url": 'https://www.blueapron.com/recipes/chorizo-enchiladas?srsltid=AfmBOoqP1I3hf21JkXUKSjbfa0rtGow_33SysDJXGuh343-9MleXcQ11',
                "servings": 2, "cook_time": 120, "cuisine": 'mexican', "calories": 1400, "restrictions": ['dairy','gluten','meat','pork'], "diet": ''},
    {"rec_id":4, "rec_name":'Chorizo Enchiladas', "url":'https://www.blueapron.com/recipes/chorizo-enchiladas?srsltid=AfmBOoqP1I3hf21JkXUKSjbfa0rtGow_33SysDJXGuh343-9MleXcQ11',
                "servings":2, "cook_time":120, "cuisine":'mexican', "calories":1400, "restrictions":('{dairy,gluten,meat,pork}'), "diet":''},]
rec_nutrients_list = [
    {"rec_id":1, "carbs":40},
    {"rec_id":2, "carbs":140},
    {"rec_id":3, "carbs":100},
    {"rec_id":4, "carbs":100}]

query_test = {
     "rec_names_selected":'',
     "cuisine_selected": None,
     "cook_time_selected":150,
     "calories_selected": None,
     "restrictions_selected": ['dairy', 'shellfish'],
     "diet_selected": None}

# ------------------------------------------------------------------

import psycopg2 as pg
import psycopg2.extras as extras
import os

conn = pg.connect(
    host="localhost", #localhost or IP Address (127.0.0.1) can be used as well
    port="5432",
    user="postgres",
    password=os.getenv('PGSQL_BASE_PW'),
    database="test1") #specify the DB tables are in
if(conn):
    print("Connected")
else:
    print("Error connecting")
cur = conn.cursor()
cur.execute('CREATE EXTENSION IF NOT EXISTS btree_gin;')
cur.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm;')


"""TABLE CREATION"""
cur.execute('CREATE TABLE IF NOT EXISTS recipes  (rec_id INT PRIMARY KEY,  rec_name VARCHAR(250),  url VARCHAR(500), '
            'servings SMALLINT NULL,  cook_time SMALLINT NULL,  cuisine VARCHAR(250) NULL,  calories SMALLINT,  restrictions TEXT[] NULL, diet VARCHAR(15) NULL);')
# vv  Finish Nutrient decisions, then restructure these 2:
cur.execute('CREATE TABLE IF NOT EXISTS rec_nutrients  (rec_id INT PRIMARY KEY REFERENCES recipes(rec_id) ON DELETE CASCADE,  carbs SMALLINT);')
cur.execute('CREATE TABLE IF NOT EXISTS ingredients_nut_ref  (ing_name VARCHAR(500) PRIMARY KEY,  restriction varchar(50) NULL,  calories SMALLINT)')


"""DROP INDEXES"""  # either use a "Drop All" method  OR  just go by name ;  Don't need this yet...
# cur.execute()


"""DATA INSERTION"""
recipe_data_insert = ("INSERT INTO recipes (rec_id, rec_name, url, servings, cook_time, cuisine, calories, restrictions, diet)"
                      "VALUES (%(rec_id)s, %(rec_name)s, %(url)s, %(servings)s, %(cook_time)s, %(cuisine)s, %(calories)s, %(restrictions)s, %(diet)s);")
extras.execute_batch(cur, recipe_data_insert, recipe_list)

nutrients_data_insert = "INSERT INTO rec_nutrients (rec_id, carbs) VALUES (%(rec_id)s, %(carbs)s);"
extras.execute_batch(cur, nutrients_data_insert, rec_nutrients_list)


"""FIND AND DELETE DUP RECIPES (prep for UNIQUE Index)"""
cur.execute("SELECT url, COUNT(*) FROM recipes GROUP BY url HAVING COUNT(*) > 1;")
duplicates = cur.fetchall()
cur.execute("DELETE FROM recipes a USING recipes b WHERE a.ctid > b.ctid AND a.url = b.url;")


"""INDEX CREATION"""  # Recipes:  REGULAR(url, cook_time, cuisine, calories) ;  GIN(rec_name, restrictions)
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS recipes_url ON recipes(url);")
cur.execute("CREATE INDEX IF NOT EXISTS recipes_cook_time ON recipes(cook_time);")
cur.execute("CREATE INDEX IF NOT EXISTS recipes_cuisine ON recipes(cuisine);")
cur.execute("CREATE INDEX IF NOT EXISTS recipes_calories ON recipes(calories);")
cur.execute("CREATE INDEX IF NOT EXISTS recipes_rec_name ON recipes USING gin (rec_name) ;")
cur.execute("CREATE INDEX IF NOT EXISTS recipes_restrictions ON recipes USING gin (restrictions) ;")


"""DATA SELECTION"""
query_test2 = [120]
recipe_select = ("SELECT * FROM recipes JOIN rec_nutrients ON recipes.rec_id = rec_nutrients.rec_id WHERE"
        "(((%(cook_time_selected)s) IS NULL OR cook_time <= (%(cook_time_selected)s))" 
        "AND ((%(calories_selected)s) IS NULL OR calories <= (%(calories_selected)s))"
        "AND ((%(cuisine_selected)s) IS NULL OR cuisine = (%(cuisine_selected)s))"
        "AND ((%(diet_selected)s) IS NULL OR diet = (%(diet_selected)s))"
        "AND ((%(restrictions_selected)s) IS NULL OR restrictions && ARRAY[%(restrictions_selected)s])"
        ")"
        "ORDER BY similarity(rec_name, (%(rec_names_selected)s)) DESC"
        ";"
        )
cur.execute(recipe_select, query_test)
check = cur.fetchall() # <--- can also use fetchmany(#), fetchone()
print(check)


"""TEST QUERIES"""
# cur.execute("EXPLAIN ANALYZE SELECT * FROM recipes;")
# check = cur.fetchall() # <--- can also use fetchmany(#), fetchone()
# print(check)
# cur.execute("SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'recipes';")
# indexes = cur.fetchall()
# for index in indexes:
#     print(f"Index Name: {index[0]}")
#     print(f"Definition: {index[1]}\n")
#
# cur.execute("SELECT * FROM recipes;")
# check = cur.fetchall() # <--- can also use fetchmany(#), fetchone()
# print(check)
# cur.execute("SELECT * FROM rec_nutrients;")
# check = cur.fetchall() # <--- can also use fetchmany(#), fetchone()
# print(check)


cur.close()
conn.close()