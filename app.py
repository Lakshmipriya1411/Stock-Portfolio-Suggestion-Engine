import time
from datetime import datetime, timedelta
from flask import Flask, render_template, url_for, request
import json
import matplotlib
import matplotlib.pyplot as plt
import yfinance as yf
import requests
import numpy as np
from termcolor import colored as cl
app = Flask(__name__)
matplotlib.use('Agg')

@app.route('/')
@app.route('/home')
def home():
    return render_template("index.html")

investment_amount=0
data_required=[]
portfolio_of_stocks=[]

def clear_globals():
    investment_amount=0
    data_required=[]
    portfolio_of_stocks=[]

def switch(investment_type,stock_info):
    if investment_type == 'Index Investing':
        return stock_info.info['navPrice']
    else:    
        return stock_info.info['currentPrice']

def get_stock_price(history,share_count):
    total_price=[]
    iterator = iter(history['Close']) 
    while True: 
        try: 
            item_price = next(iterator) 
            total_price.append(item_price*share_count)
        except StopIteration: 
            break 
        except Exception: 
            raise 
    return total_price

def build_stock_portfolio(req_data,strategy_name,investment_amount):  
    # global present_investment_worth
    investment_worth = 0
    present_stock_price = 0
    for strategy in strategy_name:
        iterator = iter(req_data[strategy])
        while True:
            try:
                item=next(iterator)
                invested_funds= (int(item['percentage'])/100)*investment_amount
                holdings = []
                stock_data = []
                stock_info = yf.Ticker(item['symbol'])
                present_stock_price= switch(strategy,stock_info)               
                stock_data.append(item['name'])
                stock_data.append(invested_funds)
                stock_data.append(present_stock_price)
                stock_data.append(item['link'])
                data_required.append(stock_data)        
                history = stock_info.history(period="5d")
                share_count = invested_funds/present_stock_price
                holdings = get_stock_price(history,share_count)        
                portfolio_of_stocks.append(holdings)
                investment_worth += (present_stock_price*share_count)
                print("Invested Capital on ", item['name'], "is", invested_funds)
                print("Latest value of ", item['name'], "is", present_stock_price)
                print(portfolio_of_stocks)            
            except StopIteration:
                break
            except Exception:
                raise
    return data_required

def build_stock_overall_portfolio():     
    i=0  
    items=[]
    print("hello tets")
    print(portfolio_of_stocks)
    overall_portfolio = []
    while i < len(portfolio_of_stocks[0]):
        try:     
            stock_item_overall_portfolio=0 
            for j in range(len(portfolio_of_stocks)):
                if portfolio_of_stocks[j]:
                    stock_item_overall_portfolio =stock_item_overall_portfolio + portfolio_of_stocks[j][i]    
            
            overall_portfolio.append(stock_item_overall_portfolio)            
            i+=1
        except Exception:
            raise
    print("overall portfolio:",overall_portfolio)
    return overall_portfolio

def plot_stock_distribution(data,strategy_name,overall_portfolio):
    times=[]
    def prepare_stock_distribution_data(data,overall_portfolio):
        now = datetime.now()
        day = now.strftime('%m-%d-%Y')
        current_date = str(day)
        date_time = datetime.strptime(current_date, '%m-%d-%Y')
        times = [(date_time-timedelta(days=i)).strftime('%m-%d-%Y')
                for i in range(5, 0, -1)]
        final_len=min(len(times),len(overall_portfolio))
        times=times[0:final_len]
        overall_portfolio=overall_portfolio[0:final_len]
        print(overall_portfolio)
        return times    
    times = prepare_stock_distribution_data(data,overall_portfolio)      
    plt.clf()
    plt.plot(times, overall_portfolio)
    plt.xlabel("The previous five days")
    plt.ylabel("USD amount")
    plt.title("The Current State of the Portfolio")
    plt.savefig('static/images/'+str(len(strategy_name))+'-investment-strategy.jpeg')
    pie_chart_investment = np.array([])
    labels = []
    
    for strategy in strategy_name:
        iterator = iter(data[strategy])      
        while True:
            try:
                stock_item=next(iterator)
                pie_chart_investment = np.append(pie_chart_investment, int(stock_item['percentage'])/len(strategy_name))
                labels.append(stock_item['name'])
            except StopIteration:
                break
            except Exception:
                raise   
    plt.clf()
    plt.title("Money allocated to each stock")
    plt.pie(pie_chart_investment, labels = labels)
    plt.savefig('static/images/pie_chart-'+str(len(strategy_name))+'-investment-strategy.jpeg') 

def apply_investment_strategies(strategies_data,req_data,investment_value):
    investment_amount=(int(investment_value))
    strategies=[]
    for strat in strategies_data:
        strategies.append(strat)
        
    stock_current_info = build_stock_portfolio(req_data,strategies,investment_amount)
    overall_portfolio = build_stock_overall_portfolio()
    plot_stock_distribution(req_data,strategies,overall_portfolio)
    return stock_current_info

@app.route('/news', methods=['POST', 'GET'])
def news():
    stock_symbols_mapping={'Tesla, Inc.':'TSLA','United Natural Foods, Inc.':'UNFI','Weyerhaeuser Company':'WY','Alphabet Inc.':'GOOG','Petco Health and Wellness Co. Inc.':'WOOF','Lyondell Basell Industries NV':'LYB','Nielsen Holdings PLC':'NLSN','Shopify Inc':'SHOP','Invesco Dow Jones Industrial Average Dividend ETF':'DJD','Vanguard Consumer Staples Index Fund ETF':'VDC','Schwab Emerging Markets Equity ETF':'SCHE','iShares Russell 3000 ETF':'IWV','UniFirst Corp':'UNF','Comcast Corporation  ':'CMCSA','Bank of New York Mellon  ':'BK','Walt Disney Co.':'DIS','Bank of America Corporation':'BAC','The Kraft Heinz Company':'KHC','Verizon Communications Inc.':'VZ','DaVita Inc.':'DVA'}
    api_key='628c0818caf297.26782673'
    #tock='AAPL.US'
    n_news=10
    offset=0
    #res = request.form.to_dict() 
    #print(res)
    stock_symbol=request.form.get("symbol")
    print("stocksym")
    print(stock_symbol)
    symbol=stock_symbols_mapping[stock_symbol]
    #symbol='GOOG'
    res=stock_news(symbol,'','',n_news,api_key)
    #print(res)
    return render_template('stock_news.html', news=res)
    #return res

def stock_news(stock, start_date, end_date, n_news, api_key, offset = 0):
   
    url = f'https://eodhistoricaldata.com/api/news?api_token={api_key}&s={stock}&limit={n_news}&offset={offset}'
    news_json = requests.get(url).json()
    
    news = []
    
    
    for i in range(len(news_json)):
        news_item=[]
        title = news_json[-i]['title']
        content=news_json[-i]['content']
        date=news_json[-i]['date'].split('T')[0]
        sentiment=news_json[-i]['sentiment']
        polarity=sentiment['polarity']
        neg=sentiment['neg']
        neu=sentiment['neu']
        pos=sentiment['pos']
        
        news_item.append(title)
        news_item.append(content)
        news_item.append(date)
        news_item.append(polarity)
        news_item.append(neg)
        news_item.append(neu)
        news_item.append(pos)
        news_item.append(stock)
        news.append(news_item)
        print(cl('{}. '.format(i+1), attrs = ['bold']), '{}'.format(title))
    
    return news
@app.route('/result', methods=['POST', 'GET'])
def result():
    res = request.form.to_dict()    
    investment_strategy = res["strategy"]
    investment_amount = res["name"]    
    with open('investing_strategies.json') as f:
        data = json.load(f)    
    strategies = investment_strategy.split()
    print(res)
    print(data)
    stocks = []
    stock_prices = []
    stock_investment_funds = []
    stock_links=[]
    if len(strategies) == 2:
        strategies_combined=[]
        strategies_combined.append(investment_strategy)
        stock_data_res = apply_investment_strategies(strategies_combined,data, investment_amount)
        for i in range(4):
            stocks.append(stock_data_res[i][0])
            stock_investment_funds.append(stock_data_res[i][1])
            stock_prices.append(stock_data_res[i][2])
            stock_links.append(stock_data_res[i][3])
        clear_globals()
        return render_template('one_strategy.html', name=investment_amount, strategy=investment_strategy, stock1 = stocks[0], stock2 = stocks[1], stock3 = stocks[2], stock4 = stocks[3], stock1_price = stock_prices[0], stock2_price = stock_prices[1], stock3_price = stock_prices[2], stock4_price = stock_prices[3], stock1_money = stock_investment_funds[0], stock2_money = stock_investment_funds[1], stock3_money = stock_investment_funds[2], stock4_money = stock_investment_funds[3],stock1_link=stock_links[0],stock2_link=stock_links[1],stock3_link=stock_links[2],stock4_link=stock_links[3], url='static/images/1-investment-strategy.jpeg', url_pie = 'static/images/pie_chart-1-investment-strategy.jpeg')
    else:
        amount = int(investment_amount)
        strategy_one_list = strategies[0:2]
        strategy_two_list = strategies[3:]
        strategy1 = ' '.join(strategy_one_list)
        strategy2 = ' '.join(strategy_two_list)
        strategies_combined=[]
        strategies_combined.append(strategy1)
        strategies_combined.append(strategy2)
        stock_data_res = apply_investment_strategies(strategies_combined,data,amount)
        for i in range(8):
            stocks.append(stock_data_res[i][0])
            stock_investment_funds.append(stock_data_res[i][1])
            stock_prices.append(stock_data_res[i][2])
            stock_links.append(stock_data_res[i][3])
        clear_globals()
        return render_template('two_strategies.html', name=amount/2, strategy=strategy1, strategy2 = strategy2, stock1 = stocks[0], stock2 = stocks[1], stock3 = stocks[2], stock4 = stocks[3], stock5 = stocks[4], stock6 = stocks[5], stock7 = stocks[6], stock8 = stocks[7], stock1_price = stock_prices[0], stock2_price = stock_prices[1], stock3_price = stock_prices[2], stock4_price = stock_prices[3], stock5_price = stock_prices[4], stock6_price = stock_prices[5], stock7_price = stock_prices[6], stock8_price = stock_prices[7], stock1_money = stock_investment_funds[0], stock2_money = stock_investment_funds[1], stock3_money = stock_investment_funds[2], stock4_money = stock_investment_funds[3], stock5_money = stock_investment_funds[4], stock6_money = stock_investment_funds[5], stock7_money = stock_investment_funds[6], stock8_money = stock_investment_funds[7],stock1_link=stock_links[0],stock2_link=stock_links[1],stock3_link=stock_links[2],stock4_link=stock_links[3],stock5_link=stock_links[4],stock6_link=stock_links[5],stock7_link=stock_links[6],stock8_link=stock_links[7],url='static/images/2-investment-strategy.jpeg', url_pie = 'static/images/pie_chart-2-investment-strategy.jpeg')


if __name__ == "__main__":
    app.run(debug=True)
