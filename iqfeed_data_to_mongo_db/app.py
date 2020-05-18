import pandas as pd
import logging
import datetime
import json
import glob
import os

from data_import import move_csv_to_mongo_db


def read_config():
    with open("config.json") as json_file:
        configuration = json.load(json_file)
    return configuration


def update_config(configuration):
    with open("config.json", 'w') as json_file:
        json.dump(configuration, json_file, indent=4)
    return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("mongo_saver")
    currentDT = datetime.datetime.now()
    handler = logging.FileHandler("vnpy_data_to_mongo" + currentDT.strftime("%Y_%m_%d_%H_%M_%S") + ".log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # constant year and month_codes
    __YEARS__ = ["06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]
    __MONTH_CODES__ = ["F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"]

    # read info from config
    config = read_config()
    symbols_frame = pd.read_csv(config["symbols_csv_path"])
    symbols_frame = symbols_frame.loc[19:, ]
    data_folder = config["data_folder_path"]
    path_list = glob.glob(os.path.join(config["data_folder_path"], "*.csv"))

    for ix, row in symbols_frame.iterrows():
        symbol_root = row.loc["symbol_roots"]
        symbol_ib_root = row.loc["symbol_ib_roots"]
        symbol_exchange = row.loc["symbol_exchange"]
        for year in __YEARS__:
            for month_code in __MONTH_CODES__:
                symbol = "".join([symbol_root, month_code, year])
                symbol_csv_string = "".join([symbol, "_1.csv"])
                symbol_csv_path = os.path.join(data_folder, symbol_csv_string)
                ib_symbol = "".join([symbol_ib_root, month_code, year])
                if symbol_csv_path in path_list:
                    move_csv_to_mongo_db(symbol_csv_path,
                                         ib_symbol,
                                         symbol_exchange,
                                         logger)
