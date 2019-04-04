from time import sleep

from bs4 import BeautifulSoup
from selenium.webdriver.support.select import Select

import lib

signal_url = {
    'tokyo': 'https://www.japanesebulls.com/members/SignalList.aspx?lang=en&MarketSymbol=TOKYO'
}


def extract_signal_page(browser):
    source = browser.page_source
    soup = BeautifulSoup(source, 'lxml')
    table_data = soup.findAll('td')
    table_data = table_data[45:-1]
    table_data = list(map(lambda x: x.text.strip(), table_data))

    data = []
    for i in range(0, len(table_data), 12):
        temp = table_data[i:i + 12]
        temp[0] = temp[0].split('.T')[0]
        for j in [2, 3, 4]:
            temp[j] = temp[j].replace('☆', '')
            if temp[j] == '':
                temp[j] = '0'
        for j in [6, 7, 8, 9]:
            temp[j] = str(float(temp[j]))
        temp[-1] = lib.no_comma(temp[-1])
        temp = temp[:5] + temp[6:-2] + temp[-1:]
        data.append(temp)
    return data


def select_all_signal_types(browser, wait):
    lib.print_time('select all signal types')
    select = Select(browser.find_element_by_id('MainContent_SelectSignal'))
    select.select_by_visible_text('ALL SIGNAL TYPES')
    sleep(wait)


def signal_sort_by_ticker(browser, wait):
    lib.print_time('sort by ticker')
    browser.find_element_by_id('MainContent_SignalListGrid1_col0').click()
    sleep(wait)


def download(browser, market, wait):
    url = signal_url[market]
    lib.to(browser, url, wait)
    select_all_signal_types(browser, wait)
    signal_sort_by_ticker(browser, wait)

    output_path = f'../result/{market}/'
    output_name = lib.get_date() + '-signal.csv'
    columns = 'ticker,name,star6,star12,star24,o,h,l,c,v'

    lib.create_csv(output_path, output_name, columns)

    page_no = 1
    max_page_no = lib.get_max_page_no(browser, wait)
    lib.print_time(f'signal max page no is {max_page_no}')
    while True:
        try:
            data = extract_signal_page(browser)
            lib.append_to_csv(output_path, output_name, data)
            page_no += 1
            lib.next_page(browser, page_no, wait)
        except Exception:
            if page_no == max_page_no + 1:
                lib.print_time('the end of the page')
                break
            else:
                raise Exception


def main():
    market = 'tokyo'
    wait = 3

    lib.print_time(f'download {market} signals')
    browser = lib.bulls_login(market, wait)

    if lib.is_today(browser):
        download(browser, market, wait)
        lib.bulls_logout(browser, market, wait)
    else:
        lib.print_time('old data')
        lib.bulls_logout(browser, market, wait)
        raise Exception


if __name__ == '__main__':
    main()
