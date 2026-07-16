import httpx
import json
from unidecode import unidecode
import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)

cookbook_url = "https://www.blueapron.com/cookbook"
# test_url = "https://www.blueapron.com/recipes/standard-meal-kit/flank-steaks-tangy-homemade-steak-sauce-with-mashed-potatoes-sauteed-carrots?page_source=cookbook&_rsc=pqeii"
# test_url = "https://www.blueapron.com/recipes/standard-meal-kit/creamy-romesco-chicken-garlic-bread-with-roasted-broccoli-parmesan-cheese?page_source=cookbook"
params = {"page_source": "cookbook", "_rsc": "pqeii"}
headers = {
    "rsc": "1",
    "User-Agent": "Mozilla/5.0...",
    "accept": "*/*"
}

'''Getting Info from BlueApron website for URL creation'''
recipe_info = {}
cookbook = httpx.get(cookbook_url, params=params, headers=headers)
# print(cookbook.text)
for line in cookbook.text.split('\n'):
    # print(line)
# check what line it's on ;  44*, 46* & 47* are previous locations
    if line.startswith('47:['):
        cookbook_data = json.loads(line[3:])
        if cookbook_data[3]['state']:
            recipe_info = (cookbook_data[3]['state']['queries'][0]['state']['data']['products'])
            # print(recipe_info)
        else:
            break
    if line.startswith('46:['):
        cookbook_data = json.loads(line[3:])
        if cookbook_data[3]:
            recipe_info = (cookbook_data[3]['state']['queries'][0]['state']['data']['products'])
        else:
            break
    if line.startswith('44:['):
        cookbook_data = json.loads(line[3:])
        if cookbook_data[3]:
            recipe_info = (cookbook_data[3]['state']['queries'][0]['state']['data']['products'])
        else:
            break
            # print(recipe_info)

'''URL Creation'''
recipe_url_check = []
""" maybe grab all URLs from RECIPE DB and put them here FIRST to check """
remove_specs = str.maketrans('', '', '"\',')
for recipe in recipe_info:
    recipe_type = recipe['primary_product_type'].replace('_', '-')
    if recipe_type == "FIFTEEN-MINUTE-MEAL-KIT":
        recipe_type = "15-MINUTE-MEAL-KIT"
    url_name = (recipe['name']+' '+recipe['subtitle']).replace(' ', '-')
    recipe_url = unidecode(f"https://www.blueapron.com/recipes/{recipe_type}/{url_name}").lower()
    recipe_url = recipe_url.translate(remove_specs)
    refined_url = recipe_url.replace("&-", "")
    if refined_url.endswith('-'):
        refined_url = refined_url[:-1]
    if refined_url not in recipe_url_check:
        recipe_url_check.append(refined_url)
    # print(refined_url)

'''Check if recipe is already in SQL DB ^HERE^ ;  if not, adds Name+Link '''
# xxx

'''Recipe Info Scraping from NEW^ Created URLs'''
rough_recipes = []
for url in recipe_url_check:
    # print(url)
    recipe = httpx.get(url, params=params, headers=headers)  # recipe =  <class 'httpx.Response'>
    # print(recipe)
    # Parsing to find the JSON
    recipelines = iter(recipe.text.split('\n'))
    for line in recipelines:  # line = <class 'str'>
        # print(line, flush=True)
        if line.endswith('"HydrationBoundary"]'):
            # print(line)
            x = next(recipelines)
            # print(x)
            rough_recipes.append(x)
# for line in rough_recipes:
#     with open('recipes.txt', 'a') as f:
#         # if line in rough_recipes:
#         #     continue
#         # else:
#             f.write(f"{line}\n")
            # f.write('\n')

'''Recipe Refining into Dicts --> Tables '''
recipes_table_dict = [] # dict of recipes to be added to Recipes PSQL table
meal_keys_to_add = ['name', 'subtitle', 'total_cook_time', 'cuisine_type', 'serving_size']
ing_amount_conversions = {"¼": ".25",  "⅓": ".33",  "½": ".5",  "⅔": ".66",  "¾": ".75"}
ing_skip_list = []
# ing_keys_to_add = ['name','quantity_unicode_str']  # May not need  
# ings_to_convert = {}  # May not need  
# df_ings_data = []  # for checking ingredients with pandas
for line in rough_recipes:
    if line.startswith('44:['):
        # Remove the '4:' prefix and parse as JSON
        recipe_data = json.loads(line[3:])  # recipe_data = <class 'LIST'>
        # print(recipe_data)
        # recipe data is deeply nested in the "React Query state"
        refined_data = recipe_data[3]['state']['queries'][1]['state']['data']  # refined_data = <class 'DICT'>
        # print(refined_data)
        # ^ check recipe listing "type" (login-required recipes have slightly different key names)
        """Refining KV Pairs ;  Recipe and Ing data"""
        if 'product' in refined_data:  # creates DICTIONARIES of info
            meal_info = refined_data['product']  
            ing_info = refined_data['item']  
        else:
            meal_info = refined_data['product_basic']  
            ing_info = refined_data['items']   
            
        if type(ing_info) is list:  # for recipes w/ ingredient substitutions
            sorted_recipes_table_dict = meal_info | ing_info[0]
            sorted_ing_data = ing_info[0]['ingredients']
        else:
            sorted_recipes_table_dict = meal_info | ing_info   # contains  ^ meal_keys_to_add ^
            sorted_ing_data = ing_info['ingredients'] # contains  ^ ing_keys_to_add ^ ;  ingredients[0='quantity_unicode_str', 1='name']
            
        # print(sorted_ing_data)
        """compiling Recipe Dict data"""
        single_recipe_dict = {key: sorted_recipes_table_dict[key] for key in meal_keys_to_add if key in sorted_recipes_table_dict}
        recipe_name = single_recipe_dict['name'] + ' ' + single_recipe_dict['subtitle']
        single_recipe_dict['recipe_name'] = recipe_name
        del single_recipe_dict["name"]
        del single_recipe_dict["subtitle"]
        """create and add UUID here"""
        # x
        
        # print(single_recipe_dict) 

        """refining Ingredient data"""
        # if item["ingedient"] in ings_to_convert:
            # item["ingedient"] = ings_to_convert[item["ingedient"]]
            # OR save ^ as variable and insert it below
        # else:
        #     print(item)
        #     continue
        """create dict of ings + amounts + measurements"""
        rec_ing_list = []  
        for item in sorted_ing_data:
            info = item['quantity_unicode_str'].split()
            info = [ing_amount_conversions.get(num, num) for num in info]
            # print(f"{len(info)} length")
            if len(info) == 3:
                nums = [info[i] for i in [0, 1]]
                amount = "".join(nums)
                ing_info = {"ingredient": item['name'], "amount": amount, "measurement": info[2]}
                # print(ing_info)
                ##  MAY NEED TO USE ACTUAL UNIQUE KEYS INSTEAD OF 'inf_info'...
                if ing_info["ingredient"] not in ing_skip_list:
                    rec_ing_list.append(ing_info)
            if len(info) > 0 and len(info) <3:
                ing_info = {"ingredient": item['name'], "amount": info[0], "measurement": info[1]}
                # print(ing_info)
                ##  ^
                if ing_info["ingredient"] not in ing_skip_list:
                    rec_ing_list.append(ing_info)
            else:
                continue
        # print(rec_ing_list)

        """checking ing values with pandas """
        # indiv_ing_df = pd.DataFrame(rec_ing_list)
        # print(indiv_ing_df.head())
        # indiv_ing_df.to_csv(f'ingredients/{single_recipe_dict['recipe_name']}.csv', index=False)
        """checking ing values with pandas 2* """
        # df_ings_data.append(ing_info)

        """Check if all ['ingredient']s EXIST in 'ALL_INGS_NUTRIENTS' SQL table:  
              if not, use API --> add each to 'ing_table_dict' --> add 'ing_table_dict' to 'ALL_INGS_NUTRIENTS' """
            # for ing in rec_ing_list:
                # if ing not in 'ing_skip_list':
                #    ?

        """Grab Nutrient amounts for all Ings (dict?) from ALL_INGS table """

        """Add Nutrient amounts to 'Totals Counter' ;  add any 'categories' to 'Restrictions' (dict/list?) """
        #     restrictions_dict = {Dairy = 'Dairy and Egg Products', 'Poultry' = 'Poultry Products', 'meat' = ('Sausages and Luncheon Meats',"Beef Products","Lamb, Veal, and Game Products") 'pork' = 'Pork Products', 'nuts' = "Nut and Seed Products",  shellfish = "Finfish and Shellfish Products", gluten = ("Baked Products","Cereal Grains and Pasta")
        #     maybe check WWEIA if possible...

        #     }
        """Once all ^ finished, add Nutrient Totals to RecNut table (w/ name) & 'Restrictions' List + 'Calories' to Recipe Dict """

        # single_recipe_dict['calories'] = calories
        # recipes_table_dict.append(single_recipe_dict)  


"""checking ing values with pandas ^ """
ing_df = pd.DataFrame(df_ings_data)
# print(ing_df.head())
# print(ing_df.describe())
# for column in ing_df.columns:
#     unique_values = ing_df[column].unique()
#     print(f"Unique values in column '{column}': {unique_values}")
# ing_df.to_csv('ingredients/0_all_ingredients.csv', index=False)

"""checking rectable values with pandas"""
# meal_df = pd.DataFrame(recipes_table_dict)
# print(meal_df.shape)
# print(meal_df.head())
# for column in meal_df.columns:
#     unique_values = meal_df[column].unique()
#     print(f"Unique values in column '{column}': {unique_values}")
# meal_df.to_csv('recipestable.csv')
# meal_df.to_csv('recipestable_noindex.csv', index=False)

# check if recipe has "customizations"
#         with open ('recipes3.json', 'a') as f:
#             # json.dump(meal_info, f)
#             if type(ing_info) is list:
#                 json.dump(ing_info[0]["ingredients"], f, indent=4)
#                 f.write('\n')  #adds new line between dict/list of ing dicts
#             else:
#                 json.dump(ing_info["ingredients"], f, indent=4)
#                 f.write('\n')  #adds new line between dict/list of ing dicts