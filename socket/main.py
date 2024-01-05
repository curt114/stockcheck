"""
=======================================================
NAME: CURT LEBENSORGER
PROJECT: AUTOMATE REAL TIME STOCK TRADES
DATE: 12/19/2023
=======================================================
"""

"""
https://pypi.org/project/python-dotenv/
"""
import threading
import os
import rel
from finnhub_websocket import FinnhubClient
from api import Api
from dotenv import load_dotenv

def main():
  """
    load_dotenv is used to store environment variables

    Establish two classes
      ws_client
        Creates websocket connection to Finnhub API
        Allows this script to send and receive information
      queries
        GET and POST requests to node.js (express) server

    Threads
      This application has four threads that work concurrently
      together.
      main thread - Establishes websocket connection
      thread_two - Retrieves stocks users want to monitor
      thread_three - Posts stock data to node.js server
      thread_four - Retrieves all US stock exchanges from Finnhub API
  """
  load_dotenv(dotenv_path="../.env")
  finnhub_api_key = os.getenv('FINNHUB_API_KEY')
  domain = os.getenv('SERVER_DOMAIN')
  key = os.getenv('SECRET_KEY')

  finnhub_websocket_url = f"wss://ws.finnhub.io?token={finnhub_api_key}"
  stocks_to_watch_url = f"{domain}/api/v1/stocks/watch"
  stocks_us_to_post_url = f"{domain}/api/v1/stocks/us"
  stocks_url = f"{domain}/api/v1/stocks"
  stocks_us_url = f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={finnhub_api_key}"

  ws_client = FinnhubClient(finnhub_websocket_url)
  queries = Api(stocks_to_watch_url, stocks_us_to_post_url, stocks_url, stocks_us_url)

  thread_two = threading.Thread(target=queries.retrieve_stocks,
                                  args=(ws_client,))
  thread_three = threading.Thread(target=queries.post_stocks,
                                  args=(ws_client, key))
  thread_four = threading.Thread(target=queries.us_stocks,
                                  args=(key,))

  thread_two.start()
  thread_three.start()
  thread_four.start()

  ws_client.start()

  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
  ws_client.ws.run_forever(dispatcher=rel, reconnect=5)
  rel.signal(2, rel.abort)
  rel.dispatch()

  thread_two.join()
  thread_three.join()
  thread_four.join()

if __name__ == "__main__":
    main() # Entry point of program