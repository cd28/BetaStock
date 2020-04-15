# BetaStock
Japanese stock market daily high profit factor stocks extractor
----
BetaStockは、japanesebulls.comから毎日の株式データをダウンロードして分析するプログラムです。 japanesebulls.comは、各銘柄ごとに異なるローソク足の過去のリターンをすでに持っていますが、銘柄が多すぎて、翌日売買するため、最上部を抽出が必要です。 また、各ローソク足パターンの歴史profit factor（total profit/total loss）の計算はありません。このプログラムは、東京証券取引所のすべての株式データを毎日クロールし、取引可能なパターンをロックアウトします。6か月、12か月、24か月のローソク足チャートを使用して、4つ以上の星（ローソク足チャートでの取引により適しているという意味）を抽出するプログラムです。 profit factorを計算し、それを翌日に売買するための推奨株として使用できます。



japanesebulls.comは非常に古いWebサイトなので、Seleniumを使用してログインと一部クロールしました。



出力例：

https://github.com/cd28/BetaStock/blob/master/result/tokyo/2019-04-05-stock.csv 
