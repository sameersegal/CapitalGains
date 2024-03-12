import unittest
from unittest import TestCase
from scraper import download_cii_data
from bs4 import BeautifulSoup

class TestDownloadCII(TestCase):

    def test_download_cii(self):
        html = download_cii_data()
        with open(f"cii.html", "w") as file:
            soup = BeautifulSoup(html, "html.parser")
            html = soup.prettify()
            file.write(html)
        print(html)

if __name__ == "__main__":
    unittest.main()
