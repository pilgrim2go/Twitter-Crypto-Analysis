import sys
from cryptocompy import coin
from textblob import TextBlob
from searchtweets import ResultStream, gen_rule_payload, load_credentials, collect_results, gen_params_from_config
import matplotlib.pyplot as plt
import numpy as np
from addLogo import add_logo
from datetime import date, timedelta


#Twitter Credentials
premium_search_args = load_credentials(filename="twitter_keys.yaml", yaml_key="search_tweets_api", env_overwrite=False)


def inputArgs():

    sysArguments = []
    if len(sys.argv) > 1:
        test = True
        for i in range(1,len(sys.argv)):
            sysArguments.append(sys.argv[i].upper())
    print(sysArguments, "\n")

    try:
        coins = coin.get_coin_list(coins=sysArguments)
        # print(coins)
    except KeyError:
        print("""That Is Not A Valid Crypto Symbol Or The Coin Is Not Available On Most Major Exchanges.
    Please Enter A Valid Symbol After python crypto.py
    Example: python crypto.py btc ltc eth""")
        exit()


    fullNames = []
    if test == True:
        for j in range (0, len(sysArguments)):
            print(coins[sysArguments[j]]["CoinName"])
            fullName = coins[sysArguments[j]]['CoinName']
            fullNames.append(fullName)


    #Match symbol with full name of coin for future data.
    nameSymbolPair = []
    counter = 0
    for elem in sysArguments:
        temp = [elem,fullNames[counter]]
        counter += 1
        nameSymbolPair.append(temp)


    #Initialize queries
    queries = []
    for elem in nameSymbolPair:
        print(elem)
        if elem[0] == "HOT":
            queries.append('Holochain')
        else:
            queries.append('"${0}" OR "{1}"'.format(elem[0], elem[1]))
            counter += 1

    counts(queries, nameSymbolPair)
    sentiment(queries, nameSymbolPair)



#Sentiment Function That Will Perform The Sentiment Analysis On SysArg Variables
def sentiment(queriesParam, nameList):

    sentimentList = []
    for elem in queriesParam:
        rule = gen_rule_payload(elem, results_per_call=100)
        tweets = collect_results(rule, max_results = 100, result_stream_args=premium_search_args)
        temp = [tweet.all_text for tweet in tweets]
        sentimentList.append(temp)

    #Sentiment Analysis Using TextBlob. Uses Polarity on -1 to 1 scale with 0 being neutral.
    blobList=[]
    for elem in sentimentList:
        temp = []
        for i in range(0,len(elem)):
            blob = TextBlob(elem[i])
            temp.append(blob.sentiment[0])
        blobList.append(temp)

    print(blobList)

    #Makes a tuple of the coins full name/market name
    nametup = []
    for elem in nameList:
        nametup.append(elem[0])

    nametup = tuple(nametup)


    sentimentDict = {}
    for elem in nameList:
        sentimentDict[elem[1]] = None

    dictCounter = 0
    positiveTup= []
    negativeTup= []
    neutralTup= []

    for elem in blobList:
            print(len(elem), "\n")
            subdict = {"Sample Size": 100, "Positive": None, "Negative": None, "Neutral": None}
            sumPositive = sum(i > 0.0 for i in elem)
            sumNegative = sum(i<0.0 for i in elem)
            subdict["Positive"] = sumPositive
            subdict["Negative"] = sumNegative
            subdict["Neutral"] = 100 - sumPositive - sumNegative
            sentimentDict[nameList[dictCounter][1]] = subdict

            positiveTup.append(subdict["Positive"])
            negativeTup.append(subdict["Negative"])
            neutralTup.append(subdict["Neutral"])
            dictCounter += 1

    print(sentimentDict)


    #Beginning of analysis and graphing of charts
    positiveTup = tuple(positiveTup)
    neutralTup = tuple(neutralTup)
    negativeTup = tuple(negativeTup)

    print(positiveTup, neutralTup, negativeTup)

    yesterday = date.today() - timedelta(1)
    yesterday = str(yesterday)

    title = """Sentiment Analysis On Tweets About Crypto Currencies
    (Data Taken From 100 Most Recent Tweets)\n""" + yesterday

    fig2 = plt.figure(2)
    ax1 = fig2.add_subplot(111)

    font = {'family': 'Times New Roman',
            'color': 'black',
            'weight': 'bold',
            'size': 12,
            }

    plt.title(title, fontweight="bold")
    plt.xlabel('Crypto Currencies', fontdict = font)
    plt.ylabel('Sample Size', fontdict = font)


    N = len(nametup)
    ind = np.arange(N)
    width=0.30

    positive = plt.bar(ind, positiveTup, width, bottom = np.array(neutralTup) + np.array(negativeTup))
    neutral = plt.bar(ind, neutralTup, width, bottom = negativeTup)
    negative = plt.bar(ind, negativeTup, width)

    plt.yticks(np.arange(0,101,10))
    plt.xticks(ind, nametup)
    plt.legend((positive[0], neutral[0], negative[0]), ('Positive', 'Neutral', 'Negative'))
    #Info text on top right

    coordinate = 0.9
    counter = 0
    for elem in nameList:
        plt.figtext(0.95,coordinate,"[{0} = Positive {1}%/Negative {2}%/Neutral {3}%]".format(elem[1],sentimentDict[elem[1]]["Positive"],sentimentDict[elem[1]]["Negative"],sentimentDict[elem[1]]["Neutral"]), fontsize='8')
        coordinate = coordinate - 0.03
        counter += 1

    # plt.show()

    plt.savefig("sentimentchart.png", bbox_inches = "tight")
    add_logo("sentimentchart.png", "logo.png", "sentimentchart" + "(" + str(yesterday) + ").png")
    plt.close(fig2)



def counts(queries, nameList):
    # premium_search_args = load_credentials(filename="twitter_keys.yaml", yaml_key="search_tweets_api", env_overwrite=False)
    # queries = ['"$LTC" OR "Litecoin"','"$ETH" OR "Ethereum"','"$BTC" OR "Bitcoin"', 'Holochain', '"$NPXS" OR "Pundi X"']

    counts = []
    for i in range(0, len(queries)):
        count_rule = gen_rule_payload(queries[i], count_bucket="day")
        temp = collect_results(count_rule, result_stream_args=premium_search_args)
        print(temp)
        print("\n")
        counts.append(temp[1]['count'])
    print('\n', counts)


    """CryptoCompare"""
    from cryptocompy import price

    avgPrices = []
    toCurr = 'USD'
    yesterday = date.today() - timedelta(1)
    datestr = str(yesterday) + ' 00:00:00'

    for elem in nameList:
        # avgtemp = price.get_day_average_price(elem[0], toCurr)[elem[0]]['USD']
        # avgPrices.append(avgtemp)
        eodtemp = price.get_historical_eod_price(elem[0], toCurr, datestr, try_conversion=True)
        eodtemp = eodtemp[elem[0]][toCurr]
        avgPrices.append(eodtemp)

    plot(counts, avgPrices, nameList)


def plot(counts, avgPrices, nameList):
    """Data to plot"""
    yesterday = date.today() - timedelta(1)
    yesterday = str(yesterday)
    fig = plt.figure(1)
    ax0 = fig.add_subplot(111)
    plt.title("""Relation Between # of Tweet Mentions/Hashtags and Current Crypto Prices
    (Price Shown Is End Of Day Price)\n""" + yesterday, fontweight="bold")

    #Set Axis
    xRange = .25 * max(counts) + max(counts)
    randomColor = ['ro', 'bo', 'co', 'mo', 'yo', 'ko', 'go', '#eeefff']


    ax0.axis([0,xRange,0,max(avgPrices) + 500])
    counter = 0
    for el in counts:
        ax0.plot([el], [avgPrices[counter]], randomColor[counter], label=nameList[counter][0])
        counter += 1



    #Set labels and text, adjust text for each data point based on price and number of tweets.
    font = {'family': 'Times New Roman',
            'color': 'black',
            'weight': 'bold',
            'size': 12,
            }

    plt.xlabel('Number of Tweet Mentions/Hashtags', fontsize ='12', fontdict = font)
    plt.ylabel('Current Coin Price ($USD)', fontsize='12', fontdict = font)

    """Old implementation, used algorithm to place text above data points, worked fine with
    current BTC price but scared about future so reimplemented to just list prices outside axis"""

    changingVal = 0.9
    constantVal = 0.95
    counter = 0
    for el in nameList:
        plt.figtext(constantVal, changingVal, '[${0}/{1}/{2}]'.format(avgPrices[counter], counts[counter], el[0]))
        changingVal = changingVal - 0.03
        counter += 1
    plt.grid()
    plt.legend()


    plt.savefig("chart.png", bbox_inches = "tight")
    add_logo("chart.png", "logo.png", "tweetvolume" + "(" + yesterday + ").png")
    plt.close(fig)



inputArgs()
