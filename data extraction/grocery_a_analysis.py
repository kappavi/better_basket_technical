import json
import re 
import os
from utils import formatName

"""
Setting directory paths for the data files and the destination file.
"""
root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
data_file_path_a = os.path.join(root_directory, 'data/grocery_store_a.json')
dst_file_path_a = os.path.join(root_directory, 'data/grocery_a_parsed_products.json')


"""
Main analysis function that extracts product name and price from the json data.
"""
def main():
    with open(data_file_path_a, 'r') as f:
        json_data = json.load(f)

    # iterate through the json data and extract product name and price
    products = []
    for item in json_data:
        try:
            data = item["data"]
            raw_name = data["product"]["name"]
            product_name = formatName(raw_name)
            price = data["product"]["priceInfo"]["currentPrice"]["price"]
            price = f"${price:.2f}" # format price to two decimal places

            if product_name and price:
                products.append({"name": product_name, "price": price}) # the other data file has string price, so let's keep it consistent
        except:
            continue

    with open(dst_file_path_a, 'w') as f:
        json.dump(products, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()