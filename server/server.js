/*
=================================================
NAME: CURTIS LEBENSORGER
PROJECT: STOCKS SERVER
DATE: 12/28/2023
=================================================
*/

const dotenv = require('dotenv');
const express = require("express");
const app = express();
app.use(express.json({ limit: "50mb" }));
dotenv.config({path: "../.env"})

// Ip address and port to run server
const ip = "192.168.1.130";
const port = 5000;

let result = {};      // Real-time stock trades from Finnhub API
let stocksUs = [];    // US stock exchanges from Finnhub API
let watchStocks = [   // Initial stocks to watch and get real-time trades
  "BINANCE:BTCUSDT",
  "NVDA",
  "AMD",
  "AAPL",
  "META",
  "COST",
  "TSLA",
  "GOOGL",
];

app.get("/api/v1/stocks/watch", (request, response) => {
  // GET an array of stocks the users want to monitor
  response.json(watchStocks);
});

app.get("/api/v1/stocks/us", (request, response) => {
  // GET an array of US stock exchanges
  response.json(stocksUs);
});

app.get("/api/v1/stocks/", (request, response) => {
  // GET the current real-time trades data
  response.json(result);
});

app.post("/api/v1/stocks/watch", (request, response) => {
  // POST stock symbol to watchStocks if symbol is found in US stock exchange.
  const findSymbol = stocksUs.find(
    (stock) => stock.displaySymbol === request.body.symbol
  );

  if (!findSymbol) response.json("Stock not found.");

  const monitor = new Set(watchStocks);
  monitor.add(findSymbol.displaySymbol);
  watchStocks = [...monitor];
  response.json(`${request.body.symbol} has been added.`);
});

app.post("/api/v1/stocks/us", (request, response) => {
  // POST US stock exchanges to stocksUs variable
  stocksUs = request.body.data;
  response.json("Received US Stocks.");
});

app.post("/api/v1/stocks", (request, response) => {
  // POST real-time stock data from Finnhub API to the result variable
  result = request.body.data;
  response.json("Received");
});

app.listen(port, ip, () => {
  // Run the Node Server
  console.log(`Server is running at ${ip}:${port}`);
});
