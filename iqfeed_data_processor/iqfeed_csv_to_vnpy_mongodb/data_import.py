from vnpy.trader.constant import (Exchange, Interval)
from vnpy.trader.database import database_manager
from vnpy.trader.object import (BarData)
import pandas as pd
import time
import datetime


def move_1_min_csv_to_mongo_db(csv_path: str, symbol: str, exchange: str, interval, logger):
    try:
        start_time = time.time()
        logger.info("saving {} starts".format(symbol))
        imported_data = pd.read_csv(csv_path)
        imported_data.columns = ["datetime", "open", "high", "low", "close", "volume"]
        imported_data.loc[:, "exchange"] = Exchange(exchange)
        imported_data.loc[:, "open_interest"] = 0.0
        imported_data.loc[:, "interval"] = interval
        imported_data.loc[:, "symbol"] = symbol
        datetime_format = '%Y%m%d %H:%M:%S'
        imported_data['datetime'] = pd.to_datetime(imported_data['datetime'], format=datetime_format)
        float_columns = ['open', 'high', 'low', 'close', 'volume', 'open_interest']
        for col in float_columns:
            imported_data.loc[:, col] = imported_data[col].astype('float')

        def move_df_to_mongodb(import_data: pd.DataFrame, collection_name: str):
            bars = []
            start = None
            count = 0
            bar = None

            for row in import_data.itertuples():

                bar = BarData(

                    symbol=row.symbol,
                    exchange=row.exchange,
                    datetime=row.datetime,
                    interval=row.interval,
                    volume=row.volume,
                    open_price=row.open,
                    high_price=row.high,
                    low_price=row.low,
                    close_price=row.close,
                    open_interest=row.open_interest,
                    gateway_name="DB",

                )

                bars.append(bar)

                # do some statistics
                count += 1
                if not start:
                    start = bar.datetime
            end = bar.datetime

            # insert into database
            database_manager.save_bar_data(bars, collection_name)
            print(f"Insert Bar: {count} from {start} - {end}")

        move_df_to_mongodb(imported_data, symbol)
        end_time = time.time()
        logger.info("time used is {}".format(end_time - start_time))
        logger.info("saving {} successful".format(symbol))
    except (ValueError, Exception):
        logger.info("saving {} failed".format(symbol))


def move_day_csv_to_mongo_db(csv_path: str, symbol: str, exchange: str, interval, logger):
    try:
        start_time = time.time()
        logger.info("saving {} starts".format(symbol))
        imported_data = pd.read_csv(csv_path)
        imported_data.columns = ["datetime", "open", "high", "low", "close", "volume", "open_interest"]
        imported_data.loc[:, "exchange"] = Exchange(exchange)
        imported_data.loc[:, "interval"] = interval
        imported_data.loc[:, "symbol"] = symbol
        datetime_format = '%Y-%m-%d'
        imported_data['datetime'] = pd.to_datetime(imported_data['datetime'], format=datetime_format)
        float_columns = ['open', 'high', 'low', 'close', 'volume', 'open_interest']
        for col in float_columns:
            imported_data.loc[:, col] = imported_data[col].astype('float')

        def move_df_to_mongodb(import_data: pd.DataFrame, collection_name: str):
            bars = []
            start = None
            count = 0
            bar = None

            for row in import_data.itertuples():

                bar = BarData(

                    symbol=row.symbol,
                    exchange=row.exchange,
                    datetime=row.datetime,
                    interval=row.interval,
                    volume=row.volume,
                    open_price=row.open,
                    high_price=row.high,
                    low_price=row.low,
                    close_price=row.close,
                    open_interest=row.open_interest,
                    gateway_name="DB",

                )

                bars.append(bar)

                # do some statistics
                count += 1
                if not start:
                    start = bar.datetime
            end = bar.datetime

            # insert into database
            database_manager.save_bar_data(bars, collection_name)
            print(f"Insert Bar: {count} from {start} - {end}")

        move_df_to_mongodb(imported_data, symbol)
        end_time = time.time()
        logger.info("time used is {}".format(end_time - start_time))
        logger.info("saving {} successful".format(symbol))
    except (ValueError, Exception):
        logger.info("saving {} failed".format(symbol))