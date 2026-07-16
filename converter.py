import json
import csv

def csv_to_json(csv_file_path, json_file_path):
    # Read the CSV data into a list of dictionaries
    data = []
    with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            data.append(row)

    # Write the list of dictionaries to a JSON file
    with open(json_file_path, mode='w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4)  # Use indent=4 for human-readable output


# Example usage
csv_to_json('RecipeSearchResultsTestX.csv', 'RecipeSearchResultsTest.json')