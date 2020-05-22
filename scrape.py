import json
import time

from bs4 import BeautifulSoup
import requests
import pandas as pd

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from tqdm import tqdm

base_url = "https://trustpilot.com"


def get_soup(url):
    return BeautifulSoup(requests.get(url).content, 'lxml')

data = {}

soup = get_soup(base_url + '/categories')
for category in soup.findAll('div', {'class': 'subCategory___BRUDy'}):
    header = category.find('h3', {'class': 'subCategoryHeader___36ykD'})
    span = header.find('a',{'class':'navigation___2Efid'})
    name = span.find('span').text
    name = name.strip()
    data[name] = {}
    sub_categories = category.find('div', {'class': 'subCategoryList___r67Qj'})
    for sub_category in sub_categories.findAll('div', {'class': 'subCategoryItem___3ksKz'}):
        sub_category_span = sub_category.find('a', {'class': 'navigation___2Efid'})
        sub_category_name =  sub_category_span.find('span').text
        sub_category_uri = sub_category.find('a', {'class': 'navigation___2Efid'})['href']
        data[name][sub_category_name] = sub_category_uri

def extract_company_urls_form_page():
    a_list = driver.find_elements_by_xpath('//a[@class="navigation___2Efid"]')
    print(a_list)
    urls = [a.get_attribute('href') for a in a_list]
    dedup_urls = list(set(urls))
    return dedup_urls


def go_next_page():
    try:
        button = driver.find_element_by_xpath('//a[@class="button button--primary next-page"]')
        return True, button
    except NoSuchElementException:
        return False, None

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('start-maximized')
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")

prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)
#driver = webdriver.Chrome(chrome_options=options, executable_path=r'C:\Users\Desktop\chromedriver_win32\chromedriver.exe')

driver = webdriver.Chrome(ChromeDriverManager().install(), options = options)


#driver = webdriver.Chrome(executable_path='/Users/akankshapriya/PycharmProjects/Real-time-sentiment-analysis-of-Brand-reviews/chromedriver', options=options)

timeout = 3

company_urls = {}
for category in tqdm(data):
    for sub_category in tqdm(data[category], leave=False):
        company_urls[sub_category] = []

        url = base_url + data[category][sub_category] + "?numberofreviews=0&timeperiod=0&status=all"
        driver.get(url)
        try:
            element_present = EC.presence_of_element_located(
                (By.CLASS_NAME, 'category-business-card card'))

            WebDriverWait(driver, timeout).until(element_present)
        except:
            pass

        next_page = True
        c = 1
        while next_page:
            extracted_company_urls = extract_company_urls_form_page()
            print("extracted_company_urls",extracted_company_urls)
            company_urls[sub_category] += extracted_company_urls
            next_page, button = go_next_page()

            if next_page:
                c += 1
                next_url = base_url + data[category][
                    sub_category] + "?numberofreviews=0&timeperiod=0&status=all" + f'&page={c}'
                driver.get(next_url)
                try:
                    element_present = EC.presence_of_element_located(
                        (By.CLASS_NAME, 'category-business-card card'))

                    WebDriverWait(driver, timeout).until(element_present)
                except:
                    pass

with open('./exports/company_urls_en', 'w') as f:
    json.dump(company_urls, f)

consolidated_data = []

for category in data:
    for sub_category in data[category]:
        for url in company_urls[sub_category]:
            consolidated_data.append((category, sub_category, url))

df_consolidated_data = pd.DataFrame(consolidated_data, columns=['category', 'sub_category', 'company_url'])

df_consolidated_data.to_csv('./exports/consolidate_company_urls.csv', index=False)

#df_consolidated_data.head()