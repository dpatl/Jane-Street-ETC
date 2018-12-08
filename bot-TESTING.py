#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json
import datetime
import time
import random

# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name="PLAINJANES"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = True

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=0
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname
tcp_ip = '10.0.172.88'

# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.connect((exchange_hostname, port))
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())

def read_response(exchange):
    return json.loads(exchange.readline())

def getBuyOrders(output, security):
    if 'buy' in output and output['symbol'] == security:
        print(security, " BUY ------------")
        symbol = str(output['symbol'])
        buyOrders = output['buy']
        print(str(output['buy']))
    return 1

def getSellOrders(output, security):
    # LOOK for which exchange reads are for sell/buy orders
    if 'sell' in output and output['symbol'] == security:
        print(security, " SELL ------------")
        symbol = str(output['symbol'])
        sellOrders = output['sell']
        print("The ", security , " sell orders are: ")
        print(str(output['sell']))
    return 1

def getAvgBuyOrders(output, security):
    avg = 0
    minimum = 0
    maximum = 0
    volume = 0
    if 'buy' in output and output['symbol'] == security:
        print(security, " BUY =========")
        symbol = str(output['symbol'])
        buyOrders = output['buy']
        orders = [order[0] for order in output['buy']]
        volumes = [order[1] for order in output['buy']]
        volume = sum(volumes)
        avg = sum(orders)/len(orders)
        minimum = min(orders)
        maximum = max(orders)
        print(str(avg))
    return {'low':minimum, 'high':maximum , 'avg':avg, 'volume':volume}

def getAvgSellOrders(output, security):
    avg = 0
    minimum = 0
    maximum = 0
    volume = 0
    if 'sell' in output and output['symbol'] == security:
        print(security, " SELL =========")
        symbol = str(output['symbol'])
        buyOrders = output['sell']
        orders = [order[0] for order in output['sell']]
        volumes = [order[1] for order in output['buy']]
        volume = sum(volumes)
        avg = sum(orders)/len(orders)
        minimum = min(orders)
        maximum = max(orders)
        print(str(avg))
    return {'low':minimum, 'high':maximum ,'avg':avg, 'volume':volume}


#def arbitrageTrade(output, adr, etf):





# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_message = read_from_exchange(exchange)
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!

    while True:
        timeid = str(datetime.datetime.now()).split(" ")[1].replace(":","").split(".")[0]
        write_to_exchange(exchange, {"type": "add", "order_id": int(timeid) + random.randint(1,1001), "symbol": "BOND", "dir": "BUY", "price": 997, "size": 33})
        write_to_exchange(exchange, {"type": "add", "order_id": int(timeid) + random.randint(1,1001), "symbol": "BOND", "dir": "BUY", "price": 998, "size": 33})

        write_to_exchange(exchange, {"type": "add", "order_id": int(timeid) + random.randint(1,1001), "symbol": "BOND", "dir": "BUY", "price": 999, "size": 33})
        write_to_exchange(exchange, {"type": "add", "order_id": int(timeid) + random.randint(1,1001), "symbol": "BOND", "dir": "SELL", "price": 1002, "size": 99})


        #Exchange runs:
        #print("Hello Message:", hello_message, file=sys.stderr)

        message = read_from_exchange(exchange)
        #print("Echange:", message, file=sys.stderr)

        adr_sell = getAvgSellOrders(message, "BABA")
        etf_sell = getAvgSellOrders(message, "BABZ")
        adr_buy = getAvgBuyOrders(message, "BABA")
        etf_buy = getAvgBuyOrders(message, "BABZ")

        if etf_sell['low'] + 10 < adr_buy['high']:
            write_to_exchange(exchange, {"type": "add", "order_id": random.randint(1,1001), "symbol": "BABZ", "dir": "BUY", "price": etf_sell['low'], "size": max(1, etf_sell['volume']/3)})
            write_to_exchange(exchange, {"type": "convert", "order_id": random.randint(1,1001), "symbol": "BABA", "dir": "BUY", "size": max(1, adr_buy['volume']/4)})
            write_to_exchange(exchange, {"type": "add", "order_id": random.randint(1,1001), "symbol": "BABA", "dir": "SELL", "price": adr_buy['high'], "size": max(adr_buy['volume']/3)})
        elif adr_sell['low'] + 10 < etf_buy['high']:
            write_to_exchange(exchange, {"type": "add", "order_id": random.randint(1,1001), "symbol": "BABA", "dir": "BUY", "price": adr_sell['low'], "size": max(1, adr_buy['volume']/4)})
            write_to_exchange(exchange, {"type": "convert", "order_id": random.randint(1,1001), "symbol": "BABA", "dir": "SELL", "size": adr_buy['volume']/3})        
            write_to_exchange(exchange, {"type": "add", "order_id": random.randint(1,1001), "symbol": "BABZ", "dir": "SELL", "price": etf_buy['high'], "size": max(1, adr_buy['volume']/4)})
        message = read_from_exchange(exchange)
        print("Echange:", message, file=sys.stderr)

        #getAdrSellOrders(message, "BABA")
        #getAdrSellOrders(message, "BABZ")

if __name__ == "__main__":
    main()
