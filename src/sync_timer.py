import config
import datetime
import sync_logic

last_sync_result = None
last_sync_interval_begin_timestamp = None


def initial_sync():
    global last_sync_result
    global last_sync_interval_begin_timestamp
    print('Initializing trade synchronization from Binance to Firefly-III\n')
    begin_of_sync_timestamp = config.sync_begin_timestamp
    last_sync_interval_begin_timestamp = import_all_from_binance(begin_of_sync_timestamp)
    last_sync_result = 'ok'
    return


def sync():
    global last_sync_interval_begin_timestamp
    global last_sync_result

    if last_sync_interval_begin_timestamp is None:
        print("SYNC: The sync was not initialized properly")
        exit(-700)
    if last_sync_result is None or not last_sync_result.lower() == 'ok':
        print("SYNC: The last sync did not finish successful: " + last_sync_result)
        exit(-700)

    config_sync_interval = config.sync_inverval
    sync_interval(last_sync_interval_begin_timestamp, config_sync_interval)


def sync_interval(begin_timestamp_in_millis, interval):
    global last_sync_interval_begin_timestamp
    global last_sync_result

    current_datetime = datetime.datetime.now()

    print("Now: " + str(datetime.datetime.now()))
    print("Last Interval Begin: " + str(datetime.datetime.fromtimestamp(begin_timestamp_in_millis / 1000)))

    previous_last_sync_interval_begin_timestamp = last_sync_interval_begin_timestamp
    last_sync_interval_begin_timestamp = get_last_interval_begin_millis(config.sync_inverval, current_datetime)

    last_sync_result = sync_logic.interval_processor(previous_last_sync_interval_begin_timestamp, last_sync_interval_begin_timestamp, False)


def get_last_interval_begin_millis(interval, current_datetime):
    if interval == 'hourly':
        epoch_counter = int(current_datetime.timestamp() / (60 * 60))
        last_epoch = epoch_counter - 1
        return last_epoch * 60 * 60 * 1000
    elif interval == 'daily':
        epoch_counter = int(current_datetime.timestamp() / (60 * 60 * 24))
        last_epoch = epoch_counter - 1
        return last_epoch * 60 * 60 * 24 * 1000
    elif interval == 'debug':
        epoch_counter = int(current_datetime.timestamp() / 10)
        return epoch_counter * 10 * 1000
    else:
        print("The configured interval is not supported. Use 'hourly' or 'daily' within your config.")
        exit(-749)


def import_all_from_binance(begin_of_sync_timestamp):
    current_datetime = datetime.datetime.now()
    to_timestamp = get_last_interval_begin_millis(config.sync_inverval, current_datetime)
    begin_timestamp = int(datetime.datetime.fromisoformat(config.sync_begin_timestamp).timestamp() * 1000)
    sync_logic.interval_processor(begin_timestamp, to_timestamp, True)
    return to_timestamp


def add_trade_to_firefly(trade):
    return
