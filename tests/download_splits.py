import unittest
from unittest import TestCase
from scraper import download_splits_data, extract_table
from bs4 import BeautifulSoup


class TestDownloadSplits(TestCase):

    def test_download_splits(self):
        code = "AAPL"
        html = download_splits_data(code)
        with open(f"{code}.html", "w") as file:
            soup = BeautifulSoup(html, "html.parser")
            html = soup.prettify()
            file.write(html)
        print(html)

    def test_extract_table(self):
        code = "AAPL"
        with open(f"{code}.html", "r") as file:
            html = file.read()

        data = extract_table(code, html)
        self.assertEqual(len(data), 5)

    def test_no_split(self):
        code = "ETSY"
        html = download_splits_data(code)
        with open(f"{code}.html", "w") as file:
            soup = BeautifulSoup(html, "html.parser")
            html = soup.prettify()
            file.write(html)
        with open(f"{code}.html", "r") as file:
            html = file.read()
        data = extract_table(code, html)
        self.assertEqual(len(data), 0)


if __name__ == "__main__":
    unittest.main()
