import re
import requests
from bs4 import BeautifulSoup


def get_splits(code: str):
    pass


def download_splits_data(code: str) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    url = f"https://www.stocksplithistory.com/{code.lower()}/"
    response = requests.get(url, headers=headers)
    if response.status_code != 200 and response.status_code != 404:
        raise Exception(
            f"Failed to download {url} with status code {response.status_code}")
    else:
        return response.text


def extract_table(code: str, html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    pattern = re.compile(f"{code} Split History", re.IGNORECASE)

    b_tag = soup.find('b', string=pattern)

    if not b_tag:
        raise Exception(f"No split history found for {code}")

    table = b_tag.find_parent('table').find_parent('td').find_parent('tr')

    split_history = []

    for row in table.find_next_siblings('tr'):
        columns = row.find_all('td')
        date = columns[0].text.strip()
        ratio = columns[1].text.strip()
        split_history.append((date, ratio))

    return split_history[1:]

def download_cii_data() -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    url = "https://cleartax.in/s/cost-inflation-index"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(
            f"Failed to download {url} with status code {response.status_code}")
    else:
        return response.text
