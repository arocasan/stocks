
from threading import Lock
from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit
import requests
import json
# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

symbols = "AMC,APE"

url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbols}"

headers = {
    "Accept": "application/json",
    "User-Agent": "",

}

response = requests.request(
    "GET",
    url,
    headers=headers,
)

response = response.json()

multiple_tickers = response["quoteResponse"]["result"]
def background_thread():

    while True:
        socketio.sleep(1)
        for ticker in multiple_tickers:
            regular_price = ticker["regularMarketPrice"]
            ticker_symbol = ticker["symbol"]
            if ticker_symbol == "AMC":
                amc_symbol = "AMC"
                amc_price = regular_price
            if ticker_symbol == "APE":
                ape_symbol = "APE"
                ape_price = regular_price


        reg_sum = ape_price + amc_price
        print("{:.3f}".format(reg_sum))
        formatted_sum = "{:.3f}".format(reg_sum)
        print(f"Formatted reg sum {formatted_sum}")
        print(f"Raw regular sum:{amc_price+ape_price}")
        print(f"AMC price {amc_price}$USD")
        print(f"APE price {ape_price}$USD")
        socketio.emit('regular_market',
                      {'amc_symbol': f"${amc_symbol}", 'ape_symbol': f"${ape_symbol}",
                       'amc_price': amc_price, 'ape_price': ape_price
                       })

        socketio.sleep(1)
        for ticker in multiple_tickers:
            try:
                post_price = ticker["postMarketPrice"]
            except:
                post_price = ticker["regularMarketPreviousClose"]
                ticker_symbol = ticker["symbol"]
                if ticker_symbol == "AMC":
                    amc_symbol = "AMC"
                    amc_post_price = post_price
                if ticker_symbol == "APE":
                    ape_symbol = "APE"
                    ape_post_price = post_price
            else:
                ticker_symbol = ticker["symbol"]
            if ticker_symbol == "AMC":
                amc_symbol = "AMC"
                amc_post_price = post_price
            if ticker_symbol == "APE":
                ape_symbol = "APE"
                ape_post_price = post_price

        post_sum = ape_post_price + amc_post_price
        print("{:.3f}".format(post_sum))
        formatted_post_sum = "{:.3f}".format(post_sum)
        print(f"Formatted post sum{formatted_post_sum}")
        print(f"RAW post sum:{amc_post_price + ape_post_price}")
        print(f"AMC post price {amc_post_price}$USD")
        print(f"APE post price {ape_post_price}$USD")
        socketio.emit('post_market',
                      {'amc_symbol': f"${amc_symbol}", 'ape_symbol': f"${ape_symbol}",
                       'amc_price': amc_post_price, 'ape_price': ape_post_price
                       })

        socketio.sleep(1)
        for ticker in multiple_tickers:
            try:
                pre_price = ticker["preMarketPrice"]
            except:
                pre_price = ticker["regularMarketPreviousClose"]
                ticker_symbol = ticker["symbol"]
                if ticker_symbol == "AMC":
                    amc_symbol = "AMC"
                    amc_pre_price = pre_price
                if ticker_symbol == "APE":
                    ape_symbol = "APE"
                    ape_pre_price = pre_price
            else:
                ticker_symbol = ticker["symbol"]
                if ticker_symbol == "AMC":
                    amc_symbol = "AMC"
                    amc_pre_price = pre_price
                if ticker_symbol == "APE":
                    ape_symbol = "APE"
                    ape_pre_price = pre_price

        pre_sum = ape_pre_price + amc_pre_price
        print("{:.3f}".format(pre_sum))
        formatted_pre_sum = "{:.3f}".format(pre_sum)
        print(f"Formatted pre sum{formatted_pre_sum}")
        print(f"RAW pre sum:{amc_pre_price+ape_pre_price}")
        print(f"AMC pre price {amc_pre_price}$USD")
        print(f"APE pre price {ape_pre_price}$USD")
        socketio.emit('pre_market',
                      {'amc_symbol': f"${amc_symbol}", 'ape_symbol': f"${ape_symbol}",
                       'amc_price': amc_pre_price, 'ape_price': ape_pre_price
                       })


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})

if __name__ == '__app__':
    socketio.run(app)