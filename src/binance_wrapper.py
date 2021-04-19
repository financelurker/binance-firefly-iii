from __future__ import print_function
from binance.client import Client
from binance.exceptions import BinanceAPIException
from datetime import datetime

import config
from pprint import pprint

client = None

invalid_trading_pairs = []


def connect():
    try:
        print('Trying to connect to your Binance account...')

        new_client = Client(config.binance_api_key, config.binance_api_secret)
        info = new_client.get_account()
        # new_client.get_my_trades()

        print('Connection to your Binance account established.\n')
        # pprint(info)

        global client
        client = new_client

        lending_account = client.get_lending_account()

        return True
    except Exception as e:
        print('Cannot connect to your Binance account.' % e)
        exit(-500)


def get_list_of_trading_pairs(list_of_symbols_and_codes):
    global invalid_trading_pairs

    result = []

    for symbol_or_code in list_of_symbols_and_codes:
        for trading_symbol_or_code in list_of_symbols_and_codes:
            if symbol_or_code == trading_symbol_or_code:
                continue
            trading_pair = symbol_or_code + trading_symbol_or_code
            if any(trading_pair in s for s in invalid_trading_pairs):
                continue

            result.append(symbol_or_code + trading_symbol_or_code)

    return result


def get_trading_pair_message_log(list_of_trading_pairs):
    log_message = "Trading pairs: ["
    trading_pair_counter = 0
    for trading_pair in list_of_trading_pairs:
        if trading_pair_counter > 0:
            log_message += ","
        log_message += " \"" + trading_pair.pair + "\" "
        trading_pair_counter += 1
    log_message += "]"
    return log_message


def get_lendings():
    global client

    pass


def get_trades(from_timestamp, to_timestamp, list_of_trading_pairs):
    global client
    global invalid_trading_pairs

    trades_of_trading_pairs = []

    print("Get trades from " + str(datetime.fromtimestamp(from_timestamp / 1000)) + " to " + str(datetime.fromtimestamp(to_timestamp / 1000 - 1)))

    trading_pairs_log_message = get_trading_pair_message_log(list_of_trading_pairs)
    print(trading_pairs_log_message)

    for trading_pair in list_of_trading_pairs:
        try:
            if (to_timestamp - from_timestamp) / 1000 - 1 > 60 * 60 * 24:
                trades_total = client.get_my_trades(symbol=trading_pair.pair)
                relevant_trades = []
                for trade in trades_total:
                    if int(trade.get('time')) - from_timestamp >= 0:
                        relevant_trades.append(trade)
                my_trades = relevant_trades
            else:
                my_trades = client.get_my_trades(symbol=trading_pair.pair, startTime=from_timestamp, endTime=to_timestamp)
            if len(my_trades) > 0:
                trades_of_trading_pairs.append(my_trades)
                print("Found " + str(len(my_trades)) + " trades for " + trading_pair.pair)
        except BinanceAPIException as e:
            if e.status_code == 400 and e.code == -1100:
                # print("Invalid character found in trading pair: " + trading_pair)
                invalid_trading_pairs.append(trading_pair.pair)
            elif e.status_code == 400 and e.code == -1121:
                # print("Invalid trading pair found: " + trading_pair)
                invalid_trading_pairs.append(trading_pair.pair)
            else:
                pprint(e)

    return trades_of_trading_pairs


def get_valid_trading_pairs(list_of_symbols_and_codes):
    list_of_valid_trading_pairs = []
    return list_of_valid_trading_pairs
