import unittest
import re
from utils import formatName, formatPrice, findBestMatch, findPriceDiff, findUnitPrice

"""
This class is for verifying utils functions and ensuring that they are 
meeting expected outputs before their use with the larger analysis files.
"""
class TestUtilsFunctions(unittest.TestCase):

    def test_formatName(self):
        # strings should return equal even with punctuation and different case
        input_name = "Hello, World! This is a test."
        expected_output = "HELLO WORLD THIS IS A TEST"
        self.assertEqual(formatName(input_name), expected_output)

    def test_formatPrice_with_slash(self):
        # when price has a slash (like 2/4.00) saying 2 items for 4 dollars, we should extract just price
        input_price = "2/$4.00"
        expected_output = "$4.00"
        self.assertEqual(formatPrice(input_price), expected_output)

    def test_formatPrice_with_cents(self):
        # if the price is given in cents, it should be converted to dollars.
        input_price = "40¢"
        expected_output = "0.40"
        self.assertEqual(formatPrice(input_price), expected_output)

    def test_formatPrice_with_units(self):
        # if a price ends with a unit, it should be removed
        input_price = "$4.00 oz"
        expected_output = "$4.00"
        self.assertEqual(formatPrice(input_price), expected_output)

    def test_findPriceDiff(self):
        # test from string conversion to int diffrence
        price_a = "$4.00"
        price_b = "$3.50"
        expected_diff = "$0.50"
        self.assertEqual(findPriceDiff(price_a, price_b), expected_diff)

    def test_findBestMatch(self):
        # dummy list of rpoduct names
        dummy_keys = ["APPLE JUICE", "BANANA SMOOTHIE", "ORANGE JUICE"]
        product_name = "APPLE JUICE"
        # call findBestMatch function
        best = findBestMatch(product_name, dummy_keys)
        self.assertIsNotNone(best) # should definitely find a match
        best_match, score, _ = best
        # ensure that the best_match should be "APPLE JUICE" and the score should be high (greater than 90)
        self.assertEqual(best_match, "APPLE JUICE")
        self.assertTrue(score >= 90)

    def test_findUnitPrice_with_quantity(self):
        # when the product name contains a quantity and unit, the function should calculate the unit price
        # it should extract this info from the product name and price
        product_name = "APPLE JUICE 500 ml"
        price = "$2.00"
        unit_price, quantity, unit = findUnitPrice(product_name, price)
        expected_unit_price = 2.0 / 500
        self.assertAlmostEqual(unit_price, expected_unit_price, places=5)
        self.assertEqual(quantity, 500)
        self.assertEqual(unit.upper(), "ML")

    def test_findUnitPrice_without_quantity(self):
        # if no quantity is found in the product name, the function should default to the entire price,
        # a quantity of 1, and a unit of "ITEM"
        product_name = "APPLE JUICE"
        price = "$2.00"
        unit_price, quantity, unit = findUnitPrice(product_name, price)
        self.assertEqual(unit_price, 2.0)
        self.assertEqual(quantity, 1)
        self.assertEqual(unit, "ITEM")

if __name__ == '__main__':
    unittest.main()