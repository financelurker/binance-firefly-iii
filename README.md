# binance-firefly-iii

This collection of scripts lets you sync your Binance account to your FireFly-III account. Keep an overview of your traded crypto assets.

This module runs stateless next to your Firefly-iii instance (as Docker container or standalone) and periodically processes new data from Binance. Just spin it up and watch your trades being imported right away.

Disclaimer:
This app needs access tokens for your Firefly-III instance and a valid API-Key for your Binance account. It is aboslutely okay to only give read-permissions to that Binance API-Key, as there will be no writing actions to Binance itself.

## Imported Movements from Binance to Firefly-III

The following movements on your Binance account will be imported to your FireFly-III instance:

### Executed trades
- creates transactions for each trade happened
  - adds/lowers funds to/from your "security" account - the asset account of the coin you have bought or sold in that trade
  - lowers/adds funds to/from your "currency" account - the asset account of the coin you have sold or bought in that trade
  - transactions get a tag "binance" assigned
  - transactions get a note "py1binance2firefly3:binance-trade"
- Paid fees on trades
  - For each trade in Binance there is a paid commission (either in BNB or any other coin/token). For this paid commission an additional transaction is created, linking the asset account holding the commission currency and the Binance expense account.
  - transactions get a tag "binance" assigned
  - transactions get a note "py1binance2firefly3:binance-fee"
- _**Known limitations:**_
  - Only 500 transactions will be imported for each trading pair. (I'll fix that in the future with a more sophisticated import query with the Binance API)
  - Binance API rate limiting: if you run this app in debug mode the Binance API will be polled every 10 seconds. You'll probably get blocked sometime from further API calls. Make sure that you're using Binance testnet when running this in debug-mode to not interfer with your IP rates at Binance (or you know what you're doing).

### ToDos

- Deposits from / Withdrawals to your other crypto addresses
- Received Interest vía lending or staking
- On-/Off-ramping from or to SEPA asset account (via IBAN-matching)

## How to Use

### Prepare your Firefly-III instance

To import your movements from Binance your FireFly-III installation has to be extended as follows:

- Currencies for crypto coins/tokens
  - Add custom currencies which you are trading on Binance (e.g. name "Bitcoin", symbol "₿", code "BTC", digits "8")
- Asset Accounts for currency funds on Binance
  - Create exactly one account for each coin/token you trade on Binance (type = 'asset')
  - Make sure you select the currency for that account, so the code or symbol matches the trading symbol for that currency on Binance.
  - Add **"py1binance2firefly3:binance-fund"** to the notes of that account.
- Revenue Accounts for lending/staking revenues
  - For each coin/token you manage on Binance create exactly one new account (type = 'revenue')
  - Make sure you select the currency for that account, so the code or symbol matches the trading symbol for that currency on Binance.
  - Add **"py1binance2firefly3:binance-interest"** to the notes of that account.
- Expenses Accounts for fees
  - Create exactly one account for each possible crypto coins/tokens for paid fees.
  - Make sure you select the currency for that account, so the code or symbol matches the trading symbol for that currency on Binance.
  - Add **"py1binance2firefly3:binance-fees"** to the notes of that account.

### Working environments

- Firefly-III Version 5.4.6
- Binance API Change Log up to 2021-04-08

### Run it standalone

Check out the repository, make sure you set the environmental variables and start thy python script:

```
git clone https://github.com/financelurker/binance-firefly-iii.git
cd binance-firefly-iii
python -m pip install --upgrade setuptools pip wheel
python -m pip install --upgrade pyyaml
python -m pip install python-binance
python -m pip install Firefly-III-API-Client
python main.py
```

If you are having any troubles, make sure you're using **python 3.9** (the corresponding Docker image is **"python:3.9-slim-buster"** for version referencing).

### Run as Docker container

Check out the repository and build the docker image locally. Pass the environmental variables with your "docker run" command.

```
git clone https://github.com/financelurker/binance-firefly-iii.git
cd binance-firefly-iii
docker build .
docker run --env....
```

### Configuration

This image is configured via **environmental variables**. As there are many ways to set them up for your runtime environment please consult that documentation.

Make sure you have them set as there is no exception handling for missing values from the environment.
- **FIREFLY_HOST**
  - Description: The url to your Firefly-III instance you want to import trades. (e.g. "https://some-firefly-iii.instance:62443" and **make sure it's a test system for now!!**)
  - Type: string
- **FIREFLY_VALIDATE_SSL**
  - Description: Enables or disables the validation of ssl certificates, if you're using your own x509 CA.
    (there probably are better ways of doing this)
  - Type: boolean [ false | any ]
  - Optional
  - Default: true
- **FIREFLY_ACCESS_TOKEN**
  - Description: Your access token you have created within your Firefly-III instance.
  - Type: string
- **BINANCE_API_KEY**
  - Description: The api key of your binance account. It is highly recommended to create a dedicated api key with only read permissions on your Binance account.
  - Type: string
- **BINANCE_API_SECRET**
  - Description: The api secret of that api key.
  - Type: string
- **SYNC_BEGIN_TIMESTAMP**
  - Description: The date of the transactions must not be older than this timestamp to be imported. This helps you to import from back to 2017 initially and once you have imported them all you can set the date to a date near the container runtime start to reduce probable bandwith-costs on Binance-side. (e.g. "2018-01-22")
  - Type: date [ yyyy-MM-dd ]
- **SYNC_TRADES_INTERVAL**
  - Description: This defines on how often this module will check for new Binance trades.
    Only trades up to the last full interval (hour or day) are synchronized.
    The debug mode fetches every 10 seconds.
  - Type: enum [ hourly | daily | debug ]
- **DEBUG**
  - Description: Adds to each written object an additional tag 'dev'. Any other value than true will be handled as false and will disable debug tagging.
  - Type: boolean [ true | any ]
  - Optional
  - Default: false
