import pandas as pd
import multiprocessing
import os
import time
import glob
os.environ['NUMEXPR_MAX_THREADS'] = '12'
os.environ['NUMEXPR_NUM_THREADS'] = '12'


def chunks(lst, n) -> list:
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


if __name__ == "__main__":

    data_path = r"e:\data\zipline_csv_data\daily_stock"
    symbol_list = pd.read_csv(
        r"E:\project\trade_engine\data_processing\quandl_data_processor\stock_symbols.csv").loc[
                  :, "symbols"].tolist()

    _start_time = time.time()
    for symbol in symbol_list:
        try:
            if not os.path.exists(os.path.join(data_path, symbol + ".csv")):
                stock_data_store = pd.HDFStore(r'E:\project\trade_engine\data_processing\quandl_data_processor\stock_day.h5')
                # 从hdf中把数据读进内存中
                symbol_frame = stock_data_store.select('day', where=['symbol=="{}"'.format(symbol)])
                new_frame = pd.DataFrame()
                new_frame.loc[:, "open"] = symbol_frame.loc[:, "adj_open"]
                new_frame.loc[:, "high"] = symbol_frame.loc[:, "adj_high"]
                new_frame.loc[:, "low"] = symbol_frame.loc[:, "adj_low"]
                new_frame.loc[:, "close"] = symbol_frame.loc[:, "adj_close"]
                new_frame.loc[:, "volume"] = symbol_frame.loc[:, "adj_volume"]
                new_frame.loc[:, "divedend"] = symbol_frame.loc[:, "dividends"]
                new_frame.loc[:, "split"] = symbol_frame.loc[:, "splits"]
                new_frame.to_csv(os.path.join(data_path, symbol + ".csv"))
        except Exception:
            print("{} fails".format(symbol))



    # 记录用时F
    _end_time = time.time()
    print("Finished using time {:.2f}".format(_end_time - _start_time))
