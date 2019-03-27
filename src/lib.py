from datetime import datetime
from json import load
from math import floor
from os import listdir, unlink
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver

site_url = {
    'japanese': {
        'login': 'https://www.japanesebulls.com/Signin.aspx?lang=en',
        'logout': 'https://www.japanesebulls.com/members/Logout.aspx?lang=en&RememberMe=0'
    }
}


######################################################
def market_to_site(market):
    if market == 'tokyo':
        site = 'japanese'
    else:
        raise Exception
    return site


def bulls_login(market, wait):
    site = market_to_site(market)
    url = site_url[site]['login']
    browser = webdriver.Chrome()
    print_time(f'{site}bulls login')
    browser.get(url)

    handler = open('../config.json', 'r', encoding='utf-8')
    login = load(handler)
    handler.close()

    email = login['bulls_email']
    password = login['bulls_password']

    email_box = browser.find_element_by_id('MainContent_uEmail')
    email_box.send_keys(email)
    password_box = browser.find_element_by_id('MainContent_uPassword')
    password_box.send_keys(password)
    browser.find_element_by_id('MainContent_btnSubmit').click()

    sleep(wait)
    return browser


def bulls_logout(browser, market, wait):
    site = market_to_site(market)
    url = site_url[site]['logout']
    print_time(f'{site}bulls logout')
    browser.get(url)

    sleep(wait)
    browser.close()


def to(browser, url, wait):
    print_time(f'to {url}')
    browser.get(url)
    sleep(wait)


def next_page(browser, page_no, wait):
    print_time(f'go to page {page_no}')
    browser.find_element_by_class_name('dxWeb_pNext').click()
    sleep(wait)


def get_stock_page_source(browser, market, ticker, wait):
    site = market_to_site(market)
    url = f'https://www.{site}bulls.com/members/SignalPage.aspx?lang=en&Ticker={ticker}'
    to(browser, url, wait)
    return browser.page_source


######################################################
def monex_login(wait):
    print_time('monex login')
    browser = webdriver.Chrome()
    url = 'https://www.monex.co.jp'
    browser.get(url)

    handler = open('../config.json', 'r', encoding='utf-8')
    login = load(handler)
    handler.close()

    id = login['monex_id']
    password = login['monex_password']

    id_box = browser.find_element_by_id('loginid')
    id_box.send_keys(id)
    password_box = browser.find_element_by_id('passwd')
    password_box.send_keys(password)
    browser.find_element_by_class_name('btn_login_top').click()

    sleep(wait)
    return browser


def monex_logout(browser, wait):
    print_time('monex logout')
    browser.find_element_by_class_name('btn_logout').click()

    sleep(wait)
    browser.close()


def search(browser, ticker, wait):
    print_time(f'monex search {ticker}')
    ticker_box = browser.find_element_by_id('txt_order-buy')
    ticker_box.send_keys(ticker)
    browser.find_element_by_class_name('btn_order-buy').click()
    sleep(wait)

    page_source = browser.page_source
    soup = BeautifulSoup(page_source, 'lxml')

    current_price = soup.find('span', {'id': 'currentPrice'}).text
    ask = soup.find('strong', {'id': 'ask'}).text
    ask_vol = soup.find('span', {'id': 'askVol'}).text
    bid = soup.find('strong', {'id': 'bid'}).text
    bid_vol = soup.find('span', {'id': 'bidVol'}).text

    prev_price = soup.find('td', {'id': 'prevPrice'}).text
    open_price = soup.find('td', {'id': 'oPrice'}).text
    high_price = soup.find('td', {'id': 'hPrice'}).text
    low_price = soup.find('td', {'id': 'lPrice'}).text
    volume = soup.find('td', {'id': 'volume'}).text

    stock_info = {
        'ticker': ticker,
        'open': float_no_comma(open_price),
        'high': float_no_comma(high_price),
        'low': float_no_comma(low_price),
        'close': float_no_comma(current_price),
        'prev_close': float_no_comma(prev_price),
        'volume': int_no_comma(volume),
        'bid': float_no_comma(bid),
        'ask': float_no_comma(ask),
        'bid_vol': int_no_comma(bid_vol),
        'ask_vol': int_no_comma(ask_vol),
    }
    return stock_info


######################################################
def get_date():
    return datetime.now().strftime('%Y-%m-%d')


def print_time(string):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'{now} => {string}')


def create_csv(filepath, filename, columns):
    print_time(f'create {filepath}{filename}, and write columns')
    handler = open(filepath + filename, 'w', encoding='utf-8')
    handler.write(f'{columns}\n')
    handler.close()


def append_to_csv(filepath, filename, data):
    print_time(f'append to {filepath}{filename}')
    handler = open(filepath + filename, 'a', encoding='utf-8')
    for line in data:
        handler.write(','.join(line) + '\n')
    handler.close()


def have_files(filenames, directory):
    if set(filenames) == set(listdir(directory)):
        return True
    return False


def clear_directory(directory):
    filenames = listdir(directory)
    for filename in filenames:
        unlink(directory + filename)
    if len(listdir(directory)) == 0:
        print_time(f'{directory} is clean')


def save(filepath, filename, data):
    print_time(f'save to {filepath}{filename}')
    handler = open(filepath + filename, 'w', encoding='utf-8')
    handler.write(data)
    handler.close()


def floor2(num):
    return floor(num * 100) / 100


def no_comma(string):
    return ''.join(string.split(','))


def int_no_comma(num):
    return int(no_comma(num))


def float_no_comma(num):
    return float(no_comma(num))
