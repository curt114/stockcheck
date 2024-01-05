"""
==============================================================================
NAME: CURT LEBENSORGER
DATE: 12/19/2023
==============================================================================
"""

"""
https://pypi.org/project/requests/
"""
import time
import requests

class Api:
  def __init__(self, stocks_to_watch_url, stocks_us_to_post_url, stocks_url, stocks_us_url):
    """
    Constructor
      stores multiple URLs for the node.js server.
      timeout is the amount of time in seconds to wait for a response
      from the node.js server.
    """
    self.stocks_to_watch_url = stocks_to_watch_url
    self.stocks_us_to_post_url = stocks_us_to_post_url
    self.stocks_url = stocks_url
    self.stocks_us_url = stocks_us_url
    self.timeout = 5

  def post_stocks(self, ws_client, key):
    """
    Send the most current stock trades to the node.js server.
    Repeat this action every second.
    """
    while True:
      try:
        response = requests.post(self.stocks_url,
                                json={'data': ws_client.trades, 'key': key},
                                timeout=self.timeout)
      except:
        print("Not able to post data.")
      time.sleep(1)

  def retrieve_stocks(self, ws_client):
    """
    Check the node.js server if any users want to monitor
    more stocks.
    If there are more stocks to monitor, subscribe the stock
    to the Finnhub API.
    Repeat this action every second.
    """
    while (True):
      if ws_client:
        try:
          response = requests.get(self.stocks_to_watch_url,
                                  timeout=self.timeout)
          watch = response.json()
          for stock in watch:
            ws_client.send_message(stock)
        except:
          print("Reconnecting...")
      else:
        print("Websocket is closed.")
      time.sleep(1)

  def retrieve_us_stocks(self):
    """
    Retrieve a list of all stock exchanges in the US.
    """
    retrieved = False
    result = []
    while (retrieved == False):
      try:
        print("Attempting to retrieve US stocks")
        response = requests.get(self.stocks_us_url, timeout=self.timeout)
        us_stocks = response.json()

        for stock in us_stocks:
          result.append({
            "description": stock["description"],
            "displaySymbol": stock["displaySymbol"]
          })
        retrieved = True
        print("US stocks successfully retrieved from Finnhub.")
      except:
        print("Not able to retrieve US stock data.")
        time.sleep(1)
    return [ result, retrieved ]

  def post_us_stocks(self, us_stocks, key):
    """
    Post all stocks in the US stock exchange to the node.js server.
    """
    sent = False

    while (sent == False):
      try:
        print("Attempting to post US stocks.")
        response = requests.post(self.stocks_us_to_post_url,
                                json={'data': us_stocks, 'key': key},
                                timeout=self.timeout)
        sent = True
        print("US stocks have been successfully posted.")
      except:
        print("Not able to send US stock data.")
        time.sleep(1)

  def us_stocks(self, key):
    """
    Retrieve a list of all US stock exchanges from the Finnhub API.
    Post all US stock exchanges to the node.js server.
    """
    while True:
      [ us_stocks, retrieved ] = self.retrieve_us_stocks()
      if retrieved:
        self.post_us_stocks(us_stocks, key)
      time.sleep(30)
