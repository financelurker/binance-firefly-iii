from __future__ import print_function

import datetime

import urllib3
import firefly_iii_client
import config
from enum import Enum


class TradingPair(object):
    def __init__(self, from_coin, to_coin, pair):
        self.security = from_coin
        self.currency = to_coin
        self.pair = pair


class TransactionCollection(object):
    def __init__(self, _trading_pair, _binance_transaction, _from_ff_account, _to_ff_account, _commission_ff_account,
                 _collection_type, _from_commission_account):
        self.trading_pair = _trading_pair
        self.binance_transaction = _binance_transaction
        self.from_ff_account = _from_ff_account
        self.to_ff_account = _to_ff_account
        self.commission_account = _commission_ff_account
        self.collection_type = _collection_type
        self.from_commission_account = _from_commission_account


class CollectionType(Enum):
    BUY = 1
    SELL = 2


class FireflyAccountCollection(object):
    def __init__(self, security):
        self.security = security
        self.asset_account = None
        self.expense_account = None
        self.revenue_account = None

    def set_expense_account(self, _expense_account):
        self.expense_account = _expense_account

    def set_revenue_account(self, _revenue_account):
        self.revenue_account = _revenue_account

    def set_asset_account(self, _asset_account):
        self.asset_account = _asset_account


urllib3.disable_warnings()

firefly_config = None


def connect():
    try:
        print('Trying to connect to your FireFly-III account...')

        firefly_iii_client.configuration.verify_ssl = False

        configuration = firefly_iii_client.configuration.Configuration(
            host=config.firefly_host
        )

        configuration.verify_ssl = config.firefly_verify_ssl
        configuration.access_token = config.firefly_access_token

        # Enter a context with an instance of the API client
        with firefly_iii_client.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = firefly_iii_client.AboutApi(api_client)

            try:
                api_instance.get_about()
            except Exception as e:
                print("Cannot get server instance About information." % e)

        print('Connection to your FireFly-III account established.\n')
        global firefly_config
        firefly_config = configuration
        return True
    except Exception as e:
        print('Cannot connect to your FireFly-III account.' % e)
        exit(-600)


def get_binance_symbols_and_codes():
    with firefly_iii_client.ApiClient(firefly_config) as api_client:
        # Create an instance of the API class
        accounts_api = firefly_iii_client.AccountsApi(api_client)

        try:
            accounts = accounts_api.list_account().data

            list_of_symbols_and_codes = []
            relevant_accounts = []

            for account in accounts:
                if account.attributes.type == 'asset' and \
                        account.attributes.notes is not None and \
                        "py1binance2firefly3:binance-fund" in account.attributes.notes:
                    relevant_accounts.append(account)

            print(str(relevant_accounts.__len__()) + " Binance accounts found within your FireFly-III instance.")

            for account in relevant_accounts:
                if not any(account.attributes.currency_code in s for s in list_of_symbols_and_codes):
                    list_of_symbols_and_codes.append(account.attributes.currency_code)
                if not any(account.attributes.currency_symbol in s for s in list_of_symbols_and_codes):
                    list_of_symbols_and_codes.append(account.attributes.currency_symbol)

            return list_of_symbols_and_codes
        except Exception as e:
            print('There was an error getting the accounts' % e)
            exit(-601)


def write_commission(transaction_collection):
    with firefly_iii_client.ApiClient(firefly_config) as api_client:
        transaction_api = firefly_iii_client.TransactionsApi(api_client)
        list_inner_transactions = []

        currency_code = transaction_collection.from_ff_account.currency_code
        currency_symbol = transaction_collection.from_ff_account.currency_symbol
        amount = transaction_collection.binance_transaction.get('quoteQty')
        foreign_amount = float(transaction_collection.binance_transaction.get('qty'))

        tags = ['binance']
        if config.debug:
            tags.append('dev')

        split = firefly_iii_client.TransactionSplit(
            amount=amount,
            date=datetime.datetime.fromtimestamp(int(transaction_collection.binance_transaction.get('time') / 1000)),
            description="Binance | FEE | Security: " + transaction_collection.trading_pair.security + " | Currency: " + currency_code + " | Ticker " + transaction_collection.trading_pair.pair,
            type='withdrawal',
            tags=tags,
            source_name=transaction_collection.from_ff_account.name,
            source_type=transaction_collection.from_ff_account.type,
            currency_code=currency_code,
            currency_symbol=currency_symbol,
            destination_name=transaction_collection.commission_account.name,
            destination_type=transaction_collection.commission_account.type,
            external_id=transaction_collection.binance_transaction.get('id'),
            notes="py1binance2firefly3:binance-trade"
        )
        list_inner_transactions.append(split)
        new_transaction = firefly_iii_client.Transaction(apply_rules=False, transactions=list_inner_transactions)

        try:
            pass
            # print('Writing a new transaction.')
            # pprint(new_transaction)
            # transaction_api.store_transaction(new_transaction)
        except Exception as e:
            print('There was an error writing a new transaction' % e)
            exit(-602)


def write_new_transaction(transaction_collection):
    with firefly_iii_client.ApiClient(firefly_config) as api_client:
        transaction_api = firefly_iii_client.TransactionsApi(api_client)
        list_inner_transactions = []
        if transaction_collection.collection_type == CollectionType.BUY:
            type_string = "BUY"
        else:
            type_string = "SELL"

        if type_string == "BUY":
            currency_code = transaction_collection.from_ff_account.currency_code
            currency_symbol = transaction_collection.from_ff_account.currency_symbol
            foreign_currency_code = transaction_collection.to_ff_account.currency_code
            foreign_currency_symbol = transaction_collection.to_ff_account.currency_symbol
            amount = transaction_collection.binance_transaction.get('quoteQty')
            foreign_amount = float(transaction_collection.binance_transaction.get('qty'))
        else:
            currency_code = transaction_collection.from_ff_account.currency_code
            currency_symbol = transaction_collection.from_ff_account.currency_symbol
            foreign_currency_code = transaction_collection.to_ff_account.currency_code
            foreign_currency_symbol = transaction_collection.to_ff_account.currency_symbol
            amount = transaction_collection.binance_transaction.get('qty')
            foreign_amount = float(transaction_collection.binance_transaction.get('quoteQty'))

        tags = ['binance']
        if config.debug:
            tags.append('dev')

        split = firefly_iii_client.TransactionSplit(
            amount=amount,
            date=datetime.datetime.fromtimestamp(int(transaction_collection.binance_transaction.get('time') / 1000)),
            description='Binance | ' + type_string + " | Security: " + transaction_collection.trading_pair.security + " | Currency: " + transaction_collection.trading_pair.currency + " | Ticker " + transaction_collection.trading_pair.pair,
            type='transfer',
            tags=tags,
            source_name=transaction_collection.from_ff_account.name,
            source_type=transaction_collection.from_ff_account.type,
            currency_code=currency_code,
            currency_symbol=currency_symbol,
            destination_name=transaction_collection.to_ff_account.name,
            destination_type=transaction_collection.to_ff_account.type,
            foreign_currency_code=foreign_currency_code,
            foreign_currency_symbol=foreign_currency_symbol,
            foreign_amount=foreign_amount,
            external_id=transaction_collection.binance_transaction.get('id'),
            notes="py1binance2firefly3:binance-trade"
        )
        list_inner_transactions.append(split)
        new_transaction = firefly_iii_client.Transaction(apply_rules=False, transactions=list_inner_transactions)

        try:
            print('Writing a new transaction.')
            # pprint(new_transaction)
            transaction_api.store_transaction(new_transaction)
        except Exception as e:
            print('There was an error writing a new transaction' % e)
            exit(-602)


def get_binance_currencies_for_accounts(accounts):
    with firefly_iii_client.ApiClient(firefly_config) as api_client:
        # Create an instance of the API class
        currency_api = firefly_iii_client.CurrenciesApi(api_client)

        try:
            relevant_currencies = []

            for account in accounts:
                print('Fetching currency with code ' + str(account.attributes.currency_code))
                account_currency = currency_api.get_currency(account.attributes.currency_code)
                relevant_currencies.append(account_currency.data)

            return relevant_currencies
        except Exception as e:
            print('There was an error while getting currencies from FireFly-III' % e)
            exit(-603)


def get_account_from_firefly(security, account_type, notes_keywords):
    with firefly_iii_client.ApiClient(firefly_config) as api_client:
        # Create an instance of the API class
        accounts_api = firefly_iii_client.AccountsApi(api_client)
        try:
            accounts = accounts_api.list_account().data

            for account in accounts:
                if account.attributes.type == account_type and \
                        account.attributes.notes is not None and \
                        notes_keywords in account.attributes.notes:
                    if security is None:
                        return account
                    else:
                        if account.attributes.currency_code == security or account.attributes.currency_symbol == security:
                            return account
        except Exception as e:
            print('There was an error getting the accounts from Firefly-III' % e)
            exit(-604)
    return None


def get_asset_account_for_security(security):
    return get_account_from_firefly(security, 'asset', 'py1binance2firefly3:binance-fund')


def get_expense_account_for_security(security):
    return get_account_from_firefly(None, 'expense', 'py1binance2firefly3:binance-fees')


def get_revenue_account_for_security(security):
    return get_account_from_firefly(security, 'revenue', 'py1binance2firefly3:binance-interest')


def create_firefly_account_collection(security):
    result = FireflyAccountCollection(security)

    asset_account = get_asset_account_for_security(security)
    result.set_asset_account(asset_account)

    expense_account = get_expense_account_for_security(security)
    result.set_expense_account(expense_account)

    revenue_account = get_revenue_account_for_security(security)
    result.set_revenue_account(revenue_account)

    return result


def get_firefly_account_collections_for_pairs(list_of_trading_pairs):
    result = []

    relevant_securities = []
    for trading_pair in list_of_trading_pairs:
        if any(trading_pair.security in s for s in relevant_securities):
            continue
        relevant_securities.append(trading_pair.security)
    for trading_pair in list_of_trading_pairs:
        if any(trading_pair.currency in s for s in relevant_securities):
            continue
        relevant_securities.append(trading_pair.currency)
    for relevant_security in relevant_securities:
        result.append(create_firefly_account_collection(relevant_security))

    return result


def import_transaction_collection(transaction_collection):
    write_new_transaction(transaction_collection)
    write_commission(transaction_collection)


def import_transaction_collections(transaction_collections):
    for transaction_collection in transaction_collections:
        import_transaction_collection(transaction_collection)
