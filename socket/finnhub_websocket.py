"""
==============================================================================
NAME: CURT LEBENSORGER
DATE: 12/19/2023
==============================================================================
"""

#https://pypi.org/project/websocket_client/
import websocket
import time
import json

class FinnhubClient:
  def __init__(self, url):
    """
    Constructor
      url - Finnhub API websocket url.
      trades - Object key = stock symbol. values are price and timestamp.
      stocks - stock symbols client users want to monitor.
      ws - websocket to Finnhub API.
    """
    self.url = url
    self.trades = {}
    self.stocks = set()
    self.ws = None

  def create_trade(self, c, p, s, t, v):
    """
    Parse data from Finnhub websocket
      c - List of trade conditions.
      p - Last stock price.
      t - UNIX milliseconds timestamp.
      s - stock symbol.
      v - volume

    This app is only interested in price and timestamp.
    """
    return {
      "price": "{:.2f}".format(p),
      "timestamp": t,
    }

  def on_message(self, ws, message):
    """
    Stock data received from Finnhub API we subscribed to.
    Store the last stock trade in the trades variable.
    """
    response = json.loads(message)
    data = response["data"]
    message_type = response["type"]

    if (message_type == "trade"):
      for entry in data:
        trade = self.create_trade(**entry)
        symbol = entry["s"]
        timestamp = trade["timestamp"]

        if symbol in self.trades:
          if timestamp >= self.trades[symbol]["timestamp"]:
            self.trades[symbol] = trade
        else:
          self.trades[symbol] = trade

  def on_error(self, ws, error):
    """
    Print any errors received from the websocket (ws)
    """
    print(error)

  def on_close(self, ws, close_status_code, close_msg):
    """
    If the websocket is closed, restart the connection.
    """
    print("### Websocket connection closed ###")

  def on_open(self, ws):
    """
    If the websocket is opened, subscribe to stocks our users
    are interested in.
    """
    print("### Websocket connection opened ###")
    for stock in self.stocks:
      self.ws.send(json.dumps({"type":"subscribe","symbol": stock}))

  def send_message(self, stock):
    """
    Subscribe new stocks our users want to monitor to the Finnhub API.
    """
    if stock in self.stocks:
      return

    connected = self.ws and self.ws.sock and self.ws.sock.connected
    if connected:
      self.ws.send(json.dumps({"type":"subscribe","symbol": stock}))
      self.stocks.add(stock)

  def close(self):
    """
    Properly close the websocket
    """
    if self.ws:
      self.ws.close()
    self.ws = None

  def restart(self):
    """
    Close the websocket.
    Start a new connection after five seconds.
    """
    self.close()
    time.sleep(5)
    self.start()

  def start(self):
    """
    Establish a websocket connection to the Finnhub API.
    """
    print("### Attempting to start websocket connection... ###")
    websocket.enableTrace(False)
    self.ws = websocket.WebSocketApp(self.url,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
    self.ws.on_open = self.on_open
