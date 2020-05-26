from vnpy.trader.constant import Interval, Exchange
import logging
import datetime
import glob
import os

from data_import import move_day_csv_to_mongo_db


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("mongo_saver")
    currentDT = datetime.datetime.now()
    handler = logging.FileHandler("vnpy_data_to_mongo" + currentDT.strftime("%Y_%m_%d_%H_%M_%S") + ".log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # read info from config
    data_folder = r"D:\data\iqfeed\stock\stock_data_day_per_exchange_iqfeed\amex"
    path_list = glob.glob(os.path.join(data_folder, "*.csv"))

    for path in path_list:
        symbol = os.path.basename(path)[:-6]
        move_day_csv_to_mongo_db(path,
                                 symbol,
                                 Exchange.NYSE.value,
                                 Interval.DAILY,
                                 logger)
