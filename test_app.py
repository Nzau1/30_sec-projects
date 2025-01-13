import unittest
import pandas as pd
import os

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class TestExcelSearch(unittest.TestCase):
    def setUp(self):
        # Create a test Excel file
        data = {
            "Name": ["Alice", "Bob", "Charlie", "David"],
            "Age": [25, 30, 35, 40],
            "City": ["New York", "Los Angeles", "Chicago", "Houston"]
        }
        self.df = pd.DataFrame(data)
        self.file_path = os.path.join(UPLOAD_FOLDER, "test_file.xlsx")
        self.df.to_excel(self.file_path, index=False)

    def tearDown(self):
        # Remove the test file after tests
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def test_file_upload(self):
        # Test if the file exists
        self.assertTrue(os.path.exists(self.file_path))

    def test_search_all_columns_case_insensitive(self):
        # Test search in all columns (case insensitive)
        search_value = "alice"
        matches = self.df[self.df.apply(lambda row: row.astype(str).str.contains(search_value, case=False).any(), axis=1)]
        self.assertEqual(len(matches), 1)

    def test_search_specific_column_case_sensitive(self):
        # Test search in specific column (case sensitive)
        search_value = "David"
        matches = self.df[self.df["Name"].astype(str).str.contains(search_value, case=True)]
        self.assertEqual(len(matches), 1)

    def test_search_no_results(self):
        # Test search with no results
        search_value = "NotInData"
        matches = self.df[self.df.apply(lambda row: row.astype(str).str.contains(search_value, case=False).any(), axis=1)]
        self.assertTrue(matches.empty)

if __name__ == "__main__":
    unittest.main()
