import time
from datetime import datetime, timedelta
from flask import Flask, render_template, url_for, request
import json
import matplotlib
import matplotlib.pyplot as plt
import seaborn
import yfinance as yf
import numpy as np
app = Flask(__name__)
matplotlib.use('Agg')

@app.route('/')
@app.route('/home')
def home():
    return render_template("index.html")

investment_amount=0
investment_present_Worth=0    
data_required=[]
portfolio_of_stocks=[]
overall_portfolio=[]
nav_price=0
current_price=0
present_investment_worth=0
def index_Investing():
    return nav_price
def default():
    return current_price

switcher = {
    'Index Investing': index_Investing   
    }
def switch(investment_type):
    return switcher.get(investment_type, default)()

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
    for strategy in strategy_name:
        iterator = iter(req_data[strategy])
        while True:
            try:
                item=next(iterator)
                invested_funds= (int(item['percentage'])/100)*investment_amount
                holdings = []
                stock_data = []
                stock_info = yf.Ticker(item['symbol'])
                nav_price=stock_info['navPrice']
                current_price=stock_info['currentPrice']
                present_stock_price= switch(strategy_name)
                stock_data.extend(item['name'])
                stock_data.extend(invested_funds)
                stock_data.extend(present_stock_price)
                data_required.append(stock_data)        
                history = stock_info.history(period="5d")
                share_count = invested_funds/present_stock_price
                holdings = get_stock_price(history,share_count)        
                portfolio_of_stocks.append(holdings)
                present_investment_worth = present_investment_worth + (present_stock_price*share_count)
                print("Invested Capital on ", item['name'], "is", invested_funds)
                print("Latest value of ", item['name'], "is", current_price)
                print(portfolio_of_stocks)            
            except StopIteration:
                break
            except Exception:
                raise
    return data_required

def build_stock_overall_portfolio():     
    i=0  
    items=[]
    while i < range(len(portfolio_of_stocks[0])):
        try:     
            stock_item_overall_portfolio=0 
            for j in range(len(portfolio_of_stocks)):
                stock_item_overall_portfolio =stock_item_overall_portfolio + portfolio_of_stocks[j][i]    
            
            overall_portfolio.append(stock_item_overall_portfolio)            
            i+=1
        except Exception:
            raise
    print("overall portfolio:",overall_portfolio)

def plot_stock_distribution(data,strategy_name):
    times=[]
    def prepare_stock_distribution_data(data):
        now = datetime.now()
        day = now.strftime('%m-%d-%Y')
        current_date = str(day)
        date_time = datetime.strptime(current_date, '%m-%d-%Y')
        times = [(date_time-timedelta(days=i)).strftime('%m-%d-%Y')
                for i in range(5, 0, -1)]
        print(overall_portfolio)
        print(times)    
        print(present_investment_worth)        
    plt.clf()
    plt.plot(times, overall_portfolio)
    plt.xlabel("The previous five days")
    plt.ylabel("USD amount")
    plt.title("The Current State of the Portfolio")
    plt.savefig('static/images/'+len(strategy_name)+'-investment-strategy.jpeg')
    pie_chart_investment = np.array([])
    labels = []
    
    for strategy in strategy_name:
        iterator = iter(data[strategy])      
        while True:
            try:
                stock_item=next(iterator)
                pie_chart_investment = np.append(pie_chart_investment, int(stock_item['percentage']/len(strategy_name)))
                labels.append(stock_item['name'])
            except StopIteration:
                break
            except Exception:
                raise   
    plt.clf()
    plt.title("Money allocated to each stock")
    plt.pie(pie_chart_investment, labels = labels)
    plt.savefig('static/images/pie_chart-'+len(strategy_name)+'-investment-strategy.jpeg') 

def apply_investment_strategies(strategies,req_data,investment_value):
    investment_amount=(int(investment_value))
    strategies=[]
    for strat in strategies:
        strategies.append(strat)
        
    stock_current_info = build_stock_portfolio(req_data,strategies,investment_amount)
    build_stock_overall_portfolio()
    plot_stock_distribution(req_data,strategies)
    return stock_current_info

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

    if len(strategies) == 2:
        stock_data_res = apply_investment_strategies(investment_strategy,data, investment_amount)
        for i in range(4):
            stocks.append(stock_data_res[i][0])
            stock_investment_funds.append(stock_data_res[i][1])
            stock_prices.append(stock_data_res[i][2])
        
        return render_template('one_strategy.html', name=investment_amount, strategy=investment_strategy, stock1 = stocks[0], stock2 = stocks[1], stock3 = stocks[2], stock4 = stocks[3], stock1_price = stock_prices[0], stock2_price = stock_prices[1], stock3_price = stock_prices[2], stock4_price = stock_prices[3], stock1_money = stock_investment_funds[0], stock2_money = stock_investment_funds[1], stock3_money = stock_investment_funds[2], stock4_money = stock_investment_funds[3], url='static/images/1-investment-strategy.jpeg', url_pie = 'static/images/pie_chart-1-investment-strategy.jpeg')
    else:
        amount = int(investment_amount)
        strategy_one_list = strategies[0:2]
        strategy_two_list = strategies[3:]
        strategy1 = ' '.join(strategy_one_list)
        strategy2 = ' '.join(strategy_two_list)
        strategies_combined=[]
        strategies_combined.append(strategy1)
        strategies_combined.append(strategy2)
        info = apply_investment_strategies(strategies_combined,data,amount)
        for i in range(8):
            stocks.append(stock_data_res[i][0])
            stock_investment_funds.append(stock_data_res[i][1])
            stock_prices.append(stock_data_res[i][2])
       
        return render_template('two_strategies.html', name=investment_amount/2, strategy=strategy1, strategy2 = strategies, stock1 = stocks[0], stock2 = stocks[1], stock3 = stocks[2], stock4 = stocks[3], stock5 = stocks[4], stock6 = stocks[5], stock7 = stocks[6], stock8 = stocks[7], stock1_price = stock_prices[0], stock2_price = stock_prices[1], stock3_price = stock_prices[2], stock4_price = stock_prices[3], stock5_price = stock_prices[4], stock6_price = stock_prices[5], stock7_price = stock_prices[6], stock8_price = stock_prices[7], stock1_money = stock_investment_funds[0], stock2_money = stock_investment_funds[1], stock3_money = stock_investment_funds[2], stock4_money = stock_investment_funds[3], stock5_money = stock_investment_funds[4], stock6_money = stock_investment_funds[5], stock7_money = stock_investment_funds[6], stock8_money = stock_investment_funds[7],url='static/images/2-investment-strategy.jpeg', url_pie = 'static/images/pie_chart-2-investment-strategy.jpeg')


if __name__ == "__main__":
    app.run(debug=True)
