
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

url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=APE,AMC"

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
sum = 0

print(response)
print(sum)
multiple_tickers = response["quoteResponse"]["result"]
def background_thread(sum_reg=0):
    """Example of how to send server generated events to clients."""
    print(multiple_tickers)
    while True:

        socketio.sleep(1)
        for ticker in multiple_tickers:
            regular_price = ticker["regularMarketPrice"]
            ticker_symbol = ticker["symbol"]
            if ticker_symbol == "AMC":
                amc_price = regular_price
            if ticker_symbol ==  "APE":
                ape_price = regular_price
        socketio.emit('my_response',
                      {'amc_price': amc_price,
                       'ape_price': ape_price,
                       'pooop': "poop"})

        print(amc_price+ape_price)
        print(f"AMC price {amc_price}")
        print(f"APE price {ape_price}")

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@socketio.event
def my_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})

# Receive the test request from client and send back a test response
@socketio.on('test_message')
def handle_message(data):
    print('received message: ' + str(data))
    emit('test_response', {'data': 'Test response sent'})

# Broadcast a message to all clients
@socketio.on('broadcast_message')
def handle_broadcast(data):
    print('received: ' + str(data))
    emit('broadcast_response', {'data': 'Broadcast sent'}, broadcast=True)

@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})

if __name__ == '__app__':
    socketio.run(app)