# To use full API, devs should familiarize themselves with the database by reading the database docs
#       available via links on Data Type Documentation (https://fdc.nal.usda.gov/data-documentation)
# This ^ provides detailed definitions and descriptions needed to understand the data elements ref'd in the API docs

# Anyone may access and use the API. However, a data.gov API key must be incorporated into each API request.
#   Sign up to obtain a key, then follow the instructions for how to use your key.
#       https://fdc.nal.usda.gov/api-key-signup ;  https://api.data.gov/docs/api-key/
#   It is the API Key-holder's responsibility to ensure that their key is not made publicly available.
#       Any API keys discovered online, such as those in a code repository, will be deactivated to prevent malicious use.
# Can use DEMO_KEY for API key to initially explore the API before signing up, but it has much lower rate limits.
#       Hourly Limit: 30 requests per IP address per hour
#       Daily Limit: 50 requests per IP address per day

# Rate Limits
    # FDC currently limits # of API requests to a default rate of 1,000 / hour / IP address.
        # For each API key, these limits are applied across ALL api.data.gov API requests
    # Exceeding this ^ will cause API key to be blocked for 1 hour. More detailed info https://api.data.gov/docs/rate-limits.
    # You can check your current rate limit and usage details with the X-RateLimit-Limit and X-RateLimit-Remaining HTTP headers that are returned on every API response.

# Errors:  https://api.data.gov/docs/developer-manual/

# Suggested Citation:
#       U.S. Department of Agriculture, Agricultural Research Service. FoodData Central, 2019. fdc.nal.usda.gov


# 2 endpoints:
    # Food Search endpoint =  returns foods that match desired search criteria
    # Food Details endpoint = returns details on a particular food.

# API Endpoints
    # URL	        Verb	    Purpose
    # /food/{fdcId}	GET	        Fetches details for one food item by FDC ID
    # /foods	    GET | POST	Fetches details for multiple food items using input FDC IDs
    # /foods/list	GET | POST	Returns a paged list of foods, in the 'abridged' format
    # /foods/search	GET | POST	Returns a list of foods that matched search (query) keywords
# Query Params:
#     EX: {"query":"Cheddar cheese",  "dataType":["Branded"],  "sortBy":"fdcId",  "sortOrder":"desc"}
#     EX2:  {"pageSize":25}
#     ???:  -H "Content-Type:application/json"


""" NUTRIENTS:
       Survey (FNDDS) = seems to be per 100g of Food Item
       Foundation = ^
       SR Legacy = ^^
       Branded =  check "servingSizeUnit" and "servingSize"... DOES NOT always include all Nutrients...
       Experimental = XXX  (don't use)
"""

import requests
import time
import json
import csv
import pandas as pd
import os

main_endpoint_url = "https://api.nal.usda.gov/fdc/v1"
foods = "/foods"
    #List of multiple FDC ID's. Should be comma separated list (e.g. fdcIds=534358,373052) or repeating parameters (e.g. fdcIds=534358&fdcIds=373052).
listfoods = "/foods/list"
searchfoods = "/foods/search"
API_KEY = os.getenv('APIKEY')


# define params inside IF statement
# food = "Top Sirloin Steaks"
food = "brown rice"

params = {
    'api_key': API_KEY,
    'query': food
    # ,"sortBy": "score"
    ,"dataType": "SR Legacy"
    ,"pageNumber": 1
    ,"pageSize": 15
    ,"requireAllWords": True
}

response = requests.get(url=f"{main_endpoint_url}{foods}", params={'fdcIds': '2684441', 'api_key': API_KEY})   # WORKS
    # Retrieves list of up to 20 foods (by FDC ID)
    # CAN use {"format": "abridged"} with {"nutrients": [list of intIDs]} to get SPECIFIC nutrients
#     Maybe use this AFTER making a list of specific FDCIDs?? (can use minimal reqs to get exact nutrients)

# response = requests.get(url=f"{main_endpoint_url}/foods/search?api_key=DEMO_KEY", params={'query': 'abalone'})  # WORKS
#     SEARCH PARAMS:
#           Query: 	Search terms to use in the search.
#               The string may also include standard search operators (https://fdc.nal.usda.gov/help#bkmk-2)
#               USE THESE ^^^
#           dataType:  Filter on a specific data type; specify one or more values in an array. minItems: 1,   maxItems: 4
#               EX: "dataType": [ "Foundation", "SR Legacy" ]
#           sortBy = Specify one of the possible values to sort by that field.
#                 EX: "sortBy": "dataType
#           sortOrder = The sort direction for the results. Only applicable if sortBy is specified.
#                 EX:  "sortOrder": "asc"
#
# response = requests.get(url=f"{main_endpoint_url}{foods}", params={'fdcIds': '2706337', 'api_key': API_KEY, "format": "abridged", "nutrients": [203,204,205]})   # WORKS
#
# response = requests.get(url=f"{main_endpoint_url}{searchfoods}", params=params)   # WORKS
#
response.raise_for_status()
pretty_response = json.dumps(response.json(), indent=4)
print(pretty_response)
# print(response.json())
# print(response.json()["totalHits"])
# for food in response.json()['foods']:
#     print(food['description'])
#     print(food['score'])
#     print(food['dataType'])
# Response details:
    # foods['score'] = "Relative score indicating how well the food matches the search criteria"
          # ^ sort by this?? YES
    # foods['dataType'] = "source type" #(maybe filter out 'Branded', etc)

"""remove 'Aluminum Tray' and other non-ingredients"""
"""Replace 'é, è, î, ñ' with regular chars"""
"""if food['score'] are identical, prioritize 'Survey'/'Foundation'??"""

# line = 'Mirin (salted cooking wine)'
# ing_check_dict = {}
# with open('IngredientsToCheck', 'r') as file:
#     for line in file:
#         # print(line)
#         reffood = line.split(':')[0]
#         # print(reffood)
#
#         params = {
#             'api_key': API_KEY,
#             'query': reffood,
#             "sortBy": "score"
#             , "pageNumber": 1
#             , "pageSize": 1
#         }
#         try:
#             response = requests.get(url=f"{main_endpoint_url}{searchfoods}", params=params)  # WORKS
#             response.raise_for_status()
#             # print(response.json())
#         except requests.exceptions.HTTPError as errh:
#             time.sleep(2)
#             response = requests.get(url=f"{main_endpoint_url}{searchfoods}", params=params)  # WORKS
#             response.raise_for_status()
#         for food in response.json()['foods']:
#             # ing_check_dict[line] = (line, food['description'], food['score'], food['dataType'])
#             nutrients = {}
#             for nutrient in food['foodNutrients']:
#             #     nutrients[nutrient['nutrientName']] = (nutrient['nutrientId'], nutrient['nutrientNumber'], nutrient['value'], nutrient['unitName'])
#             # # print(nutrients)
#             # ing_check_dict[line] = {"foodused":food['description'], "source":food['dataType'], "category":food['foodCategory'], "nutrients":nutrients}
#                 if nutrient['nutrientName'] == "Protein":
#                     print(nutrient['unitName'])
#     # for key, value in ing_check_dict.items():
#     #     print(f"{key}: {value}")
#
#     # print(ing_check_dict)
#     # ing_check_df = pd.DataFrame(ing_check_dict)
#     # # ing_check_df.to_csv('ingredients_check_results.csv', index=False)
    # ing_check_df.to_csv('ingredients_check_resultsNUTRIENTS.csv', index=False)