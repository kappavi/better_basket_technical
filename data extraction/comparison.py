import json
import re
import os
from utils import findBestMatch, findPriceDiff, findUnitPrice

SIMILARITY_THRESHOLD = 90

"""
Setting directory paths for the data files and the destination file.
"""
root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
file_path_a = os.path.join(root_directory, 'data/grocery_a_parsed_products.json')
file_path_b = os.path.join(root_directory, 'data/grocery_b_parsed_products.json')
dst_file_path = os.path.join(root_directory, 'results/grocery_comparison.json')

"""
Iterate through elements of dataset A and find the best match in dataset B.
"""
def main():
    with open(file_path_a, 'r') as f:
        json_data_a = json.load(f)

    with open(file_path_b, 'r') as f:
        json_data_b = json.load(f)

    # hash the smaller dataset -- in this case, grocery store A
    grocery_a_hashed = {}
    for product in json_data_a:
        grocery_a_hashed[product["name"]] = product["price"]

    # compute the hashed keys to pass into the findBestMatch function
    grocery_a_keys = list(grocery_a_hashed.keys())
    
    # iterate through the larger dataset -- grocery store B
    matched_products = []
    for product in json_data_b:
        product_name = product["name"]
        price = product["price"]
        best = findBestMatch(product_name, grocery_a_keys)
        if best:
            # best match is a tuple of (product_name, score, and ___)
            best_match, score, _ = best
            if score >= SIMILARITY_THRESHOLD:
                product_name_a = product_name
                product_name_b = best_match
                price_a = price
                price_b = grocery_a_hashed[best_match]
                price_diff = findPriceDiff(price_a, price_b)
                unit_price_a, quantity_a, unit_a = findUnitPrice(product_name_a, price_a)
                unit_price_b, quantity_b, unit_b = findUnitPrice(product_name_b, price_b)
                unit_price_diff = abs(unit_price_a - unit_price_b)
                matching_score = score
                matched_products.append({
                    "product_name_a": product_name_a,
                    "product_name_b": product_name_b,
                    "price_a": price_a,
                    "price_b": price_b,
                    "price_diff": price_diff,
                    "unit_price_a": "${:.4f}".format(unit_price_a) + " PER " + unit_a,
                    "unit_price_b": "${:.4f}".format(unit_price_b) + " PER " + unit_b,
                    "unit_price_diff": "${:.4f}".format(unit_price_diff),
                    "matching_score": matching_score
                })
    
    with open(dst_file_path, 'w') as f:
        json.dump(matched_products, f, indent=4, ensure_ascii=False)
    
if __name__ == '__main__':
    main()
