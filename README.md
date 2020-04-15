# BetaStock
Japanese stock market daily high profit factor stocks extractor
----
BetaStockは、japanesebulls.comから毎日の株式データをダウンロードして分析するプログラムです。 japanesebulls.comは、各銘柄ごとに異なるローソク足の過去のリターンをすでに持っていますが、銘柄が多すぎて、翌日売買するため、最上部を抽出が必要です。 また、各ローソク足パターンの歴史profit factor（total profit/total loss）の計算はありません。このプログラムは、東京証券取引所のすべての株式データを毎日クロールし、取引可能なパターンをロックアウトします。6か月、12か月、24か月のローソク足チャートを使用して、4つ以上の星（ローソク足チャートでの取引により適しているという意味）を抽出するプログラムです。 profit factorを計算し、それを翌日に売買するための推奨株として使用できます。



japanesebulls.comは非常に古いWebサイトなので、Seleniumを使用してログインと一部クロールしました。



出力例：

https://github.com/cd28/BetaStock/blob/master/result/tokyo/2019-04-05-stock.csv 
----
When I was studying candlestick charts online, I found a good website that stats the past performance of daily candlestick charts
but I want to do more analysis locally.
BetaStock is a program that downloads and analyzes daily stock data from japanesebulls.com. japanesebulls.com already has a
different candlestick past return for each stock, but there are too many stocks to buy and sell the next day, so the top ones must
be extracted.
There is no calculation of historical profit factor (total profit / total loss) for each candlestick pattern. This program crawls all
stock data on the Tokyo Stock Exchange daily and locks out tradeable patterns. A program that extracts four or more stars
(meaning better for trading on candlestick charts) using candlestick charts for 6, 12, and 24 months. You can calculate the profit
factor and use it as a recommended stock to buy and sell the next day.
japanesebulls.com is a very old website, so I used Selenium and BeautifulSoup to log in and crawl the data.
Example output: https://github.com/cd28/BetaStock/blob/master/result/tokyo/2019-04-05-stock.csv
