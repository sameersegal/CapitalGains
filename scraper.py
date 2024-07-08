import re
import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_splits(code: str):

    if code == "GRINDWELL":
        splits = pd.DataFrame(columns=["Date", "Splits"], data=[["07/14/2016", "2 for 1"]])
    else:

        html = download_splits_data(code)
        data = extract_table(code, html)
        print(f"Splits for {code}")
        splits = pd.DataFrame(data, columns=["Date", "Splits"])

    r = re.compile(r'(\d+) for (\d+)')

    def extract_ratio(x):
        m = r.match(x)
        return int(m.group(1)) / int(m.group(2)) if m else 1

    splits.loc[:, 'Ratio'] = splits['Splits'].apply(
        lambda x: extract_ratio(x))
    # print(splits)

    # convert date from MM/DD/YYYY to YYYY-MM-DD
    splits['Date'] = pd.to_datetime(splits['Date'], format='%m/%d/%Y')

    return splits


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
    

def download_usd_to_inr() -> float:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    url = "https://www.xe.com/currencyconverter/convert/?Amount=1&From=USD&To=INR"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(
            f"Failed to download {url} with status code {response.status_code}")
    html = response.text

    soup = BeautifulSoup(html, "html.parser")
    pattern = re.compile(f"1.00 US Dollar =", re.IGNORECASE)

    p_tag = soup.find('p', string=pattern)
    text = p_tag.find_next_sibling('p').text

    pattern = re.compile(r'(\d+.\d+) Indian Rupees')
    m = pattern.match(text)
    if m:
        return float(m.group(1))
    else:
        raise Exception(f"Failed to extract USD to INR conversion rate")