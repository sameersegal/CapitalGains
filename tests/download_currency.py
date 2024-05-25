from unittest import TestCase
from scraper import download_usd_to_inr

class TestCurrency(TestCase):

    def test_download_currency(self):
        price = download_usd_to_inr()
        self.assertAlmostEqual(price, 83, delta=1.0)