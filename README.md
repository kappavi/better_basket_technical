# Grocery Store Data Comparison and Analysis

Hey BetterBasket team! I created this README to document a little about this repo structure and my process in completing your guys' technical task.

---

## Directory Structure

```
/
├── data/                     # parsed and cleaned data (original data omitted due to size)
├── data_extraction/          # scripts for cleaning, extracting, and normalizing data
│   └── comparison.py         # final script that compares cleaned datasets and outputs results to results/grocery_comparison.json
├── results/                  # output directory for comparison results
│   └── grocery_comparison.json
└── requirements.txt          # list of required Python packages
```

Note: the given json files are not included in this repository since they are rather large.

## Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/kappavi/better_basket_technical/
   cd better_basket_technical
2. **Create Virtual Environment (optional):**

   ```bash
   python -m venv venv
   source venv/bin/activate    # On Windows use: venv\Scripts\activate
3. **Install Depdendencies**
   ```bash
   pip install -r requirements.txt
# Process
### utils.py

I included a collection of utility functions in `utils.py` that streamline the data extraction and comparison processes. They are meant for handling common tasks such as cleaning and formatting product names and prices, performing fuzzy matching, and calculating unit prices. All of these functions are thoroughly unit tested in `util_tests.py`. Each function and test is commented and explained in the respective files.

### Grocery Store B - Data Cleaning

I ended up looking at this json first, and was printing the first item just to look at the format. I saw that inside the "data" objects there was HTML data, so I used BeautifulSoup for analysis and extraction.

After some iterations of displaying data and some format analysis,  I realized that the product information was consistently embedded within specific HTML elements such as \<h3>, \<a>, and \<p>. This insight allowed me to refine my extraction process: I could reliably target the product grids, extract explicit quantity information, normalize the valid data using regex, and dump the cleaned data. Later, I had to revisit the extraction logic to adjust the conversion of cents to dollars.

### Grocery Store A - Data Cleaning

The JSON from Grocery Store A was more structured and formatted. I examined the first element with a JSON viewer to understand its structure and found that it contained consistent information for product names, prices, etc. Since explicit quantity data was not available, I combined the product name with the available quantity details. The data was then normalized using regex and dumped for further processing.

### Creating the Result Data

For the comparison phase, I hashed the smaller dataset (Grocery Store A) and used RapidFuzz for fuzzy matching—a C++ wrapped in Python library that delivers fast performance.

For each product in Grocery Store A, the script finds the best possible match (using fuzzy matching) in Grocery Store B and appends it to the output JSON if the matching score exceeds a configurable threshold (default > 90). Fuzzy matching is a technique used to identify strings that are similar but not exactly the same. This is particularly useful when comparing product names that might have minor differences in formatting, spelling, or word order.

One of the core algorithms behind fuzzy matching is the **Levenshtein distance**. This metric calculates the minimum number of single-character edits—insertions, deletions, or substitutions—required to transform one string into another. A smaller Levenshtein distance implies that two strings are more similar.

RapidFuzz, the library used in our script, employs highly optimized C++ implementations of these algorithms. In our specific case, we use the `token_sort_ratio` scorer from RapidFuzz. This scorer not only computes the Levenshtein distance but also preprocesses the strings by tokenizing and sorting the words. This preprocessing step reduces the impact of differences in word order, making the matching process more robust for product names. There are several examples in the output file where the product is the same but the order of words is different, showing the effectiveness in the tokenization and sorting of words.

The result is a similarity score normalized between 0 and 100, where a score of 100 represents an exact match. By setting a threshold (default > 90), the script filters out matches that are not sufficiently similar, thereby improving the accuracy of the comparison between products from the two datasets.

Currently, this process operates at $O(n^2)$ complexity since for each product in Grocery Store B, we have to check every single key of the hashed Grocery Store A for the best match. However, for future considerations, I may consider training a basic model or implementing more efficient lookup methods in the future to reduce this to $O(n)$. 

I also noticed stark price differences when units varied (eg. 12oz vs 5oz), so I added of a new extraction method to compute per-unit prices.

## Output and Format

After running the comparison script, the results are saved as a JSON file (e.g., `results/grocery_comparison.json`). This output file contains an array of objects, where each object represents a pair of matched products from the two grocery datasets. Each object includes the following fields:

- **product_name_a:** The product name from Grocery Store A.
- **product_name_b:** The product name from Grocery Store B that best matches the product from A, determined by fuzzy matching.
- **price_a:** The price for the product from Grocery Store A (formatted with a dollar sign).
- **price_b:** The price for the matched product from Grocery Store B (formatted with a dollar sign).
- **price_diff:** The absolute difference between `price_a` and `price_b`, formatted as a dollar value.
- **unit_price_a:** The calculated unit price for the product from Grocery Store A. This value is expressed per the unit extracted (e.g., per OZ or per LB).
- **unit_price_b:** The calculated unit price for the product from Grocery Store B, expressed similarly.
- **unit_price_diff:** The absolute difference between the unit prices from the two stores.
- **matching_score:** A similarity score (0-100) obtained from the fuzzy matching process, indicating how closely the product names match.

### Example Entry

```json
{
    "product_name_a": "IDAHOAN MASHED POT BUTTERY HOMESTYLE 15 OZ",
    "product_name_b": "IDAHOAN BUTTERY HOMESTYLE MASHED POTATOES 15 OZ CUP",
    "price_a": "$2.29",
    "price_b": "$1.67",
    "price_diff": "$0.62",
    "unit_price_a": "$0.1527 PER OZ",
    "unit_price_b": "$0.1113 PER OZ",
    "unit_price_diff": "$0.0413",
    "matching_score": 90.32258064516128
}

```

## Overall Notes

- **BeautifulSoup for HTML Parsing:**  
  BeautifulSoup was excellent in navigating the HTML structure, extract product details, and isolate key elements (like \<h3>, \<a>, and \<p> tags). Its flexible parsing capabilities made it an great choice for this assessment.

- **Handling Inconsistent Data Formats:**  
  Since both Grocery Store datas were differently formatted, this required some custom logic on both ends (regular JSON traversal for store A and HTML parsing for store B), hence the two separate analysis.py files. I made it point to normalize the data as much as possible when creating the parsed_product files (eg. all uppercase, no punctuation, same formats and names for all variables) so that later Fuzzy Matching would be able to really compare the content of the strings without having to worry about format.

- **RapidFuzz for Fuzzy Matching:**  
  This was my first time using RapidFuzz for Fuzzy Matching / Levehnstein Distance, but despite minor differences in naming conventions or formatting, it was great for computing similarity scores, allowing me to match products even when there were slight differneces in the names between the datasets. However, since the current approach involves $O(n^2)$ comparisons, there is room for optimization (discussed later).

- **Normalization and Unit Price Calculation:**  
  Normalization of data was a critical step. This included standardizing product names, extracting quantities, and converting price formats (e.g. making all cents into dollars). To address discrepancies caused by different quantities (like 12oz vs 5oz), the process was extended to compute unit prices. This helps in making more accurate comparisons, particularly when products are sold in different package sizes, but there is still some room for improvement when comparing products accross different quantity types.

## Future TODO

- **Standardize units and add unit conversions:**  
  There were a few situations where the data ended up with the same product but different units (LB vs oz, for example), so some later support where units are calculated and standardized even more based on conversions between units would be optimal.

- **Improving Efficiency with a Model:**  
  Like I mentioned earlier, final results is being computed in $O(n^2)$ time because every single product in Grocery Store B is being checked against all the keys of the hashed Grocery Store A. If there was instead a simple model that directly "hashed" every single product name to some consistent file, then we could ultimately compute the final comparison in $O(n)$ since checking for a "best match" in the hashed Grocery Store A would become a $O(1)$ lookup.

- **Other Enhancements:**  
  Using some sort of implementation of candidate filtering techniques, such as locality-sensitive hashing (LSH) or embedding-based similarity search could likely narrow down the pool of potential matches, thereby reducing the number of expensive fuzzy comparisons required. Perhaps using other data structures like inverted indexes could further streamline lookup times and improve overall performance.

