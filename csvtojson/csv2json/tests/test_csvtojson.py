import unittest
import os
import json
from src.csvtojson import csv_to_json

class TestCsvToJson(unittest.TestCase):

    def setUp(self):
        self.csv_file = 'test.csv'
        self.json_file = 'test.json'
        with open(self.csv_file, 'w') as f:
            f.write("name,age\nAlice,30\nBob,25\n")

    def tearDown(self):
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)
        if os.path.exists(self.json_file):
            os.remove(self.json_file)

    def test_conversion_creates_json_file(self):
        csv_to_json(self.csv_file, self.json_file)
        self.assertTrue(os.path.exists(self.json_file))

    def test_conversion_content(self):
        csv_to_json(self.csv_file, self.json_file)
        with open(self.json_file, 'r') as f:
            data = json.load(f)
        expected_data = [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]
        self.assertEqual(data, expected_data)

    def test_conversion_without_json_file(self):
        csv_to_json(self.csv_file)
        expected_json_file = 'test.json'
        self.assertTrue(os.path.exists(expected_json_file))

    def test_empty_csv(self):
        empty_csv_file = 'empty.csv'
        with open(empty_csv_file, 'w') as f:
            f.write("")
        csv_to_json(empty_csv_file, self.json_file)
        with open(self.json_file, 'r') as f:
            data = json.load(f)
        self.assertEqual(data, [])
        os.remove(empty_csv_file)

if __name__ == '__main__':
    unittest.main()