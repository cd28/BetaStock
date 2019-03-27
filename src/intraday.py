from math import ceil, floor
from os import listdir

import pandas as pd

import lib


def main():
    wait = 3
    browser = lib.monex_login(wait)

    market = 'tokyo'
    input_path = f'../result/{market}/'

    input_file = sorted(listdir(input_path))
    input_file = list(filter(lambda x: 'stock' in x, input_file))[-1]

    stocks = pd.read_csv(input_path + input_file, index_col=0, encoding='utf-8').T
    for ticker in stocks.index:
        monex = lib.search(browser, ticker, wait)
        o = monex['open']
        bid = monex['bid']
        ask = monex['ask']

        pattern = stocks.loc[ticker, 'pattern']
        target = float(stocks.loc[ticker, 'target'])
        stop = float(stocks.loc[ticker, 'stop'])

        if 'BULLISH' in pattern:
            buy = float(stocks.loc[ticker, 'buy'])

            if ask <= o or ask <= buy:
                lib.print_time(f'{ticker}, buy: {buy}, ask: {ask}, drop {ticker}')
                stocks.drop(ticker, inplace=True)
                continue

            reward = floor(target - ask)
            risk = ceil(ask - stop)
            stocks.loc[ticker, 'entry'] = ask
        elif 'BEARISH' in pattern:
            sell = float(stocks.loc[ticker, 'sell'])

            if bid >= o or bid >= sell:
                lib.print_time(f'{ticker}, sell: {sell}, bid: {bid}, drop {ticker}')
                stocks.drop(ticker, inplace=True)
                continue

            reward = floor(bid - target)
            risk = ceil(stop - bid)
            stocks.loc[ticker, 'entry'] = bid
        else:
            raise Exception

        rr = lib.floor2(reward / risk)
        er = lib.floor2((target / ask - 1) * 100)

        volume_price_min = 100000 * 1000
        er_min = 5
        rr_min = 1.5

        volume_price = monex['volume'] * stocks.loc[ticker, 'entry']
        if volume_price < volume_price_min:
            lib.print_time(f'{volume_price} < {volume_price_min}, drop {ticker}')
            stocks.drop(ticker, inplace=True)
            continue

        if er < er_min:
            lib.print_time(f'er: {er} < {er_min}, rr: {rr}, drop {ticker}')
            stocks.drop(ticker, inplace=True)
            continue

        if er < er_min:
            lib.print_time(f'er: {er} < {er_min}, rr: {rr}, drop {ticker}')
            stocks.drop(ticker, inplace=True)
            continue

        if rr < rr_min:
            lib.print_time(f'rr: {rr} < {rr_min}, er: {er}, drop {ticker}')
            stocks.drop(ticker, inplace=True)
            continue

        stocks.loc[ticker, 'er'] = er
        stocks.loc[ticker, 'n_rr'] = rr
        stocks.loc[ticker, 'n_reward'] = reward
        stocks.loc[ticker, 'n_risk'] = risk
        stocks.loc[ticker, 'n_v'] = monex['volume']

    lib.monex_logout(browser, wait)

    if len(stocks) != 0:
        stocks = stocks.sort_values(by=['er', 'n_rr'], ascending=False)
        lib.print_time(stocks.T)

    lib.print_time(f'{len(stocks)} stock(s)!')


if __name__ == '__main__':
    main()
