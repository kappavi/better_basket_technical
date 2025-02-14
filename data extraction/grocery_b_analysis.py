import json
import re
from bs4 import BeautifulSoup
import os 
from utils import formatName, formatPrice

"""
Setting directory paths for the data files and the destination file.
"""
root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
data_file_path_b = os.path.join(root_directory, 'data/grocery_store_b.json')
dst_file_path_b = os.path.join(root_directory, 'data/grocery_b_parsed_products.json')


"""
Extract product info using CSS selectors, when possible. Used within parse_products_from_html.
"""
def parse_product_from_container(container):
    # try to get product name from a heading/link
    name_tag = container.find("h3")
    if name_tag and name_tag.find('a'):
        product_name = name_tag.find('a').get_text(strip=True)
    else:
        product_name = container.get_text(strip=True)
    
    # get quantity using a p tag that might have a class like "text-muted"
    # many times, secondary data has this "texted-muted" class
    quantity_tag = container.find('p', class_=re.compile('text-muted'))
    quantity = quantity_tag.get_text(strip=True) if quantity_tag else None

    # get price from a tag with class containing "precio"
    price_tag = container.find('p', class_=re.compile('precio'))
    price = price_tag.get_text(strip=True) if price_tag else None
    
    # let's combine product and quantity
    if quantity:
        product_name = f"{product_name} {quantity}"
    
    # format name (remove special characters, make uppercase) and price
    product_name = formatName(product_name)
    price = formatPrice(price)
    # price = "${:.2f}".format(float(price))

    return {"name": product_name, "price": price}


"""
Given an HTML string, try 2 approaches (structured and heuristic) to extract product info.
This is the primary extraction function for this dataset.
"""
def parse_products_from_html(html):
    soup = BeautifulSoup(html, "lxml")
    products = []

    # if the product-grid-item class is found, use structured parsing
    containers = soup.find_all(class_="product-grid-item")
    if containers:
        for container in containers:
            info = parse_product_from_container(container)
            # we need at least product and price info to add it
            if info["name"] and info["price"]:
                products.append(info)
    else:
        # in the case we cannot find structured data, use heuristics
        lines = list(soup.stripped_strings)
        # remove any promo labels (in Spanish) that might be there
        promo_labels = {"ESPECIAL", "OFERTA", "PARTICIPANTE"} # are these all the promo labels?
        filtered_lines = []
        for line in lines:
            if line.upper() not in promo_labels:
                filtered_lines.append(line)
        
        # assuming here that products are listed in groups of 3 lines
        for i in range(0, len(filtered_lines) - 2, 3):
            product = filtered_lines[i]
            quantity = filtered_lines[i + 1]
            product_name = formatName(f"{product} {quantity}" if quantity else product)

            price = filtered_lines[i + 2]
            # need to make sure the third line is actually a price, otherwise skip this data
            if re.search(r'[\$]', price):
                products.append({"name": product_name, "price": price})
    return products

"""
Main analysis function that extracts product name and price from the json data.
"""
def main():
    # loading the json file
    with open(data_file_path_b, 'r') as f:
        json_data = json.load(f)

    all_products = []
    # process each item in the data
    for item in json_data:
        html = item["data"]["html_data"]
        products = parse_products_from_html(html)
        all_products.extend(products)

    # dump the file 
    with open(dst_file_path_b, 'w') as f:
        json.dump(all_products, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()

# testing code -----------------

"""
This was some initial testing to see how the data was structured.
"""

def test1():
    with open('grocery_store_b.json', 'r') as f:
        json_data = json.load(f)

    item1 = json_data[0]["data"]["html_data"]
    soup = BeautifulSoup(item1, "lxml")
    containers = soup.find_all(class_="product-grid-item")
    print(soup.prettify())

"""
Some key example outputs:

<p class="text-center text-muted">
18 OZ
</p>

<p class="text-center precio" style="">
$3.75
</p>
"""