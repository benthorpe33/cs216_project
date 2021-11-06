import pandas as pd
from pandas import DataFrame
import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
url = 'https://www.nba.com/stats/players/shots-general/'
driver.get(url=url)
page_source = driver.page_source
bs = BeautifulSoup(page_source, 'html.parser')
num_pages = int(bs.findAll(True, {'class': 'stats-table-pagination__info'})[0].text.strip()[-1])
all_players = pd.DataFrame()
for i in range(0, num_pages):
    table = bs.find_all('table')[0]
    df = pd.read_html(str(table))[0].droplevel(level=0, axis=1)
    all_players = pd.concat([all_players, df])
    element = driver.find_element_by_class_name('stats-table-pagination__next')
    element.click()
    time.sleep(.5)
    page_source = driver.page_source
    bs = BeautifulSoup(page_source, 'html.parser')
all_players.reset_index(drop=True, inplace=True)
all_players['Year'] = 2021