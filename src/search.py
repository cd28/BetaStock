from os import listdir

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from math import ceil, floor

import lib
import signal
import status


def filter_stocks(market):
    signal_path = f'../result/{market}/' + lib.get_date() + '-signal.csv'
    status_path = f'../result/{market}/' + lib.get_date() + '-status.csv'
    sig = pd.read_csv(signal_path, index_col=0, encoding='utf-8')
    sta = pd.read_csv(status_path, index_col=0, encoding='utf-8')

    sta_in_sig = sig.loc[sta.index, ['name', 'star6', 'star12', 'star24', 'v', 'c']]
    stocks = pd.concat([sta, sta_in_sig], axis=1)
    stocks = stocks[['name', 'star6', 'star12', 'star24', 'v', 'c', 'buy', 'stop', 'sell']]

    stocks.index = stocks.index.astype(str)

    star6_min = 4
    star12_min = 4
    star24_min = 4
    volume_min = 0
    close_min = 0
    volume_close_min = volume_min * close_min
    stocks = stocks[
        (stocks['star6'] >= star6_min) &
        (stocks['star12'] >= star12_min) &
        (stocks['star24'] >= star24_min) &
        (stocks['v'] * stocks['c'] >= volume_close_min)]

    need_drop = stocks[np.isnan(stocks['buy']) & np.isnan(stocks['sell'])]
    stocks.drop(need_drop.index, inplace=True)

    lib.print_time(f'filter {len(stocks)} of {len(sta)} from {len(sig)}')
    return stocks


def download(browser, market, tickers, wait):
    filepath = f'../temp/{market}/'
    filenames = list(map(lambda x: f'{x}.html', tickers))
    if lib.have_files(filenames, filepath):
        lib.print_time(f'{len(tickers)} ticker(s) all downloaded')
    else:
        lib.clear_directory(filepath)
        for ticker in tickers:
            source = lib.get_stock_page_source(browser, market, ticker, wait)
            filename = f'{ticker}.html'
            lib.save(filepath, filename, source)


def analyze(market, stocks):
    input_path = f'../temp/{market}/'
    htmls = listdir(input_path)
    for html in htmls:
        input_handler = open(input_path + html, 'r', encoding='utf-8')
        soup = BeautifulSoup(input_handler, 'lxml')
        input_handler.close()

        ticker = soup.find('span', {'id': 'MainContent_CompanyTicker'}).text
        ticker = ticker.split('.T')[0]

        name = soup.find('span', {'id': 'MainContent_Name'}).text
        if name != stocks.loc[ticker, 'name']:
            lib.print_time(f'wrong name: {name}, drop {ticker}')
            stocks.drop(ticker, inplace=True)
            continue

        history_first_row = soup.find('tr', {'id': 'MainContent_PatternHistory_DXDataRow0'})
        history_first_row = history_first_row.find_all('td')
        history_first_row = list(map(lambda x: x.text, history_first_row))
        date = history_first_row[0]
        pattern = history_first_row[1]

        if '*' in pattern:
            pattern = pattern.replace(' *', '')

        patterns = soup.findAll('a', {'class': 'dxeHyperlink dx-nowrap'})
        patterns = list(map(lambda x: x.text, patterns))
        patterns_data = soup.findAll('td', {'class': 'dx-wrap dxgv dx-ar'})
        patterns_data = list(map(lambda x: x.text, patterns_data))
        patterns_data = list(map(lambda x: int(x.split('%')[0]) if '%' in x else int(x), patterns_data))

        performance = []
        for i in range(len(patterns)):
            temp = [patterns[i]]
            for j in patterns_data[8 * i:8 * i + 8]:
                temp.append(j)
            performance.append(temp)

        index = patterns.index(pattern)
        pattern_data = performance[index]
        total = pattern_data[1]
        confirmed = pattern_data[2]
        success = pattern_data[3]
        profit = pattern_data[6]
        loss = pattern_data[7]

        if confirmed == 0:
            lib.print_time(f'{confirmed} confirmation, drop {ticker}')
            stocks.drop(ticker, inplace=True)
            continue

        e = success / confirmed * profit - (confirmed - success) / confirmed * loss
        e = lib.floor2(e)

        stop = stocks.loc[ticker, 'stop']
        if 'BULLISH' in pattern:
            buy = stocks.loc[ticker, 'buy']
            target = floor(buy + buy * e / 100)
            reward = floor(target - buy)
            risk = ceil(buy - stop)
        elif 'BEARISH' in pattern:
            sell = stocks.loc[ticker, 'sell']
            target = ceil(sell - sell * e / 100)
            reward = floor(sell - target)
            risk = ceil(stop - sell)
        else:
            raise Exception

        rr = lib.floor2(reward / risk)

        e_min = 0
        rr_min = 0
        if e < e_min:
            lib.print_time(f'e: {e} < {e_min}, rr: {rr}, drop {ticker}')
            stocks.drop(ticker, inplace=True)
            continue

        if rr < rr_min:
            lib.print_time(f'rr: {rr} < {rr_min}, e: {e}, drop {ticker}')
            stocks.drop(ticker, inplace=True)
            continue

        stocks.loc[ticker, 'date'] = date
        stocks.loc[ticker, 'pattern'] = pattern
        stocks.loc[ticker, 'total'] = total
        stocks.loc[ticker, 'confirmed'] = confirmed
        stocks.loc[ticker, 'success'] = success
        stocks.loc[ticker, 'profit'] = profit
        stocks.loc[ticker, 'loss'] = loss
        stocks.loc[ticker, 'e'] = e
        stocks.loc[ticker, 'rr'] = rr
        stocks.loc[ticker, 'target'] = target
        stocks.loc[ticker, 'reward'] = reward
        stocks.loc[ticker, 'risk'] = risk

    if len(stocks) != 0:
        stocks = stocks.sort_values(by=['e', 'rr'], ascending=False)
        lib.print_time(stocks.T)

    output_path = f'../result/{market}/' + lib.get_date() + '-stock.csv'
    stocks.T.to_csv(output_path, index_label='ticker', encoding='utf-8')
    lib.print_time(f'{len(stocks)} stock(s)!')


def main():
    market = 'tokyo'
    wait = 3

    browser = lib.bulls_login(market, wait)
    signal.download(browser, market, wait)
    status.download(browser, market, wait)
    stocks = filter_stocks(market)
    download(browser, market, stocks.index, wait)
    lib.bulls_logout(browser, market, wait)
    analyze(market, stocks)


if __name__ == '__main__':
    main()
