"""
This file contains utility functions that are used in the data extraction process.
"""

import re
from rapidfuzz import process, fuzz

"""------------------------------------ analysis methods ---------------------------------------------"""

"""
Uses regex to remove all non-alphanumeric characters and make upper case.
"""
def formatName(name):
    cleaned_name = re.sub(r'[^\w\s]', '', name.upper()).strip()
    return cleaned_name

"""
Clean price by converting cents to dollars and removing any units at the end.
"""
def formatPrice(price):
    if "/" in price:
            price = price.split("/", 1)[1].strip() # remove the part before the slash
    if "¢" in price:
        price = re.sub(r'[^\d]', '', price) # isolate numbers
        price = f"{float(price) / 100:.2f}" # cents -> dollars
    # finally if there is LBs or OZ at the end, remove it
    price = re.sub(r'\s*(lb|oz)\s*$', '', price, flags=re.IGNORECASE)
    return price 

"""------------------------------------ comparison.py methods ---------------------------------------------"""

"""
Given a product name, find the best match in dataset B.
"""
def findBestMatch(product_name, hashed_list_keys):
    best = process.extractOne(product_name, hashed_list_keys, scorer=fuzz.token_sort_ratio)
    return best 

"""
Since prices are in string format, we need to convert them to integers and find the difference.
"""
def findPriceDiff(price_a, price_b):
    # use regex to convert to float and remove any non-numeric characters except the decimal point
    price_a = float(re.sub(r'[^\d.]', '', price_a))
    price_b = float(re.sub(r'[^\d.]', '', price_b))
    formatted = "${:.2f}".format(abs(price_a - price_b))
    return formatted

"""
In case two products have the same name but different quantity, add a metric to compare unit prices.
"""
def findUnitPrice(product_name, price):
    # firstly find name and quatity from the product name
    # (\d+(?:\.\d+)?)                  finds a integer or decimal
    # \s*                              finds optional whitespace
    # (fl oz|oz|ml|lb|g|ct|pk|pack|fo) finds one of the valid units
    pattern = re.compile(r'(\d+(?:\.\d+)?)\s*(fl oz|oz|ml|lb|g|ct|pk|pack|fo)', re.IGNORECASE)
    
    price = float(re.sub(r'[^\d.]', '', price))
    match = pattern.search(product_name)
    if match:
        quantity_str = match.group(1) # the first number is the quantity
        unit = match.group(2) # the second group is the unit
        try:
            quantity = float(quantity_str)
            if quantity > 0:
                unit_price = price / quantity
                return unit_price, quantity, unit
        except ValueError:
            pass

    # default answer if error is thrown
    return price, 1, "ITEM"

"""
Executing some unit tests for the utility functions.
"""
def main():
    
    pass

if __name__ == '__main__':
    main()