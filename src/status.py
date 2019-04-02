from time import sleep

from bs4 import BeautifulSoup
from selenium.webdriver.support.select import Select

import lib

status_url = {
    'tokyo': 'https://www.japanesebulls.com/members/StatusList.aspx?lang=en&MarketSymbol=TOKYO'
}


def extract_status_page(browser):
    source = browser.page_source
    soup = BeautifulSoup(source, 'lxml')
    table_data = soup.findAll('td')
    table_data = table_data[51:-1]
    table_data = list(map(lambda x: x.text.strip(), table_data))

    data = []
    for i in range(0, len(table_data), 13):
        temp = table_data[i:i + 13]
        temp[0] = temp[0].split('.T')[0]
        for j in [6, 7, 8]:
            if temp[j] != '':
                temp[j] = str(float(temp[j]))
        temp = temp[:1] + temp[6:9]
        data.append(temp)
    return data


def select_status_type(browser, pattern, wait):
    lib.print_time(f'select {pattern} patterns')
    select = Select(browser.find_element_by_id('MainContent_SelectFormation'))
    if pattern == 'bullish':
        select.select_by_visible_text('ALL BULLISH PATTERNS')
    elif pattern == 'bearish':
        select.select_by_visible_text('ALL BEARISH PATTERNS')
    else:
        raise Exception
    sleep(wait)


def status_sort_by_ticker(browser, wait):
    lib.print_time('sort by ticker')
    browser.find_element_by_id('MainContent_StatusListGrid1_col0').click()
    sleep(wait)


def download(browser, market, wait):
    output_path = f'../result/{market}/'
    output_name = lib.get_date() + '-status.csv'
    columns = 'ticker,buy,stop,sell'
    lib.create_csv(output_path, output_name, columns)

    url = status_url[market]
    status = ['bullish', 'bearish']
    for pattern in status:
        lib.to(browser, url, wait)
        select_status_type(browser, pattern, wait)
        status_sort_by_ticker(browser, wait)

        page_no = 1
        max_page_no = lib.get_max_page_no(browser, wait)
        lib.print_time(f'{pattern} max page no is {max_page_no}')
        while True:
            try:
                data = extract_status_page(browser)
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

    lib.print_time(f'download {market} status')
    browser = lib.bulls_login(market, wait)
    download(browser, market, wait)
    lib.bulls_logout(browser, market, wait)


if __name__ == '__main__':
    main()
